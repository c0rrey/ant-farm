# Task Summary: ant-farm-j6jq
**Task**: Shell code blocks in reviews.md lack production quality: magic numbers, inverted sentinel, buried constraints
**Commit**: 306a457
**Files Changed**: orchestration/templates/reviews.md

## 1. Approaches Considered

**Approach A: Named constants + renamed sentinel + prominent constraint block (selected)**
Replace `TIMEOUT=30` and `POLL_INTERVAL=2` with `POLL_TIMEOUT_SECS=30` and `POLL_INTERVAL_SECS=2`, each with a rationale comment. Rename `TIMED_OUT=1` to `REPORTS_FOUND=0` (non-inverted: 0=not found, set to 1 on success). Add a `# --- CONSTRAINT: which reports to expect per round ---` header block before the while loop with a round summary table.
- Pro: Addresses all three acceptance criteria minimally and clearly; no structural change to the loop logic.
- Con: Slightly longer constant names (minor readability tradeoff, far outweighed by clarity).

**Approach B: Named constants only, keep TIMED_OUT with an explanatory comment**
Add rationale comments to `TIMEOUT` and `POLL_INTERVAL` but leave `TIMED_OUT=1` with a comment like `# starts as 1 (assumed timed out); cleared to 0 on success`.
- Pro: Smaller diff.
- Con: The task explicitly requires "fix inverted sentinel logic" — explaining the inversion is not fixing it. A comment is not a substitute for a clear variable name.

**Approach C: Restructure as a named function**
Wrap the polling logic in a `wait_for_reports()` function with local variables.
- Pro: Best scoping; local variables can't collide.
- Con: This is a documentation template for an LLM (Big Head) to execute in a single Bash invocation. A function definition is unnecessary complexity in that context and deviates from the template's established style.

**Approach D: Use `until` loop instead of `while` to remove the need for TIMED_OUT altogether**
`until check_all_reports; do sleep ...; done` — the loop exits naturally when all reports are found; a separate timeout counter handles the outer limit.
- Pro: Elegant; no sentinel variable needed.
- Con: Requires significant restructuring; changes the observable loop semantics; harder for a reader to audit the timeout logic at a glance. Scope creep beyond the stated defects.

## 2. Selected Approach with Rationale

Approach A. It precisely addresses each of the three stated defects without restructuring the loop logic. Named constants with rationale comments make the values self-documenting. Renaming `TIMED_OUT` to `REPORTS_FOUND` with an inline comment (`# set to 1 when all expected reports are present`) uses positive/non-inverted semantics — `REPORTS_FOUND=0` means "not yet found" and the failure check is `if [ $REPORTS_FOUND -eq 0 ]`, which reads naturally. The `# --- CONSTRAINT ---` block before the while loop prominently surfaces the round-specific report rules that were previously buried as inline comments inside the loop body.

## 3. Implementation Description

Changes to `orchestration/templates/reviews.md` (L495-581), within the polling loop bash code block:

**Magic numbers (AC1):**
- `TIMEOUT=30` replaced with `POLL_TIMEOUT_SECS=30` plus rationale comment: "30 seconds: enough for a slow reviewer to write its report; short enough to return a clear error rather than block the Queen indefinitely."
- `POLL_INTERVAL=2` replaced with `POLL_INTERVAL_SECS=2` plus rationale comment: "2 seconds: balances responsiveness against unnecessary busy-polling."
- All usages updated: `$TIMEOUT` → `$POLL_TIMEOUT_SECS`, `$POLL_INTERVAL` → `$POLL_INTERVAL_SECS`.

**Inverted sentinel (AC2):**
- `TIMED_OUT=1` (starts true, cleared to 0 on success) removed.
- `REPORTS_FOUND=0` added with inline comment `# set to 1 when all expected reports are present`.
- `TIMED_OUT=0` inside the `break` branch replaced with `REPORTS_FOUND=1`.
- `if [ $TIMED_OUT -eq 1 ]` replaced with `if [ $REPORTS_FOUND -eq 0 ]`.

**Buried constraints (AC3):**
- Removed the inline `# Round 1: check all 4 / # Round 2+: check only correctness and edge-cases` comment from inside the while loop body.
- Added a `# --- CONSTRAINT: which reports to expect per round ---` block above the placeholder guard section, with a two-line summary table listing both round cases and the glob-avoidance rule. This makes the round logic visible before entering the loop, not hidden inside it.

Total diff: 18 insertions, 16 deletions in reviews.md. No changes to fill-review-slots.sh or any other file.

## 4. Correctness Review

**orchestration/templates/reviews.md (L495-583):**
- `POLL_TIMEOUT_SECS=30` and `POLL_INTERVAL_SECS=2` are used consistently throughout: `while [ $ELAPSED -lt $POLL_TIMEOUT_SECS ]`, `sleep $POLL_INTERVAL_SECS`, `ELAPSED=$((ELAPSED + POLL_INTERVAL_SECS))`, and `within ${POLL_TIMEOUT_SECS}s` in the error message.
- `REPORTS_FOUND=0` initialized before the while loop. Set to `REPORTS_FOUND=1` in the success branch. Checked as `if [ $REPORTS_FOUND -eq 0 ]` after the loop — reads as "if reports were not found". Non-inverted. Clear.
- The `# --- CONSTRAINT ---` block is placed after the timing constants and before the placeholder guard, ensuring it is read before entering any loop. It lists all four round rules and the glob-avoidance rule.
- Loop body: redundant inline round comments removed (replaced by the constraint block). The `if [ "$REVIEW_ROUND" -eq 1 ]` conditionals from 352c.1 are preserved intact.
- No changes to narrative text, review type definitions, or other sections outside the bash code block.

**Acceptance Criteria Verification:**
- AC1 (magic numbers replaced with named constants or documented): PASS. `POLL_TIMEOUT_SECS` and `POLL_INTERVAL_SECS` replace `TIMEOUT` and `POLL_INTERVAL`, with rationale comments for both values.
- AC2 (sentinel logic is clear and non-inverted): PASS. `REPORTS_FOUND=0` starts false; set to 1 on success; checked as `-eq 0` for timeout path. Non-inverted throughout.
- AC3 (important constraints prominently placed): PASS. `# --- CONSTRAINT: which reports to expect per round ---` block appears before the while loop with the complete round breakdown, not buried in inline loop comments.

## 5. Build/Test Validation

- `bash -n scripts/fill-review-slots.sh` — not applicable (reviews.md is a template, not a script). Script syntax unchanged.
- The bash code block itself is not standalone-executable (contains `<session-dir>` placeholder literals). However, the shell control flow constructs (`while`, `if`, `[ ]`, `sleep`, arithmetic) are all standard POSIX sh.
- All variable references updated consistently: confirmed by reading the full modified block (L495-581) after edit.

## 6. Acceptance Criteria Checklist

- [x] AC1: Magic numbers replaced with named constants or documented — PASS. `POLL_TIMEOUT_SECS=30` (with rationale) and `POLL_INTERVAL_SECS=2` (with rationale) replace bare `TIMEOUT=30` and `POLL_INTERVAL=2`.
- [x] AC2: Sentinel logic is clear and non-inverted — PASS. `REPORTS_FOUND=0` (not found = 0, found = 1) replaces `TIMED_OUT=1` (timed out = 1, success = 0). Failure check is `if [ $REPORTS_FOUND -eq 0 ]`.
- [x] AC3: Important constraints are prominently placed — PASS. `# --- CONSTRAINT: which reports to expect per round ---` block with complete round breakdown placed before the while loop, replacing buried inline loop comments.
