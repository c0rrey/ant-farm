# Task: ant-farm-rlne
**Status**: success
**Title**: Pantry placeholder contamination detection ambiguous for {UPPERCASE} patterns
**Type**: bug
**Priority**: P1
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- `orchestration/templates/pantry.md:44-89` — fail-fast Condition 3

## Root Cause
Pantry Step 2 Condition 3 placeholder contamination detection relies on model judgment rather than a concrete syntactic definition. Real metadata files may legitimately contain `{UPPERCASE}` strings when a task references configuration placeholders. The Pantry may incorrectly flag valid metadata as contaminated.

## Expected Behavior
Contamination detection should use a precise syntactic rule that distinguishes Scout placeholders from legitimate task content.

## Acceptance Criteria
1. Condition 3 defines a precise regex or syntactic pattern for contamination detection
2. `{UPPERCASE}` patterns are explicitly excluded from contamination with rationale
3. An example is provided showing a legitimate `{SESSION_DIR}` reference in task metadata
