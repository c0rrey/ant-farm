# Task: ant-farm-lajv
**Status**: success
**Title**: Research tmux + iTerm2 control mode integration for spawning Claude Code sessions
**Type**: task
**Priority**: P2
**Epic**: ant-farm-753
**Agent Type**: data-researcher
**Dependencies**: {blocks: [ant-farm-hz4t], blockedBy: []}

## Affected Files
- docs/plans/2026-02-19-meta-orchestration-plan.md — Update tmux examples with correct iTerm2 control mode commands

## Root Cause
Meta-orchestration design and dummy reviewer instrumentation require spawning Claude Code sessions in tmux windows visible within iTerm2. The exact commands for creating windows and sending keystrokes within iTerm2's control mode may differ from standard tmux usage.

## Expected Behavior
Document exact commands for tmux control mode session management within iTerm2.

## Acceptance Criteria
1. Document the exact commands needed to: start a tmux control mode session, create a new window, send a prompt to that window, and check window status
2. Verify whether tmux send-keys works as expected in control mode or if an alternative is needed
3. Update the dummy reviewer bead's description with correct iTerm2-compatible commands
4. Update the meta-orchestration plan tmux examples with correct iTerm2 control mode commands
