# Task Brief: ant-farm-lbcy
**Task**: fix: double-brace placeholder tier {{SLOT}} absent from PLACEHOLDER_CONVENTIONS.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-79d4200e/summaries/lbcy.md

## Context
- **Affected files**:
  - orchestration/templates/PLACEHOLDER_CONVENTIONS.md:L7-13 -- Overview table missing Tier 4
  - orchestration/templates/PLACEHOLDER_CONVENTIONS.md:L99-119 -- File-by-File Audit table needs reviews.md row fix
- **Root cause**: Double-brace convention was introduced by review slot-filling scripts without updating the placeholder conventions document.
- **Expected behavior**: PLACEHOLDER_CONVENTIONS.md should document the {{DOUBLE_BRACE}} tier and correctly reflect reviews.md usage in the audit table.
- **Acceptance criteria**:
  1. PLACEHOLDER_CONVENTIONS.md documents the {{DOUBLE_BRACE}} tier
  2. Tier 4 description identifies fill-review-slots.sh as the substitution mechanism
  3. File-by-File Audit table for reviews.md reflects the double-brace usage
  4. All {{SLOT}} markers across templates are accounted for in the new tier description

## Scope Boundaries
Read ONLY: orchestration/templates/PLACEHOLDER_CONVENTIONS.md:L1-236 (full file), CONTRIBUTING.md:L93-101 (placeholder conventions cross-reference for context)
Do NOT edit: Any file other than orchestration/templates/PLACEHOLDER_CONVENTIONS.md

## Focus
Your task is ONLY to add the {{DOUBLE_BRACE}} tier documentation and fix the reviews.md row in the audit table in PLACEHOLDER_CONVENTIONS.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
