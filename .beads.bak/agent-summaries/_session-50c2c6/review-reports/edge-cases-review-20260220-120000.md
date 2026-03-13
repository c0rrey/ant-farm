# Report: Edge Cases Review (Round 2)

**Scope**: orchestration/RULES.md, orchestration/templates/checkpoints.md, orchestration/templates/queen-state.md, orchestration/templates/reviews.md
**Reviewer**: edge-cases / code-reviewer
**Round**: 2 (fix verification)

## Findings Catalog

### Finding 1: WARN definition for DMVDC now conflicts with the new PARTIAL definition
- **File(s)**: orchestration/templates/checkpoints.md:54-57 and :59
- **Severity**: P2
- **Category**: edge-case
- **Description**: The fix (ant-farm-4l0t) added a new `PARTIAL` verdict state for DMVDC and CCB (line 59), but left the existing `WARN` definition at lines 54-57 unchanged. Line 57 still reads: "DMVDC WARN: Partial failures detected. Agent can repair and resubmit." — which is semantically identical to the new PARTIAL definition at line 59: "Some checks failed. Agent can repair and resubmit." DMVDC now has two distinct named verdicts (WARN and PARTIAL) that describe the same trigger condition and the same response. Pest Control agents reading the Common Verdict Definitions section will encounter both labels for the same situation and may emit either one unpredictably. The Threshold table (lines 70-72) uses only PARTIAL, not WARN — so if an agent emits `WARN` for a DMVDC result, the table offers no matching entry to drive the Queen's response.
- **Suggested fix**: Remove "DMVDC WARN" from the WARN block at line 57, leaving WARN defined only for CCO and WWD. The WARN block header (line 54) should be updated to read "(checkpoints: CCO, WWD only)" to match. DMVDC partial failures are now unambiguously PARTIAL.
- **Cross-reference**: Correctness-reviewer should also assess whether this ambiguity creates a logic error in the Queen's response flow (WARN vs PARTIAL producing different downstream behavior).

### Finding 2: Escalation cap in RULES.md is unreachable if user always chooses "fix now" silently
- **File(s)**: orchestration/RULES.md:122-126
- **Severity**: P3
- **Category**: edge-case
- **Description**: The new round cap text says "If round 4 completes and P1/P2 findings are still present, do NOT start round 5." The cap is checked only at the point where the Queen would start round 5 — but the flow in Step 3c has "If P1 or P2 issues found: Present findings to user: 'Fix now or defer?'" The user is presented with two options (fix now, defer), and the round cap is listed as a third conditional below those two. If the user answers "fix now" every round without the Queen first checking the round counter, the Queen may spawn round 5 agents before hitting the cap check. The cap instruction is positioned after the fix/defer branch, not before it — making it easy for an LLM to execute the "fix now" branch before reading the cap.
- **Suggested fix**: Reorder Step 3c so the round cap check comes FIRST, before the fix/defer presentation: "1. Check round cap: if current round == 4 and P1/P2 still present → escalate, do not offer fix/defer. 2. Otherwise present fix/defer choice." This ordering makes the cap a hard gate, not an afterthought.
- **Cross-reference**: None.

### Finding 3: queen-state.md escalation cap field has no placeholder value for "round 4 triggered, user chose continue"
- **File(s)**: orchestration/templates/queen-state.md:36
- **Severity**: P3
- **Category**: edge-case
- **Description**: The new `Escalation cap` field shows two states: `not triggered` and `triggered (round 4: X P1, Y P2 — awaiting user decision)`. There is no placeholder for the state after the user responds: e.g., "triggered — user chose continue (round 5 in progress)" or "triggered — user chose abort." If the session state file is read mid-decision (e.g., on context recovery), the Queen cannot determine whether the user has already been asked and responded, or whether the escalation is still pending. This could cause the Queen to present the escalation prompt a second time on session resume.
- **Suggested fix**: Add a third placeholder value: `triggered — user responded: <continue | abort> (round N)`. This makes the field a complete state machine with an unambiguous terminal state.
- **Cross-reference**: None.

---

## Preliminary Groupings

### Group A: WARN/PARTIAL overlap in checkpoints.md creates ambiguous verdict vocabulary
- Finding 1 — standalone; no other finding shares this root cause.
- **Suggested combined fix**: Remove DMVDC from the WARN block; update the WARN block header to "(CCO, WWD only)".

### Group B: Round cap ordering and state completeness
- Finding 2, Finding 3 — both stem from the same root cause: the escalation cap was added as an append to existing flow rather than integrated into the flow's structure. Finding 2 is a sequencing issue (cap check after fix/defer branch) and Finding 3 is a state-machine completeness issue (missing terminal state after user decision). A single review of the cap's integration would fix both.
- **Suggested combined fix**: Restructure Step 3c to check round cap first (Finding 2) and extend the queen-state escalation field to include post-decision states (Finding 3).

---

## Summary Statistics
- Total findings: 3
- By severity: P1: 0, P2: 1, P3: 2
- Preliminary groups: 2

---

## Cross-Review Messages

### Sent
- To correctness-reviewer: "Finding 1 (WARN vs PARTIAL ambiguity in checkpoints.md) crosses into your domain — if DMVDC emits WARN instead of PARTIAL, the Threshold table has no matching entry and the Queen's response flow is undefined. Please assess whether this produces a logic gap in the Queen's downstream handling." -- Action: flagging for correctness coverage.

### Received
- From correctness-reviewer: "Finding 1 already catalogued in my round 2 report as P2 (incomplete fix). Confirmed the downstream logic gap: Queen's response handlers say 'On PARTIAL or FAIL' — a WARN string from Pest Control does not match and is silently treated as PASS, meaning the agent is never resumed." -- Action taken: deferred Finding 1 to correctness-reviewer; no duplicate filing needed.

### Deferred Items
- "WARN/PARTIAL ambiguity in checkpoints.md" (Finding 1) — Deferred to correctness-reviewer because they catalogued it first and have the complete downstream logic analysis. Big Head should use correctness-reviewer's version as the authoritative entry.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| orchestration/RULES.md | Findings: #2 | Reviewed fix at lines 122-126; surrounding Step 3c context (lines 109-127) read in full to assess ordering; no other changes in this file within the commit range |
| orchestration/templates/checkpoints.md | Findings: #1 | Reviewed fix at lines 54-57 and 59-72; WARN and PARTIAL definitions compared; Details by Checkpoint section (lines 86-94) read to confirm DMVDC PARTIAL specifics; no other changes in this file within the commit range |
| orchestration/templates/queen-state.md | Findings: #3 | Reviewed fix at lines 35-36; all Review Rounds fields read (lines 33-39); placeholder values assessed for state completeness |
| orchestration/templates/reviews.md | Reviewed -- no issues | Fix at lines 144 (escalation cap text) and 410-487 (Step 0 exact-path checks and polling loop); both fixes verified correct. The stale-glob issue from round 1 is resolved: Step 0 now uses `[ -f "<exact-path>" ]` checks, and the polling loop uses `[ -f "$EXACT_PATH" ]` with a comment explicitly prohibiting globs. The `exit 1` added at line 485 correctly signals failure from the bash block. No new edge cases introduced. |

---

## Overall Assessment
**Score**: 8.5/10
**Verdict**: PASS WITH ISSUES

The two primary fixes (stale glob replacement in reviews.md and exit 1 for polling timeout) are correctly implemented and close the P2 issues from round 1. One new P2 emerges: the WARN/PARTIAL overlap in checkpoints.md leaves DMVDC with two conflicting names for the same verdict state, which will produce unpredictable agent behavior. Two P3s address incomplete state handling around the new escalation cap.
