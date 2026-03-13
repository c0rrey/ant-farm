# Task: ant-farm-jmvi
**Status**: success
**Title**: Implement trail commands
**Type**: task
**Priority**: P1
**Epic**: ant-farm-e7em
**Agent Type**: python-pro
**Dependencies**: {blocks: [ant-farm-dhh8, ant-farm-fdz2], blockedBy: [ant-farm-l7pk]}
**Blocked by**: ant-farm-l7pk (Wave 2)

## Affected Files
- crumb.py -- add trail create/show/list/close subcommands with auto-close and auto-reopen behavior

## Root Cause
N/A (new feature)

## Expected Behavior
Trail (epic) management: crumb trail create with T-prefixed auto-ID, crumb trail show with child crumb listing, crumb trail list with completion summaries, crumb trail close with open-children rejection. Auto-close when last child closes, auto-reopen when new open crumb linked.

## Acceptance Criteria
1. crumb trail create --title 'test trail' creates trail entry with AF-T{n} ID format in tasks.jsonl
2. crumb trail show <id> displays trail fields plus list of all child crumbs with their statuses
3. crumb trail list shows all trails with 'X/Y closed' completion counts
4. crumb trail close <id> exits 1 with stderr listing open children if any exist
5. Closing the last open child of a trail auto-closes the trail (sets status=closed, closed_at)
6. Linking a new open crumb to a closed trail as parent auto-reopens the trail
