# Task: ant-farm-3fm
**Status**: success
**Title**: checkpoints.md CCB lists report paths twice (duplication risk)
**Type**: bug
**Priority**: P3
**Epic**: ant-farm-753
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/checkpoints.md:383-387 — Individual reports section
- orchestration/templates/checkpoints.md:392-396 — Check 0 section (duplicate listing)

## Root Cause
The CCB template in checkpoints.md lists the 4 individual report paths in both the 'Individual reports' section (lines 383-387) and the 'Check 0: Report Existence Verification' section (lines 392-396). Path format changes must be updated in two places.

## Expected Behavior
Report paths appear only once in the CCB template, with Check 0 referencing the earlier listing.

## Acceptance Criteria
1. Report paths appear only once in the CCB template, with Check 0 referencing the earlier listing
