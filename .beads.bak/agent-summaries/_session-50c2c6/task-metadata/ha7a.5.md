# Task: ant-farm-ha7a.5
**Status**: success
**Title**: Update review checklists for round-aware team composition
**Type**: task
**Priority**: P2
**Epic**: ant-farm-ha7a
**Agent Type**: technical-writer
**Dependencies**: blocks: [ant-farm-ha7a.11], blockedBy: [ant-farm-ha7a.3 (closed), ant-farm-ha7a.4 (closed)]

## Affected Files
- `orchestration/templates/reviews.md` — both operational checklists: Nitpicker Checklist and Big Head Consolidation Checklist

## Root Cause
The Nitpicker Checklist and Big Head Consolidation Checklist in reviews.md were written for a single-round review flow and do not include round-aware checks. They need to be updated so orchestrators can verify round-dependent behavior (team size, prompt count, out-of-scope bar, P3 auto-filing) at runtime.

## Expected Behavior
- `### Nitpicker Checklist (verify before launching team)` contains: review round number check, round-dependent prompt count (4 round 1 / 2 round 2+), out-of-scope finding bar for round 2+, round-dependent team size (6 round 1 / 4 round 2+), Big Head P3 auto-filing instructions for round 2+.
- `### Big Head Consolidation Checklist (after all Nitpickers finish)` first item is round-aware report count; contains P3 auto-filing check for round 2+.
- Exact checklist items are specified in `docs/plans/2026-02-19-review-loop-convergence.md` Task 5.

## Acceptance Criteria
1. Nitpicker Checklist contains `Review round number passed to Pantry` item
2. Nitpicker Checklist contains item mentioning both "6 members" and "4 members" in round-dependent format
3. Nitpicker Checklist contains `Round 2+ reviewers include out-of-scope finding bar` item
4. Big Head Checklist first item says `Round 1: Read all 4 Nitpicker reports; Round 2+: Read 2 reports`
5. Big Head Checklist contains `Round 2+ on PASS: P3 beads auto-filed to "Future Work" epic` item
