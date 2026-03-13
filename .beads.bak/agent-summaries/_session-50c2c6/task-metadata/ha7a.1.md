# Task: ant-farm-ha7a.1
**Status**: success
**Title**: Add review round counter to queen-state template
**Type**: task
**Priority**: P2
**Epic**: ant-farm-ha7a
**Agent Type**: technical-writer
**Dependencies**: blocks: [ant-farm-ha7a.11, ant-farm-ha7a.6], blockedBy: []

## Affected Files
- orchestration/templates/queen-state.md — Queen state tracking template; insert `## Review Rounds` section between `## Pest Control` and `## Queue Position`

## Root Cause
The queen-state template has no field to track which review round is active, so the Queen has no persistent state to distinguish round 1 (full review) from round 2+ (fix verification).

## Expected Behavior
A `## Review Rounds` section with 4 placeholder fields (current round, round 1 commit range, fix commit range, termination status) is inserted between `## Pest Control` and `## Queue Position`. Exact markdown content is in `docs/plans/2026-02-19-review-loop-convergence.md` Task 1 Step 1.

## Acceptance Criteria
1. `grep "## Review Rounds" orchestration/templates/queen-state.md` returns a match
2. The section appears between `## Pest Control` and `## Queue Position` — verify section order: Pest Control → Review Rounds → Queue Position
3. The template includes all 4 placeholder fields: "Current round", "Round 1 commit range", "Fix commit range", "Termination"
4. Existing `## Pest Control` and `## Queue Position` sections remain intact and unmodified
