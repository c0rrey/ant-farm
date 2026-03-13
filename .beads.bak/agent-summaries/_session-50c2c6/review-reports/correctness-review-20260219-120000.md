# Report: Correctness Redux Review

**Scope**: orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/checkpoints.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/queen-state.md, orchestration/templates/reviews.md
**Reviewer**: correctness / code-reviewer

---

## Acceptance Criteria Verification

All 11 task IDs (ant-farm-ha7a.1 through ant-farm-ha7a.11) were retrieved via `bd show`. Each is verified against the implemented files.

### ha7a.1 — Add review round counter to queen-state template
- `grep "## Review Rounds" queen-state.md` → MATCH at line 33. PASS.
- Section order: `## Pest Control` (L23) → `## Review Rounds` (L33) → `## Queue Position` (L39). PASS.
- All 4 placeholder fields present: `Current round`, `Round 1 commit range`, `Fix commit range`, `Termination`. PASS.
- `## Pest Control` and `## Queue Position` intact and unmodified. PASS.

### ha7a.2 — Add round-aware review protocol and team setup to reviews.md
- `grep "## Round-Aware Review Protocol" reviews.md` → MATCH at line 110. PASS.
- Section appears before `## Review 1: Clarity (P3)` at line 156. PASS.
- All 4 subsections present: `### Round 1 (Full Review)` (L114), `### Round 2+ (Fix Verification)` (L123), `### Termination Rule` (L135), `### Round 2+ Reviewer Instructions` (L146). PASS.
- Team Setup says "**Round 1**: The Queen creates the Nitpicker team with **6 members**" (L53) and "**Round 2+**: The Queen creates the Nitpicker team with **4 members**" (L75). PASS.
- `### Messaging Guidelines` at line 98 remains immediately after `### Team Setup` (L49). PASS.

### ha7a.3 — Update Big Head verification and summary for round-aware report counts
- Step 0 text: "The number of expected reports depends on the review round:" present at reviews.md:408. Separate Round 1 and Round 2+ bash blocks at lines 410 and 419. PASS.
- Step 0a polling loop contains `# <IF ROUND 1>` at line 469 and `# </IF ROUND 1>` at line 473. PASS.
- `**Pantry responsibility**` note at line 488. PASS.
- Consolidated summary reviews-completed line: `<Round 1: Clarity, Edge Cases, Correctness, Excellence | Round 2+: Correctness, Edge Cases>` at reviews.md:578. PASS.
- Read Confirmation table uses `<for each report in this round>` at reviews.md:592. PASS.

### ha7a.4 — Add P3 auto-filing, termination check, and mandatory re-review
- `### P3 Auto-Filing (Round 2+ Only)` at reviews.md:677. PASS.
- P3 Auto-Filing section contains both `bd epic create` (L686) and `bd dep add ... --type parent-child` (L692). PASS.
- `### Termination Check` at reviews.md:750, before `### If P1 or P2 issues found:` at line 761. PASS.
- `c. **Re-run reviews** (MANDATORY):` at reviews.md:788. PASS.
- `### Handle P3 Issues (Queen's Step 4)` immediately followed by `> **Round 1 only.**` at line 800. PASS.

### ha7a.5 — Update review checklists for round-aware team composition
- Nitpicker Checklist item `Review round number passed to Pantry` at reviews.md:712. PASS.
- Checklist item with "6 members" and "4 members" at reviews.md:721. PASS.
- Checklist item `Round 2+ reviewers include out-of-scope finding bar` at reviews.md:715. PASS.
- Big Head Checklist first item: `Round 1: Read all 4 Nitpicker reports; Round 2+: Read 2 reports` at reviews.md:727. PASS.
- Big Head Checklist `Round 2+ on PASS: P3 beads auto-filed to "Future Work" epic` at reviews.md:734. PASS.

### ha7a.6 — Update RULES.md Step 3b/3c for round-aware review loop
- Step 3b contains `**Review round**: read from session state (default: 1)` at RULES.md:92, `**Round 1**:` at L100, `**Round 2+**:` at L103. PASS.
- Step 3c contains `**Termination check**: If zero P1 and zero P2 findings:` at RULES.md:112. PASS.
- Step 3c fix-now path says `re-run Step 3b with round N+1` at RULES.md:119 and `increment review round, record fix commit range` at L120. PASS.
- `grep "L631" RULES.md` → no matches. PASS.
- Hard Gates Reviews row: "re-runs after fix cycles with reduced scope (round 2+)" at RULES.md:138. PASS.

