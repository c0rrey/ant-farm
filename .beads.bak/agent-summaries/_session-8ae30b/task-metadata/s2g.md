# Task: ant-farm-s2g
**Status**: success
**Title**: AGG-017: Remove circular reference in Pantry Big Head data file instructions
**Type**: bug
**Priority**: P1
**Epic**: ant-farm-7hh
**Agent Type**: technical-writer
**Dependencies**: blocks: [], blockedBy: [ant-farm-0o4 (closed)]

## Affected Files
- ~/.claude/orchestration/templates/pantry.md — Section 2 instructs Pantry to read reviews.md before composing Big Head data file, creating circular dependency
- ~/.claude/orchestration/templates/reviews.md — may cross-reference pantry.md; reference must be narrowed to specific section

## Root Cause
pantry.md instructs the Pantry to read reviews.md before composing the Big Head data file, but pantry.md Section 2 already IS the review mode instructions. This creates a circular dependency where Pantry reads pantry.md which says read reviews.md which may reference pantry.md.

## Expected Behavior
pantry.md Section 2 is self-contained for Big Head data file composition with no circular references. A cold Pantry agent can compose the Big Head data file by reading only pantry.md.

## Acceptance Criteria
1. pantry.md Section 2 is self-contained for Big Head data file composition (no circular refs)
2. If reviews.md is still referenced, the reference specifies exactly which section to read and why
3. A cold Pantry agent can compose the Big Head data file by reading only pantry.md
