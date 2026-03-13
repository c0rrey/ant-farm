# Task: ant-farm-yn1r
**Status**: success
**Title**: compose-review-skeletons.sh sed regex converts all {UPPERCASE} tokens, not just slot markers
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- scripts/compose-review-skeletons.sh:99-102 — sed pattern and comment

## Root Cause
sed 's/{\([A-Z][A-Z_]*\)}/{{\1}}/g' blanket converts any {UPPERCASE} text, not just slot markers. Also requires 2+ chars (undocumented).

## Expected Behavior
Either whitelist known slot names or document the assumption. Comment should accurately describe regex behavior.

## Acceptance Criteria
1. Comment accurately describes the regex behavior (2+ char minimum)
2. Either whitelist approach or documented assumption added
