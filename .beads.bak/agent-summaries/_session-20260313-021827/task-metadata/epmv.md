# Task: ant-farm-epmv
**Status**: success
**Title**: Migrate pantry.md (semantic)
**Type**: task
**Priority**: P2
**Epic**: ant-farm-f4h5
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-e7em (closed)]}

## Affected Files
- orchestration/templates/pantry.md — 6 bd references across distinct commands

## Root Cause
Pantry template contains 6 bd references across distinct command patterns (show, create, list, label, dep add) requiring semantic translation.

## Expected Behavior
All 6 bd references converted to crumb equivalents with correct flag syntax; workflow logic preserved.

## Acceptance Criteria
1. All 6 bd references in pantry.md converted to crumb equivalents
2. bd dep add patterns converted to crumb link with correct flag (--parent or --blocked-by)
3. bd label references removed
4. grep -c '\bbd\b' orchestration/templates/pantry.md returns 0
5. Pantry prompt composition workflow logic preserved
