# Task: ant-farm-asdl.5
**Status**: success
**Title**: Verify all Big Head template changes are consistent and complete
**Type**: task
**Priority**: P2
**Epic**: ant-farm-asdl
**Agent Type**: code-reviewer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-asdl.1, ant-farm-asdl.2, ant-farm-asdl.3, ant-farm-asdl.4]}
**Blocked by**: ant-farm-asdl.1, ant-farm-asdl.2, ant-farm-asdl.3, ant-farm-asdl.4
**Expected blocker completion**: Wave 2 (asdl.2 and asdl.3 are Wave 2; asdl.1 is Wave 1; asdl.4 is P3 outside scope but is a blocker)

## Affected Files
- orchestration/templates/big-head-skeleton.md — verify no bare bd create, dedup present, 5 sections, step numbering
- orchestration/templates/reviews.md — verify dedup protocol present
- orchestration/templates/pantry.md — verify no bare bd create
- agents/big-head.md — verify dedup and --body-file references
- scripts/build-review-prompts.sh — verify extraction compatibility

## Root Cause
Verification task to ensure consistency across all 4 files modified by the asdl epic.

## Expected Behavior
All 5 verification checks (V1-V5) pass.

## Acceptance Criteria
1. V1: zero bare bd create commands found (every instance has --body-file or references it in prose)
2. V2: bd list --status=open appears in both big-head-skeleton.md and reviews.md
3. V3: all 5 description template sections present in skeleton
4. V4: build-review-prompts.sh extraction logic is compatible with the modified skeleton
5. V5: step numbers are sequential with correct cross-references
