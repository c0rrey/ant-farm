# Task: ant-farm-9vq
**Status**: success
**Title**: scrub-pii.sh grep pattern defined as variable but duplicated inline in verification
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- scripts/scrub-pii.sh:35,38,52-53 — PII_PATTERN variable vs inline regex

## Root Cause
PII_PATTERN is defined at line 35 and used in --check mode (line 38), but post-scrub verification (lines 52-53) re-inlines the same regex pattern. If either drifts, check and verification validate against different definitions.

## Expected Behavior
Single PII pattern source used in all grep calls.

## Acceptance Criteria
1. PII_PATTERN variable is used in all three grep calls
2. No duplicated inline patterns
