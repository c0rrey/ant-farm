# Task: ant-farm-rgg3
**Status**: success
**Title**: build-review-prompts.sh FOCUS_AREAS_FILE missing readable check
**Type**: bug
**Priority**: P1
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- `scripts/build-review-prompts.sh:149-153` — FOCUS_AREAS_FILE validation

## Root Cause
FOCUS_AREAS_FILE only checks `-f` (existence) but not `-r` (readability), unlike skeleton file checks at L59-68. If the file exists but is not readable, `extract_focus_block` silently produces empty content, leading to degraded review quality.

## Expected Behavior
FOCUS_AREAS_FILE validation should check both `-f` and `-r`, matching the pattern used for skeleton files.

## Acceptance Criteria
1. FOCUS_AREAS_FILE validation checks both `-f` and `-r` (matching skeleton file checks at L59-68)
2. A comment explains the sibling-path derivation for FOCUS_AREAS_FILE
3. Script exits with a clear error message if the file is not readable
