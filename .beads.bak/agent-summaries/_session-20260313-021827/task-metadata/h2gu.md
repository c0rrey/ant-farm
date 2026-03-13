# Task: ant-farm-h2gu
**Status**: success
**Title**: Migrate checkpoints.md (semantic)
**Type**: task
**Priority**: P2
**Epic**: ant-farm-f4h5
**Agent Type**: technical-writer
**Dependencies**: {blocks: [ant-farm-veht], blockedBy: [ant-farm-e7em (closed)]}

## Affected Files
- orchestration/templates/checkpoints.md — 6 checkpoint definitions (SSV, CCO, WWD, DMVDC, CCB, ESV)

## Root Cause
Checkpoints template contains bd command references across 6 checkpoint definitions. ESV checkpoint has a semantic flag change (--after syntax differs).

## Expected Behavior
All 6 checkpoint definitions updated with crumb commands; ESV --after flag updated to crumb syntax.

## Acceptance Criteria
1. All 6 checkpoint definitions (SSV, CCO, WWD, DMVDC, CCB, ESV) have bd -> crumb command updates
2. ESV --after flag updated: bd list --status=open --after={date} -> crumb list --open --after {date}
3. Checkpoint verification logic (pass/fail criteria) remains unchanged
4. grep -c '\bbd\b' orchestration/templates/checkpoints.md returns 0
5. All command examples in checkpoints reflect valid crumb CLI syntax