### ha7a.7 — Update big-head-skeleton for round-aware consolidation
- Placeholder list includes `{REVIEW_ROUND}` at big-head-skeleton.md:13 with description "review round number (1, 2, 3, ...). Determines report count and P3 handling." PASS.
- File contains `**Round 1**: Big Head is the 5th member; Pest Control is the 6th.` (L26) and `**Round 2+**: Big Head is the 3rd member; Pest Control is the 4th.` (L42). PASS.
- Agent template says "Consolidate the Nitpicker reports" (no hardcoded "4") at big-head-skeleton.md:67, followed by `**Review round**: {REVIEW_ROUND}` at L69. PASS.
- Step 10 `**Round 2+ only — P3 auto-filing**` at L93 with `bd dep add <id> <epic-id> --type parent-child` at L95. PASS.

### ha7a.8 — Add round-aware scope instructions to nitpicker-skeleton
- `grep "REVIEW_ROUND" nitpicker-skeleton.md` → matches in placeholder list (L12) and agent template (L20). PASS.
- Placeholder entry reads `{REVIEW_ROUND}: 1, 2, 3, ... (determines scope instructions; filled by Pantry)` at L12. PASS.
- Agent template contains `**Review round**: {REVIEW_ROUND}` at L20. PASS.
- Round 2+ scope text mentions "fix commits only", "runtime failure", "silently wrong results" at nitpicker-skeleton.md:21. PASS.

### ha7a.9 — Update pantry review mode for round-aware brief composition
- Input spec includes "review round number (1, 2, 3, ...)" at pantry.md:201. PASS.
- Brief composition: `**Round 1**: Compose 4 review briefs` at pantry.md:230 and `**Round 2+**: Compose 2 review briefs` at L231. PASS.
- Files-to-write: `**Round 1**:` (4 files) at L244 and `**Round 2+**:` (2 files) at L249. PASS.
- Step 4 mentions "Review round number" (L263), "P3 auto-filing" (L265), and `**Polling loop adaptation**` (L267). PASS.
- Step 5 mentions `{REVIEW_ROUND}` placeholder at pantry.md:276. PASS.
- Step 6 has `**Round 1 return table:**` (L286) with 4 data rows and `**Round 2+ return table:**` (L299) with 2 data rows. PASS.

### ha7a.10 — Update CCB checkpoint for round-aware report counts
- CCB header contains "4 reports in round 1, 2 in round 2+" at checkpoints.md:458. PASS.
- Individual reports section has `Round 1:` (4 files, L474) and `Round 2+:` (2 files, L480) subsections. PASS.
- Document count: "round 1: 5 total = 4 reports + consolidated; round 2+: 3 total = 2 reports + consolidated" at checkpoints.md:484. PASS.
- Check 0: `**Round 1** — verify exactly 4 report files:` at L489 and `**Round 2+** — verify exactly 2 report files:` at L495. PASS.
- Check 1 math format includes both "Round 1:" and "Round 2+:" patterns at checkpoints.md:505. PASS.

### ha7a.11 — Verify cross-file consistency
All 11 invariants verified as part of this correctness review. See Findings section for issues detected.

---

## Findings Catalog

### Finding 1: Termination Rule "directly" implies skipping Round 1 P3 handling

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:141`
- **Severity**: P3
- **Category**: correctness
- **Description**: The `### Termination Rule` section (lines 135-144) bullet 3 reads: "Queen proceeds directly to RULES.md Step 4 (documentation)". Bullet 2 correctly says Round 1 P3s follow the Handle P3 Issues flow. However, the word "directly" in bullet 3 — immediately following bullet 2 — can be read as "skip Handle P3 Issues and go straight to RULES.md Step 4". The more detailed `### Termination Check` section (lines 750-759) properly enumerates the order: handle P3s (step 2), then proceed to RULES.md Step 4 (step 4). The `### Termination Rule` section is less precise. RULES.md Step 3c (lines 112-116) correctly enumerates them separately. The ambiguity exists only in the `### Termination Rule` summary block, which is a compact description of the same logic.
- **Suggested fix**: Change reviews.md:141 from "Queen proceeds directly to RULES.md Step 4 (documentation)" to "Queen proceeds to RULES.md Step 4 (documentation) — Round 1: after Handle P3 Issues; Round 2+: directly (P3s already auto-filed by Big Head)". This removes ambiguity without requiring a structural change.
- **Cross-reference**: Received from edge-cases-reviewer as potential correctness issue; confirmed P3 (not P2) because the authoritative Termination Check section and RULES.md Step 3c resolve it unambiguously.

