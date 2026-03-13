# Report: Correctness Redux Review

**Scope**: AGENTS.md, agents/pantry-review.md, orchestration/RULES.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
**Reviewer**: Correctness Redux Review (code-reviewer)

---

## Findings Catalog

### Finding 1: reviews.md fallback section references typo — `review-clarify.md` instead of `review-clarity.md`
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:130`
- **Severity**: P2
- **Category**: correctness
- **Description**: The fallback workflow (Step 1 of Fallback Workflow) lists the prompt file as `review-clarify.md`. The canonical short name for the clarity review type is `clarity` (see Review Type Canonical Names table, reviews.md:53). The correct filename is `review-clarity.md`. An agent following this fallback path would look for the wrong file, fail to find it, and be unable to spawn the clarity reviewer.
- **Suggested fix**: Change `review-clarify.md` to `review-clarity.md` at line 130 in `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md`.
- **Cross-reference**: None. Correctness domain only.
- **Acceptance criteria source**: ant-farm-3mk — "Both the team path and fallback path produce the same output artifacts (4 review reports)." A filename typo breaks the fallback path and prevents it from producing the clarity review report.

---

### Finding 2: pantry.md Section 2 polling loop adaptation still says "adapt from reviews.md" — circular dependency not fully resolved
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md:422`
- **Severity**: P2
- **Category**: correctness
- **Description**: The fix for ant-farm-s2g (circular reference) inlined the Big Head deduplication protocol, bead filing instructions, consolidated summary format, and P3 auto-filing instructions directly into pantry.md Section 2. However, the **polling loop** adaptation note at line 422 now reads: "When composing the Big Head brief, include report path checks for the current round: round 1 includes all 4 reports …; round 2+ includes only correctness and edge-cases reports." This is descriptive guidance — the actual polling loop code/template was NOT inlined. The original text (pre-fix) read "adapt the Step 0a polling loop from reviews.md," which was the circular reference. The new text avoids naming reviews.md, but a cold Pantry agent must still find and read the polling loop template somewhere — it is not self-contained in pantry.md. The acceptance criterion for ant-farm-s2g is: "A cold Pantry agent can compose the Big Head data file by reading only pantry.md." The polling loop shell script (with timeout, sleep, etc.) resides entirely in `reviews.md` Big Head Consolidation Protocol Step 0a. Without that code, the Pantry cannot compose a correct Big Head brief that includes a working polling loop.
- **Suggested fix**: Inline the complete polling loop template from `reviews.md` Step 0a directly into pantry.md Section 2 Step 4, so a cold Pantry agent reading only pantry.md has everything it needs.
- **Cross-reference**: Related to ant-farm-s2g acceptance criterion.
- **Acceptance criteria source**: ant-farm-s2g — "A cold Pantry agent can compose the Big Head data file by reading only pantry.md."

---

### Finding 3: pantry.md Section 2 still references reviews.md implicitly for Big Head Step 0 verification gate
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md:311-424`
- **Severity**: P3
- **Category**: correctness
- **Description**: The inlined Big Head bead filing instructions and deduplication protocol in pantry.md are complete. However, the Big Head Consolidation Protocol in reviews.md also includes Step 0 (Verify All Reports Exist — the MANDATORY GATE) and Step 0a (remediation path/polling loop). These steps are substantive behavioural requirements for Big Head. The pantry.md Section 2 Big Head data file composition instructions (Step 4) do not include Step 0 or Step 0a — they are only in reviews.md. The Pantry's job is to write the Big Head data file that Big Head executes. If the Pantry doesn't know to include Step 0/Step 0a in that data file, Big Head may not perform the prerequisite gate. This is a lower-severity extension of Finding 2.
- **Suggested fix**: Either (a) inline Step 0 and Step 0a into pantry.md Section 2 Step 4 alongside the polling loop (combined fix with Finding 2), or (b) explicitly note that Step 0/0a are part of big-head-skeleton.md (if they are), so the Pantry knows they are handled by the skeleton and not the data file.
- **Cross-reference**: Groups with Finding 2.
- **Acceptance criteria source**: ant-farm-s2g — "pantry.md Section 2 is self-contained for Big Head data file composition."

---

### Finding 4: RULES.md Step 3b-i timestamp format string is inconsistent with RULES.md Step 0 date command
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:104`
- **Severity**: P3
- **Category**: correctness
- **Description**: The fix for ant-farm-7qp updated RULES.md Step 3b-i to read: "The Queen generates ONE timestamp at the start of Step 3b using `date +%Y%m%d-%H%M%S` format (YYYYMMDD-HHMMSS)." The format specifier `%H%M%S` is correct for HH:MM:SS without separators. However, the format string itself (`%Y%m%d-%H%M%S`) is not a bash command — it is presented as inline guidance without the full `date +...` invocation that would appear in a real terminal command. The SESSION_ID at Step 0 uses `date +%s | shasum | head -c 6` — a complete command. The Step 3b timestamp lacks the shell expansion context (`SESSION_TIMESTAMP=$(date +%Y%m%d-%H%M%S)`). An agent reading Step 3b-i literally has to infer how to store and pass this timestamp. The inconsistency is cosmetic but could cause an agent to produce the timestamp correctly yet fail to store it in a variable for reuse.
- **Suggested fix**: Add an explicit shell variable assignment example: `REVIEW_TIMESTAMP=$(date +%Y%m%d-%H%M%S)`. Mirrors the Session Directory setup block style at Step 0.
- **Cross-reference**: None.
- **Acceptance criteria source**: ant-farm-7qp — "The chosen owner's workflow step explicitly includes when and how to generate the timestamp."

