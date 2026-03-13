# Task Brief: ant-farm-pid
**Task**: AGG-038: Clarify wildcard artifact path matching in reviews.md transition gate
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/pid.md

## Context
- **Affected files**:
  - orchestration/templates/reviews.md:L4-17 -- Transition Gate Checklist section
  - orchestration/templates/reviews.md:L11 -- DMVDC artifact verification using wildcard * for timestamp portion
  - NOTE: Scout metadata had bare filename (no line numbers). Lines identified by Pantry via content analysis.
- **Root cause**: reviews.md specifies verifying artifacts with wildcard * for the timestamp portion. Multiple files could match due to retries, and the instruction does not specify which to check.
- **Expected behavior**: Clarified: Verify at least one DMVDC artifact exists with PASS verdict. If multiple exist, the most recent by timestamp must show PASS.
- **Acceptance criteria**:
  1. reviews.md transition gate specifies which artifact to check when multiple match the wildcard
  2. The most-recent-by-timestamp rule is documented for retry scenarios
  3. The PASS verdict requirement is explicit (not just file existence)

## Scope Boundaries
Read ONLY: orchestration/templates/reviews.md:L1-28 (Transition Gate Checklist and Pre-Spawn Directory Setup sections)
Do NOT edit: Agent Teams Protocol (L30+), Review type sections (L215+), Nitpicker Report Format (L374+), Big Head Consolidation Protocol (L449+), Queen's Checklists (L767+)

## Focus
Your task is ONLY to clarify wildcard artifact path matching in the transition gate checklist.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
