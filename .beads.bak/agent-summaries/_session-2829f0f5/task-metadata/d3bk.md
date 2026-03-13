# Task: ant-farm-d3bk
**Status**: success
**Title**: fix: fill-review-slots.sh @file argument notation undocumented in RULES.md
**Type**: bug
**Priority**: P3
**Epic**: ant-farm-908t
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md:168-170 — Step 3b-ii script invocation documentation

## Root Cause
fill-review-slots.sh (lines 78-94) implements an @file prefix notation for multiline arguments but RULES.md Step 3b-ii does not mention this feature. The core argument count and order match, but the convenience feature is undiscoverable from RULES.md alone.

## Expected Behavior
RULES.md mentions @file prefix for multiline arguments.

## Acceptance Criteria
1. RULES.md mentions @file prefix for multiline arguments (optional note/parenthetical)
