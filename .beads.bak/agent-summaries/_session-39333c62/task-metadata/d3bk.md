# Task: ant-farm-d3bk
**Status**: success
**Title**: fix: fill-review-slots.sh @file argument notation undocumented in RULES.md
**Type**: bug
**Priority**: P3
**Epic**: ant-farm-908t
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md — Step 3b-ii (lines 168-170): add @file notation note

## Root Cause
fill-review-slots.sh implements @file prefix notation for multiline arguments, but RULES.md Step 3b-ii does not mention this feature.

## Expected Behavior
RULES.md mentions @file prefix for multiline arguments.

## Acceptance Criteria
1. RULES.md mentions @file prefix for multiline arguments (optional parenthetical)
