# Task: ant-farm-prjj
**Status**: success
**Title**: Contradictory follow-exactly-except structure in work.md Step 3
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- skills/work.md:115-128 — contradictory "follow exactly / except" structure

## Root Cause
skills/work.md says "Read orchestration/RULES.md and follow its workflow from Step 1 onward" then immediately lists exceptions. The "follow exactly" instruction contradicts the override list.

## Expected Behavior
The instruction should lead with the exception list, making override scope explicit before the reader reaches the "follow RULES.md" instruction.

## Acceptance Criteria
1. The "follow RULES.md" instruction explicitly states exceptions exist before the reader reaches the instruction
2. Override commands are listed in a structured format
