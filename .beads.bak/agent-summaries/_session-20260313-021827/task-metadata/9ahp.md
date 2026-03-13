# Task: ant-farm-9ahp
**Status**: success
**Title**: setup.sh does not copy CLAUDE.md to ~/.claude/CLAUDE.md
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- `scripts/setup.sh` — missing CLAUDE.md sync step

## Root Cause
setup.sh is introduced as the unified setup script replacing sync-to-claude.sh, but it does NOT copy CLAUDE.md to ~/.claude/CLAUDE.md. Users running setup.sh will not get updated global config.

## Expected Behavior
Running setup.sh should copy CLAUDE.md to ~/.claude/CLAUDE.md using the existing backup_and_copy pattern.

## Acceptance Criteria
1. Running `scripts/setup.sh` copies CLAUDE.md to `~/.claude/CLAUDE.md`
2. If CLAUDE.md content differs, a timestamped .bak backup is created before overwriting
3. setup.sh output confirms CLAUDE.md was synced (or skipped if unchanged)
