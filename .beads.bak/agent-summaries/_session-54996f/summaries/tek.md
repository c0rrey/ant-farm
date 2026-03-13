# Summary: ant-farm-tek

**Task**: Fix fragile wc -l polling loop in reviews.md Step 0a
**Commit**: bf6e38b
**File changed**: orchestration/templates/reviews.md (lines 363-395)

---

## 1. Approaches Considered

**Approach A: Individual per-type variables with `[ -f ]` checks (selected)**
Each report type gets its own variable (`FOUND_CLARITY`, etc.) set via `ls ... | head -1`. The loop condition uses `[ -f "$VAR" ]` on each independently. A `TIMED_OUT` flag initialized to 1 and cleared to 0 on success provides unambiguous post-loop detection. Tradeoff: slightly more verbose than the original, but fully correct under all conditions including re-runs with multiple matching files.

**Approach B: Separate `ls` commands with `&&` short-circuit**
Keep per-type `ls` calls but combine with `&&` in the loop condition rather than piping to `wc -l`. Tradeoff: cleaner than wc -l but still does not handle multiple matching files (ls could return multiple lines per type yet the `&&` succeeds). Rejected.

**Approach C: `find` with `-maxdepth 1 -name` and result check**
Use `find <dir> -maxdepth 1 -name "clarity-review-*.md" | head -1` to get the first match, then `[ -f ]`. More portable than `ls` for glob handling. Tradeoff: `find` invocation is heavier than `ls` and the behavior difference is minimal for this use case. Not selected over Approach A for simplicity.

**Approach D: Count distinct report types via `find -name` into a counter variable**
Use a running counter incremented per type found. Tradeoff: still numeric counting, susceptible to the same class of issues if logic is incorrect. Variable naming would not be inverted but the counting pattern remains fragile. Rejected.

---

## 2. Selected Approach with Rationale

**Approach A** was selected. It:
- Eliminates the `wc -l` fragility entirely by checking file existence per type
- Uses `head -1` to safely cap results when multiple files match (re-run scenario)
- Provides `TIMED_OUT=1` sentinel initialized before the loop, cleared only on success, checked post-loop
- Fixes the inverted variable name (`MISSING_REPORTS` -> `FOUND_*` per type)
- Adds the required comment about single-invocation execution

---

## 3. Implementation Description

Replaced lines 370-383 in `orchestration/templates/reviews.md` with:

- `TIMED_OUT=1` flag initialized before the while loop
- Four per-type `FOUND_*` variables assigned via `ls ... | head -1` inside the loop
- Loop break condition: `[ -f "$FOUND_CLARITY" ] && [ -f "$FOUND_EDGE" ] && [ -f "$FOUND_CORRECTNESS" ] && [ -f "$FOUND_EXCELLENCE" ]`
- On success: `TIMED_OUT=0; break`
- Post-loop: `if [ $TIMED_OUT -eq 1 ]` block that echoes a timeout message before falling through to the error return template

Added a header comment in the bash block: "IMPORTANT: This entire block must execute in a single Bash invocation. Shell state (variables) does not persist across separate Bash tool calls."

---

## 4. Correctness Review

**File: orchestration/templates/reviews.md (lines 363-395)**

- The `TIMED_OUT` flag is set before loop entry and only cleared inside the loop on success. Post-loop detection is unambiguous. Correct.
- Each `FOUND_*` variable captures only the first matching filename via `head -1`, so multiple glob matches (re-run scenario) do not produce a count > 1. Correct.
- `[ -f "$FOUND_CLARITY" ]` on an empty string evaluates to false. If `ls` returns no output, `head -1` produces an empty string, and `[ -f "" ]` is false. Correct.
- Variable names `FOUND_CLARITY`, `FOUND_EDGE`, `FOUND_CORRECTNESS`, `FOUND_EXCELLENCE` accurately reflect what they contain (found report paths). Correct.
- Single-invocation comment is present at the top of the bash block. Correct.
- Lines outside L354-424 were not modified. Scope respected.

**Acceptance criteria verification:**
1. Uses individual `[ -f ]` checks — PASS
2. Variable names accurately reflect contents — PASS (FOUND_* and TIMED_OUT)
3. Post-loop code distinguishes timeout from success — PASS (TIMED_OUT flag + post-loop if block)
4. Comment notes single Bash invocation requirement — PASS

---

## 5. Build/Test Validation

No automated test suite exists for markdown prompt templates. Manual inspection confirms:
- The bash block is syntactically valid POSIX sh
- `[ -f "" ]` correctly returns false (standard behavior)
- `ls ... 2>/dev/null | head -1` on a non-matching glob produces empty string (verified behavior)
- The `TIMED_OUT` pattern is a standard sentinel variable approach

---

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| Polling loop uses individual [ -f ] file existence checks instead of wc -l | PASS |
| Variable naming accurately reflects contents (FOUND_* per type, not MISSING_REPORTS) | PASS |
| Post-loop code distinguishes between timeout and success paths | PASS |
| Comment notes polling block must execute in single Bash invocation | PASS |
