# Task: ant-farm-txw
**Status**: success
**Title**: Templates lack failure artifact specification for error paths
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/big-head-skeleton.md — Step 0 missing failure artifact
- orchestration/templates/pantry.md — needs failure artifact convention
- orchestration/templates/reviews.md — needs failure artifact convention

## Root Cause
Multiple templates specify FAIL conditions but do not specify what artifact to write on failure. Big Head Step 0 says 'Do NOT proceed' when reports missing but does not instruct writing a failure artifact. Downstream consumers have no written record of the failure.

## Expected Behavior
When any template reaches a FAIL condition, it writes a brief artifact to the expected output path explaining the failure.

## Acceptance Criteria
1. Big Head Step 0 writes failure artifact when reports missing
2. Convention documented for all templates
