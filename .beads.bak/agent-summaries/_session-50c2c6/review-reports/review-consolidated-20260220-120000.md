# Consolidated Review Summary (Round 2)

**Scope**: orchestration/RULES.md, orchestration/templates/checkpoints.md, orchestration/templates/queen-state.md, orchestration/templates/reviews.md
**Commit Range**: 002ee87..d9201c9 (3 fix commits)
**Reviews completed**: Edge Cases, Correctness (Round 2 -- fix verification)
**Reports verified**: edge-cases-review-20260220-120000.md [check], correctness-review-20260220-120000.md [check]
**Total raw findings**: 5 across both reviews
**Root causes identified**: 3 after deduplication
**Beads filed**: 3

---

## Read Confirmation

**Both reports read and processed by Big Head consolidation:**

| Report Type | File | Status | Finding Count |
|-------------|------|--------|---------------|
| Correctness | correctness-review-20260220-120000.md | Read | 2 findings |
| Edge Cases | edge-cases-review-20260220-120000.md | Read | 3 findings |

**Total findings from both reports**: 5

---

## Fix Verification Summary

The 3 round-1 P2 fixes were verified by both reviewers:

| Round 1 Bead | Fix Commit | Correctness Verdict | Edge Cases Verdict | Consolidated |
|--------------|-----------|--------------------|--------------------|-------------|
| ant-farm-60mh (stale glob) | 002ee87 | PASS | No issues | PASS -- fix is complete |
| ant-farm-4l0t (PARTIAL verdict) | 023ee0f | PARTIAL | New P2 finding | INCOMPLETE -- residual contradiction |
| ant-farm-rcdd (round cap) | d9201c9 | PARTIAL | New P2 + P3 findings | INCOMPLETE -- structural ordering issue |

- **ant-farm-60mh**: Fully resolved. Step 0 bash blocks and polling loop now use exact `[ -f "<path>" ]` checks with no wildcard globs. `exit 1` added after TIMEOUT echo. Both reviewers confirm no regressions.
- **ant-farm-4l0t**: Partially resolved. PARTIAL was correctly added to the summary and the table was updated, but the WARN block at checkpoints.md:54-57 still lists DMVDC, creating a contradiction between WARN and PARTIAL for the same checkpoint.
- **ant-farm-rcdd**: Partially resolved. Round cap language was added consistently across all 3 files, but the cap block is positioned after the "fix now" action in Step 3c, allowing a Queen to spawn round 5 before encountering the cap check.

---

## Root Causes Filed

| Bead ID | Priority | Title | Contributing Reviews | Surfaces |
|---------|----------|-------|---------------------|----------|
| ant-farm-oj79 | P2 | Incomplete ant-farm-4l0t fix: WARN block still lists DMVDC, contradicting new PARTIAL definition | correctness, edge-cases | checkpoints.md:54,57,59 |
| ant-farm-gy9p | P2 | Round cap in RULES.md Step 3c placed after fix-now action, allowing round 5 to start before cap fires | correctness, edge-cases | RULES.md:119,122-126, reviews.md:144 |
| ant-farm-s7l8 | P3 | queen-state.md escalation cap field missing post-decision terminal state | edge-cases | queen-state.md:36 |

---

## Root Cause Groupings with Merge Rationale

### RC-1: ant-farm-oj79 (P2) -- WARN block still lists DMVDC after PARTIAL fix

- **Root cause**: The ant-farm-4l0t fix correctly added PARTIAL as a new verdict state and updated the Checkpoint-Specific Thresholds table, but did not remove DMVDC from the WARN definition block. checkpoints.md:54 still reads `**WARN** (checkpoints: CCO, WWD, **DMVDC** only)` and line 57 still reads `- DMVDC WARN: Partial failures detected. Agent can repair and resubmit.` This directly contradicts the new PARTIAL definition at line 59. A Pest Control agent reading the Common Verdict Definitions will see two named verdicts (WARN and PARTIAL) that describe the same trigger and response for DMVDC.
- **Affected surfaces**:
  - checkpoints.md:54 -- WARN header still includes DMVDC (from correctness F1, edge-cases F1)
  - checkpoints.md:57 -- DMVDC WARN bullet still present (from correctness F1, edge-cases F1)
  - checkpoints.md:59 -- New PARTIAL definition contradicts WARN bullet (from edge-cases F1)
