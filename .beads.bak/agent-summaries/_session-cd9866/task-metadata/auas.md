# Task: ant-farm-auas
**Status**: success
**Title**: Missing input validation guards on Queen-owned review path (REVIEW_ROUND, CHANGED_FILES, TASK_IDS)
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md — Queen review path logic
- orchestration/templates/pantry.md — receives REVIEW_ROUND, CHANGED_FILES, TASK_IDS
- orchestration/templates/checkpoints.md — references REVIEW_ROUND
- orchestration/templates/nitpicker-skeleton.md — receives review inputs
- orchestration/templates/big-head-skeleton.md — receives review inputs

## Root Cause
Missing input validation guards on Queen-owned review path for REVIEW_ROUND, CHANGED_FILES, TASK_IDS variables. No description available in bd; details from title indicate these variables need validation before use.

## Expected Behavior
All Queen-owned review path variables are validated before being passed to subagents.

## Acceptance Criteria
1. REVIEW_ROUND, CHANGED_FILES, TASK_IDS are validated before use
2. Missing or malformed values produce actionable error messages
