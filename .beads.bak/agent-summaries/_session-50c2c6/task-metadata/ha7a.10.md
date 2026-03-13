# Task: ant-farm-ha7a.10
**Status**: success
**Title**: Update CCB checkpoint for round-aware report counts
**Type**: task
**Priority**: P2
**Epic**: ant-farm-ha7a
**Agent Type**: technical-writer
**Dependencies**: blocks: [ant-farm-ha7a.11], blockedBy: []

## Affected Files
- orchestration/templates/checkpoints.md — CCB checkpoint section; update header, individual reports list, document count, Check 0 (Report Existence Verification), and Check 1 (Finding Count Reconciliation) for round-aware report counts

## Root Cause
The CCB checkpoint hardcodes 4 review reports and 5 documents, which will be incorrect in round 2+ (only 2 reports = 3 total documents). This will cause CCB to fail spuriously after fix cycles.

## Expected Behavior
CCB header mentions "4 reports in round 1, 2 in round 2+". Individual reports section has separate Round 1 (4 files) and Round 2+ (2 files) subsections. Document count says "round 1: 5 total = 4 reports + consolidated; round 2+: 3 total". Check 0 has round-dependent verification. Check 1 math format includes both round patterns. Exact content in `docs/plans/2026-02-19-review-loop-convergence.md` Task 10.

## Acceptance Criteria
1. CCB header line contains "4 reports in round 1, 2 in round 2+"
2. Individual reports section has "Round 1:" (4 files) and "Round 2+:" (2 files) subsections
3. Document count says "round 1: 5 total = 4 reports + consolidated; round 2+: 3 total = 2 reports + consolidated"
4. Check 0 has "**Round 1** — verify exactly 4 report files:" and "**Round 2+** — verify exactly 2 report files:"
5. Check 1 math format includes both "Round 1:" and "Round 2+:" counting patterns in the "Report the math" line