### Finding 2: Wildcard glob in Step 0 and polling loop matches stale prior-round reports

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:413-416`, `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:464-472`
- **Severity**: P2
- **Category**: correctness
- **Description**: Step 0's bash blocks and the polling loop use `ls ...-review-*.md` wildcards to detect whether reports exist. In a multi-round session, round 1 report files (`correctness-review-<round1-timestamp>.md`, `edge-cases-review-<round1-timestamp>.md`) remain on disk when round 2+ begins. The wildcard matches these stale files, so `ALL_FOUND=1` evaluates true immediately — Big Head proceeds to consolidate the wrong round's data and files beads based on round 1 findings instead of the round 2+ fix-verification findings. The `head -1` comment at line 460 ("ensures re-runs with multiple matching files don't break the check") acknowledges the multi-file case but misunderstands it: it silently picks the first match, which could be the stale round-1 file.

  The Pantry responsibility note (line 488) says the Pantry writes the concrete polling loop with "exact paths" — but the template itself shows wildcard globs, and there is no instruction to the Pantry to substitute the exact timestamp. `pantry.md:258` says "round 1: all 4; round 2+: 2 (correctness, edge-cases)" for report paths but does not specify that the Pantry should resolve wildcards to timestamped filenames. The review timestamp is passed to the Pantry (line 201) but there is no explicit instruction to embed it into the polling loop variables.

- **Suggested fix**: In the Pantry brief composition (Step 4), explicitly instruct the Pantry to substitute the concrete timestamp into the polling loop paths when writing the Big Head brief — e.g., `FOUND_CORRECTNESS=$(ls <session-dir>/review-reports/correctness-review-<timestamp>.md 2>/dev/null | head -1)` using the exact `{timestamp}` value from the Queen. Alternatively, add a check in the polling loop that compares the found file's timestamp suffix against the expected one.
- **Cross-reference**: Received from edge-cases-reviewer; confirmed as correctness issue (P2, not P1 — requires a prior round to have completed, which only happens on round 2+).

### Finding 3: Polling loop timeout path does not prevent Big Head from continuing

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:483-485`
- **Severity**: P2
- **Category**: correctness
- **Description**: The polling loop ends with `if [ $TIMED_OUT -eq 1 ]; then echo "TIMEOUT: ..."; fi` at lines 483-485. There is no `exit 1`, no return value, and no signal that prevents execution from continuing past this block. The block is embedded in a bash code block that an LLM reads and follows, not runs natively — so an LLM model following these instructions could observe "TIMEOUT echoed" and proceed to the "Error return" section (line 490+) as directed. However, the connection between the shell block echoing TIMEOUT and the prose at line 492 ("If timeout is reached and any reports are still missing, IMMEDIATELY return an error") depends on the LLM correctly bridging the gap. If the LLM treats the bash block as complete and moves to the next prose section (Step 1), it will consolidate with missing data and produce incorrect bead filings.

  The correct behavior is for the TIMED_OUT check to be the entry condition for the "Error return" block — but as written, the prose immediately after the bash block begins with "**Pantry responsibility**" (line 488), which is an unrelated note. The "Error return (if timeout exceeded)" prose (line 490) follows after the Pantry note. A model could parse this as: bash block ends → Pantry note → move to step 1 → error return is a separate (possibly conditional) section it skips.

- **Suggested fix**: In the polling loop bash block, replace the `echo "TIMEOUT..."` with a signal that is unambiguous for an LLM:
  ```bash
  if [ $TIMED_OUT -eq 1 ]; then
    echo "TIMEOUT: Not all expected reports arrived within ${TIMEOUT}s"
    echo "ACTION_REQUIRED: Follow the Error return format below. Do NOT proceed to Step 1."
    exit 1
  fi
  ```
  Additionally, move the "Error return (if timeout exceeded)" prose to immediately follow the bash block, before the "Pantry responsibility" note, to eliminate any ambiguity about the execution path.
- **Cross-reference**: Received from edge-cases-reviewer; confirmed as P2 correctness issue (silently wrong results — beads filed from incomplete/wrong-round data).

