# Task: ant-farm-ha7a.2
**Status**: success
**Title**: Add round-aware review protocol and team setup to reviews.md
**Type**: task
**Priority**: P1
**Epic**: ant-farm-ha7a
**Agent Type**: technical-writer
**Dependencies**: blocks: [ant-farm-ha7a.11, ant-farm-ha7a.3, ant-farm-ha7a.4, ant-farm-ha7a.7, ant-farm-ha7a.9], blockedBy: []

## Affected Files
- orchestration/templates/reviews.md — Review pipeline protocol; two edits: (1) insert `## Round-Aware Review Protocol` section before `## Review 1: Clarity (P3)`, (2) update `### Team Setup` with round-dependent 6/4 member blocks

## Root Cause
The reviews.md file defines a fixed 4-reviewer, 6-member-team pipeline with no concept of review rounds, causing the review loop to run full reviews on every fix cycle instead of narrowing scope.

## Expected Behavior
A `## Round-Aware Review Protocol` section is inserted before the first review type heading, containing subsections for Round 1 (Full Review), Round 2+ (Fix Verification), Termination Rule, and Round 2+ Reviewer Instructions. Team Setup is updated to show round-dependent team sizes (6 for round 1, 4 for round 2+). Exact markdown in `docs/plans/2026-02-19-review-loop-convergence.md` Task 2.

## Acceptance Criteria
1. `grep "## Round-Aware Review Protocol" orchestration/templates/reviews.md` returns a match
2. The section appears before `## Review 1: Clarity (P3)` — verify heading order
3. The section contains all 4 subsections: Round 1 (Full Review), Round 2+ (Fix Verification), Termination Rule, Round 2+ Reviewer Instructions
4. Team Setup shows "**Round 1**: The Queen creates the Nitpicker team with **6 members**" and "**Round 2+**: The Queen creates the Nitpicker team with **4 members**"
5. `### Messaging Guidelines` section still exists immediately after Team Setup
