# Task: ant-farm-hf9a
**Status**: success
**Title**: Batch mode boundary conditions underdocumented
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md:L119-131 -- batch mode documentation; add partial commit handling and N=1 clarification

## Root Cause
RULES.md:L119-131 batch mode documentation does not handle boundary values. (a) Partial wave commit: if some agents crash without committing, no instruction on when to run WWD for committed subset. (b) N=1: single-agent wave technically triggers batch mode but serial mode is simpler.

## Expected Behavior
Batch mode documentation handles partial commit and N=1 edge cases clearly.

## Acceptance Criteria
1. Partial commit handling added: instructions for when to run WWD if some agents crash without committing
2. N=1 clarification added: single-agent wave uses serial mode (simpler)
3. Changes stay within RULES.md Step 3 WWD section
