# Task Brief: ant-farm-szcy
**Task**: sync-to-claude.sh script selection has no explanatory comment
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/szcy.md

## Context
- **Affected files**: scripts/sync-to-claude.sh:L27-33 -- script iteration without comment explaining rationale
- **Root cause**: Iterates over two hardcoded script names (compose-review-skeletons.sh and fill-review-slots.sh) without explaining why only these two are synced and not others in the scripts/ directory.
- **Expected behavior**: Comment should explain the script selection rationale.
- **Acceptance criteria**:
  1. Comment explains the script selection rationale

## Scope Boundaries
Read ONLY: scripts/sync-to-claude.sh:L1-53 (full file, focus on L27-33)
Do NOT edit: scripts/install-hooks.sh, scripts/scrub-pii.sh, any other scripts

## Focus
Your task is ONLY to add a comment explaining why only compose-review-skeletons.sh and fill-review-slots.sh are synced.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
