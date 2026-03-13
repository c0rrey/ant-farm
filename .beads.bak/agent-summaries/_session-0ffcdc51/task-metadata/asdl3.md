# Task: ant-farm-asdl.3
**Status**: success
**Title**: Update agents/big-head.md with dedup instruction and --body-file reference
**Type**: task
**Priority**: P2
**Epic**: ant-farm-asdl
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [ant-farm-asdl.5], blockedBy: [ant-farm-asdl.1]}
**Blocked by**: ant-farm-asdl.1 (Wave 1)

## Affected Files
- `agents/big-head.md:22-23` — Replace step 6 with two new steps (dedup + body-file filing), renumber step 7 to step 8

## Root Cause
The Big Head agent definition at line 22 has prose saying to include descriptions but provides no concrete command example. Agents follow concrete examples over prose, so the instruction is ignored.

## Expected Behavior
Step 6 should be a concrete dedup instruction referencing 'bd list --status=open'. Step 7 should reference 'bd create --body-file'. Old step 7 (write consolidated report) should become step 8.

## Acceptance Criteria
1. agents/big-head.md contains a dedup instruction referencing 'bd list --status=open' before the filing step
2. agents/big-head.md references '--body-file' (not bare 'bd create') in the filing instruction
3. Steps in the 'When consolidating:' list are sequentially numbered 1-8 with no gaps
4. Old step 7 ('Write the consolidated report') is renumbered to step 8 with content unchanged
