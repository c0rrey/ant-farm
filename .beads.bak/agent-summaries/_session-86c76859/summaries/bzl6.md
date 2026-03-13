# Summary: ant-farm-bzl6

**Task**: Add self-contained input validation to build-review-prompts.sh (REVIEW_ROUND >= 1 regex check and non-empty CHANGED_FILES check)
**Commit**: `ed0a651`
**Status**: Implementation complete. Do NOT close bead — awaiting Queen DMVDC verification.

---

## 1. Approaches Considered

### Approach A: Minimal targeted edits (two separate blocks)
Change the regex on L95 in-place and insert a separate CHANGED_FILES check block between L89 and L95. Keeps the sections separate as they appear in the original file. Two small, surgical edits with no structural changes.

**Tradeoff**: Leaves validation split across two code locations — the CHANGED_FILES check above the comment header, the REVIEW_ROUND check below it. Slightly harder to scan.

### Approach B: Consolidate into one "Input validation" section (selected)
Remove the existing L95-98 REVIEW_ROUND block and add a unified "Input validation" section immediately after L89 containing both checks in order: CHANGED_FILES first (depends on resolved value), then REVIEW_ROUND. Directly satisfies acceptance criterion #5 ("consolidating all input validation in one section").

**Tradeoff**: Slightly more structural change than Approach A, but produces cleaner code organization and is explicitly required by AC5.

### Approach C: Extract a `validate_inputs()` function
Wrap both checks in a named function called after argument resolution. Cleaner architecture for larger validation suites.

**Tradeoff**: Adds indirection for only two simple guard checks. Overkill here.

### Approach D: Use `grep -qE` for both checks (keep original style)
Keep `grep -qE` for REVIEW_ROUND (fixing only the regex pattern) and use `grep -qvE '^[[:space:]]*$'` for CHANGED_FILES.

**Tradeoff**: Spawns subprocesses for each check. The RULES.md Step 3b-i.5 uses bash parameter expansion (`${CHANGED_FILES//[[:space:]]/}`) and `[[ =~ ]]` — subprocess-free and more portable. Using `grep` diverges from the canonical reference without benefit.

### Approach E: Add validation inside `resolve_arg()` function
Add a non-empty check at the end of `resolve_arg()`, triggered conditionally for CHANGED_FILES.

**Tradeoff**: Requires adding a second argument to `resolve_arg` to flag which arguments to validate, or always checking all resolved args. Overcomplicates a general-purpose helper; the caller site is the right place for application-level invariants.

---

## 2. Selected Approach

**Approach B** (consolidated section) combined with **bash-native style from Approach D**.

**Rationale**:
- AC5 explicitly requires a single consolidated validation section placed after argument resolution and before downstream logic.
- Using `[[ =~ ]]` for REVIEW_ROUND and `${VAR//[[:space:]]/}` for CHANGED_FILES matches RULES.md Step 3b-i.5 exactly, making the two validation guards consistent with the Queen's own checks.
- No subprocess overhead; simpler and more portable.

---

## 3. Implementation Description

**File changed**: `scripts/build-review-prompts.sh`

**What was removed**: The old validation section at L91-98:
```bash
# ---------------------------------------------------------------------------
# Validate review round
# ---------------------------------------------------------------------------

if ! echo "$REVIEW_ROUND" | grep -qE '^[0-9]+$'; then
    echo "ERROR: REVIEW_ROUND must be a positive integer, got: $REVIEW_ROUND" >&2
    exit 1
fi
```

**What replaced it** (now at L91-106):
```bash
# ---------------------------------------------------------------------------
# Input validation (after @file resolution)
# ---------------------------------------------------------------------------

# CHANGED_FILES: must be non-empty (at least one changed file)
# Strip all whitespace via parameter expansion — no subprocesses required.
if [[ -z "${CHANGED_FILES//[[:space:]]/}" ]]; then
    echo "ERROR: CHANGED_FILES is empty (got: '${CHANGED_FILES_RAW}'). Expected: at least one file path (or a non-empty @file)." >&2
    exit 1
fi

# REVIEW_ROUND: must be a positive integer >= 1
if ! [[ "${REVIEW_ROUND}" =~ ^[1-9][0-9]*$ ]]; then
    echo "ERROR: REVIEW_ROUND must be a positive integer >= 1, got: '${REVIEW_ROUND}'. Expected format: ^[1-9][0-9]*\$ (e.g. 1, 2, 10)." >&2
    exit 1
fi
```

