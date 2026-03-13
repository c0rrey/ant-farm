# Task: ant-farm-r8m
**Status**: success
**Title**: checkpoints.md {checkpoint} placeholder not defined in term definitions block
**Type**: bug
**Priority**: P3
**Epic**: ant-farm-753
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/checkpoints.md:20 — {checkpoint} used in filename pattern without definition
- orchestration/templates/checkpoints.md:4-7 — Term definitions block

## Root Cause
The filename pattern on line 20 of checkpoints.md uses {checkpoint} as a placeholder, but this is not defined in the term definitions block (lines 4-7). While its meaning is inferable from context, it breaks the convention of all placeholders being explicitly defined.

## Expected Behavior
{checkpoint} is defined in the term definitions block or has an explanatory note.

## Acceptance Criteria
1. {checkpoint} is defined in the term definitions block or has an explanatory note
