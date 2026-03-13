# Task: ant-farm-3imu
**Status**: success
**Title**: Write /ant-farm:init skill definition
**Type**: task
**Priority**: P2
**Epic**: ant-farm-r8ru
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-e7em (closed)]}

## Affected Files
- skills/init.md — new file

## Root Cause
N/A — new feature. /ant-farm:init slash command needed to scaffold .crumbs/ in target projects.

## Expected Behavior
skills/init.md exists with skill frontmatter, scaffolds .crumbs/ directory structure, installs crumb.py, detects project language/stack.

## Acceptance Criteria
1. skills/init.md exists with correct skill frontmatter (name, description, trigger pattern)
2. Skill creates .crumbs/tasks.jsonl, .crumbs/config.json, .crumbs/sessions/, .crumbs/history/
3. config.json populated with prefix (prompted or auto-derived), default_priority P2, counters at 1
4. .crumbs/sessions/ added to .gitignore (not the whole .crumbs/)
5. crumb.py installation step included with PATH verification
6. Idempotent: re-running on existing .crumbs/ doesn't overwrite data
