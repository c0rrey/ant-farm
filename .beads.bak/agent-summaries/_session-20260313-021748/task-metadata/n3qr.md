# Task: ant-farm-n3qr
**Status**: success
**Title**: Write /ant-farm:status skill definition
**Type**: task
**Priority**: P2
**Epic**: ant-farm-r8ru
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-e7em (closed)]}

## Affected Files
- skills/status.md — new file

## Root Cause
N/A — new feature. /ant-farm:status slash command needed for quick view dashboard.

## Expected Behavior
skills/status.md exists with skill frontmatter, displays trail completion counts, crumb status summary, last session summary.

## Acceptance Criteria
1. skills/status.md exists with correct skill frontmatter and trigger pattern
2. Displays trail completion counts using crumb trail list output
3. Displays crumb status summary: open count, blocked count, in_progress count, closed count
4. Shows last session summary from most recent .crumbs/history/exec-summary-*.md
5. Handles edge case: no tasks exist, no sessions completed yet
6. Output is concise and scannable (dashboard format, not raw command output)
