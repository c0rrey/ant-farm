# Task Summary: ant-farm-ti6g

**Task**: fill-review-slots.sh accepts review round 0 as valid input
**Commit**: e4b5e96

## Approaches Considered

1. **Change regex to `^[1-9][0-9]*$`** — Matches strings starting with a digit 1-9 followed by zero or more digits. Rejects 0, 00, empty string, and non-numeric input. Accepts 1, 2, 10, 99, etc. Single-character change to the regex. Chosen approach.

2. **Keep `^[0-9]+$` and add `[ "$REVIEW_ROUND" -lt 1 ]` arithmetic check** — Two-step validation: format check then range check. Correct, but adds an extra line and exit path for a problem solvable in the regex alone. Rejected in favor of approach 1.

3. **Arithmetic expression `(( REVIEW_ROUND >= 1 ))`** — Replace the entire grep block with bash arithmetic. Under `set -e`, non-numeric input would cause an arithmetic error, but the error message would be a bash syntax error rather than the script's custom "must be a positive integer" message. User experience is worse. Rejected.

4. **Use awk for combined format + range check** — `echo "$REVIEW_ROUND" | awk '$1 ~ /^[0-9]+$/ && $1 >= 1'`. Correct but spawns an extra process for a simple regex fix. Rejected.

5. **Regex `^[0-9]*[1-9][0-9]*$`** — Also rejects 0/00 but accepts leading zeros in valid rounds (e.g., `09` would be accepted). Less strict and less conventional than `^[1-9][0-9]*$`. Rejected.

## Selected Approach

**Approach 1 — Change regex to `^[1-9][0-9]*$`.**

Rationale: Minimum delta, directly encodes the constraint (first digit must be 1-9), aligns with the task's suggested fix, and matches the existing error message ("positive integer"). Updated the error message to include ">= 1" for additional clarity.

## Implementation Description

Single regex change at L103:

```bash
# Before
if ! echo "$REVIEW_ROUND" | grep -qE '^[0-9]+$'; then

# After
if ! echo "$REVIEW_ROUND" | grep -qE '^[1-9][0-9]*$'; then
```

Error message updated from "must be a positive integer" to "must be a positive integer (>= 1)" to make the lower bound explicit to the caller.

## Correctness Review

**scripts/fill-review-slots.sh** (full file reviewed, focus on L103-106):

- L103: `^[1-9][0-9]*$` — first character must be in [1-9], followed by zero or more [0-9]. Empty string: no match (grep returns non-zero), script errors. "0": no match (starts with 0, not 1-9). "00": no match. "1": matches. "10": matches. "abc": no match. Correct.
- L104: Error message updated to clarify ">= 1" requirement. Correct.
- L137: `if [ "$REVIEW_ROUND" -eq 1 ]` — this numeric comparison is still valid; REVIEW_ROUND is guaranteed to be a positive integer by the time it reaches here. Correct.
- No other uses of REVIEW_ROUND depend on the regex; all downstream uses are arithmetic comparisons. Correct.

Acceptance criteria verification:
- AC1 (round 0 is rejected with error message): `^[1-9][0-9]*$` does not match "0"; script prints "ERROR: REVIEW_ROUND must be a positive integer (>= 1), got: 0" and exits 1. PASS.
- AC2 (round 1 and higher continue to work): `^[1-9][0-9]*$` matches 1, 2, ..., 10, 99, etc. PASS.

## Build/Test Validation

- `bash -n scripts/fill-review-slots.sh` — syntax check passed.
- Regex boundary tests: 0 REJECT, 1 ACCEPT, 2 ACCEPT, 10 ACCEPT, 99 ACCEPT, "00" REJECT, "abc" REJECT, "1a" REJECT, "-1" REJECT, "" REJECT. All correct.

## Acceptance Criteria Checklist

- [x] Round 0 is rejected with an error message — PASS (regex rejects 0, error message printed to stderr)
- [x] Round 1 and higher continue to work — PASS (regex accepts all positive integers)
