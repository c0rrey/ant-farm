# Task Brief: ant-farm-yn1r
**Task**: compose-review-skeletons.sh sed regex converts all {UPPERCASE} tokens, not just slot markers
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/yn1r.md

## Context
- **Affected files**: scripts/compose-review-skeletons.sh:L99-102 -- sed pattern 's/{\([A-Z][A-Z_]*\)}/{{\1}}/g' and associated comment
- **Root cause**: sed blanket converts any {UPPERCASE} text to {{UPPERCASE}}, not just known slot markers. Also requires 2+ uppercase chars (undocumented -- single-char {A} would not match).
- **Expected behavior**: Either whitelist known slot names or document the assumption. Comment should accurately describe regex behavior.
- **Acceptance criteria**:
  1. Comment accurately describes the regex behavior (2+ char minimum)
  2. Either whitelist approach or documented assumption added

## Scope Boundaries
Read ONLY: scripts/compose-review-skeletons.sh:L1-227 (full file, focus on L99-102 sed pattern)
Do NOT edit: scripts/fill-review-slots.sh, scripts/parse-progress-log.sh, any other scripts

## Focus
Your task is ONLY to fix the comment and either whitelist known slot names or document the blanket-conversion assumption.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
