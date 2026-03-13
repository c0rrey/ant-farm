# Task: ant-farm-aozr
**Status**: success
**Title**: README Hard Gates table stale for WWD
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- README.md:L267-273 -- Hard Gates table; WWD row says "Next agent in wave" (stale pre-fix text)

## Root Cause
RULES.md Hard Gates table was updated with serial/batch blocking semantics for WWD but README.md:L267-273 still reads "Next agent in wave" (pre-fix text).

## Expected Behavior
README.md Hard Gates WWD row matches RULES.md (describes serial/batch blocking semantics).

## Acceptance Criteria
1. README.md Hard Gates WWD row updated to match RULES.md serial/batch semantics
2. Text accurately reflects current WWD behavior
