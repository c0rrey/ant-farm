# Task Brief: ant-farm-j6jq
**Task**: Shell code blocks in reviews.md lack production quality: magic numbers, inverted sentinel, buried constraints
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/j6jq.md

## Context
- **Affected files**:
  - orchestration/templates/reviews.md:L501-504 -- magic numbers: TIMEOUT=30, ELAPSED=0, POLL_INTERVAL=2, TIMED_OUT=1 are hardcoded without explanatory constants or rationale
  - orchestration/templates/reviews.md:L504 -- inverted sentinel: TIMED_OUT=1 starts as "true" (1) and is set to 0 on success, which is opposite the typical FOUND=0/FOUND=1 pattern and confusing
  - orchestration/templates/reviews.md:L546-577 -- buried constraints: important logic (which reports to check per round, timeout behavior) is inline in the polling loop with minimal structural separation
  - NOTE: Scout metadata had bare filenames without line numbers. Line numbers above were determined by Pantry via direct file inspection.
- **Root cause**: Shell code blocks in reviews.md have magic numbers (hardcoded values without named constants or documented rationale), inverted sentinel logic (TIMED_OUT=1 as default/true is confusing boolean usage), and buried constraints (important rules like round-specific report checking are hidden in inline code comments rather than prominently placed).
- **Expected behavior**: Shell code blocks should use named constants (or document rationale for values), clear sentinel logic (non-inverted boolean naming), and prominently placed constraints (important rules separated from implementation detail).
- **Acceptance criteria**:
  1. Magic numbers replaced with named constants or documented
  2. Sentinel logic is clear and non-inverted
  3. Important constraints are prominently placed

## Scope Boundaries
Read ONLY:
- orchestration/templates/reviews.md:L490-580 (the polling loop shell code block)
- orchestration/templates/reviews.md:L459-489 (the Step 0 verification shell code block for context)

Do NOT edit:
- orchestration/templates/reviews.md content outside shell code blocks (narrative text, review type definitions, report format, checklists)
- scripts/fill-review-slots.sh
- scripts/compose-review-skeletons.sh

## Focus
Your task is ONLY to improve shell code block quality in reviews.md: replace magic numbers with named constants or add rationale, fix inverted sentinel logic, and prominently place buried constraints.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
