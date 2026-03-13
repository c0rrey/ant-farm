# Task: ant-farm-mg0r
**Status**: success
**Title**: Scaffold crumb.py with CLI framework and core infrastructure
**Type**: task
**Priority**: P1
**Epic**: ant-farm-e7em
**Agent Type**: python-pro
**Dependencies**: {blocks: [ant-farm-l7pk], blockedBy: []}

## Affected Files
- crumb.py (new file) -- single-file Python CLI with argparse, JSONL utilities, flock locking, atomic writes

## Root Cause
N/A (new feature)

## Expected Behavior
A foundational crumb.py file providing CLI framework, .crumbs/ directory discovery, config.json read/write, file locking, atomic writes, JSONL utilities, stale .tmp cleanup, and error handling.

## Acceptance Criteria
1. crumb.py exists as a single executable Python file with #!/usr/bin/env python3 shebang
2. Running python crumb.py without args prints usage help listing all subcommands and exits 0
3. .crumbs/ directory discovery walks up from cwd to filesystem root, returns first .crumbs/ found
4. config.json is read/written with fields: prefix, default_priority, next_crumb_id, next_trail_id
5. File locking acquires exclusive flock on .crumbs/tasks.lock before any read-modify-write
6. Atomic writes use tempfile then os.rename() -- incomplete writes never corrupt tasks.jsonl
7. Missing .crumbs/tasks.jsonl prints error message to stderr and exits 1
