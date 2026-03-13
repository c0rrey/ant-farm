# Task: ant-farm-veht
**Status**: success
**Title**: Add TDV checkpoint definition to checkpoints.md
**Type**: task
**Priority**: P2
**Epic**: ant-farm-f4h5
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-h2gu]}
**Blocked by**: ant-farm-h2gu
**Expected wave**: Wave 2 (after h2gu completes in Wave 1)

## Affected Files
- orchestration/templates/checkpoints.md — add new TDV checkpoint definition

## Root Cause
TDV (Trail Decomposition Verification) checkpoint needs to be added alongside existing checkpoints (SSV, CCO, WWD, DMVDC, CCB, ESV) for the decomposition workflow.

## Expected Behavior
TDV checkpoint added with 5 structural checks, 3 heuristic warnings, verdict definitions, and retry logic.

## Acceptance Criteria
1. TDV checkpoint added to checkpoints.md with same format as existing checkpoints
2. All 5 structural checks documented with pass/fail criteria
3. 3 heuristic warnings documented as warnings (not blockers)
4. Verdict definitions: TDV PASS -> handoff, TDV FAIL -> Architect retry with gap list
5. Max 2 retries documented with escalation to user after limit
6. Provisional wave computation algorithm documented (for scope coherence check)
7. TDV property table included: name, run by, model, when, blocks, max retries, checks
