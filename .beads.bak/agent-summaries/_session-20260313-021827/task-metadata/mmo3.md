# Task: ant-farm-mmo3
**Status**: success
**Title**: Migrate agent definitions (mechanical)
**Type**: task
**Priority**: P2
**Epic**: ant-farm-irgq
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-e7em (closed)]}

## Affected Files
- ~/.claude/agents/scout-organizer.md — bd command references in tool descriptions
- ~/.claude/agents/nitpicker.md — 3 bd references

## Root Cause
Agent definition files contain bd command references needing mechanical substitution.

## Expected Behavior
All bd command references replaced with crumb equivalents; agent descriptions remain functionally correct.

## Acceptance Criteria
1. agents/scout-organizer.md: all bd command references replaced with crumb equivalents
2. agents/nitpicker.md: all 3 bd references replaced with crumb equivalents
3. grep -c '\bbd\b' on both files returns 0
4. Agent descriptions and tool references remain functionally correct after substitution
