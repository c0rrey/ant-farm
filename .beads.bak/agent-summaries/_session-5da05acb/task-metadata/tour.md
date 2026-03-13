# Task: ant-farm-tour
**Status**: success
**Title**: SESSION_PLAN_TEMPLATE stale review decision logic contradicts RULES.md
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/SESSION_PLAN_TEMPLATE.md:207-224 — Review Wave section describes sequential model; current uses parallel TeamCreate
- orchestration/templates/SESSION_PLAN_TEMPLATE.md:226-237 — Review Follow-Up Decision thresholds contradict RULES.md Step 3c

## Root Cause
SESSION_PLAN_TEMPLATE.md was not updated after the review workflow was redesigned. The Review Wave section describes sequential reviews with per-agent time estimates, but the current workflow uses parallel TeamCreate. The decision thresholds contradict RULES.md Step 3c.

## Expected Behavior
Review Wave section should describe parallel TeamCreate model. Decision block should reference RULES.md Step 3c or be marked deprecated.

## Acceptance Criteria
1. Review Wave section describes parallel TeamCreate model (not sequential)
2. Review Follow-Up Decision block references RULES.md Step 3c or is marked deprecated
3. No specific issue-count thresholds that contradict the root-cause-based triage in RULES.md
