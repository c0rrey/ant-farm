# Task: ant-farm-bi3
**Status**: success
**Title**: Pantry template lacks fail-fast for missing task-metadata dir and empty file list
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/pantry.md — missing fail-fast guards in Step 2 and Section 2

## Root Cause
orchestration/templates/pantry.md has two fail-fast gaps: (1) Step 2 (implementation mode) reads task-metadata/{TASK_SUFFIX}.md but does not check if the task-metadata/ directory itself exists. (2) Section 2 (review mode) receives a changed-file list from the Queen but has no guard against an empty list.

## Expected Behavior
Missing task-metadata/ produces actionable error. Empty file list produces immediate failure.

## Acceptance Criteria
1. Missing task-metadata/ produces actionable error
2. Empty file list produces immediate failure
3. 'Read this file' replaced with explicit file name reference
4. Introduce {REVIEW_TIMESTAMP} placeholder
