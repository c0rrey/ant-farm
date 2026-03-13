# Task Brief: ant-farm-bi3
**Task**: Pantry template lacks fail-fast for missing task-metadata dir and empty file list
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/bi3.md

## Context
- **Affected files**: orchestration/templates/pantry.md:L44 (Step 2 reads task-metadata files without dir existence check), orchestration/templates/pantry.md:L251-286 (Section 2 review mode receives file list without empty guard), orchestration/templates/pantry.md:L37 (uses ambiguous 'Read this file' instead of explicit filename)
- **Root cause**: orchestration/templates/pantry.md has two fail-fast gaps: (1) Step 2 (implementation mode) reads task-metadata/{TASK_SUFFIX}.md but does not check if the task-metadata/ directory itself exists before iterating. (2) Section 2 (review mode) receives a changed-file list from the Queen but has no guard against an empty list (the guard at L275-286 exists but AC requires verification it covers all entry points). Additionally, the phrase 'Read this file' at L37 is ambiguous and should use the explicit filename.
- **Expected behavior**: Missing task-metadata/ produces actionable error. Empty file list produces immediate failure. 'Read this file' replaced with explicit file name reference.
- **Acceptance criteria**:
  1. Missing task-metadata/ directory produces an actionable error message before any per-task iteration
  2. Empty file list in Section 2 produces immediate failure with descriptive message
  3. 'Read this file' at L37 replaced with explicit file name reference (e.g., 'Read `~/.claude/orchestration/templates/implementation.md`')
  4. Introduce {REVIEW_TIMESTAMP} placeholder or equivalent for timestamp consistency

## Scope Boundaries
Read ONLY: orchestration/templates/pantry.md:L1-557
Do NOT edit: orchestration/RULES.md, orchestration/templates/implementation.md, orchestration/templates/reviews.md, any scripts/ files

## Focus
Your task is ONLY to add fail-fast guards for missing task-metadata directory and empty file list, replace ambiguous 'Read this file' with explicit filename, and introduce a REVIEW_TIMESTAMP placeholder.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
