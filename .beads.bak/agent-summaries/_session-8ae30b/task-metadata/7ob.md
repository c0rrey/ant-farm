# Task: ant-farm-7ob
**Status**: success
**Title**: RULES.md pantry.md section references not explicit
**Type**: task
**Priority**: P3
**Epic**: ant-farm-7hh
**Agent Type**: technical-writer
**Dependencies**: blocks: [], blockedBy: []

## Affected Files
- ~/.claude/orchestration/RULES.md — Steps 2 and 3b reference "templates/pantry.md" without section numbers

## Root Cause
pantry-impl.md references "pantry.md, Section 1" and pantry-review.md references "pantry.md, Section 2", but RULES.md Steps 2 and 3b just say "→ templates/pantry.md" without section numbers. This reduces traceability when debugging which section applies to which workflow step.

## Expected Behavior
RULES.md Steps 2 and 3b include section numbers when referencing pantry.md, matching the explicitness of pantry-impl.md and pantry-review.md.

## Acceptance Criteria
1. RULES.md Steps 2 and 3b reference pantry.md with explicit section numbers
2. References are consistent with section numbering in pantry.md itself
