# Task Brief: ant-farm-epmv
**Task**: Migrate pantry.md (semantic)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/epmv.md

## Context
- **Affected files**: orchestration/templates/pantry.md:L91,L165,L276,L329,L331,L333-334 (6 bd references across distinct command patterns)
- **Root cause**: Pantry template contains 6 bd references across distinct command patterns (show, create, list, label, dep add) requiring semantic translation.
- **Expected behavior**: All 6 bd references converted to crumb equivalents with correct flag syntax; workflow logic preserved.
- **Acceptance criteria**:
  1. All 6 bd references in pantry.md converted to crumb equivalents
  2. bd dep add patterns converted to crumb link with correct flag (--parent or --blocked-by)
  3. bd label references removed
  4. grep -c '\bbd\b' orchestration/templates/pantry.md returns 0
  5. Pantry prompt composition workflow logic preserved

## Scope Boundaries
Read ONLY: orchestration/templates/pantry.md (full file, focus on L91, L165, L276, L329, L331, L333-334)
Do NOT edit: Any file other than orchestration/templates/pantry.md. Do not change the task brief format, preview composition logic, or session summary format.

## Focus
Your task is ONLY to migrate bd CLI commands to crumb CLI equivalents in pantry.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
