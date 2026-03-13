# Task Brief: ant-farm-6gg6
**Task**: Migrate Scout and implementation templates (mechanical)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/6gg6.md

## Context
- **Affected files**:
  - orchestration/templates/scout.md:L34-46,L83,L138,L267-285 — bd ready, bd show, bd list, bd blocked references
  - orchestration/templates/implementation.md:L25-26,L47,L71,L115,L168,L194,L197 — bd show, bd update, bd close references
- **Root cause**: Scout and implementation templates contain bd command references that need mechanical substitution to crumb equivalents.
- **Expected behavior**: All bd command references replaced with crumb equivalents; .beads/ paths replaced with .crumbs/.
- **Acceptance criteria**:
  1. scout.md contains zero occurrences of 'bd ready', 'bd show', 'bd list', 'bd blocked' -- replaced with crumb equivalents
  2. implementation.md contains zero occurrences of 'bd show', 'bd update', 'bd close' -- replaced with crumb equivalents
  3. grep -c '\bbd\b' on both files returns 0
  4. All .beads/ path references replaced with .crumbs/ equivalents
  5. No semantic changes to surrounding logic -- only string substitution

## Scope Boundaries
Read ONLY: orchestration/templates/scout.md (full file), orchestration/templates/implementation.md (full file)
Do NOT edit: Any other template files, RULES.md, pantry.md, checkpoints.md, or any file outside these two

## Focus
Your task is ONLY to replace bd command references with crumb equivalents and .beads/ paths with .crumbs/ in scout.md and implementation.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