- **Combined priority**: P2 (both reviewers rated P2)
- **Fix**: Remove DMVDC from the WARN header at line 54 (change to `(checkpoints: CCO, WWD only)`). Delete the `- DMVDC WARN: Partial failures detected. Agent can repair and resubmit.` line at line 57. The PARTIAL definition at line 59 now covers this case. Two-line change.
- **Merge rationale**: Correctness F1 and Edge-cases F1 identify the exact same lines (checkpoints.md:54-57) and the exact same issue: the WARN block was not updated when PARTIAL was added. Both reviewers independently describe the same contradiction. The root cause is that the ant-farm-4l0t fix addressed the table (lines 70-72) but not the prose definition block (lines 54-57). One edit fixes both findings.
- **Acceptance criteria**: (1) DMVDC does not appear in the WARN header or bullet list; (2) WARN is defined for CCO and WWD only; (3) DMVDC's intermediate verdict is unambiguously PARTIAL throughout the file.

### RC-2: ant-farm-gy9p (P2) -- Round cap positioned after the action it prevents

- **Root cause**: The ant-farm-rcdd fix added a "Round cap -- escalate after round 4" block in RULES.md Step 3c, but positioned it as a sibling after the "fix now" and "defer" branches. A Queen executing the "fix now" path reads "re-run Step 3b with round N+1" and proceeds to spawn before reaching the cap block that follows. The cap check effectively fires one round late: a Queen enters round 5 before the cap text blocks it. The same ordering issue exists in reviews.md:144 where the Escalation cap paragraph sits at the end of the Termination Rule section rather than inside the loop logic.
- **Affected surfaces**:
  - RULES.md:119 -- "fix now" action says "re-run Step 3b with round N+1" before cap check (from correctness F2, edge-cases F2)
  - RULES.md:122-126 -- Round cap block positioned after fix/defer branches (from correctness F2, edge-cases F2)
  - reviews.md:144 -- Escalation cap paragraph at end of Termination Rule, not inside decision path (from correctness F2)
- **Combined priority**: P2 (correctness rated P2, edge-cases rated P3; taking highest)
- **Fix**: Restructure RULES.md Step 3c so the round cap check comes first:
  ```
  - **If "fix now"**:
    - If current round < 4: Spawn fix tasks, then re-run Step 3b with round N+1
      - Update session state: increment review round, record fix commit range
    - If current round = 4: Do NOT start round 5. Escalate to user with full round history.
  ```
  Remove the separate "Round cap" sibling block (now inline). In reviews.md, move the Escalation cap note inside the loop description.
- **Merge rationale**: Correctness F2 and Edge-cases F2 identify the same structural ordering problem in the same code path (RULES.md Step 3c fix/defer branch). Correctness additionally notes the reviews.md placement issue. The root cause is the same: the cap was appended as a new block rather than integrated into the existing decision flow. One restructuring of the decision order fixes both.
- **Acceptance criteria**: (1) The round cap check appears before or inside the "fix now" branch, not after it; (2) A Queen following "fix now" in round 4 encounters the cap before spawning round 5; (3) reviews.md Escalation cap is inside the loop logic, not appended after it.

### RC-3: ant-farm-s7l8 (P3) -- Escalation cap field missing terminal state

- **Root cause**: The queen-state.md `Escalation cap` field added by ant-farm-rcdd has two states: `not triggered` and `triggered (...awaiting user decision)`. It lacks a terminal state for after the user responds (e.g., "user chose continue" or "user chose abort"). On session resume, a Queen reading the state file cannot distinguish "escalation pending" from "escalation already handled."
- **Affected surfaces**:
  - queen-state.md:36 -- Escalation cap field (from edge-cases F3)
