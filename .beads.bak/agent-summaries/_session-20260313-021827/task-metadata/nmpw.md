# Task: ant-farm-nmpw
**Status**: success
**Title**: Scout continues with errored tasks in wave plan producing invalid conflict analysis
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- `orchestration/templates/scout.md:83-110` — error handling section

## Root Cause
Tasks with error status have no Affected Files, Root Cause, or Agent Type data, but the Scout includes them in conflict analysis and wave planning. This can produce misleading conflict assessments and strategy proposals.

## Expected Behavior
Error-status tasks should be excluded from wave 1 or explicitly flagged as unreliable in the strategy.

## Acceptance Criteria
1. Error-status tasks are either excluded from wave 1 or explicitly flagged as unreliable in the strategy
2. Conflict analysis notes which tasks had error status and warns about incomplete data
