# Task: ant-farm-mx0
**Status**: success
**Title**: (BUG) prompts/ directory creation is redundant between RULES.md Step 0 and pantry.md Review Mode
**Type**: bug
**Priority**: P3
**Epic**: ant-farm-7hh
**Agent Type**: technical-writer
**Dependencies**: blocks: [], blockedBy: []

## Affected Files
- ~/.claude/orchestration/RULES.md — line 115 (mkdir -p includes prompts/ via brace expansion)
- ~/.claude/orchestration/templates/pantry.md — lines 107-110 (Review Mode Step 3 also creates prompts/)

## Root Cause
RULES.md Step 0 creates the prompts/ directory via brace expansion in mkdir. pantry.md Review Mode Step 3 also says "Create the prompts directory if needed." The redundancy is harmless (mkdir -p is idempotent) but creates confusion about who owns directory creation.

## Expected Behavior
The intentional redundancy is documented with a comment in pantry.md noting that the Queen pre-creates this directory at Step 0, but create if needed as a safety net.

## Acceptance Criteria
1. pantry.md contains a comment clarifying the intentional redundancy: "The Queen pre-creates this directory at Step 0, but create if needed as a safety net"
