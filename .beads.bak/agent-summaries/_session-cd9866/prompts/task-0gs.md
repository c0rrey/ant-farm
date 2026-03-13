# Task Brief: ant-farm-0gs
**Task**: Step 0 wildcard glob may match stale reports from prior review cycles
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/0gs.md

## Context
- **Affected files**: orchestration/templates/reviews.md:L519 (comment warns about glob matching stale reports but the code examples at L471-483 use exact paths with timestamps -- need to verify all references consistently use exact paths, not globs), orchestration/RULES.md:L280-298 (Step 0 references that may use globs for report discovery)
- **Root cause**: The Step 0 report verification may use wildcard globs (e.g., `*-review-*.md`) that could match stale reports from prior review cycles. Reviews.md:L519 explicitly warns "Use [ -f "$EXACT_PATH" ] -- no globs. Globs match stale reports from prior rounds." but the implementation across all templates needs to be verified to ensure no glob patterns leak through. If a prior review cycle left reports in the same session directory, a glob-based check would falsely report them as present.
- **Expected behavior**: Step 0 glob only matches reports from the current review cycle, using exact timestamp-qualified paths rather than wildcard patterns.
- **Acceptance criteria**:
  1. All report existence checks across templates use exact timestamp-qualified paths, not wildcard globs that could match stale reports from prior review cycles

## Scope Boundaries
Read ONLY: orchestration/templates/reviews.md:L455-590 (Step 0/0a verification), orchestration/RULES.md:L270-310 (review path logic)
Do NOT edit: orchestration/templates/pantry.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/implementation.md, any scripts/ files, agents/ files

## Focus
Your task is ONLY to ensure Step 0 report verification uses exact timestamp-qualified paths instead of wildcard globs.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
