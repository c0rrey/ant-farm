# Task: ant-farm-pid
**Status**: success
**Title**: AGG-038: Clarify wildcard artifact path matching in reviews.md transition gate
**Type**: task
**Priority**: P1
**Epic**: ant-farm-753
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/reviews.md — Transition gate wildcard matching clarification

## Root Cause
reviews.md specifies verifying artifacts with wildcard * for the timestamp portion. Multiple files could match due to retries, and the instruction doesn't specify which to check.

## Expected Behavior
Clarified: Verify at least one DMVDC artifact exists with PASS verdict. If multiple exist, the most recent by timestamp must show PASS.

## Acceptance Criteria
1. reviews.md transition gate specifies which artifact to check when multiple match the wildcard
2. The most-recent-by-timestamp rule is documented for retry scenarios
3. The PASS verdict requirement is explicit (not just file existence)