---

### Finding 5: pantry-review.md still exists as an agent definition despite pantry-review being deprecated
- **File(s)**: `/Users/correy/projects/ant-farm/agents/pantry-review.md:1-72`
- **Severity**: P3
- **Category**: correctness
- **Description**: RULES.md Agent Types table (line 180) marks `pantry-review` as **Deprecated**: "replaced by `fill-review-slots.sh` bash script called directly by Queen in Step 3b." The agent file `agents/pantry-review.md` still exists and was modified in this commit range. Its timestamp instructions were correctly updated to point to the Queen as owner. However, the file itself is a registered agent type that the system will load. If a Queen reads RULES.md and sees the deprecation notice, but then an agent's template cross-references or accidentally spawns `pantry-review`, the timestamp fix in this file is wasted — or worse, the agent runs with the updated instructions but the "DEPRECATED" marking in RULES.md is never seen by the agent itself. The file's header at line 1-5 does not include any deprecation warning, so a Queen or other agent discovering it cold would not know it is deprecated.
- **Suggested fix**: Add a deprecation notice at the top of `agents/pantry-review.md`: "DEPRECATED: This agent is no longer spawned by the Queen. See RULES.md Step 3b — `fill-review-slots.sh` replaces this workflow." This is a documentation gap that could cause re-activation by a future agent. P3 since the RULES.md deprecation notice is authoritative.
- **Cross-reference**: Clarity domain may also flag this.
- **Acceptance criteria source**: Not directly tied to a specific task. General correctness concern about a deprecated agent with no deprecation signal in the file itself.

---

### Finding 6: AGENTS.md review-findings gate added but step number conflict with CLAUDE.md
- **File(s)**: `/Users/correy/projects/ant-farm/AGENTS.md:23`
- **Severity**: P3
- **Category**: correctness
- **Description**: The fix for ant-farm-7hl added a Step 3 "Review-findings gate" to AGENTS.md. AGENTS.md now has 8 steps (Step 1–8). CLAUDE.md also has 8 steps and matches the sequence. However, reviewing them: AGENTS.md Step 3 says "If reviews ran and found P1 issues, present findings to user before proceeding." CLAUDE.md Step 3 says "If reviews ran and found P1 issues…". These are identical in substance — the fix correctly aligned them. One minor discrepancy: AGENTS.md Step 6 cleanup note is "(Session artifacts in .beads/agent-summaries/_session-*/ are retained for posterity. Prune old sessions manually when needed.)" while CLAUDE.md Step 6 has the same note. This is a clean match. The acceptance criterion "diff of landing sections between files shows no contradictions in step sequence" is met.
- **Suggested fix**: None required — this is an observation that the fix is correct.
- **Cross-reference**: N/A (no issue found).
- **Acceptance criteria source**: ant-farm-7hl — all criteria met.

---

