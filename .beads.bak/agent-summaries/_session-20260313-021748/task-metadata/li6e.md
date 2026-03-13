# Task: ant-farm-li6e
**Status**: success
**Title**: Shell script robustness gaps in setup.sh — glob, find, exit/return
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- scripts/setup.sh:100 — glob expansion without nullglob
- scripts/setup.sh:149 — find exit code not handled in process substitution
- scripts/setup.sh:67 — exit 1 in backup_and_copy function called from process substitution context

## Root Cause
scripts/setup.sh relies on implicit shell behavior rather than explicit error handling in three install loops.

## Expected Behavior
Explicit nullglob, find exit code handling, and correct return/exit propagation in process substitution contexts.

## Acceptance Criteria
1. Empty agents/ directory does not produce shell misbehavior
2. find failure in orchestration walk produces a user-visible error message
3. backup_and_copy failure propagates correctly regardless of calling context
