# Task: ant-farm-0gs
**Status**: success
**Title**: Step 0 wildcard glob may match stale reports from prior review cycles
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/reviews.md — Step 0 wildcard glob logic
- orchestration/RULES.md — Step 0 references

## Root Cause
Step 0 wildcard glob may match stale reports from prior review cycles. No description available in bd; details to be gathered from source code inspection.

## Expected Behavior
Step 0 glob only matches reports from the current review cycle.

## Acceptance Criteria
1. Stale reports from prior cycles are not matched by Step 0 glob
