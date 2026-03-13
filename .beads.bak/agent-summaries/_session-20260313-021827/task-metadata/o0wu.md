# Task: ant-farm-o0wu
**Status**: success
**Title**: Migrate RULES-review.md (semantic)
**Type**: task
**Priority**: P2
**Epic**: ant-farm-f4h5
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-e7em (closed)]}

## Affected Files
- orchestration/RULES-review.md — review workflow rules with bd command references

## Root Cause
RULES-review.md contains review workflow rules referencing bd commands for issue queries and status updates.

## Expected Behavior
All bd command references replaced with crumb equivalents; review workflow logic preserved.

## Acceptance Criteria
1. All bd command references replaced with crumb equivalents
2. Review workflow logic preserved -- only command syntax changes
3. grep -c '\bbd\b' orchestration/RULES-review.md returns 0
4. Any .beads/ path references updated to .crumbs/