### Finding 7: Wrong runtime path for scripts — `~/.claude/orchestration/scripts/` does not exist
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md:148`, `/Users/correy/projects/ant-farm/orchestration/RULES.md:108`
- **Severity**: P2
- **Category**: correctness
- **Description**: Both pantry.md (Section 1, Step 2.5) and RULES.md (Step 3b-ii) reference scripts at the path `~/.claude/orchestration/scripts/`. Verified on disk: `~/.claude/orchestration/scripts/` does not exist. The actual scripts live at `scripts/` in the repo root, syncing at runtime to `~/.claude/scripts/` (not `~/.claude/orchestration/scripts/`). RULES.md Path Reference Convention (lines 6-11) documents `orchestration/` → `~/.claude/orchestration/` and `agents/` → `~/.claude/agents/` but makes no mention of `scripts/`. The correct runtime invocations are:
  - `bash ~/.claude/scripts/compose-review-skeletons.sh ...` (pantry.md:148)
  - `bash ~/.claude/scripts/fill-review-slots.sh ...` (RULES.md:108)
  Running the documented command would fail with "No such file or directory." Any Pantry or Queen agent following these instructions would be unable to assemble review skeletons or fill review slots.
- **Suggested fix**: Update both references to use `~/.claude/scripts/` and update the Path Reference Convention in RULES.md to document the `scripts/` → `~/.claude/scripts/` translation alongside the existing `orchestration/` and `agents/` mappings.
- **Cross-reference**: Flagged by edge-cases-reviewer (Finding 4, P2) — confirmed as also a correctness failure since the path is functionally wrong. Big Head should merge these.
- **Acceptance criteria source**: Not tied to a specific task in this session. The scripts were relied on by ant-farm-7qp and ant-farm-s2g fixes (both use fill-review-slots.sh or compose-review-skeletons.sh paths). A broken path defeats the workflow added to resolve those tasks.

---

### Finding 8: round=0 passes validation and produces silently wrong reviewer composition
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:104`
- **Severity**: P3
- **Category**: correctness
- **Description**: RULES.md Step 3b-i states "Review round: read from session state (default: 1)." Neither RULES.md nor pantry.md enforces a minimum of 1 before invoking `fill-review-slots.sh`. If a Queen passes `round=0` (e.g., uninitialized state, typo), the script would receive 0, evaluate `0 -eq 1` as false, and produce only the round-2+ reviewer set (correctness + edge-cases) instead of all 4 round-1 reviewers — silently wrong output with no error. The impact is: a session that intended a full round-1 review would get a partial review without any error surfaced. Severity is P3 rather than P2 because the "default: 1" in Step 3b-i makes round=0 require an explicit override, and the shell script input validation is out of scope for this review. The risk is real but requires an unusual error condition.
- **Suggested fix**: Add a guard in RULES.md Step 3b-i: "Verify REVIEW_ROUND ≥ 1 before calling fill-review-slots.sh. A value of 0 will produce an incorrect reviewer composition without error."
- **Cross-reference**: Flagged by edge-cases-reviewer (Finding 2, P2) — I assess this as P3 from a correctness standpoint since the trigger requires a state error that the documented default prevents. Big Head should adjudicate the final severity from both reports.
- **Acceptance criteria source**: Not tied to a specific closed task.

---

