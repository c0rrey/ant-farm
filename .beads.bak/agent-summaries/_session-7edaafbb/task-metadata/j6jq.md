# Task: ant-farm-j6jq
**Status**: success
**Title**: Shell code blocks in reviews.md lack production quality: magic numbers, inverted sentinel, buried constraints
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/reviews.md — shell code blocks throughout

## Root Cause
Shell code blocks in reviews.md have magic numbers (hardcoded values without named constants), inverted sentinel logic (confusing boolean checks), and buried constraints (important rules hidden in inline comments).

## Expected Behavior
Shell code blocks should use named constants, clear sentinel logic, and prominently placed constraints.

## Acceptance Criteria
1. Magic numbers replaced with named constants or documented
2. Sentinel logic is clear and non-inverted
3. Important constraints are prominently placed