### Finding 4: Pantry empty-file-list guard does not validate against git diff (deferred)

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md:216-228`
- **Severity**: P3
- **Category**: correctness
- **Description**: The Pantry's guard (lines 216-228) checks only that the file list is non-empty. It does not verify the list matches `git diff --name-only <commit-range>`. A stale file list from a prior session would pass this guard and produce review briefs for wrong files. CCO Check 1 (checkpoints.md:201) does run `git diff --name-only` and compares it to the prompt — this is a genuine independent backstop that would catch the mismatch before Nitpickers are spawned. Because CCO is a hard gate (FAIL blocks spawn), the risk of wrong files reaching reviewers is mitigated. This is a defense-in-depth gap, not an unguarded failure path.
- **Suggested fix**: Add a second step to the Pantry guard: run `git diff --name-only <commit-range>` and compare against the Queen-provided file list, failing if there is a mismatch. This makes the Pantry self-sufficient rather than depending on CCO to catch a Pantry-level error. Low urgency given CCO coverage.
- **Cross-reference**: Received from edge-cases-reviewer; assessed P3 (not P2) because CCO provides a sufficient hard gate preventing this from producing wrong reviewer output.

### Finding 5: PARTIAL verdict missing from "Common Verdict Definitions" and DMVDC row in summary table uses WARN where individual sections use PARTIAL

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md:50`, `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md:68-69`
- **Severity**: P2
- **Category**: correctness
- **Description**: Two related problems exist in the Verdict Thresholds Summary section:

  **Problem A — "Common Verdict Definitions" claim (line 50)**: "All checkpoints use three verdict states: PASS, WARN, FAIL." This is false — DMVDC (lines 369, 427) and CCB (line 550) use a fourth verdict state, PARTIAL, which means "some checks failed, agent can repair and resubmit." PARTIAL is distinct from WARN (which is approved, soft-gate behavior for CCO/WWD) and from FAIL (which blocks and escalates). A Pest Control agent reading the preamble first and internalizing "three states" may be primed to force its output into PASS/WARN/FAIL even when PARTIAL is the correct verdict for a partially-failing DMVDC run.

  **Problem B — Checkpoint-Specific Thresholds table (lines 68-69)**: The DMVDC rows say "WARN allows resubmission; FAIL escalates." WARN is not a valid DMVDC verdict — the individual DMVDC sections (lines 369, 427) define PARTIAL (not WARN) as the resubmit path. If Pest Control uses the table as its reference and outputs "WARN" for a partial DMVDC result, the Queen's response handler ("On PARTIAL or FAIL", lines 443, 567) will not match the "WARN" string, causing the WARN to be silently treated as a PASS — the agent is never resumed, and the gap is never repaired.

  Note: PARTIAL is correctly defined in "Details by Checkpoint" (lines 84-92), which is inside the same summary section. So PARTIAL is not completely absent from the file's summary — but the contradiction with the "three verdict states" claim and the WARN/PARTIAL mismatch in the table creates a real risk of misclassification.

- **Suggested fix**: (1) Change line 50 from "All checkpoints use three verdict states" to "CCO and WWD use three verdict states (PASS, WARN, FAIL); DMVDC and CCB use three verdict states (PASS, PARTIAL, FAIL) — PARTIAL replaces WARN for these checkpoints." (2) In the Checkpoint-Specific Thresholds table, change the DMVDC rows' Queue Blocking column from "WARN allows resubmission; FAIL escalates" to "PARTIAL allows resubmission; FAIL escalates."
- **Cross-reference**: Received from clarity-reviewer as a potential correctness issue. Confirmed P2 (not P1): the misclassification risk is real but occurs only when a DMVDC run partially fails, and the "Details by Checkpoint" subsection does define PARTIAL correctly — an attentive agent reading the full summary would see both definitions. P1 would require no correct definition existing anywhere in the file; the correct definition at lines 84-92 reduces this to P2.

---

## Preliminary Groupings

### Group A: Multi-round data isolation failure (root cause: wildcard glob without timestamp binding)
- Finding 2 (stale glob in Step 0 and polling loop) — wildcard globs pick up prior-round files
- Finding 3 (timeout path does not halt execution) — shares root cause: the polling loop was designed as a bash template for LLM interpretation rather than for execution, and its failure signaling relies on prose-to-code bridging that LLMs may not follow reliably
- **Suggested combined fix**: When the Pantry writes the Big Head brief's polling loop, substitute the exact timestamped filenames. Also add an unambiguous failure signal (`exit 1` + immediate prose) to the timeout path. These two together make the loop both correct (finds only current-round files) and robust (fails loudly).

### Group B: Verdict vocabulary inconsistency (root cause: PARTIAL not integrated into summary-level definitions)
- Finding 5 (PARTIAL absent from common definitions; DMVDC table uses WARN instead of PARTIAL) — the "Details by Checkpoint" subsection defines PARTIAL correctly but the preamble and table contradict it
- **Suggested combined fix**: Two-line edit: update the "three verdict states" claim and replace WARN with PARTIAL in the DMVDC table rows.

### Group C: Standalone items
- Finding 1 (Termination Rule "directly") — standalone, single-line wording ambiguity
- Finding 4 (Pantry guard) — standalone, defense-in-depth gap covered by CCO

