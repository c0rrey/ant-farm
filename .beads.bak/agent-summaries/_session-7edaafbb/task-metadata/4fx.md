# Task: ant-farm-4fx
**Status**: success
**Title**: install-hooks.sh backup uses fixed filename, losing backup history on re-run
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- scripts/install-hooks.sh — backup file naming

## Root Cause
Backup uses a fixed filename. Re-running install-hooks.sh overwrites the previous backup, losing backup history.

## Expected Behavior
Backup filenames should include a timestamp or sequence number to preserve history.

## Acceptance Criteria
1. Each backup has a unique filename
2. Previous backups are not overwritten
