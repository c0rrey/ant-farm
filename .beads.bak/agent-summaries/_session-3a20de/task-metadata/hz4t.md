# Task: ant-farm-hz4t
**Status**: success
**Title**: Add instrumented dummy reviewer via tmux for context usage measurement
**Type**: task
**Priority**: P2
**Epic**: ant-farm-753
**Agent Type**: ai-engineer
**Blocked by**: ant-farm-lajv
**Dependencies**: {blocks: [], blockedBy: [ant-farm-lajv]}

## Affected Files
- orchestration/RULES.md — Add step to spawn dummy reviewer tmux pane during review phase
- orchestration/templates/pantry.md — Compose a data file for the dummy reviewer

## Root Cause
No empirical data on how much context window reviewers consume during a review cycle. Without measurement data, any planning-time file budget would be a guess.

## Expected Behavior
Dummy reviewer spawns as a tmux window during review phase, receives identical input to correctness reviewer, and user can observe context usage.

## Acceptance Criteria
1. Dummy reviewer spawns as a tmux window during the review phase
2. Dummy reviewer receives identical input to the correctness reviewer
3. Big Head does not read or consolidate the dummy reviewer's report
4. User can observe context usage in the dummy reviewer's tmux pane
5. After data collection period, the dummy reviewer can be removed without affecting the rest of the review workflow

**Wave note**: Blocked by ant-farm-lajv (expected Wave 1). This task goes in Wave 2.
