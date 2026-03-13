# Task: ant-farm-ha7a.8
**Status**: success
**Title**: Add round-aware scope instructions to nitpicker-skeleton
**Type**: task
**Priority**: P2
**Epic**: ant-farm-ha7a
**Agent Type**: technical-writer
**Dependencies**: blocks: [ant-farm-ha7a.11, ant-farm-ha7a.9], blockedBy: []

## Affected Files
- orchestration/templates/nitpicker-skeleton.md — Nitpicker reviewer skeleton template; (1) add `{REVIEW_ROUND}` to placeholder list, (2) update agent-facing template with round-aware review scope instructions

## Root Cause
The nitpicker-skeleton has no `{REVIEW_ROUND}` placeholder, so the Pantry agent cannot inject round information into reviewer prompts. Round 2+ reviewers need scope constraints limiting them to fix commits only.

## Expected Behavior
`{REVIEW_ROUND}` is added to the placeholder list after the last existing placeholder. In the agent-facing template, the "Perform a {REVIEW_TYPE} review" line is kept, `**Review round**: {REVIEW_ROUND}` is added after it, and round 2+ scope instructions follow (scope limited to fix commits only, out-of-scope findings only for runtime failures or silently wrong results). Exact content in `docs/plans/2026-02-19-review-loop-convergence.md` Task 8.

## Acceptance Criteria
1. `grep "REVIEW_ROUND" orchestration/templates/nitpicker-skeleton.md` returns matches in both the placeholder list and the agent template
2. Placeholder entry reads `{REVIEW_ROUND}: 1, 2, 3, ... (determines scope instructions; filled by Pantry)`
3. Agent template contains `**Review round**: {REVIEW_ROUND}` after the "Perform a {REVIEW_TYPE} review" line
4. Round 2+ scope text mentions "fix commits only", "runtime failure", and "silently wrong results"
