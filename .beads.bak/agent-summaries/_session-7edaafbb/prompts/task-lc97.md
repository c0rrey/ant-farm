# Task Brief: ant-farm-lc97
**Task**: fill-review-slots.sh resolve_arg accepts empty file content without warning
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/lc97.md

## Context
- **Affected files**: scripts/fill-review-slots.sh:L59-71 -- resolve_arg function
- **Root cause**: resolve_arg handles @file references. When file exists but is empty (0 bytes), cat returns empty string without error. Script continues with blank CHANGED_FILES or TASK_IDS, producing review prompts with empty slot fills.
- **Expected behavior**: Empty @file content should produce a warning or error.
- **Acceptance criteria**:
  1. Empty @file content produces a warning or error
  2. Non-empty files continue to work unchanged

## Scope Boundaries
Read ONLY: scripts/fill-review-slots.sh:L1-183 (full file, focus on L59-71 resolve_arg function)
Do NOT edit: scripts/compose-review-skeletons.sh, orchestration/ templates, any other scripts

## Focus
Your task is ONLY to add empty-file detection in resolve_arg for @file references.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
