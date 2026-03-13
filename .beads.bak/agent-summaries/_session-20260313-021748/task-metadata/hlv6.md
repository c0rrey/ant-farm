# Task: ant-farm-hlv6
**Status**: success
**Title**: Create decomposition orchestration template
**Type**: task
**Priority**: P2
**Epic**: ant-farm-6w50
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-xtu9]}
**Blocked by**: ant-farm-xtu9 (Wave 2)

## Affected Files
- orchestration/templates/decomposition.md — SHARED with ant-farm-xtu9 (same file!)

## Root Cause
N/A — new feature. Decomposition orchestration template needed for Architect workflow.

## Expected Behavior
orchestration/templates/decomposition.md contains the Architect's complete workflow orchestration template with crumb CLI examples and decomposition brief output template.

## Acceptance Criteria
1. orchestration/templates/decomposition.md exists with clear step-by-step workflow
2. Input reading order defined: spec.md first, then research briefs, then codebase structure
3. crumb trail create and crumb create --from-json command examples with full JSON payloads
4. blocked_by wiring guidance: when to add dependencies, how to detect data/API dependencies
5. scope.files and scope.agent_type assignment guidance with examples
6. decomposition-brief.md output template included

NOTE: This task's primary file (decomposition.md) is also created by ant-farm-xtu9. These two tasks should be batched to the same agent or serialized with xtu9 first.
