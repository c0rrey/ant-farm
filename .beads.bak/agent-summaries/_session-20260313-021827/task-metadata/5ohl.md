# Task: ant-farm-5ohl
**Status**: success
**Title**: build-review-prompts.sh resolve_arg exit code swallowed by subshell
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- `scripts/build-review-prompts.sh:74-86` — resolve_arg function

## Root Cause
resolve_arg calls `exit 1` when `@file` path is not found, but exit inside a function only exits the subshell created by `$()` command substitution. The parent script sees an empty string and produces a misleading error.

## Expected Behavior
resolve_arg failure should cause the parent script to exit with a clear error message.

## Acceptance Criteria
1. resolve_arg failure causes the parent script to exit with a clear error message
2. The error message includes the original input value for debugging
3. Same pattern applied to all resolve_arg call sites (CHANGED_FILES_RAW, COMMIT_RANGE_RAW, TASK_IDS_RAW)