**Placement**: Immediately after L88-89 where `resolve_arg` resolves CHANGED_FILES and TASK_IDS, before the output directory setup at L108. No other sections of the file were modified.

---

## 4. Correctness Review

### scripts/build-review-prompts.sh

**Changed lines**: L91-106 (validation section)

**CHANGED_FILES check (L97-100)**:
- Uses `${CHANGED_FILES//[[:space:]]/}` to strip all whitespace (spaces, tabs, newlines).
- `-z` check correctly catches empty string, whitespace-only string, and newline-only string (e.g. an @file containing only a blank line).
- Error message includes `'${CHANGED_FILES_RAW}'` (the original argument, not the resolved content) — this is intentional: if CHANGED_FILES_RAW is `@/tmp/empty.txt`, showing the raw arg tells the user which file was empty. The error also states the expected format.
- Emits to stderr, exits 1. Correct.

**REVIEW_ROUND check (L103-106)**:
- Regex `^[1-9][0-9]*$` rejects 0, empty string, non-numeric values, negative values, and floats. Accepts 1, 2, 10, 100, etc.
- `[[ =~ ]]` is bash-native and subprocess-free.
- Error message includes `'${REVIEW_ROUND}'` (the received value) and `Expected format: ^[1-9][0-9]*$`. Correct.
- Emits to stderr, exits 1. Correct.

**No other sections modified**: The `resolve_arg` function (L74-86), argument parsing (L50-57), output directory setup (L108+), and downstream round logic (L121-126) are all untouched.

**Regression risk**: None. Valid inputs (REVIEW_ROUND=1, 2, 10; non-empty CHANGED_FILES) proceed past validation and reach the same downstream logic as before. The only behavioral change is rejection of previously-accepted invalid values (REVIEW_ROUND=0, empty CHANGED_FILES).

---

## 5. Build/Test Validation

**Syntax check**: `bash -n scripts/build-review-prompts.sh` → OK

**Functional tests** (run with dummy skeleton files):

| Test | Input | Expected | Result |
|------|-------|----------|--------|
| 1 | REVIEW_ROUND=0, valid CHANGED_FILES | exit=1, REVIEW_ROUND error | PASS |
| 2 | REVIEW_ROUND=1, CHANGED_FILES="" | exit=1, CHANGED_FILES error | PASS |
| 3 | REVIEW_ROUND=1, CHANGED_FILES="   " | exit=1, CHANGED_FILES error | PASS |
| 4 | REVIEW_ROUND=1, CHANGED_FILES="file.txt" | exit=0, script runs | PASS |
| 5 | REVIEW_ROUND=2, CHANGED_FILES="file.txt" | exit=0, script runs | PASS |
| 6 | REVIEW_ROUND=10, CHANGED_FILES="file.txt" | exit=0, script runs | PASS |
| 7 | REVIEW_ROUND=abc, valid CHANGED_FILES | exit=1, REVIEW_ROUND error | PASS |

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | REVIEW_ROUND validation uses regex `^[1-9][0-9]*$` (or equivalent) that rejects 0 while accepting 1, 2, 10 | PASS |
| 2 | After resolve_arg resolves CHANGED_FILES, a validation check confirms the result is non-empty and not whitespace-only; on failure, emits a clear error to stderr and exits 1 | PASS |
| 3 | Error messages for both validation failures include the invalid value received and the expected format | PASS |
| 4 | Existing valid inputs (REVIEW_ROUND=1, REVIEW_ROUND=2, non-empty file lists) continue to work without regression | PASS |
| 5 | The validation block is placed after argument resolution (L88-89) but before the existing REVIEW_ROUND check (L95), consolidating all input validation in one section | PASS |
