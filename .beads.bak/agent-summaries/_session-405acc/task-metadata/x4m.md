# Task: ant-farm-x4m
**Status**: success
**Title**: AGG-031: Add data file format specification to skeleton templates
**Type**: task
**Priority**: P1
**Epic**: ant-farm-21d
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-0o4 (already closed/done)]}

## Affected Files
- `orchestration/templates/dirt-pusher-skeleton.md` (line 29, Step 0 section) — "Read your task context from {DATA_FILE_PATH}" with no format spec
- `orchestration/templates/nitpicker-skeleton.md` (line 19, Step 0 section) — "Read your full review brief from {DATA_FILE_PATH}" with no format spec

## Root Cause
Skeleton templates reference {DATA_FILE_PATH} but never specify the file format. A cold agent might expect JSON or YAML instead of markdown.

## Expected Behavior
Each skeleton should include a brief format note (e.g., "The data file is markdown with sections: Context, Scope Boundaries, Focus.") so agents know how to parse it.

## Acceptance Criteria
1. dirt-pusher-skeleton.md specifies the data file format and expected sections
2. nitpicker-skeleton.md specifies the data file format and expected sections
3. Both skeletons explicitly state the file is markdown (not JSON/YAML)
