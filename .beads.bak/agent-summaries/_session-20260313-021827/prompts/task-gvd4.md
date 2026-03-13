# Task Brief: ant-farm-gvd4
**Task**: Migrate dirt-pusher, nitpicker, scribe skeletons (mechanical)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/gvd4.md

## Context
- **Affected files**:
  - orchestration/templates/dirt-pusher-skeleton.md:L36,L44 — bd show, bd update, bd close references
  - orchestration/templates/nitpicker-skeleton.md:L39,L52 — bd show reference, bd create reference
  - orchestration/templates/scribe-skeleton.md:L47,L53 — bd show, 'beads' terminology
- **Root cause**: Skeleton templates contain bd command references needing mechanical substitution.
- **Expected behavior**: All bd command references replaced with crumb equivalents; beads/bead terminology updated to crumbs/crumb.
- **Acceptance criteria**:
  1. dirt-pusher-skeleton.md: all bd -> crumb command references updated
  2. nitpicker-skeleton.md: 3 bd references replaced with crumb equivalents (L39, L52, plus any others found)
  3. scribe-skeleton.md: bd show -> crumb show, 'beads' -> 'crumbs' terminology throughout
  4. grep -c '\bbd\b' on all three files returns 0
  5. No semantic changes to skeleton prompt logic

## Scope Boundaries
Read ONLY: orchestration/templates/dirt-pusher-skeleton.md (full file), orchestration/templates/nitpicker-skeleton.md (full file), orchestration/templates/scribe-skeleton.md (full file)
Do NOT edit: Any other template files, implementation.md, scout.md, queen-state.md, or any file outside these three

## Focus
Your task is ONLY to replace bd command references with crumb equivalents and beads terminology with crumbs in dirt-pusher-skeleton.md, nitpicker-skeleton.md, and scribe-skeleton.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
