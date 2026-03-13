# Task Brief: ant-farm-d3bk
**Task**: fix: fill-review-slots.sh @file argument notation undocumented in RULES.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2829f0f5/summaries/d3bk.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L168-170 -- Step 3b-ii script invocation documentation
- **Root cause**: fill-review-slots.sh (lines 78-94) implements an @file prefix notation for multiline arguments but RULES.md Step 3b-ii does not mention this feature. The core argument count and order match, but the convenience feature is undiscoverable from RULES.md alone.
- **Expected behavior**: RULES.md mentions @file prefix for multiline arguments.
- **Acceptance criteria**:
  1. RULES.md mentions @file prefix for multiline arguments (optional note/parenthetical)

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L160-180, scripts/fill-review-slots.sh:L78-94 (reference only, do not edit)
Do NOT edit: scripts/fill-review-slots.sh or any file other than orchestration/RULES.md.

## Focus
Your task is ONLY to add a note about the @file prefix notation to RULES.md Step 3b-ii.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
