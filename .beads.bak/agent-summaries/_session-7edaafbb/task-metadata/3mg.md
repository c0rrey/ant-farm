# Task: ant-farm-3mg
**Status**: success
**Title**: install-hooks.sh does not ensure sync-to-claude.sh is executable after clone
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- scripts/install-hooks.sh — missing chmod for sync-to-claude.sh

## Root Cause
After fresh clone, sync-to-claude.sh may not have execute permissions. install-hooks.sh does not ensure this.

## Expected Behavior
install-hooks.sh should chmod +x sync-to-claude.sh (and other script dependencies).

## Acceptance Criteria
1. install-hooks.sh ensures sync-to-claude.sh is executable
2. Other referenced scripts also checked for execute permission
