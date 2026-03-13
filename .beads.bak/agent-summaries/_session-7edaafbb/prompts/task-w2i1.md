# Task Brief: ant-farm-w2i1
**Task**: Fragile comment-delimited conditionals and missing placeholder validation in template system
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/w2i1.md

## Context
- **Affected files**:
  - orchestration/templates/reviews.md:L527-541, L560-563 -- comment-delimited conditional blocks (IF ROUND 1 markers)
  - scripts/fill-review-slots.sh:L345-373 -- output verification section lacks placeholder validation for unfilled {{SLOT}} markers
  - NOTE: Scout metadata had bare filenames without line numbers. Line numbers above were determined by Pantry via direct file inspection.
- **Root cause**: Template system uses comment-delimited conditionals (# <IF ROUND 1> / # </IF ROUND 1>) that are fragile because they rely on LLM interpretation to strip them in round 2+. Additionally, fill-review-slots.sh verifies output files exist and are non-empty (L345-373) but does not check whether {{SLOT}} markers survived substitution, meaning unfilled slots pass silently.
- **Expected behavior**: Conditionals should be robust and placeholder validation should catch unfilled slots.
- **Acceptance criteria**:
  1. Conditional block processing is more robust
  2. Placeholder validation catches unfilled slots

## Scope Boundaries
Read ONLY:
- orchestration/templates/reviews.md:L490-580 (polling loop with conditional markers)
- scripts/fill-review-slots.sh:L1-386 (full file, focus on L168-249 fill_all_slots and L345-373 verification)

Do NOT edit:
- orchestration/templates/reviews.md content outside the polling loop shell blocks (L1-489, L580-921)
- scripts/compose-review-skeletons.sh
- orchestration/RULES.md

## Focus
Your task is ONLY to make conditional block processing more robust and add placeholder validation for unfilled slot markers in fill-review-slots.sh.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
