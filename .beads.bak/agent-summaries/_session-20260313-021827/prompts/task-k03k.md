# Task Brief: ant-farm-k03k
**Task**: Migrate reference and setup documentation (mechanical)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/k03k.md

## Context
- **Affected files**:
  - orchestration/reference/dependency-analysis.md:L59-60,L195 — bd show, bd blocked references
  - orchestration/SETUP.md:L87,L93,L226 — bd create, bd show references
- **Root cause**: Reference and setup documentation contain bd references needing mechanical substitution.
- **Expected behavior**: All bd references replaced with crumb equivalents; .beads/ paths updated to .crumbs/.
- **Acceptance criteria**:
  1. dependency-analysis.md: 4 bd references replaced with crumb equivalents (L59, L60, L195, plus any others found)
  2. SETUP.md: 3 bd references replaced with crumb equivalents (L87, L93, L226)
  3. grep -c '\bbd\b' on both files returns 0
  4. .beads/ paths updated to .crumbs/ where present

## Scope Boundaries
Read ONLY: orchestration/reference/dependency-analysis.md (full file), orchestration/SETUP.md (full file)
Do NOT edit: Any other reference files, RULES.md, templates/, or any file outside these two

## Focus
Your task is ONLY to replace bd command references with crumb equivalents and .beads/ paths with .crumbs/ in dependency-analysis.md and SETUP.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
