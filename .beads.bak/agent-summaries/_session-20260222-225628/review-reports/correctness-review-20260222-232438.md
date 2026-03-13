# Report: Correctness Review

**Scope**: orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/checkpoints.md, orchestration/templates/reviews.md
**Reviewer**: Correctness Review — Nitpicker (sonnet)
**Review round**: 1
**Commit range**: de35516..HEAD

---

## Findings Catalog

### Finding 1: `team_name: "nitpickers"` in reviews.md does not match canonical team name "nitpicker-team"

- **File(s)**: `orchestration/templates/reviews.md:985`
- **Severity**: P1
- **Category**: correctness
- **Description**: The Fix Workflow section of reviews.md introduces fix agents using `team_name: "nitpickers"`, but the team is created in big-head-skeleton.md with `name="nitpicker-team"` and every other reference in RULES.md consistently uses `"nitpicker-team"`. Using `"nitpickers"` would cause the Task tool to target a non-existent team, causing all fix agent spawns to fail at runtime. References confirming `"nitpicker-team"` as canonical: RULES.md:237, 319, 339, 341, 343, 536, 537, 538, 649; big-head-skeleton.md:30, 46.
- **Suggested fix**: Change `team_name: "nitpickers"` to `team_name: "nitpicker-team"` at reviews.md:985.
- **Acceptance criterion violated**: ant-farm-ygmj.3 AC: "Fix workflow section describes fix DPs and fix PCs spawning into the persistent team via Task with team_name parameter" — the parameter value is wrong.

---

### Finding 2: `briefs/` directory referenced in reviews.md round-transition does not exist in session directory structure

- **File(s)**: `orchestration/templates/reviews.md:1091`
- **Severity**: P2
- **Category**: correctness
- **Description**: The round-transition section for re-tasking the Correctness reviewer lists `"Brief path: {session-dir}/briefs/review-brief-<timestamp>.md (same brief, new scope)"`. The `briefs/` subdirectory does not exist in the canonical session directory structure (RULES.md:572 defines the mkdir: `{task-metadata,previews,prompts,pc,summaries}`). No `briefs/` directory is created at Step 0 or lazily. The Queen following this instruction would send a nonexistent file path to reviewers in the round-transition SendMessage, causing reviewers to attempt to read a file that isn't there.
- **Suggested fix**: Either change `{session-dir}/briefs/review-brief-<timestamp>.md` to an existing path (e.g., `{session-dir}/prompts/review-correctness.md` or the relevant task-metadata file), or document and create the `briefs/` directory in RULES.md's Session Directory section.
- **Acceptance criterion context**: ant-farm-ygmj.3 AC: "Round transition protocol uses SendMessage to re-task Correctness and Edge Cases reviewers" — the round transition is documented but references a nonexistent artifact path.

---

### Finding 3: Edge Cases reviewer output path omitted from both RULES.md and reviews.md round-transition specification

- **File(s)**: `orchestration/RULES.md:393`, `orchestration/templates/reviews.md:1094`
- **Severity**: P2
- **Category**: correctness
- **Description**: Step 3c-iv in RULES.md specifies the Correctness reviewer output path explicitly as `{SESSION_DIR}/review-reports/correctness-r<N+1>-<timestamp>.md`. For the Edge Cases reviewer, it says "same fields as above" (RULES.md:393) and reviews.md says "same fields as above" (reviews.md:1094) — with no distinct output path. Big Head in step 3 of the round transition receives "Report paths: paths from step 1 and 2 above" (RULES.md:395), meaning it needs both paths. But the edge-cases output path is never defined: by symmetry the Queen would produce `edge-cases-r<N+1>-<timestamp>.md`, but this is not stated. If the Queen reads this specification and applies "same fields" literally, both reviewers could write to the correctness path, corrupting the correctness report. The pattern `edge-cases-r<N+1>-<timestamp>.md` is never defined in the canonical output path table (reviews.md:50 only shows `edge-cases-review-<timestamp>.md` for round 1).
- **Suggested fix**: At RULES.md:393 and reviews.md:1094, add an explicit output path: `{SESSION_DIR}/review-reports/edge-cases-r<N+1>-<timestamp>.md` as a distinct field, mirroring the Correctness reviewer's path definition.
- **Acceptance criterion violated**: ant-farm-ygmj.4 AC: "Step 3c documents: Big Head handoff -> Scout (outside team) -> SSV -> fix agents spawn into team -> inner loop -> round transition" — the round-transition fields are incomplete.

---

## Preliminary Groupings

### Group A: Team name mismatch (Finding 1)
- Finding 1 — standalone
- Root cause: reviews.md fix workflow section uses the wrong `team_name` literal value, diverging from the canonical name established in big-head-skeleton.md and repeated throughout RULES.md.
- **Combined fix**: Change `"nitpickers"` → `"nitpicker-team"` at reviews.md:985.

