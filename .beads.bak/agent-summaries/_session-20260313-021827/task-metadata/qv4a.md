# Task: ant-farm-qv4a
**Status**: success
**Title**: Temp file leak on error paths in fill_slot and big-head dedup
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- `scripts/build-review-prompts.sh:168-202` — fill_slot function temp file
- `orchestration/templates/big-head-skeleton.md:114-127` — cross-session dedup temp file

## Root Cause
Two temp file patterns lack cleanup on error paths: (1) fill_slot creates temp via mktemp but if awk fails, function returns without cleanup. (2) big-head-skeleton writes to `/tmp/open-crumbs-$$.txt` but never cleans it up.

## Expected Behavior
Temp files should be cleaned up on all exit paths including errors.

## Acceptance Criteria
1. fill_slot temp file is cleaned up even when awk fails (trap RETURN)
2. big-head-skeleton dedup temp file is cleaned up after use
3. No temp files leaked under simulated awk failure
