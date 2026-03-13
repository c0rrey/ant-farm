# Task: ant-farm-vxpr
**Status**: success
**Title**: Implement crumb ready and blocked commands
**Type**: task
**Priority**: P1
**Epic**: ant-farm-e7em
**Agent Type**: python-pro
**Dependencies**: {blocks: [], blockedBy: [ant-farm-h7af]}
**Blocked by**: ant-farm-h7af (Wave 3)

## Affected Files
- crumb.py -- add ready and blocked subcommands with dependency resolution logic

## Root Cause
N/A (new feature)

## Expected Behavior
Dependency-aware queries: crumb ready lists open crumbs with no unresolved blockers, crumb blocked lists open crumbs with unresolved blockers. The two commands produce disjoint sets covering all open crumbs.

## Acceptance Criteria
1. crumb ready returns only open crumbs whose blocked_by entries are all closed or non-existent
2. crumb ready --limit 5 --sort priority returns at most 5 results sorted by priority (P0 first)
3. crumb blocked returns only open crumbs with at least one blocker that is open/in_progress and exists
4. Crumbs with blocked_by references to non-existent IDs appear in ready (treated as resolved)
5. For any set of open crumbs, ready union blocked = all open crumbs and ready intersect blocked = empty
6. Both commands exclude closed and in_progress crumbs from their output