- **Combined priority**: P3 (single finding)
- **Fix**: Add a third placeholder value: `triggered -- user responded: <continue | abort> (round N)`.
- **Merge rationale**: No merge -- standalone finding from one reviewer. The edge-cases reviewer proposed grouping this with F2 (cap ordering), but the root causes are distinct: F2 is about when the cap fires (ordering), F3 is about state tracking after the cap fires (completeness). They can be fixed independently.
- **Acceptance criteria**: (1) Escalation cap field has three states: not triggered, triggered (awaiting), triggered (responded); (2) The responded state includes the user's choice and the round number.
- **Auto-filed to**: Future Work epic (ant-farm-66gl)

---

## Deduplication Log

### Merged Findings

| Consolidated Bead | Merged Findings | Merge Reason |
|-------------------|-----------------|--------------|
| ant-farm-oj79 (RC-1) | Correctness F1 + Edge-cases F1 | Same lines (checkpoints.md:54-57), same issue (WARN block not updated when PARTIAL added). Both reviewers independently identified the identical contradiction. |
| ant-farm-gy9p (RC-2) | Correctness F2 + Edge-cases F2 | Same code path (RULES.md Step 3c fix/defer branch), same issue (cap block positioned after action). Correctness additionally covers reviews.md:144. |

### Standalone Findings (No Merge)

| Consolidated Bead | Source Finding | Reason Not Merged |
|-------------------|---------------|-------------------|
| ant-farm-s7l8 (RC-3) | Edge-cases F3 | Unique root cause: state machine completeness for escalation cap field. No other finding covers post-decision state tracking. |

---

## Traceability Matrix

Every raw finding mapped to its consolidated bead:

| Review | Finding # | Description (abbreviated) | Consolidated Bead |
|--------|-----------|--------------------------|-------------------|
| Correctness | F1 | WARN block still lists DMVDC after PARTIAL fix | ant-farm-oj79 |
| Correctness | F2 | Round cap placed after fix-now action | ant-farm-gy9p |
| Edge Cases | F1 | WARN/PARTIAL conflict for DMVDC | ant-farm-oj79 |
| Edge Cases | F2 | Escalation cap unreachable before round 5 | ant-farm-gy9p |
| Edge Cases | F3 | Escalation cap field missing terminal state | ant-farm-s7l8 |

**All 5 findings accounted for. 0 findings excluded.**

---

## Priority Breakdown

- **P1 (blocking)**: 0 beads
- **P2 (important)**: 2 beads
  - ant-farm-oj79: WARN block still lists DMVDC, contradicting PARTIAL definition
  - ant-farm-gy9p: Round cap placed after fix-now action, effective cap is round 5 not round 4
- **P3 (polish)**: 1 bead (auto-filed to Future Work epic ant-farm-66gl)
  - ant-farm-s7l8: Escalation cap field missing post-decision state

Priority calibration note: 2 P2 findings is appropriate. Both are residual issues from incomplete round-1 fixes: ant-farm-oj79 is a two-line omission that creates ambiguous verdict vocabulary for Pest Control agents; ant-farm-gy9p is a structural ordering issue that renders the round cap ineffective. The P3 finding is a genuine polish item (state machine completeness) with no immediate operational impact.

---

## Verdict

**NEEDS WORK**

Of the 3 round-1 P2 fixes:
- **ant-farm-60mh** (stale glob): PASS -- fully resolved, no regressions.
- **ant-farm-4l0t** (PARTIAL verdict): INCOMPLETE -- the WARN block at checkpoints.md:54-57 still lists DMVDC, preserving the core contradiction. Two-line fix required: remove DMVDC from the WARN header and delete the DMVDC WARN bullet.
- **ant-farm-rcdd** (round cap): INCOMPLETE -- the cap block is positioned after the "fix now" action, making it unreachable before round 5 starts. Restructure Step 3c to check the round cap before offering fix/defer.

Both remaining P2 issues are small, targeted fixes (2-line edit for ant-farm-oj79, reorder of 2 paragraphs for ant-farm-gy9p). A round 3 review should be narrow and fast.
