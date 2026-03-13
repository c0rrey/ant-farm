# Task: ant-farm-h7af
**Status**: success
**Title**: Implement crumb link command
**Type**: task
**Priority**: P1
**Epic**: ant-farm-e7em
**Agent Type**: python-pro
**Dependencies**: {blocks: [ant-farm-fdz2, ant-farm-izng, ant-farm-vxpr], blockedBy: [ant-farm-l7pk]}
**Blocked by**: ant-farm-l7pk (Wave 2)

## Affected Files
- crumb.py -- add link subcommand for parent, blocked-by, discovered-from link management

## Root Cause
N/A (new feature)

## Expected Behavior
Link management: crumb link for setting/changing parent trail links, appending/removing blocked_by entries, and setting discovered_from provenance. All operations use flock + atomic write. Dangling references allowed (caught by doctor).

## Acceptance Criteria
1. crumb link <id> --parent <trail-id> sets links.parent field in the crumb's JSONL entry
2. crumb link <id> --blocked-by <other-id> appends to links.blocked_by array (no duplicates)
3. crumb link <id> --remove-blocked-by <other-id> removes the specified ID from links.blocked_by
4. crumb link <id> --discovered-from <other-id> sets links.discovered_from field
5. Running crumb show <id> after link operations reflects the updated link fields
6. All link operations acquire flock and use atomic write
