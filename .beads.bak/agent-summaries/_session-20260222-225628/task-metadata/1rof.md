# Task: ant-farm-1rof
**Status**: success
**Title**: Crash recovery missing session directory existence check
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md:64-75 — crash recovery detection block

## Root Cause
The crash recovery block in `RULES.md:L64-L75` calls `parse-progress-log.sh` without first verifying the session directory exists on disk. If the directory was pruned, the script exits with an opaque "cannot read log" error instead of a diagnostic message.

## Expected Behavior
A missing session directory produces a clear "Session directory not found" error before the script runs. The existing exit-code handling for parse-progress-log.sh remains unchanged.

## Acceptance Criteria
1. A missing session directory produces a clear "Session directory not found" error before the script runs
2. The existing exit-code handling for parse-progress-log.sh remains unchanged
3. The Queen's error message to the user includes the specific path that was not found
