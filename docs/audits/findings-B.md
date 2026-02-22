# Audit Findings: Domain B (Workflow Steps)
**Audited:** 2026-02-21
**Checks performed:** 10
**Findings:** 9 (S1: 1, S2: 5, S3: 3)

---

## Findings

### B1: `review-skeletons/` and `review-reports/` missing from Step 0 mkdir command
- **Category**: UNDOCUMENTED
- **Severity**: S2
- **Intent**: Intentional
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:336 — `mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts,pc,summaries}`
- **Impl source**: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-068ecc83/` and `_session-7edaafbb/` — both contain `review-reports/` and `review-skeletons/` directories not listed in the mkdir command
- **Impact**: The mkdir at Step 0 only creates 5 subdirectories. The two missing ones are created later by separate agents/scripts: `review-skeletons/` is created by `compose-review-skeletons.sh` (called by Pantry Section 1), and `review-reports/` is created explicitly at RULES.md line 175 (`mkdir -p "${SESSION_DIR}"/review-reports`) before the review CCO gate. The lazy-creation design is intentional — these directories don't exist until their respective workflow phases. However, the Step 0 Session Directory section implies the mkdir command is the complete setup and makes no mention that two more directories will appear later, leaving a reader with an incomplete mental model of the session directory structure.
- **Suggested fix**: Add a note after RULES.md line 336 listing the two late-created dirs and when they appear: "`review-skeletons/` — created by Pantry (compose-review-skeletons.sh, Step 2); `review-reports/` — created at Step 3b-iii." Alternatively, document all expected subdirs in a comment block below the mkdir command.

---

### B2: `parse-progress-log.sh` exit codes match RULES.md documentation — PASS (see Checks That Passed)

---

### B3: Scout mode parameters consistent across all three sources — PASS (see Checks That Passed)

---

### B4: SSV model `haiku` omitted from RULES.md Model Assignments table
- **Category**: UNDOCUMENTED
- **Severity**: S3
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:292-304 — Model Assignments table contains rows for PC — CCO, PC — WWD, PC — DMVDC, PC — CCB, but no row for PC — SSV
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:89 — `(`pest-control`, `model: "haiku"`) for Scout Strategy Verification (SSV)`; `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:613 — `**Model**: \`haiku\` (pure set comparisons — no judgment required)`
- **Impact**: The model assignment for PC — SSV is specified correctly in two places (Step 1b prose and checkpoints.md), so no Queen following the workflow would use the wrong model. However, the Model Assignments table is intended as a complete reference and a reader who consults only the table would not find SSV listed. SSV artifact `pc-session-ssv-20260221-173632.md` was found in `_session-068ecc83/pc/`, confirming SSV runs in practice. The artifact path also matches the Hard Gates table entry (`${SESSION_DIR}/pc/pc-session-ssv-{timestamp}.md` at line 257).
- **Suggested fix**: Add a row to the Model Assignments table between Scout and Pantry (impl):

  ```
  | PC — SSV | Task (`pest-control`) | haiku | Pure set comparisons — no judgment required |
  ```

---

