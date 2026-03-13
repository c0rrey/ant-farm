# Correctness Review Report

**Reviewer**: Correctness Nitpicker
**Commit range**: 201ee96~1..HEAD (4 commits)
**Review round**: 1
**Timestamp**: 20260220-113708

---

## Findings Catalog

### Finding C-1: `sed '$d'` deletes last report path instead of trailing newline

- **File**: /Users/correy/projects/ant-farm/scripts/fill-review-slots.sh:238
- **Severity**: P1
- **Category**: Logic error
- **Description**: In the `write_big_head_brief` function, the expected report paths list is built by appending lines with `\n` escape sequences, then using `printf '%b' "$expected_paths" | sed '$d'` to "remove trailing newline." However, `sed '$d'` deletes the **last line** of input, not a trailing newline character. This causes the last review type's report path to be silently dropped from the Big Head expected report paths list.

  In round 1, this means excellence-review is missing (3 of 4 paths emitted). In round 2+, edge-cases-review is missing (1 of 2 paths emitted). Big Head uses this list to verify all reports exist before starting consolidation. A missing path means Big Head either (a) starts consolidation without waiting for the last reviewer, or (b) reports a missing file when the reviewer does finish.

  **Reproduced**: Direct shell test confirms the bug:
  ```
  # Round 1: 4 types, excellence dropped
  # Round 2+: 2 types, edge-cases dropped
  ```

- **Suggested fix**: Replace `sed '$d'` with a construct that strips a trailing newline without deleting lines. For example:
  ```bash
  # Option A: use printf without trailing \n on the last iteration
  local expected_paths=""
  local first=true
  for rt in "${ACTIVE_REVIEW_TYPES[@]}"; do
      if [ "$first" = true ]; then
          first=false
      else
          expected_paths="${expected_paths}
  "
      fi
      expected_paths="${expected_paths}- ${SESSION_DIR}/review-reports/${rt}-review-${TIMESTAMP}.md"
  done

  # Option B: use sed to strip trailing blank line only
  expected_paths="$(printf '%b' "$expected_paths" | sed '/^$/d')"
  ```

### Finding C-2: awk `sub()` treats `&` and `\` as special in replacement string

