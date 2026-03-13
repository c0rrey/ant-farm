# Task: ant-farm-nnmm
**Status**: success
**Title**: RULES.md Step 3 prose polish: milestone placement and variable naming
**Type**: bug
**Priority**: P3
**Epic**: ant-farm-908t
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md:131 — move WAVE_WWD_PASS progress log milestone to visually distinct position
- orchestration/RULES.md:147-149 — rename bash variable TIMESTAMP to REVIEW_TIMESTAMP

## Root Cause
Two scanability issues in RULES.md Step 3: (a) WAVE_WWD_PASS milestone is embedded mid-paragraph, (b) bash variable TIMESTAMP differs from template placeholder REVIEW_TIMESTAMP.

## Expected Behavior
Progress log milestone is visually distinct and bash variable naming matches template placeholder.

## Acceptance Criteria
1. WAVE_WWD_PASS progress log line is in a visually distinct position
2. Bash variable renamed from TIMESTAMP to REVIEW_TIMESTAMP
