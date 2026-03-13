# Task: ant-farm-bcv4
**Status**: success
**Title**: Silent failures in orchestration — unverified placeholder substitution and line cap
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES-decompose.md:127 — unsubstituted {CODEBASE_ROOT} causes silent greenfield misclassification
- orchestration/RULES-decompose.md:250 — Forager line cap has no enforcement mechanism

## Root Cause
Multiple points in the orchestration workflow rely on agents correctly performing actions without enforced verification. Failures produce incorrect results rather than errors.

## Expected Behavior
Explicit guard for CODEBASE_ROOT existence and post-research truncation enforcement for the 100-line cap.

## Acceptance Criteria
1. Unsubstituted {CODEBASE_ROOT} produces an explicit error instead of silent misclassification
2. Research files exceeding 100 lines are truncated before downstream consumption