### Group B: Incomplete round-transition specification (Findings 2 and 3)
- Finding 2 + Finding 3 — same root cause: the round-transition SendMessage fields in the reviews.md and RULES.md round-transition section are underspecified. The `briefs/` path is phantom, and the edge-cases output path is absent. Both problems affect the same protocol (the Queen's SendMessage re-tasking in Step 3c-iv).
- **Combined fix**: Audit the full field list for the round-transition SendMessages and either (a) remove the non-existent `briefs/` path field, or replace it with the correct path, and (b) add explicit edge-cases output path.

---

## Summary Statistics

- Total findings: 3
- By severity: P1: 1, P2: 2, P3: 0
- Preliminary groups: 2

---

## Acceptance Criteria Verification

### ant-farm-ygmj.1 — Upgrade CCB to sonnet and add root cause spot-check

| Criterion | Result | Evidence |
|-----------|--------|----------|
| CCB prompt in checkpoints.md specifies model as sonnet | PASS | checkpoints.md:517: `**Model**: \`sonnet\` (judgment required for bead quality and dedup correctness)` |
| Check 3b exists between Check 3 and Check 4 with spot-check instructions | PASS | checkpoints.md:276-298: Check 3b inserted after Check 3 (Bead Quality Check), before Check 4 (Priority Calibration) |
| Check 3b includes SUSPECT severity distinction (minor vs material) | PASS | checkpoints.md:579-588: "Minor" and "Material" distinctions with different actions |
| Material escalation path documented: PARTIAL verdict -> context-degradation-suspected -> fresh Big Head -> full review -> re-run CCB -> user escalation | PASS | checkpoints.md:583-588: all 6 escalation steps present |
| RULES.md Model Assignments table shows CCB as sonnet | PASS | RULES.md:532: `PC — CCB \| Task (\`pest-control\`) \| sonnet \| Judgment: bead quality and dedup correctness` |
| Existing CCB checks 0-7 unchanged | PASS | checkpoints.md:544-628: Checks 0, 1, 2, 3, 4, 5, 6, 7 all present; Check 3b is additive |

**Verdict: PASS** — all 6 criteria met.

---

### ant-farm-ygmj.2 — Add bead-list handoff to Big Head skeleton

| Criterion | Result | Evidence |
|-----------|--------|----------|
| big-head-skeleton.md contains handoff step after bead filing that sends structured message to Queen | PASS | big-head-skeleton.md:182-254: Step 12 added after step 11 (round 2+ P3 auto-filing) |
| Handoff message format includes bead IDs, priorities, root cause titles, and consolidated report path | PASS | big-head-skeleton.md:230-244: template shows all required fields |
| Message sent via SendMessage (not written to file) | PASS | big-head-skeleton.md:182: "send a structured handoff message to the Queen via SendMessage" |
| P3 beads clearly separated from P1/P2 | PASS | big-head-skeleton.md:239-242: "P3 beads (no action required — auto-filed to Future Work)" section shown separately |
| Handoff step clearly labeled and sequenced after CCB PASS | PASS | big-head-skeleton.md:182-184: Step 12 sequencing with round 1 vs round 2+ timing defined |

**Verdict: PASS** — all 5 criteria met.

---

### ant-farm-ygmj.3 — Rewrite fix workflow for in-team agents

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Fix workflow section describes fix DPs and fix PCs spawning into persistent team via Task with team_name parameter | FAIL — P1 | reviews.md:985 uses `team_name: "nitpickers"` instead of `"nitpicker-team"` |
| Fix inner loop protocol documented: DP -> fix-pc-wwd -> fix-pc-dmvdc -> iterate on fail (max 2 retries) | PASS | reviews.md:1044-1063: ASCII diagram and retry limit description present |
| Pantry/CCO skip rationale documented | PASS | reviews.md:1019-1026: rationale for both Pantry and CCO skip present |
| Round transition protocol uses SendMessage to re-task Correctness and Edge Cases reviewers | PASS (partial) | reviews.md:1086-1102: SendMessage re-tasking documented; however, edge-cases output path and `briefs/` path reference are incorrect (see Findings 2 and 3) |
| Fix-cycle Scout documented as auto-approved with SSV gate | PASS | reviews.md:989-994: auto-approval and SSV gate documented |
| Fix DP prompt structure shown (lean prompt, bead as source of truth) | PASS | reviews.md:1019-1036: lean prompt template present |
| Naming convention for fix team members documented | PASS | reviews.md:1006-1016: naming table with round suffixes present |

**Verdict: PASS WITH ISSUES** — 1 P1 finding, 1 P2 finding from this task.

---

### ant-farm-ygmj.4 — Update RULES.md for persistent team and fix inner loop

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Step 3b explicitly states team persists across full loop | PASS | RULES.md:159-164: "Team persistence" block added; "NOT torn down" stated |
| Step 3c documents: Big Head handoff -> Scout (outside team) -> SSV -> fix agents spawn into team -> inner loop -> round transition | PASS (partial) | RULES.md:319-405: all six phases documented; "outside team" for Scout is implicit (scout-organizer runs as Task agent, not team member) but not explicit |
| Fix-cycle Scout documented as auto-approved with SSV gate as mechanical safety net | PASS | RULES.md:327-333: auto-approval and SSV PASS/FAIL paths documented |
| Model Assignments table updated: CCB sonnet, fix-pc-wwd haiku, fix-pc-dmvdc sonnet, fix DPs sonnet | PASS | RULES.md:532, 536, 537, 538: all four rows updated correctly |
| Error handling covers fix DP stuck/crash, fix PC crash, reviewer failure, Big Head crash, CCB material fail | PASS | RULES.md:647-652: all five error scenarios added |
| Team naming conventions documented | PASS | RULES.md:164-165: naming convention shown in team roster progression |
| Progress log format includes new milestones for fix cycle steps | PASS | RULES.md:334, 358, 385, 400: FIX_SCOUT_COMPLETE, FIX_AGENTS_SPAWNED, FIX_DMVDC_COMPLETE, ROUND_TRANSITION milestones all added |

**Verdict: PASS WITH ISSUES** — inherited issues from reviews.md (Finding 2, 3) affect the round-transition specification consistency.

---

## Cross-Review Messages

### Sent
- To drift-reviewer: "Found stale team name reference at reviews.md:985 (`nitpickers` vs `nitpicker-team`) — this is primarily a correctness issue (wrong runtime value) but has a drift dimension: the team name was established in big-head-skeleton.md and didn't propagate to the reviews.md fix workflow. May want to scan for other uses of the old name."
- To drift-reviewer (reply): "Already filed as P1 Finding 1 with explicit AC citation for ygmj.3. File in your drift report too — Big Head will deduplicate."
- To edge-cases-reviewer (reply): "Polling loop logic is correct under single-invocation constraint; the reset-on-multi-call failure mode is your edge-cases domain."

### Received
- From edge-cases-reviewer: "Polling loop logic in big-head-skeleton.md (reviews.md:519-630) may have correctness issue — ELAPSED never advances if Big Head calls Bash per iteration." — Action taken: verified loop logic under stated single-invocation constraint. Logic is correct (terminates after 15 × 2s iterations = 30s). The reset-on-multi-call failure mode is a constraint-violation edge case, not a logic error in the script. Replied that this is correctly in edge-cases domain; no additional correctness finding added.
- From drift-reviewer: "Team name mismatch at reviews.md:985 — `nitpickers` vs `nitpicker-team` — may also mean acceptance criteria for ygmj.3/.4 not fully met." — Action taken: confirmed already filed as Finding 1 (P1) with explicit AC citation for ygmj.3. Advised drift-reviewer to also file in their report; Big Head will deduplicate.

### Deferred Items
- Polling loop termination under multi-call Bash usage — deferred to edge-cases-reviewer; constraint-violation scenario, not a logic error under the stated design.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| orchestration/RULES.md | Findings: #3 (partial), otherwise reviewed — no issues beyond those noted | 700 lines reviewed; Steps 3b-3c-iv and Model Assignments table checked against all 7 acceptance criteria for ygmj.4; retry table checked for new rows |
| orchestration/templates/big-head-skeleton.md | Reviewed — no issues | 220 lines reviewed; Step 12 new content verified against all 5 ygmj.2 acceptance criteria; SendMessage format, P3/P1/P2 separation, round 1 vs 2+ sequencing confirmed |
| orchestration/templates/checkpoints.md | Reviewed — no issues | ~900 lines reviewed; CCB model change verified, Check 3b insertion verified, existing Checks 0-7 verified unchanged; SUSPECT minor/material distinction verified; escalation path all 6 steps verified |
| orchestration/templates/reviews.md | Findings: #1 (P1), #2 (P2), #3 (P2) | ~1132 lines reviewed; Fix Workflow section fully reviewed; round-transition SendMessage fields checked; team_name literal verified against all other occurrences; `briefs/` path cross-referenced against RULES.md session directory definition |

---

## Overall Assessment

**Score**: 6/10
**Verdict**: NEEDS WORK

The implementation correctly satisfies all acceptance criteria for ant-farm-ygmj.1 (CCB sonnet upgrade + spot-check) and ant-farm-ygmj.2 (Big Head handoff step). Most of ant-farm-ygmj.3 and ygmj.4 is also correct.

However, one P1 defect will cause runtime failure: `reviews.md:985` specifies `team_name: "nitpickers"` instead of the canonical `"nitpicker-team"`, meaning fix agent spawns will target a non-existent team. Two P2 defects underspecify the round-transition protocol: a phantom `briefs/` directory path and a missing edge-cases reviewer output path definition. These need correction before the fix workflow can operate correctly end-to-end.
