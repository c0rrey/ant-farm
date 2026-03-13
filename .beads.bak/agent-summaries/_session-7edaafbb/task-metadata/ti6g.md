# Task: ant-farm-ti6g
**Status**: success
**Title**: fill-review-slots.sh accepts review round 0 as valid input
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- scripts/fill-review-slots.sh:78-83 — round validation regex

## Root Cause
Validates review round with regex '^[0-9]+$' which accepts 0. Review system uses 1-based rounds. Round 0 would silently fall into the round 2+ branch.

## Expected Behavior
Round 0 should be rejected with an error message.

## Acceptance Criteria
1. Round 0 is rejected with an error message
2. Round 1 and higher continue to work
