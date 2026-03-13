# Task: ant-farm-m5lg
**Status**: success
**Title**: fix: review-skeletons/ and review-reports/ missing from Step 0 session directory setup
**Type**: bug
**Priority**: P2
**Epic**: ant-farm-908t
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md (after line 336) — add note about review-skeletons/ and review-reports/ lazy creation

## Root Cause
review-skeletons/ and review-reports/ directories were introduced after the original Step 0 setup. They are created lazily but the Session Directory section gives no hint they will exist.

## Expected Behavior
RULES.md Session Directory section should document all 7 subdirectories including the lazily-created review dirs.

## Acceptance Criteria
1. RULES.md Session Directory section documents all 7 subdirectories that appear in practice
2. Note clarifies lazy creation (review dirs created by their respective phases, not at Step 0)
3. Crash recovery documentation accounts for directories that may not yet exist
