# Task: ant-farm-cn0
**Status**: success
**Title**: Timestamp format YYYYMMDD-HHMMSS repeated 5+ times across files
**Type**: task
**Priority**: P3
**Epic**: ant-farm-amk
**Agent Type**: technical-writer
**Dependencies**: blocks: [], blockedBy: [ant-farm-s57]

## Affected Files
- orchestration/templates/checkpoints.md — Lines 31, 97, 152, 277, 443 (timestamp format repeated)
- orchestration/templates/pantry.md — Line 101 (timestamp format repeated)

## Root Cause
The timestamp format is redefined in checkpoints.md at lines 31, 97, 152, 277, 443 and in pantry.md line 101. If the format ever changes, all 5+ locations must be updated. DRY violation.

## Expected Behavior
Format defined once at the top of checkpoints.md (after ant-farm-s57 canonicalizes which format to use). All other occurrences replaced with a reference to the canonical definition.

## Acceptance Criteria
1. Timestamp format string defined exactly once in a canonical location
2. All other occurrences in checkpoints.md and pantry.md replaced with references to the canonical definition
3. grep for the literal format string across orchestration/ returns only the single canonical definition
