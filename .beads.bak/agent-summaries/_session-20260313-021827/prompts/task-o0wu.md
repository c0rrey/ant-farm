# Task Brief: ant-farm-o0wu
**Task**: Migrate RULES-review.md (semantic)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/o0wu.md

## Context
- **Affected files**:
  - orchestration/RULES-review.md:L23,L155,L158 (bd command references and .beads/ paths in review workflow rules)
- **Root cause**: RULES-review.md contains review workflow rules referencing bd commands for issue queries and status updates.
- **Expected behavior**: All bd command references replaced with crumb equivalents; review workflow logic preserved.
- **Acceptance criteria**:
  1. All bd command references replaced with crumb equivalents
  2. Review workflow logic preserved -- only command syntax changes
  3. grep -c '\bbd\b' orchestration/RULES-review.md returns 0
  4. Any .beads/ path references updated to .crumbs/ (L23: .beads/issues.jsonl exclusion)

## Scope Boundaries
Read ONLY: orchestration/RULES-review.md (full file, focus on L23, L155, L158)
Do NOT edit: Any file other than orchestration/RULES-review.md. Do not change review step ordering, commit range logic, or file list generation workflow.

## Focus
Your task is ONLY to migrate bd CLI commands and .beads/ paths to crumb/.crumbs/ equivalents in RULES-review.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
