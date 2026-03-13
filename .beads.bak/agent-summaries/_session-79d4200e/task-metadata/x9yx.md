# Task: ant-farm-x9yx
**Status**: success
**Title**: fix: SSV checkpoint missing from RULES.md Model Assignments table
**Type**: bug
**Priority**: P2
**Epic**: ant-farm-908t
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md:297 — insert SSV row in Model Assignments table

## Root Cause
When SSV was added as a checkpoint, it was documented inline in Step 1b but the Model Assignments table was not updated.

## Expected Behavior
Model Assignments table should include PC -- SSV row with model haiku.

## Acceptance Criteria
1. Model Assignments table includes PC -- SSV row with model haiku
2. All 5 PC checkpoint types (SSV, CCO, WWD, DMVDC, CCB) have table entries
3. Table row note matches checkpoints.md:612 rationale
