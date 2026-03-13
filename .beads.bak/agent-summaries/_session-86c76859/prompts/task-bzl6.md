# Task Brief: ant-farm-bzl6
**Task**: Add self-contained input validation to build-review-prompts.sh (REVIEW_ROUND >= 1 regex check and non-empty CHANGED_FILES check)
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-86c76859/summaries/bzl6.md

## Context
- **Affected files**:
  - `scripts/build-review-prompts.sh:L95-98` -- REVIEW_ROUND validation uses `grep -qE '^[0-9]+$'` which allows 0; should use `^[1-9][0-9]*$` to enforce >= 1
  - `scripts/build-review-prompts.sh:L74-86` -- `resolve_arg()` function reads file content via `cat` but does not validate that the resolved value is non-empty; an empty @file or whitespace-only content passes through silently
- **Root cause**: `build-review-prompts.sh` relies on the Queen having already validated inputs per RULES.md Step 3b-i.5, but does not enforce these guards itself. The REVIEW_ROUND validation regex at L95 (`'^[0-9]+$'`) accepts `0`, which is not a valid round number (rounds start at 1). The `resolve_arg` function at L74-86 reads @file content but does not check whether the resolved content is non-empty, so an empty CHANGED_FILES list passes silently and produces review prompts with no files to review. If the script is called directly or the Queen's guard is bypassed, invalid inputs produce silently wrong output.
- **Expected behavior**: (1) REVIEW_ROUND validation rejects 0 by using the regex `^[1-9][0-9]*$`. (2) After resolving @file arguments, the script validates that CHANGED_FILES is non-empty (not just whitespace). Both checks emit clear error messages on failure and exit non-zero.
- **Acceptance criteria**:
  1. REVIEW_ROUND validation at L95-98 uses regex `^[1-9][0-9]*$` (or equivalent) that rejects 0 while accepting 1, 2, 10, etc.
  2. After `resolve_arg` resolves CHANGED_FILES (L88), a validation check confirms the result is non-empty and not whitespace-only; on failure, emits a clear error message to stderr and exits with code 1
  3. Error messages for both validation failures include the invalid value received and the expected format
  4. Existing valid inputs (REVIEW_ROUND=1, REVIEW_ROUND=2, non-empty file lists) continue to work without regression
  5. The validation block is placed after argument resolution (L88-89) but before the existing REVIEW_ROUND check (L95), consolidating all input validation in one section

## Scope Boundaries
Read ONLY:
- `scripts/build-review-prompts.sh:L1-390` (full file -- need to understand argument parsing at L50-57, resolve_arg at L74-86, existing validation at L95-98, and downstream usage)
- `orchestration/RULES.md:L169-191` (Step 3b-i.5 validation block -- reference for what guards the Queen is expected to run, to ensure script guards are consistent)

Do NOT edit:
- `orchestration/RULES.md` (not in scope -- ant-farm-m2cb handles parts of this file)
- `orchestration/templates/reviews.md` (not in scope)
- `orchestration/templates/big-head-skeleton.md` (not in scope)
- Any file not listed in Affected files above

## Focus
Your task is ONLY to add REVIEW_ROUND >= 1 validation and non-empty CHANGED_FILES validation to build-review-prompts.sh.
Do NOT fix adjacent issues you notice (e.g., temp file cleanup, ordering dependencies).

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
