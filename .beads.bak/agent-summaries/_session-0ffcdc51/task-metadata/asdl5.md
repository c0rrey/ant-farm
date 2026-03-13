# Task: ant-farm-asdl.5
**Status**: success
**Title**: Verify all Big Head template changes are consistent and complete
**Type**: task
**Priority**: P2
**Epic**: ant-farm-asdl
**Agent Type**: code-reviewer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-asdl.1, ant-farm-asdl.2, ant-farm-asdl.3, ant-farm-asdl.4]}
**Blocked by**: ant-farm-asdl.1 (Wave 1), ant-farm-asdl.2 (Wave 2), ant-farm-asdl.3 (Wave 2), ant-farm-asdl.4 (Wave 2)

## Affected Files
- `orchestration/templates/big-head-skeleton.md` — V1 (no bare bd create), V3 (5 sections), V5 (step numbering)
- `orchestration/templates/reviews.md` — V1 (no bare bd create), V2 (dedup protocol)
- `agents/big-head.md` — V1 (no bare bd create)
- `orchestration/templates/pantry.md` — V1 (no bare bd create)
- `scripts/build-review-prompts.sh` — V4 (extraction compatibility)

## Root Cause
After all 4 implementation tasks complete, a verification pass is needed to confirm consistency across all files.

## Expected Behavior
All 5 verification checks (V1-V5) pass: no bare bd create commands, dedup protocol in skeleton and reviews.md, all 5 description sections present, build-review-prompts.sh compatibility, sequential step numbering.

## Acceptance Criteria
1. V1 passes: zero bare bd create commands found (every instance has --body-file or references it in prose)
2. V2 passes: bd list --status=open appears in both big-head-skeleton.md and reviews.md
3. V3 passes: all 5 description template sections present in skeleton
4. V4 passes: build-review-prompts.sh extraction logic is compatible with the modified skeleton
5. V5 passes: step numbers are sequential with correct cross-references
