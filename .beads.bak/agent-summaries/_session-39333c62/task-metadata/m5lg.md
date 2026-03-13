# Task: ant-farm-m5lg
**Status**: success
**Title**: fix: review-skeletons/ and review-reports/ missing from Step 0 session directory setup
**Type**: bug
**Priority**: P2
**Epic**: ant-farm-908t
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md — after line 336: add note about review-skeletons/ and review-reports/

## Root Cause
review-skeletons/ and review-reports/ directories appear in every session reaching the review phase but are not listed in Step 0 setup. They are created lazily by their respective phases.

## Expected Behavior
RULES.md Session Directory section documents all 7 subdirectories that appear in practice, noting lazy creation for review dirs.

## Acceptance Criteria
1. RULES.md Session Directory section documents all 7 subdirectories
2. Note clarifies lazy creation (review dirs created by their respective phases, not at Step 0)
3. Crash recovery documentation accounts for directories that may not yet exist