### Finding 9: reviews.md fallback section "round 2+" coverage is incomplete
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:119-155`
- **Severity**: P3
- **Category**: correctness
- **Description**: The fallback workflow describes step 1 as "For each review type (clarity, edge-cases, correctness, excellence)." This hardcodes round 1 behavior (4 review types). Round 2+ uses only 2 reviewers (correctness, edge-cases). The fallback section does not mention how to adapt for round 2+. A Queen using the fallback in round 2 would spawn 4 reviewers (all types) when only 2 are required. The acceptance criterion for ant-farm-3mk is "Both the team path and fallback path produce the same output artifacts (4 review reports)." The fallback is meant to be a drop-in replacement for the team path, and both the team path and fallback are round-aware — the round-awareness is specified for the team path (lines 88-106) but absent from the fallback section.
- **Suggested fix**: Add round-awareness to the fallback Workflow Step 1: "Round 1: spawn clarity, edge-cases, correctness, excellence (4 reviewers). Round 2+: spawn correctness, edge-cases only (2 reviewers)."
- **Cross-reference**: None.
- **Acceptance criteria source**: ant-farm-3mk — "Both the team path and fallback path produce the same output artifacts." In round 2+ the fallback would produce 4 reports when 2 are expected.

---

### Finding 10: Deprecated `pantry-review` agent described as live in GLOSSARY.md and README.md — correctness risk if Queen reads those files first
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/GLOSSARY.md:81`, `/Users/correy/projects/ant-farm/README.md:275`, `/Users/correy/projects/ant-farm/agents/pantry-review.md:3`
- **Severity**: P2
- **Category**: correctness
- **Description**: Flagged for investigation by excellence-reviewer (P3 maintainability). After checking all references, the correctness risk is elevated to P2.

  The only in-session deprecation signal is the strikethrough in RULES.md lines 180 and 194. However:
  - `GLOSSARY.md:81` describes Pantry as having two active forms — `pantry-impl` (implementation) and `pantry-review` (review) — with no deprecation marker. A Queen reading the glossary cold would treat `pantry-review` as the canonical agent for review mode.
  - `README.md:275` lists `pantry-review` in the agent capabilities table with description "Review prompt composer: builds review briefs and combined previews" and no deprecation marker.
  - `agents/pantry-review.md:3` (the agent's own description field) reads "Use for Step 3b review cycles" — a positive, present-tense instruction. The Claude Code agent loader reads this description and could surface it as a valid spawn target.
  - `scout.md:61` does explicitly exclude `pantry-review` from Dirt Pusher recommendations — this is protective for the Scout path, but the Queen does not spawn review agents via the Scout.

  The RULES.md strikethrough-in-table pattern is not reliable on its own: (a) a Queen that reads GLOSSARY.md or README.md before RULES.md has positive evidence the agent is live; (b) `agents/pantry-review.md` itself contains no deprecation notice, so a Queen or any agent that discovers it through agent discovery would see an active, positively-described agent type. The risk is not hypothetical — the Queen's Template Lookup table (RULES.md, bottom) points to `pantry.md` for "Composing agent prompts (Step 2)"; pantry.md Section 2 now says "DEPRECATED … Do NOT spawn `pantry-review`" but Section 2 is the deprecated section itself, meaning a Queen that skips to Section 2 for review mode would read the deprecation notice. However, a Queen consulting GLOSSARY.md as a reference (which is a natural thing to do) would get conflicting information.
- **Suggested fix**: (a) Add a deprecation notice to `GLOSSARY.md:81`: mark `pantry-review` as deprecated, remove it from the "two forms" description; (b) add a deprecation marker to `README.md:275`; (c) update `agents/pantry-review.md` description field from "Use for Step 3b review cycles" to "DEPRECATED — do not spawn. Replaced by fill-review-slots.sh (RULES.md Step 3b)."
- **Cross-reference**: Flagged by excellence-reviewer as P3 architecture concern. Upgraded to P2 because out-of-scope documents (GLOSSARY.md, README.md) actively contradict the RULES.md deprecation, creating a realistic spawn risk. Big Head should note the severity difference between our two reports.
- **Acceptance criteria source**: Not tied to a specific closed task in this session. The GLOSSARY.md and README.md are out-of-scope files for this commit range but their conflicting state creates a correctness risk introduced by this session's deprecation of pantry-review.

---

## Preliminary Groupings

### Group A: Incomplete self-containment of pantry.md Section 2 (circular reference not fully resolved)
- Finding 2, Finding 3 — both stem from the same root cause: the fix for ant-farm-s2g inlined deduplication/bead-filing/summary-format content from reviews.md but did not inline the Big Head Step 0/Step 0a prerequisite gate and polling loop. The Pantry cannot produce a fully correct Big Head data file from pantry.md alone.
- **Suggested combined fix**: Inline Step 0 (file existence check) and Step 0a (polling loop with timeout) from reviews.md Big Head Consolidation Protocol into pantry.md Section 2 Step 4. One block of content covers both findings.

### Group B: reviews.md fallback section defects (typo + round-awareness gap + script path)
- Finding 1, Finding 9 — both are defects in the newly added fallback section in reviews.md. Finding 1 is a typo; Finding 9 is a missing round-conditional. Both would cause fallback mode to malfunction.
- Finding 7 (script wrong path) also affects the fallback section's effectiveness — even if the fallback were invoked, it relies on the same broken script paths.
- **Suggested combined fix**: A single editorial pass on the fallback section: fix the typo, add round-conditional instructions, and update the script path references.

### Group C: Wrong script paths across RULES.md and pantry.md
- Finding 7 — `~/.claude/orchestration/scripts/` does not exist; correct path is `~/.claude/scripts/`. Affects both RULES.md:108 and pantry.md:148.
- **Suggested combined fix**: Update both path references in a single commit; add `scripts/` → `~/.claude/scripts/` to RULES.md Path Reference Convention.

### Group E: Deprecated pantry-review agent — inconsistent deprecation signals
- Finding 5, Finding 10 — same root cause: `pantry-review` was deprecated functionally (RULES.md strikethrough, pantry.md Section 2 notice) but not structurally. The agent file, GLOSSARY.md, and README.md all still describe it as active. Finding 5 is P3 (the agent file itself lacks a header notice); Finding 10 is P2 (GLOSSARY.md and README.md actively describe it as live, creating realistic spawn risk).
- **Suggested combined fix**: A single pass touching four locations: `agents/pantry-review.md` description field, `GLOSSARY.md:81`, `README.md:275`, and optionally the agent file's front-matter description. One commit cleans all four.

### Group D: Standalone findings (no grouping)
- Finding 4 — timestamp variable assignment example missing from RULES.md Step 3b-i. Standalone.
- Finding 6 — no issue; AGENTS.md alignment confirmed correct.
- Finding 8 — round=0 validation gap in RULES.md. Standalone.

---

## Summary Statistics
- Total findings: 10 (Finding 6 is a confirmation, not an issue; Findings 7 and 8 added after cross-review message from edge-cases-reviewer; Finding 10 added after cross-review message from excellence-reviewer)
- Actionable findings: 9
- By severity: P1: 0, P2: 4, P3: 5
- Preliminary groups: 5

---

## Cross-Review Messages

### Sent
- To edge-cases-reviewer: Acknowledged receipt of two cross-domain findings. Confirmed Finding 4 (script path wrong) via disk verification — `~/.claude/orchestration/scripts/` does not exist; actual path is `~/.claude/scripts/`. Added both as Findings 7 and 8 in this report with cross-references for Big Head dedup.

### Received
- From edge-cases-reviewer: "Two findings from my edge-cases review may overlap with your correctness domain — (1) Wrong script path in pantry.md:148 and RULES.md:108-110; (2) REVIEW_ROUND=0 skips wrong review types silently." — Action taken: verified both on disk; added as Findings 7 (P2, confirmed) and 8 (P3, severity downgraded from P2 because trigger requires state error). Both flagged for Big Head dedup against edge-cases findings.
- From excellence-reviewer: "RULES.md lines 180-182 and 193-195 use strikethrough for deprecated pantry-review rows — verify: (1) do agents parse and act on the deprecated entry? (2) Is strikethrough-in-table reliable?" — Action taken: searched all references to `pantry-review` across repo. Found that GLOSSARY.md:81 and README.md:275 actively describe `pantry-review` as a live agent with no deprecation marker, and `agents/pantry-review.md` description says "Use for Step 3b review cycles." Assessed correctness risk as P2 (elevated from excellence-reviewer's P3) because out-of-scope documents contradict the RULES.md deprecation, creating a realistic accidental-spawn risk. Added as Finding 10.

### Deferred Items
- "Deprecated pantry-review.md lacks deprecation notice in file header" — potential overlap with clarity reviewer's domain (naming/documentation), but retained here as Finding 5 (P3) since it is part of the same root cause as Finding 10. Big Head should merge Findings 5 and 10 under Group E.
- "round=0 silently wrong reviewer composition" — edge-cases-reviewer assessed P2; I assess P3 in correctness domain because the "default: 1" documented in RULES.md reduces the likelihood of this state. Big Head should set final severity.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `/Users/correy/projects/ant-farm/AGENTS.md` | Reviewed — Finding 6 (no issue; confirmed correct alignment) | 42 lines, Landing the Plane section, 8-step sequence compared against CLAUDE.md |
| `/Users/correy/projects/ant-farm/agents/pantry-review.md` | Reviewed — Finding 5 (P3) | 72 lines, timestamp ownership section, deprecation status cross-checked against RULES.md |
| `/Users/correy/projects/ant-farm/orchestration/RULES.md` | Reviewed — Findings 4, 7 (partial), 8 (P3, P2, P3) | 296 lines, Step 3b-i timestamp block, Step 3b-ii script invocation, Agent Types table, Model Assignments table, Path Reference Convention |
| `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md` | Reviewed — Findings 2, 3, 7 (partial) (P2, P3, P2) | 454 lines, Section 1 Steps 1-5, Section 2 Steps 1-6, Step 2.5 script path, cross-checked against ant-farm-s2g AC and ant-farm-99o AC |
| `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md` | Reviewed — Findings 1, 9 (P2, P3) | 891 lines, Fallback section (new), Team Setup, Round-Aware Review Protocol |

---

## Overall Assessment
**Score**: 6.0/10
**Verdict**: PASS WITH ISSUES

The session addressed all targeted acceptance criteria directionally — timestamp ownership is resolved, the prompts/ directory redundancy is documented, the fallback path exists, AGENTS.md is aligned, pantry.md has the clarified extraction guidance, and pantry-review.md timestamp ownership was corrected. Four P2 issues remain: a filename typo in the fallback section (`review-clarify.md` → `review-clarity.md`); pantry.md Section 2's circular reference fix is incomplete (Big Head polling loop not inlined); both RULES.md and pantry.md reference `~/.claude/orchestration/scripts/` which does not exist; and deprecated `pantry-review` is still described as live in GLOSSARY.md, README.md, and its own agent description, creating a realistic accidental-spawn risk. Five P3 issues cover documentation gaps and missing validation guards. Score formula: 10 − (4 × 1 P2) = 6.0.
