# Correctness Review — Round 2
**Reviewer**: r2-correctness
**Timestamp**: 20260222-103344
**Commit range**: 3f52803^..3f52803
**Review scope**: Fix commits only (Round 2 — limited mandate)

---

## Findings Catalog

### FINDING C2-01

- **File**: `scripts/parse-progress-log.sh` — cross-referenced with `CONTRIBUTING.md`
- **Line**: N/A (omission — CONTRIBUTING.md has no line for this entry)
- **Severity**: P2
- **Category**: Acceptance criterion unmet / Cross-file consistency
- **Description**: The task description for ant-farm-951b explicitly includes "add cross-file dependency entry in CONTRIBUTING.md" as part of the fix. Commit 3f52803 touched only `scripts/parse-progress-log.sh` (3 insertions, 0 file additions). `CONTRIBUTING.md` was not modified. The `RULES.md dependencies` section in `CONTRIBUTING.md` (lines 233–239) documents what must be updated when RULES.md changes, but there is no corresponding section documenting what must be updated when `parse-progress-log.sh` STEP_KEYS changes (i.e., also update RULES.md progress log entries and vice versa). This means the next developer adding a milestone to RULES.md has no checklist reminder to sync `parse-progress-log.sh` — the exact gap that produced this bug in the first place.
- **Suggested fix**: Add a `### parse-progress-log.sh dependencies` section to `CONTRIBUTING.md` with a row: "If you add a progress log milestone to `RULES.md` | Also update `scripts/parse-progress-log.sh` STEP_KEYS, `step_label()`, and `step_resume_action()`". This was called out in the task description as a required fix artifact.

---

### FINDING C2-02 (INFORMATIONAL — No Action Required)

- **File**: `scripts/parse-progress-log.sh:163`
- **Severity**: Not a finding — confirming correct behavior
- **Description**: The comment at line 163 lists `WAVE_SPAWNED, WAVE_VERIFIED, REVIEW_COMPLETE, REVIEW_TRIAGED` as multi-occurrence steps but does NOT list `WAVE_WWD_PASS`. This is correct: WAVE_WWD_PASS can appear multiple times (once per wave), which makes it also a multi-occurrence step. However, the script's `map_set` behavior for multi-occurrence steps (keeping the last occurrence's details) is identical regardless of whether a key appears in the comment. The omission from the comment is a clarity issue, not a correctness issue. Routing to clarity reviewer.

---

## Preliminary Groupings

### Group A: Incomplete Fix — Missing CONTRIBUTING.md Update (C2-01)

The accepted fix scope (per the task description) had three components:
1. Add `WAVE_WWD_PASS` to `STEP_KEYS` — **done**
2. Add `step_label()` and `step_resume_action()` cases — **done**
3. Add cross-file dependency entry in `CONTRIBUTING.md` — **NOT done**

All three were listed in the same task description. Items 1 and 2 are correctly implemented and land in the right position (between WAVE_SPAWNED and WAVE_VERIFIED), matching RULES.md's ordering at lines 116, 131, 137. The missing CONTRIBUTING.md entry is the only unresolved piece.

### Group B: Core Fix Verified Correct (no finding)

The three additions in 3f52803 are logically sound:
- `STEP_KEYS` ordering: `WAVE_SPAWNED → WAVE_WWD_PASS → WAVE_VERIFIED` matches RULES.md Step 3 ordering (lines 116, 131, 137). Correct.
- `step_label("WAVE_WWD_PASS")` returns `"Wave WWD Passed: WWD verification passed"` — accurate.
- `step_resume_action("WAVE_WWD_PASS")` returns `"Proceed to DMVDC verification: WWD already passed; re-spawn Pest Control for DMVDC only."` — correct (WAVE_WWD_PASS logged means WWD passed; resuming means only DMVDC remains).
- The `UNREACHABLE` guard at line 213–215 remains correct: `WAVE_WWD_PASS` is now in `STEP_KEYS`, so `SESSION_COMPLETE` is still reachable, and the guard still cannot be triggered except via SESSION_COMPLETE early-exit.
- No regression risk identified: the added `case` branches are new keys with no existing callers passing those values before this fix. Adding them to the `step_label()` and `step_resume_action()` switches only adds handling; it cannot break existing callers.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1 | 0 |
| P2 | 1 (C2-01: CONTRIBUTING.md update omitted from fix) |
| P3 | 0 |
| **Total** | **1** |

---

## Cross-Review Messages

**Sent to r2-edge-cases**: "Comment at `scripts/parse-progress-log.sh:163` lists multi-occurrence steps but omits `WAVE_WWD_PASS`, which is also multi-occurrence. Not a correctness issue — routing to you in case you want to capture it as a documentation/edge-case note."

**Received from r2-edge-cases**: Confirmed stale comment at line 163 has no behavioral consequence — the parse loop (lines 168–185) uses generic `map_set` calls with no branching on that list, so `WAVE_WWD_PASS` is handled correctly regardless. Identified as a Clarity concern, not edge-case. Not filing; passing to Clarity reviewer.

---

## Coverage Log

| File | Status | Notes |
|------|--------|-------|
| `scripts/parse-progress-log.sh` | Reviewed — no correctness issues in the fix itself | Core fix (items 1 and 2 of 3) lands correctly |
| `CONTRIBUTING.md` | Reviewed — P2 finding (C2-01) | Fix item 3 (cross-file dependency entry) not implemented |

Note: `RULES.md` was read for context to verify ordering and cross-file consistency. Not in the formal file list but reviewed as a dependency.

---

## Overall Assessment

**Score**: 7/10

**Verdict**: PASS WITH ISSUES

The functional fix for ant-farm-951b is correct: `WAVE_WWD_PASS` is inserted at the right position in `STEP_KEYS`, and both `step_label()` and `step_resume_action()` handle it accurately. No regressions introduced. The crash-recovery behavior for sessions that logged `WAVE_WWD_PASS` will now correctly show that milestone as complete and resume at `WAVE_VERIFIED` rather than re-running WWD — which is the stated goal.

However, the fix is incomplete against the acceptance criteria stated in the task: the CONTRIBUTING.md cross-file dependency entry was listed as a required deliverable and was not committed. This is a P2 because the absent entry is a maintenance gap that has already proven itself capable of causing exactly this class of bug — it is not hypothetical.

The fix does not need to be reverted. A follow-up commit adding the CONTRIBUTING.md entry resolves the issue.
