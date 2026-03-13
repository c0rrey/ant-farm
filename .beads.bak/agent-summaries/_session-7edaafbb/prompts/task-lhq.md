# Task Brief: ant-farm-lhq
**Task**: Scout error metadata template lacks context fields (Title, Epic) present in success template
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/lhq.md

## Context
- **Affected files**: orchestration/templates/scout.md:L265-277 -- Error Handling section, error metadata template; orchestration/templates/scout.md:L86-110 -- success metadata template (for reference)
- **Root cause**: The error metadata template in scout.md (L272-277) only includes Status and Error Details fields. The success template (L86-110) includes Title, Type, Priority, Epic, Agent Type, Dependencies, etc. When bd show fails, downstream agents lose context about the task.
- **Expected behavior**: Error metadata template should include as many context fields as possible (at minimum Title and Epic from the task listing).
- **Acceptance criteria**:
  1. Error metadata template includes Title and Epic fields (from bd list output)
  2. Error template clearly marks which fields could not be populated

## Scope Boundaries
Read ONLY: orchestration/templates/scout.md:L1-286 (full file, focus on L265-277 Error Handling and L86-110 success template)
Do NOT edit: orchestration/RULES.md, orchestration/templates/pantry.md, scripts/

## Focus
Your task is ONLY to enrich the scout.md error metadata template with additional context fields.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
