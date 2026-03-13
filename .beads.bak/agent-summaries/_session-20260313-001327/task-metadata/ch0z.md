# Task: ant-farm-ch0z
**Status**: success
**Title**: TOCTOU race in cmd_doctor --fix: reads tasks.jsonl without holding FileLock
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: python-pro
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- crumb.py:1714 — `read_tasks()` called outside lock scope in `cmd_doctor`
- crumb.py:1816 — `FileLock` acquired only for the write phase

## Root Cause
`cmd_doctor` reads `tasks.jsonl` at L1714 without holding `FileLock`. The lock is only acquired later at L1816 when writing fixes. Between the read and the lock acquisition, another process can modify `tasks.jsonl`. When the doctor then writes its snapshot under lock, it silently discards the interleaved writes.

## Expected Behavior
`cmd_doctor --fix` should hold the lock for the entire read-validate-write cycle to prevent TOCTOU races.

## Acceptance Criteria
1. `cmd_doctor --fix` holds the lock for the entire read-validate-write cycle
2. Concurrent `crumb create` during `crumb doctor --fix` does not lose the created crumb
3. Doctor's malformed-line detection still works correctly under the expanded lock scope
