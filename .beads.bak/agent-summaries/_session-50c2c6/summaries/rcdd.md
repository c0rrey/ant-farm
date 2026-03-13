# Fix Summary: ant-farm-rcdd

**Issue**: No hard cap on review rounds creates unbounded retry loop risk.

**Root cause**: `reviews.md` stated "There is no hard cap on rounds." `RULES.md` Step 3c had no termination guard for non-converging review cycles. `queen-state.md` had no field for tracking a round cap.

## Changes Made

### 1. `orchestration/templates/reviews.md` — Termination Rule section

Replaced the sentence "There is no hard cap on rounds." with an explicit escalation cap paragraph:

> After round 4 with no convergence (P1 or P2 findings still present), do NOT start round 5. Instead, escalate to the user with the full round history (round numbers, finding counts per round, bead IDs) and ask whether to continue or abort.

### 2. `orchestration/RULES.md` — Step 3c

Added a "Round cap — escalate after round 4" block immediately after the "fix now / defer" decision tree. The block instructs the Queen to:
- Stop before starting round 5 if P1/P2 findings persist after round 4
- Present full round history to the user
- Await user decision (continue or abort) before any further action

### 3. `orchestration/templates/queen-state.md` — Review Rounds section

Added two new fields:
- `Max rounds: 4` — documents the cap inline in the state file
- `Escalation cap` — tracks whether the cap has been triggered and the user decision status

## Acceptance Criteria Verification

1. Round cap (round 4) documented in all 3 locations: PASS
2. `queen-state.md` tracks the cap with both a `Max rounds` and `Escalation cap` field: PASS
3. Cap is consistent across all 3 files (round 4 in every location): PASS
