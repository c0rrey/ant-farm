# Task: ant-farm-asdl.2
**Status**: success
**Title**: Add cross-session dedup and description template to reviews.md Big Head Consolidation Protocol
**Type**: task
**Priority**: P2
**Epic**: ant-farm-asdl
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [ant-farm-asdl.5], blockedBy: [ant-farm-asdl.1]}
**Blocked by**: ant-farm-asdl.1 (Wave 1)

## Affected Files
- `orchestration/templates/reviews.md:672-797` — Insert Step 2.5 dedup section (after line 672), replace bd create block (lines 775-779), update P3 auto-filing (lines 793-797)

## Root Cause
The reviews.md Big Head Consolidation Protocol has bare `bd create` commands and no cross-session dedup step, mirroring the same issues as big-head-skeleton.md.

## Expected Behavior
A Step 2.5 "Deduplicate Against Existing Beads" section should exist between Step 2 and Step 3. All bd create commands should use --body-file with structured descriptions.

## Acceptance Criteria
1. A 'Step 2.5: Deduplicate Against Existing Beads' section exists between Step 2 and Step 3 in the Big Head Consolidation Protocol, containing 'bd list --status=open' and 'bd search'
2. No bare bd create command remains in the bead filing section (lines 769-800) -- every instance includes --body-file
3. The description template in the bead filing section contains all 5 sections: Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria
4. The P3 auto-filing section (lines 793-797) uses --body-file with at minimum Root Cause, Affected Surfaces, and Acceptance Criteria
