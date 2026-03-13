# Task: ant-farm-asdl.2
**Status**: success
**Title**: Add cross-session dedup and description template to reviews.md Big Head Consolidation Protocol
**Type**: task
**Priority**: P2
**Epic**: ant-farm-asdl
**Agent Type**: technical-writer
**Dependencies**: {blocks: [ant-farm-asdl.5], blockedBy: [ant-farm-asdl.1]}
**Blocked by**: ant-farm-asdl.1
**Expected blocker completion**: Wave 1 (ant-farm-asdl.1 is P1 and ready)

## Affected Files
- orchestration/templates/reviews.md:672-674 — insert Step 2.5 between Step 2 and Step 3
- orchestration/templates/reviews.md:775-779 — replace bare bd create with --body-file pattern
- orchestration/templates/reviews.md:795-796 — replace P3 auto-filing bd create

## Root Cause
reviews.md Big Head Consolidation Protocol lacks cross-session dedup step and uses bare bd create without --body-file for structured descriptions.

## Expected Behavior
reviews.md should have a Step 2.5 for dedup and use --body-file pattern for all bd create calls.

## Acceptance Criteria
1. A 'Step 2.5: Deduplicate Against Existing Beads' section exists between Step 2 and Step 3 in the Big Head Consolidation Protocol
2. No bare bd create command remains in the bead filing section (lines 769-800) -- every instance includes --body-file
3. The description template in the bead filing section contains all 5 sections: Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria
4. The P3 auto-filing section uses --body-file with at minimum Root Cause, Affected Surfaces, and Acceptance Criteria
