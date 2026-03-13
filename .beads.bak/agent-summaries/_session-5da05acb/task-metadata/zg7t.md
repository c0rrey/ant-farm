# Task: ant-farm-zg7t
**Status**: success
**Title**: macOS (Darwin) incompatible shell commands in RULES.md
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md:381 — session ID generation uses date +%s%N which is GNU-only
- orchestration/RULES.md:156-176 — TASK_IDS validation uses tr | sed pipeline instead of bash parameter expansion
- orchestration/RULES.md:157-159 — REVIEW_ROUND validation uses echo | grep instead of bash-native [[ =~ ]]

## Root Cause
Shell commands in RULES.md assume GNU tooling behavior, but the documented platform (Darwin/macOS) uses BSD tooling. date +%s%N silently produces literal %N on macOS instead of nanoseconds.

## Expected Behavior
All shell commands should use portable macOS-compatible alternatives (uuidgen for session IDs, bash parameter expansion for validation, bash-native regex matching).

## Acceptance Criteria
1. Session ID generation does not use date +%s%N or any GNU-only date format
2. TASK_IDS validation uses bash parameter expansion (matching CHANGED_FILES pattern)
3. REVIEW_ROUND validation uses bash-native regex matching
4. All three changes verified to work on macOS (Darwin)
