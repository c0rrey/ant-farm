# Task: ant-farm-ha7a.9
**Status**: success
**Title**: Update pantry review mode for round-aware brief composition
**Type**: task
**Priority**: P2
**Epic**: ant-farm-ha7a
**Agent Type**: technical-writer
**Dependencies**: blocks: [ant-farm-ha7a.11], blockedBy: [ant-farm-ha7a.2 (closed), ant-farm-ha7a.7 (closed), ant-farm-ha7a.8 (closed)]

## Affected Files
- `orchestration/templates/pantry.md` — 6 sections in review mode: Input spec, Brief composition, Files-to-write, Step 4 (Big Head brief), Step 5 (Previews), Step 6 (Return table)

## Root Cause
pantry.md's review mode describes a fixed 4-brief flow with no concept of review rounds. It must be updated to accept a round number as input and branch behavior (4 briefs round 1, 2 briefs round 2+) so that the Pantry agent correctly composes round-appropriate review packages.

## Expected Behavior
- Input spec includes "review round number (1, 2, 3, ...)"
- Brief composition has round-aware rules: Round 1 = 4 briefs (clarity, edge-cases, correctness, excellence); Round 2+ = 2 briefs (correctness, edge-cases only) with out-of-scope finding bar from reviews.md
- Files-to-write section shows "**Round 1**:" (4 files) and "**Round 2+**:" (2 files)
- Step 4 mentions "Review round number", "P3 auto-filing", and "**Polling loop adaptation**"
- Step 5 mentions `{REVIEW_ROUND}` placeholder
- Step 6 has "**Round 1 return table:**" (4 data rows) and "**Round 2+ return table:**" (2 data rows)
- Exact content specified in `docs/plans/2026-02-19-review-loop-convergence.md` Task 9.

## Acceptance Criteria
1. Input spec includes "review round number (1, 2, 3, ...)"
2. Brief composition has `**Round 1**: Compose 4 review briefs` and `**Round 2+**: Compose 2 review briefs`
3. Files-to-write section shows "**Round 1**:" (4 files) and "**Round 2+**:" (2 files)
4. Step 4 mentions "Review round number", "P3 auto-filing", and "**Polling loop adaptation**"
5. Step 5 mentions `{REVIEW_ROUND}` placeholder
6. Step 6 has "**Round 1 return table:**" (4 data rows) and "**Round 2+ return table:**" (2 data rows)
