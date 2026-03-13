# Task: ant-farm-asdl.3
**Status**: success
**Title**: Update agents/big-head.md with dedup instruction and --body-file reference
**Type**: task
**Priority**: P2
**Epic**: ant-farm-asdl
**Agent Type**: technical-writer
**Dependencies**: {blocks: [ant-farm-asdl.5], blockedBy: [ant-farm-asdl.1]}
**Blocked by**: ant-farm-asdl.1
**Expected blocker completion**: Wave 1 (ant-farm-asdl.1 is P1 and ready)

## Affected Files
- agents/big-head.md:22-23 — replace step 6 with two new steps (dedup + --body-file filing)

## Root Cause
Big Head agent definition has prose-only filing instruction at line 22 with no concrete command example. Agents follow concrete examples over prose, so the instruction is ignored.

## Expected Behavior
agents/big-head.md should have explicit dedup instruction and --body-file reference in its step list.

## Acceptance Criteria
1. agents/big-head.md contains a dedup instruction referencing 'bd list --status=open' before the filing step
2. agents/big-head.md references '--body-file' (not bare 'bd create') in the filing instruction
3. Steps in the 'When consolidating:' list are sequentially numbered 1-8 with no gaps
4. Old step 7 ('Write the consolidated report') is renumbered to step 8 with content unchanged
