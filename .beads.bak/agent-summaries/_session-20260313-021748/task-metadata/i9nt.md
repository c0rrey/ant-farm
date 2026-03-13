# Task: ant-farm-i9nt
**Status**: success
**Title**: DECOMPOSE_DIR path mismatch — .beads/ not migrated to .crumbs/
**Type**: bug
**Priority**: P1
**Epic**: none
**Agent Type**: python-pro
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- crumb.py:1483-1484 — blocked_by.append(depends_on) adds B to A's blocked_by instead of recording that B is blocked by A

## Root Cause
In _convert_beads_record, when converting a blocks-type dependency, the code incorrectly adds the target to the source record's blocked_by list, inverting the semantic direction.

## Expected Behavior
If A blocks B, B's blocked_by should contain A (not the reverse). A reverse index should be built during two-pass conversion.

## Acceptance Criteria
1. crumb import --from-beads correctly maps blocks dependencies: if A blocks B, B's blocked_by contains A
2. Existing parent-child dependency mapping remains correct (regression check)
3. Verified against .beads/issues.jsonl entries with real blocks-type deps