---

## Summary Statistics
- Total findings: 5
- By severity: P1: 0, P2: 3, P3: 2
- Preliminary groups: 3

---

## Cross-Review Messages

### Sent
- None sent proactively.

### Received
- From edge-cases-reviewer: "3 edge-case findings crossing into correctness domain" — Action taken: investigated all three independently by reading reviews.md:406-492 and pantry.md:216-228 and checkpoints.md:199-224. Added Findings 2, 3, 4 from those findings; calibrated severity independently.
- From clarity-reviewer: "PARTIAL verdict missing from checkpoints.md summary table — potential Pest Control misclassification" — Action taken: re-read checkpoints.md lines 44-92, 367-370, 425-428, 548-551. Confirmed two distinct problems (preamble claim and table mismatch). Added as Finding 5, P2.

### Deferred Items
- None deferred outward. Finding 4 (pantry guard, P3) and Finding 5 (PARTIAL/WARN mismatch, P2) both handled here.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| orchestration/RULES.md | Reviewed — no issues | Step 0-6 workflow examined; Step 3b (lines 88-107), Step 3c (lines 109-121), Hard Gates table (lines 130-138), all examined for round-aware correctness. All 5 acceptance criteria for ha7a.6 verified PASS. |
| orchestration/templates/big-head-skeleton.md | Reviewed — no issues | Instructions block (lines 1-62), agent-facing template (lines 64-105) including all 10 steps examined. Round 1 and Round 2+ TeamCreate examples verified at lines 26-53. All 4 acceptance criteria for ha7a.7 verified PASS. |
| orchestration/templates/checkpoints.md | Findings: #5 | CCO (lines 96-163), CCO Nitpickers (lines 164-224), WWD (lines 234-302), DMVDC Dirt Pushers (lines 305-379), DMVDC Nitpickers (lines 381-437), CCB (lines 456-570) all examined. All 5 acceptance criteria for ha7a.10 verified PASS. P2 finding: PARTIAL verdict absent from "Common Verdict Definitions" preamble (line 50) and DMVDC summary table uses WARN instead of PARTIAL (lines 68-69); correctly defined in "Details by Checkpoint" at lines 84-92. |
| orchestration/templates/nitpicker-skeleton.md | Reviewed — no issues | Placeholder list (lines 1-12) and agent template (lines 14-42) examined. All 4 acceptance criteria for ha7a.8 verified PASS. |
| orchestration/templates/pantry.md | Findings: #4 | Implementation mode (Section 1, lines 15-196) and Review mode (Section 2, lines 199-316) examined. All 6 acceptance criteria for ha7a.9 verified PASS. P3 finding at lines 216-228 (empty-file-list guard does not cross-check git diff; mitigated by CCO). |
| orchestration/templates/queen-state.md | Reviewed — no issues | All 7 section headers examined (Scout, Agent Registry, Pantry, Pest Control, Review Rounds, Queue Position, Error Log). All 4 acceptance criteria for ha7a.1 verified PASS. |
| orchestration/templates/reviews.md | Findings: #1, #2, #3 | Full file examined: Transition Gate (lines 4-27), Agent Teams Protocol (lines 30-95), Round-Aware Review Protocol (lines 110-154), all 4 review briefs (lines 156-312), Nitpicker Report Format (lines 315-388), Big Head Consolidation Protocol (lines 390-705), Queen's Step 3c (lines 743-815), Review Quality Metrics (lines 817-830). All acceptance criteria for ha7a.2, ha7a.3, ha7a.4, ha7a.5 verified PASS. P3 at line 141 (Finding 1), P2 at lines 413-416 and 464-472 (Finding 2), P2 at lines 483-485 (Finding 3). |

---

## Overall Assessment
**Score**: 7/10
**Verdict**: PASS WITH ISSUES

All 11 acceptance criteria sets fully met. Three P2 correctness issues: wildcard globs matching stale prior-round reports in the Big Head polling loop (Finding 2), a timeout path that does not reliably stop an LLM from proceeding with missing data (Finding 3), and a PARTIAL/WARN vocabulary inconsistency in checkpoints.md's Verdict Thresholds Summary that could cause Pest Control to output WARN where the Queen's handler expects PARTIAL or FAIL (Finding 5). Findings 2 and 3 share a root cause and affect round 2+ only. Finding 5 is a pre-existing gap in checkpoints.md not introduced by this epic. Two P3 issues are present: a wording ambiguity in the Termination Rule summary (Finding 1) and a defense-in-depth gap in the Pantry file list guard (Finding 4, covered by CCO).
