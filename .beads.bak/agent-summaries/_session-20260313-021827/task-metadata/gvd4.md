# Task: ant-farm-gvd4
**Status**: success
**Title**: Migrate dirt-pusher, nitpicker, scribe skeletons (mechanical)
**Type**: task
**Priority**: P2
**Epic**: ant-farm-irgq
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-e7em (closed)]}

## Affected Files
- orchestration/templates/dirt-pusher-skeleton.md — bd command references
- orchestration/templates/nitpicker-skeleton.md — 3 bd references
- orchestration/templates/scribe-skeleton.md — bd show, 'beads' terminology

## Root Cause
Skeleton templates contain bd command references needing mechanical substitution.

## Expected Behavior
All bd command references replaced with crumb equivalents; beads/bead terminology updated to crumbs/crumb.

## Acceptance Criteria
1. dirt-pusher-skeleton.md: all bd -> crumb command references updated
2. nitpicker-skeleton.md: 3 bd references replaced with crumb equivalents
3. scribe-skeleton.md: bd show -> crumb show, 'beads' -> 'crumbs' terminology throughout
4. grep -c '\bbd\b' on all three files returns 0
5. No semantic changes to skeleton prompt logic
