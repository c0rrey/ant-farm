# Task Brief: ant-farm-tour
**Task**: SESSION_PLAN_TEMPLATE stale review decision logic contradicts RULES.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-5da05acb/summaries/tour.md

## Context
- **Affected files**:
  - orchestration/templates/SESSION_PLAN_TEMPLATE.md:L207-224 — Review Wave section describes sequential model; current uses parallel TeamCreate
  - orchestration/templates/SESSION_PLAN_TEMPLATE.md:L226-237 — Review Follow-Up Decision thresholds contradict RULES.md Step 3c
- **Root cause**: SESSION_PLAN_TEMPLATE.md was not updated after the review workflow was redesigned. The Review Wave section describes sequential reviews with per-agent time estimates, but the current workflow uses parallel TeamCreate. The decision thresholds contradict RULES.md Step 3c.
- **Expected behavior**: Review Wave section should describe parallel TeamCreate model. Decision block should reference RULES.md Step 3c or be marked deprecated.
- **Acceptance criteria**:
  1. Review Wave section describes parallel TeamCreate model (not sequential)
  2. Review Follow-Up Decision block references RULES.md Step 3c or is marked deprecated
  3. No specific issue-count thresholds that contradict the root-cause-based triage in RULES.md

## Scope Boundaries
Read ONLY: orchestration/templates/SESSION_PLAN_TEMPLATE.md:L200-240, orchestration/RULES.md Step 3c (for reference on current decision logic)
Do NOT edit: orchestration/RULES.md, orchestration/templates/reviews.md, orchestration/templates/pantry.md

## Focus
Your task is ONLY to update the stale review decision logic in SESSION_PLAN_TEMPLATE.md to match the current parallel TeamCreate workflow.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
