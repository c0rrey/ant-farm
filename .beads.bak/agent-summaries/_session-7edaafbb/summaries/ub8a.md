# ant-farm-ub8a — Bug Fix Summary

**Issue**: Stale `_archive/` files persist after rsync `--delete` removal
**Status**: CLOSED
**Commit**: efec458

## Problem

Removing `--delete` from the rsync command in `scripts/sync-to-claude.sh` (commit e445a40) left no mechanism to prevent previously-synced `_archive/` files from remaining at `~/.claude/orchestration/_archive/`. Agents using glob patterns could inadvertently read deprecated instruction files from that directory.

## Fix

Added `--exclude='_archive/'` to the rsync flags on line 27 of `scripts/sync-to-claude.sh`.

**Before:**
```bash
rsync -av --exclude='scripts/' "$REPO_ROOT/orchestration/" ~/.claude/orchestration/
```

**After:**
```bash
rsync -av --exclude='scripts/' --exclude='_archive/' "$REPO_ROOT/orchestration/" ~/.claude/orchestration/
```

## Files Changed

- `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh` — added `--exclude='_archive/'` to rsync command

## Outcome

The `_archive/` directory is now excluded from every sync run, preventing deprecated instruction files from ever reaching `~/.claude/orchestration/`. Existing stale files at the target path must be manually removed once (they will not be re-created by subsequent syncs).