- **File**: /Users/correy/projects/ant-farm/scripts/fill-review-slots.sh:176
- **Severity**: P3
- **Category**: Theoretical logic error
- **Description**: The `fill_slot` function uses awk's `sub(slot, val)` for text replacement. In POSIX awk, the replacement string in `sub()` treats `&` as "insert the matched text" and `\` as an escape character. If any slot value (e.g., a file path or commit range) contains `&` or `\`, the substitution would produce incorrect output.

  In the current usage, slot values are file paths, commit ranges, timestamps, and task IDs -- none of which are likely to contain `&` or `\`. This makes the bug theoretical rather than practical.

- **Suggested fix**: Escape `&` and `\` in `val` before calling `sub()`:
  ```awk
  gsub(/\\/, "\\\\", val)
  gsub(/&/, "\\&", val)
  ```

### Finding C-3: Review round validation accepts `0` as valid

- **File**: /Users/correy/projects/ant-farm/scripts/fill-review-slots.sh:80
- **Severity**: P3
- **Category**: Logic error (theoretical)
- **Description**: The validation regex `'^[0-9]+$'` accepts `0` as a valid review round. RULES.md defines review rounds starting at 1 ("default: 1"). A round of 0 would produce unexpected behavior in the round-comparison logic at line 137 (`if [ "$REVIEW_ROUND" -eq 1 ]`): round 0 would fall into the else branch and use the round 2+ reduced review types (correctness + edge-cases only), which is incorrect for a first review.

  This requires the Queen to pass `0`, which is unlikely but not validated against.

- **Suggested fix**: Change the regex to `'^[1-9][0-9]*$'` to require a positive integer >= 1.

---

## Preliminary Groupings

### Group 1: Big Head expected report paths (C-1)
- Root cause: Incorrect use of `sed '$d'` for trailing-newline removal
- Impact: Big Head receives incomplete list of expected reviewer reports
- Standalone finding, no other findings share this root cause

### Group 2: Input handling in fill_slot / fill-review-slots.sh (C-2, C-3)
- Root cause: Edge-case input assumptions in the slot-filling pipeline
- Both are low-probability issues where unusual inputs would cause incorrect behavior

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1       | 1     |
| P2       | 0     |
| P3       | 2     |
| **Total**| **3** |

---

## Cross-Review Messages

- None sent. All findings fall within correctness scope.

---

## Coverage Log

| File | Status | Findings |
|------|--------|----------|
| /Users/correy/projects/ant-farm/agents/big-head.md | Reviewed | No correctness issues found |
| /Users/correy/projects/ant-farm/agents/nitpicker.md | Reviewed | No correctness issues found |
| /Users/correy/projects/ant-farm/orchestration/RULES.md | Reviewed | No correctness issues found |
| /Users/correy/projects/ant-farm/orchestration/templates/pantry.md | Reviewed | No correctness issues found |
| /Users/correy/projects/ant-farm/orchestration/templates/scout.md | Reviewed | No correctness issues found |
| /Users/correy/projects/ant-farm/scripts/compose-review-skeletons.sh | Reviewed | No correctness issues found |
| /Users/correy/projects/ant-farm/scripts/fill-review-slots.sh | Reviewed | C-1 (P1), C-2 (P3), C-3 (P3) |
| /Users/correy/projects/ant-farm/scripts/sync-to-claude.sh | Reviewed | No correctness issues found |

---

## Acceptance Criteria Verification

### ant-farm-0cf (Parallelize review prompt composition via bash scripts)

1. **Pantry Section 1 invocation produces both implementation prompts AND review skeletons**: PASS -- pantry.md Step 2.5 calls compose-review-skeletons.sh during Section 1, producing 5 skeleton files alongside implementation prompts.
2. **No second Pantry invocation is needed for review prompt composition**: PASS -- RULES.md Step 3b now calls fill-review-slots.sh directly. pantry-review is deprecated in both Agent Types and Model Assignments tables.
3. **Queen context window absorbs zero template content from review prompt composition**: PASS -- Queen calls a bash script and reads stdout/exit code only. No file content enters Queen's context.
4. **Review prompts produced by the scripts are identical in structure to current Pantry Section 2 output**: PASS -- The skeleton + slot-fill approach produces the same structure (commit range, files, task IDs, report path, timestamp, review round). However, the Big Head expected paths list has a **data loss bug** (C-1) that breaks structural correctness for the Big Head brief specifically.
5. **Script failures surface as error messages to the Queen, not silent failures**: PASS -- Both scripts use `set -euo pipefail`, validate all inputs, check file existence, and emit structured error messages to stderr before `exit 1`.

### ant-farm-cifp (Add explicit scope fencing to Nitpicker agent definitions)

1. **Each Nitpicker reviewer has explicit 'not my job' boundaries that reference the other three review types by name**: PASS -- Each of the 4 specialization blocks (CLARITY, EDGE CASES, CORRECTNESS, EXCELLENCE) has a "NOT YOUR RESPONSIBILITY" section naming the other 3 types.
2. **Type-specific severity calibration is defined**: PASS -- Each block has "Severity calibration for {TYPE}" with P1/P2/P3 definitions.
3. **Big Head deduplication load is reduced**: PASS (structural) -- The scope fences and cross-review messaging guidelines should reduce cross-type duplicates at source.
4. **Shared concerns remain in one place, not duplicated across 4 files**: PASS -- Single nitpicker.md file with shared "Core Principles," "Workflow," and "Shared Rules" sections, plus conditional per-type blocks.

### ant-farm-7k1 (Severity conflict handling in big-head.md)

1. **big-head.md contains explicit guidance for handling 2+ level severity disagreements**: PASS -- Core principle added (line 14) and consolidation step 5 added (line 21).
2. **The guidance specifies: log discrepancy, use higher severity, flag for Queen review**: PASS -- All three actions are specified in both the principle and the step.
3. **A worked example shows the expected behavior**: PASS -- Example at big-head.md:28 shows "Reviewer A (Security) assessed P1, Reviewer B (Clarity) assessed P3" with final severity P1.

### ant-farm-w7p (Scout agent type tie-breaking)

1. **Scout reads full agent MD files for tied candidates (and only tied candidates) before falling back**: PASS -- scout.md Step 3 "Tie-breaking on equal scores" Step A specifies reading full .md files for ONLY tied candidates.
2. **Unresolved ties surface as 'PICK ONE: [type-a | type-b]' instead of 'group'**: PASS -- scout.md Step 3 Step B specifies the `PICK ONE: [type-a | type-b]` format.
3. **Each task with a tie lists its own candidates independently**: PASS -- scout.md Step 5 "Presenting tied agents" shows per-task notation in strategy output.
4. **No increase in Scout context usage when there are no ties**: PASS -- scout.md "Important" note at end of Step 3 confirms frontmatter-only reads are the default path.

---

## Overall Assessment

**Score**: 7/10

**Verdict**: PASS WITH ISSUES

The P1 finding (C-1) is a confirmed, reproduced logic bug in `fill-review-slots.sh` that silently drops the last review type from Big Head's expected report paths list. This affects every review cycle -- round 1 drops excellence, round 2+ drops edge-cases. The fix is straightforward (replace `sed '$d'` with correct trailing-newline removal).

All four tasks' acceptance criteria are met at the structural/design level. The bash scripts, agent definitions, and cross-file references are consistent and well-integrated. The only correctness issue is the `sed '$d'` bug in the slot-filling pipeline, which is a clear logic error rather than a design problem.
