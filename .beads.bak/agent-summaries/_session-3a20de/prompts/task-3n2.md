# Task Brief: ant-farm-3n2
**Task**: AGG-040: Clarify DMVDC sampling formula with plain English and examples
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/3n2.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L70 -- DMVDC Nitpickers threshold row with sampling formula max(3, min(5, ceil(N/3)))
  - orchestration/templates/checkpoints.md:L401 -- Check 1 Code Pointer Verification using the same formula
  - NOTE: Scout metadata had bare filename (no line numbers). Lines identified by Pantry via grep.
- **Root cause**: checkpoints.md requires Pest Control to calculate max(3, min(5, ceil(N/3))) for sampling review findings. LLMs may miscalculate ceil(), and the formula rationale is unexplained.
- **Expected behavior**: Expanded with plain English explanation and worked examples showing input finding counts and resulting sample sizes.
- **Acceptance criteria**:
  1. checkpoints.md DMVDC section includes plain English explanation of the sampling formula
  2. At least 3 worked examples show input finding counts and resulting sample sizes
  3. The formula and English description produce the same results for all examples

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md:L62-72 (Checkpoint-Specific Thresholds table), L382-438 (Nitpicker DMVDC section, especially Check 1)
Do NOT edit: Dirt Pusher DMVDC section (L306-380), CCO section (L97-163), WWD section (L235-303), CCB section (L457-572)

## Focus
Your task is ONLY to add plain English explanation and worked examples for the DMVDC sampling formula.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
