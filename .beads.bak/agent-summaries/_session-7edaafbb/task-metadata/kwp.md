# Task: ant-farm-kwp
**Status**: success
**Title**: SETUP.md test checklist says Queen runs bd show, contradicts Information Diet
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- SETUP.md — test checklist referencing bd show for Queen

## Root Cause
SETUP.md test checklist instructs the Queen to run bd show, but the Information Diet rule in CLAUDE.md prohibits the Queen from running bd show (the Scout subagent handles this).

## Expected Behavior
SETUP.md should not instruct the Queen to run bd show. Test checklist should reference Scout subagent behavior instead.

## Acceptance Criteria
1. SETUP.md test checklist no longer instructs Queen to run bd show
2. Checklist is consistent with Information Diet constraints in CLAUDE.md