### B4b: CCO artifact naming spec (per-task) contradicts actual practice (per-wave/session-wide)
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: UNCERTAIN
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:179 — `\`{SESSION_DIR}/pc/pc-{TASK_SUFFIX}-cco-{timestamp}.md\`` and example at line 28: `pc-74g1-cco-20260215-001145.md`
- **Impl source**: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-068ecc83/pc/pc-session-cco-20260221-133156.md` and `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-7edaafbb/pc/pc-session-cco-20260220-221023.md` — both sessions use `pc-session-cco-{timestamp}.md` (session-wide format), not per-task `pc-{TASK_SUFFIX}-cco-{timestamp}.md`
- **Impact**: checkpoints.md specifies that the CCO output for Dirt Pushers should be written to a per-task file (e.g., `pc-74g1-cco-20260215-001145.md`). In practice, the Queen batches all wave prompts and spawns a single Pest Control to audit all prompts at once, producing one session-wide report. The Hard Gates table in RULES.md uses the wildcard `${SESSION_DIR}/pc/*-cco-*.md` (line 258), which matches the actual `pc-session-cco-*` pattern. The checkpoints.md template prompt instructs PC to write to a per-task path, but PC uses its own judgment and writes a batch report. A future Pest Control agent strictly following the checkpoints.md template might write per-task files, causing the wildcard gate to continue working but making the naming inconsistent with the documented convention. Whether the per-task spec was intentional design (abandoned in favor of batch) or an oversight is unclear.
- **Suggested fix**: Either (a) update checkpoints.md CCO Dirt Pushers section to document that when the Queen batches multiple prompts into one CCO run, the output file should use the session-wide naming convention `pc-session-cco-{timestamp}.md`, or (b) update the RULES.md Hard Gates table to use the more specific per-task pattern and require per-task files.

---

### B5: Wave pipelining — evidence confirms documented behavior (PASS with observation)

Session `_session-7edaafbb` progress log and file timestamps show confirmed pipelining:
- Wave 1 Dirt Pushers spawned: `2026-02-21T03:46:25Z`
- Wave 2 Pantry previews written: `2026-02-21T03:54Z` (EST timestamp `Feb 20 22:54` converts to `Feb 21 03:54 UTC`)
- Wave 1 WAVE_VERIFIED: `2026-02-21T03:55:57Z`
- Wave 2 spawned: `2026-02-21T04:07:10Z`

The wave 2 Pantry ran concurrently with wave 1 Dirt Pushers (overlap window: `03:46–03:55 UTC`), exactly as RULES.md Step 2 documents (`wave pipelining` section, lines 107–115). This is a MATCH. No finding.

---

### B6: WWD run timing — documented as per-agent, observed as batched; entirely absent in large session
- **Category**: CONTRADICTION
- **Severity**: S1
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:118-119 — `after each agent commits, spawn Pest Control (\`model: "haiku"\`) for Wandering Worker Detection (WWD) (scope check before next agent in the wave can proceed)`; `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`:264 — `**When**: After agent commits, BEFORE spawning next agent in same wave`
- **Impl source (session 068ecc83)**: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-068ecc83/pc/` — 6 WWD files present (per-task naming: `pc-oc9v-wwd-*`, `pc-6jxn-wwd-*`, `pc-n0or-wwd-*`, etc.). All 3 wave-1 commits occurred within 8 seconds (`12:50:36`, `12:50:41`, `12:50:44 EST`); WWD artifacts appeared 47–78 seconds later at `12:51:31`, `12:51:36`, `12:52:02 EST` — effectively batched, not individually gated.
- **Impl source (session 7edaafbb)**: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-7edaafbb/pc/` — **zero WWD artifacts** despite wave 1 having 7 agents across 26 tasks. No `*-wwd-*` files exist anywhere in the session directory.
- **Impact**: The documentation states WWD is mandatory after every agent commit to prevent scope creep from cascading. checkpoints.md even cites a known failure mode (Epic 74g, agent 74g.6) where WWD would have caught the violation. In session `_session-7edaafbb` (30 tasks, largest observed session), WWD was entirely skipped — no artifacts, no evidence it ran. This is the highest-risk gap: the S1 severity is because the "before next agent in wave" blocking behavior described in docs was not enforced. In `_session-068ecc83`, WWD did run but the timing shows all three were triggered at nearly the same time (agents committed simultaneously), making the per-agent serialization gate effectively meaningless for that case.
- **Suggested fix**: Two separate fixes needed:
  1. (Process) Add an explicit note in RULES.md Step 3 that when agents are spawned in parallel and commit roughly simultaneously, WWD gates are run in batch after all commits, not one-by-one — and this is acceptable for fully parallel waves.
  2. (Compliance) Investigate why `_session-7edaafbb` has no WWD artifacts. If WWD was intentionally skipped for the large 26-task wave, document the exception criteria. If it was accidentally skipped, flag it as a process violation.

---

### B7: Review team composition matches between RULES.md and reviews.md — PASS (see Checks That Passed)

---

### B8: Dummy reviewer described in RULES.md, prompt files exist in sessions, but output reports absent
- **Category**: UNDOCUMENTED
- **Severity**: S3
- **Intent**: Intentional
- **Doc source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:186-219 — `**3b-v. Spawn dummy reviewer** (context usage instrumentation — sunset after ~30 sessions)` including: `Write your report to ${SESSION_DIR}/review-reports/dummy-review-${TIMESTAMP}.md`
- **Impl source**: `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-068ecc83/prompts/review-dummy.md` — dummy prompt file exists (copy of correctness prompt); `/Users/correy/projects/ant-farm/.beads/agent-summaries/_session-7edaafbb/prompts/review-dummy.md` — same. No `dummy-review-*.md` files found anywhere in either session's `review-reports/` directory via exhaustive search.
- **Impact**: The dummy reviewer is documented to write its output to `${SESSION_DIR}/review-reports/dummy-review-${TIMESTAMP}.md`. The prompt is copied correctly in both sessions, meaning Step 1 of the dummy reviewer process (copy prompt) was completed. The tmux launch (Step 2) may or may not have completed, but the output report was never written (or was deleted). RULES.md explicitly states the report "is discarded" and excluded from Big Head, so the absence of the output file does not affect workflow correctness. The dummy reviewer is instrumentation, not a gate. This is S3 because the missing output means the context-usage data collection goal was silently not achieved, but no workflow step depends on it.
- **Suggested fix**: Add a note to RULES.md Step 3b-v clarifying that the dummy reviewer output will only appear if the tmux window successfully runs. Consider adding a check: after the review team completes, verify whether the dummy output file exists (log a note if missing — do not block workflow). Alternatively, if the dummy reviewer is consistently failing to produce output, advance the sunset timeline.

---

### B9: Termination and round-cap logic consistent between RULES.md and reviews.md — PASS (see Checks That Passed)

---

### B10: CLAUDE.md Landing the Plane section annotated as "RULES.md Step 6" but spans Steps 4-6; Step-level content diverges
- **Category**: CONTRADICTION
- **Severity**: S2
- **Intent**: Accidental
- **Doc source**: `/Users/correy/projects/ant-farm/CLAUDE.md`:54 — `(Corresponds to RULES.md Step 6.)` labels the entire 8-step Landing the Plane section as corresponding to RULES.md Step 6 only
- **Impl source**: `/Users/correy/projects/ant-farm/orchestration/RULES.md`:244-251:
  - `**Step 4:** Documentation — update CHANGELOG, README, CLAUDE.md in single commit`
  - `**Step 5:** Verify — cross-references valid, all tasks have CHANGELOG entries`
  - `**Step 6:** Land the plane — git pull --rebase, bd sync, git push, clean up stashes and remote branches`
- **Impact**: CLAUDE.md line 54 states the entire Landing section "Corresponds to RULES.md Step 6." However, CLAUDE.md's 8-step workflow covers material from RULES.md Steps 4, 5, and 6:
  - CLAUDE.md steps 1 ("File issues for remaining work") and 2 ("Run quality gates") have no direct equivalent in RULES.md Steps 4-6.
  - CLAUDE.md step 3 ("Review-findings gate") overlaps with RULES.md Step 3c, not Step 6.
  - CLAUDE.md step 4 ("Update issue status — Close finished work") has no explicit equivalent in RULES.md.
  - CLAUDE.md step 5 ("PUSH TO REMOTE") with `git status # MUST show "up to date with origin"` corresponds to RULES.md Step 6 but adds the `git status` verification not mentioned in RULES.md.
  - CLAUDE.md steps 7 ("Verify") and 8 ("Hand off") have no RULES.md equivalents.
  - RULES.md Step 4 (documentation commit) and Step 5 (cross-reference verification) are entirely absent from CLAUDE.md's landing section.

  A Queen following CLAUDE.md's landing checklist would skip the CHANGELOG/README/CLAUDE.md documentation commit (RULES.md Step 4) and the cross-reference verification (RULES.md Step 5) because those steps are not present in CLAUDE.md's 8-step list. Conversely, a Queen following only RULES.md Step 6 would skip CLAUDE.md's steps 1-4, 7-8. Both files are read (CLAUDE.md as system prompt, RULES.md mid-turn), so a Queen sees both — but the false cross-reference annotation creates confusion about which is authoritative.
- **Suggested fix**: Update CLAUDE.md line 54 to read `(Corresponds to RULES.md Steps 4-6.)` and add the missing steps from RULES.md to CLAUDE.md's landing checklist between steps 3 and 4: a step for "Update documentation (CHANGELOG, README, CLAUDE.md in a single commit)" and a step for "Verify cross-references — all tasks have CHANGELOG entries." Also add the `git status` verification to RULES.md Step 6 to close the gap in the other direction.

---

## Checks That Passed (MATCHes)

**B2** (`parse-progress-log.sh` exit codes): RULES.md lines 352-354 documents exit 0 (resume-plan written), exit 1 (error: missing arg, missing dir, missing log, unreadable log, write failure), and exit 2 (SESSION_COMPLETE present, no resume-plan). The script at `/Users/correy/projects/ant-farm/scripts/parse-progress-log.sh` exactly implements all three codes at lines 34, 42, 47, 52, 192, and 293. No drift.

**B3** (Scout mode parameters): All four modes (`ready`, `epic <epic-id>`, `tasks <id1>, <id2>, ...`, `filter <description>`) appear in all three sources. RULES.md lines 79-82 lists all four. `agents/scout-organizer.md` lines 21-24 lists all four. `orchestration/templates/scout.md` lines 34-39 defines all four with their corresponding `bd` CLI calls. No drift.

**B4 (SSV artifact path)**: The Hard Gates table in RULES.md line 257 (`${SESSION_DIR}/pc/pc-session-ssv-{timestamp}.md`) matches the actual artifact in `_session-068ecc83/pc/pc-session-ssv-20260221-173632.md`. The pattern also matches checkpoints.md line 696 (`\`{SESSION_DIR}/pc/pc-session-ssv-{timestamp}.md\``). MATCH.

**B5** (Wave pipelining): Confirmed by timestamp analysis above. Wave N+1 Pantry ran concurrently with wave N Dirt Pushers in `_session-7edaafbb`. MATCH.

**B7** (Review team composition): RULES.md line 179 says "Round 1: 6 members — 4 reviewers + Big Head + Pest Control." `reviews.md` line 60 says "Round 1: the Queen creates the Nitpicker team with **6 members** (4 reviewers + Big Head + Pest Control)." `reviews.md` line 172 confirms "Team size: 6 (4 reviewers + Big Head + Pest Control)." Round 2+ is also consistent: RULES.md line 180 says 4 members; `reviews.md` lines 82 and 180 say 4 members. Session evidence: both `_session-068ecc83/review-skeletons/` and `_session-7edaafbb/review-skeletons/` contain exactly 5 skeleton files (`skeleton-big-head.md`, `skeleton-clarity.md`, `skeleton-correctness.md`, `skeleton-edge-cases.md`, `skeleton-excellence.md`) — the 4 reviewer types plus Big Head, consistent with the 6-member team (PC joins as a team member with its own prompt, not a skeleton file). MATCH.

**B9** (Termination and round-cap logic): RULES.md lines 226-229 specify termination at zero P1/P2 and state the decision is logged as `decision=terminated`. Lines 232-236 specify round cap at round 4. `reviews.md` lines 188-197 specify the same termination condition and the same "After round 4" escalation cap. Progress logs confirm: `_session-068ecc83` logged `decision=terminated` at round 2; `_session-7edaafbb` logged `decision=terminated` at round 2 — both consistent with the documented termination check. MATCH.

**Pre-identified finding #7** (confirmed as B1 above): `review-skeletons/` and `review-reports/` present in all observed sessions but absent from the Step 0 mkdir command. Confirmed S2 UNDOCUMENTED. The intent is intentional (lazy creation by respective workflow phases) but undocumented in the Session Directory section.
