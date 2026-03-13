# Task: ant-farm-qoig
**Status**: success
**Title**: RULES.md tmux dependency without availability check
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md:188-210 — tmux-dependent section

## Root Cause
Step 3b-v dummy reviewer spawn assumes tmux is available and Queen is running inside tmux. No availability check or fallback.

## Expected Behavior
Add command -v tmux and TMUX check before the tmux block.

## Acceptance Criteria
1. tmux availability checked before use
2. Graceful fallback when tmux is unavailable
