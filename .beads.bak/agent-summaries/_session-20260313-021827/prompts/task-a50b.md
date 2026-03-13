# Task Brief: ant-farm-a50b
**Task**: Migrate big-head-skeleton.md (semantic)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/a50b.md

## Context
- **Affected files**: orchestration/templates/big-head-skeleton.md:L115-185 (bd create, bd dep add, bd epic create, bd search, bd label add, bd list references)
- **Root cause**: Big-head skeleton contains structural command patterns requiring semantic translation (not just string replacement). bd create --type=bug needs JSON conversion; bd dep add needs crumb link; bd epic create needs crumb trail create.
- **Expected behavior**: All bd commands structurally migrated to crumb CLI equivalents with correct JSON/flag syntax.
- **Acceptance criteria**:
  1. bd create --type=bug converted to crumb create --from-json with full JSON
  2. bd dep add --type parent-child converted to crumb link --parent
  3. bd epic create converted to crumb trail create --title
  4. bd search converted to crumb search (syntax identical)
  5. bd label add references removed
  6. bd list -n 0 --short converted to crumb list --short
  7. Big Head's dedup and filing workflow logic remains intact

## Scope Boundaries
Read ONLY: orchestration/templates/big-head-skeleton.md (full file, focus on L115-185 for bd command patterns)
Do NOT edit: Any file other than orchestration/templates/big-head-skeleton.md. Do not change review logic, polling loops, or SendMessage instructions.

## Focus
Your task is ONLY to migrate bd CLI commands to crumb CLI equivalents in big-head-skeleton.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
