# Task: ant-farm-bzhs
**Status**: success
**Title**: _convert_beads_record inverts blocks dependency direction
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: python-pro
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- crumb.py:1483-1484 — `blocked_by.append(depends_on)` adds B to A's blocked_by instead of recording that B is blocked by A

## Root Cause
In `_convert_beads_record`, when converting a Beads dependency record with `type: "blocks"`, the code incorrectly adds the target to the source record's `blocked_by` list. A dependency `{issue_id: A, depends_on_id: B, type: "blocks"}` means "A blocks B" (B cannot proceed until A is done). The code does `blocked_by.append(depends_on)` which says "A is blocked by B" -- the semantic inverse.

## Expected Behavior
When processing record A with a `blocks` dep pointing to B, B should have A in its `blocked_by` list, not A having B. Requires a reverse index post-processing pass.

## Acceptance Criteria
1. `crumb import --from-beads` correctly maps `blocks` dependencies: if A blocks B, B's `blocked_by` contains A (not the reverse)
2. Existing `parent-child` dependency mapping remains correct (regression check)
3. Verified against `.beads/issues.jsonl` entries with real `blocks`-type deps
