# Task: ant-farm-m4si
**Status**: success
**Title**: Progress log key tasks_approved misleading after auto-approve change
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md:116 — progress log key `tasks_approved=<N>` that implies human approval
- scripts/parse-progress-log.sh — may reference `tasks_approved` key name (grep confirmed file is listed but no direct match found in parse script)

## Root Cause
The progress log line at orchestration/RULES.md:116 was not fully updated when the user-approval gate was removed in ant-farm-fomy. The key name `tasks_approved=<N>` implies a human approved the task list, which is no longer accurate -- approval is now automatic after SSV PASS. The derivation of `<N>` is also unspecified.

## Expected Behavior
Key should be renamed from `tasks_approved` to `tasks_accepted` or `tasks_scheduled` to reflect automatic acceptance. The derivation of `<N>` (count of tasks in briefing task list after SSV PASS) should be documented inline.

## Acceptance Criteria
1. Progress log key at RULES.md:116 no longer uses the word "approved"
2. The derivation of `<N>` (task count from briefing) is documented inline or in an adjacent comment
3. `parse-progress-log.sh` (if it parses `tasks_approved`) is updated to match the new key name
