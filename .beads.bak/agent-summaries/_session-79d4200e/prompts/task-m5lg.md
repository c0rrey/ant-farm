# Task Brief: ant-farm-m5lg
**Task**: fix: review-skeletons/ and review-reports/ missing from Step 0 session directory setup
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-79d4200e/summaries/m5lg.md

## Context
- **Affected files**:
  - orchestration/RULES.md (after L336) -- add note about review-skeletons/ and review-reports/ lazy creation
- **Root cause**: review-skeletons/ and review-reports/ directories were introduced after the original Step 0 setup. They are created lazily but the Session Directory section gives no hint they will exist.
- **Expected behavior**: RULES.md Session Directory section should document all 7 subdirectories including the lazily-created review dirs.
- **Acceptance criteria**:
  1. RULES.md Session Directory section documents all 7 subdirectories that appear in practice
  2. Note clarifies lazy creation (review dirs created by their respective phases, not at Step 0)
  3. Crash recovery documentation accounts for directories that may not yet exist

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L330-370 (Session Directory section and crash recovery)
Do NOT edit: Any section of RULES.md outside Session Directory, any other file

## Focus
Your task is ONLY to document the review-skeletons/ and review-reports/ lazy-created directories in the RULES.md Session Directory section.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
