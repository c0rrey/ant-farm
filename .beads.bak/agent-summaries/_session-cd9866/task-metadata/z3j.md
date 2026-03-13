# Task: ant-farm-z3j
**Status**: success
**Title**: Checkpoint thresholds undefined: small file, sampling N<3, CCB bd list unbounded
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/checkpoints.md:82-84 — 'small file' undefined
- orchestration/templates/checkpoints.md:301 — DMVDC sampling formula needs guard
- orchestration/templates/checkpoints.md — CCB Check 7 bd list unbounded

## Root Cause
checkpoints.md uses three undefined or broken thresholds: (1) CCO Check 7 uses 'small file' without defining line count. (2) DMVDC sampling formula returns 3 when N=1 or N=2. (3) CCB Check 7 runs bd list --status=open with no limit/scope.

## Expected Behavior
All three thresholds explicitly defined with concrete values.

## Acceptance Criteria
1. Define small file = <100 lines
2. Fix formula to min(N, max(3, min(5, ceil(N/3))))
3. Scope CCB bead list to session-start date
