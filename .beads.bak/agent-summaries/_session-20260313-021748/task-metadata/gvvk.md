# Task: ant-farm-gvvk
**Status**: success
**Title**: Incomplete bd-to-crumb CLI migration in Architect executable templates
**Type**: bug
**Priority**: P1
**Epic**: none
**Agent Type**: python-pro
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- crumb.py:520 — cmd_list --parent checks only t.get("parent"), misses links.parent
- crumb.py:523 — cmd_list --discovered checks only t.get("discovered_from"), misses links.discovered_from
- crumb.py:425-430 — _auto_close_trail_if_complete reads only links.get("parent"), misses top-level parent

## Root Cause
The codebase stores parent/discovered_from linkage in two locations: top-level fields and the links sub-dict. Three code paths check only one location, producing silently wrong results.

## Expected Behavior
All code paths should check both record.get(field) and record.get("links", {}).get(field) using a dual-lookup pattern.

## Acceptance Criteria
1. crumb list --parent AF-T1 returns crumbs linked via crumb link --parent
2. crumb list --discovered returns crumbs linked via crumb link --discovered-from
3. Closing the last open child of a trail auto-closes the trail for crumbs with top-level parent field
4. Existing dual-lookup code paths (_get_trail_children, cmd_doctor, _get_blocked_by) remain unchanged
