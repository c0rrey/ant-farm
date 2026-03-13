# Task: ant-farm-m7hn
**Status**: success
**Title**: Missing research/ subdirectory creation in plan skill
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: python-pro
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- crumb.py:181 — read_tasks() calls open(path, "r") with no try/except OSError
- crumb.py:222 — iter_jsonl() has the same unguarded open() pattern
- crumb.py:258-260 — FileLock.__enter__ calls path.touch() and open(path, "w") without catching OSError

## Root Cause
Several functions call open() or path.touch() without catching OSError, causing raw Python tracebacks instead of clean die() messages on permission errors or read-only filesystems.

## Expected Behavior
Each unguarded open()/path.touch() should be wrapped in try/except OSError following the pattern in read_config() at L139.

## Acceptance Criteria
1. read_tasks() produces a clean die() error message on permission error or missing file
2. FileLock.__enter__ produces a clean die() error message on read-only filesystem
3. iter_jsonl() produces a clean die() error message on file access failure
