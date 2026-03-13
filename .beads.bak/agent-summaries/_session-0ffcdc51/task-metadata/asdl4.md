# Task: ant-farm-asdl.4
**Status**: success
**Title**: Update deprecated pantry.md Section 2 bead filing references
**Type**: task
**Priority**: P3
**Epic**: ant-farm-asdl
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [ant-farm-asdl.5], blockedBy: [ant-farm-asdl.1]}
**Blocked by**: ant-farm-asdl.1 (Wave 1)

## Affected Files
- `orchestration/templates/pantry.md:318-319` — Replace bare bd create command with --body-file pattern and dedup instruction

## Root Cause
The Pantry template has bead filing instructions in deprecated Section 2 that use bare `bd create` without --body-file. While Section 2 is deprecated, the instructions should be updated for consistency.

## Expected Behavior
Lines 318-319 should reference the canonical --body-file pattern from big-head-skeleton.md, mention the 5 required description fields, and include the dedup instruction.

## Acceptance Criteria
1. Lines 318-319 of pantry.md no longer contain a bare bd create --title command
2. The replacement text references big-head-skeleton.md as the canonical source for the --body-file pattern
3. The replacement text mentions the 5 required description fields (root cause, affected surfaces, fix, changes needed, acceptance criteria)
4. The replacement text includes the dedup instruction (bd list --status=open)
