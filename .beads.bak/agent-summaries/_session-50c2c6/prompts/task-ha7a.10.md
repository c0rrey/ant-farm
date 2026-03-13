# Task Brief: ant-farm-ha7a.10
**Task**: Update CCB checkpoint for round-aware report counts
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-50c2c6/summaries/ha7a.10.md

## Context
- **Affected files**: orchestration/templates/checkpoints.md:L453 (CCB header -- update "after all 4 review reports" to mention round-dependent counts), orchestration/templates/checkpoints.md:L467-L472 (Individual reports list -- split into Round 1 and Round 2+ subsections), orchestration/templates/checkpoints.md:L473 (document count line -- update to round-aware), orchestration/templates/checkpoints.md:L475-L481 (Check 0: Report Existence Verification -- add round-dependent file lists), orchestration/templates/checkpoints.md:L483-L487 (Check 1: Finding Count Reconciliation -- add round-dependent counting patterns)
- **Root cause**: The CCB checkpoint hardcodes 4 review reports and 5 documents, which will be incorrect in round 2+ (only 2 reports = 3 total documents). This will cause CCB to fail spuriously after fix cycles.
- **Expected behavior**: CCB header mentions "4 reports in round 1, 2 in round 2+". Individual reports section has separate Round 1 (4 files) and Round 2+ (2 files) subsections. Document count says "round 1: 5 total = 4 reports + consolidated; round 2+: 3 total". Check 0 has round-dependent verification. Check 1 math format includes both round patterns. Exact content in docs/plans/2026-02-19-review-loop-convergence.md Task 10.
- **Acceptance criteria**:
  1. CCB header line contains "4 reports in round 1, 2 in round 2+"
  2. Individual reports section has "Round 1:" (4 files) and "Round 2+:" (2 files) subsections
  3. Document count says "round 1: 5 total = 4 reports + consolidated; round 2+: 3 total = 2 reports + consolidated"
  4. Check 0 has "**Round 1** -- verify exactly 4 report files:" and "**Round 2+** -- verify exactly 2 report files:"
  5. Check 1 math format includes both "Round 1:" and "Round 2+:" counting patterns in the "Report the math" line

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md:L450-L543 (CCB section from header through end), docs/plans/2026-02-19-review-loop-convergence.md:L722-L801 (Task 10 specification)
Do NOT edit: orchestration/templates/checkpoints.md:L1-L449 (everything before the CCB section -- CCO, WWD, DMVDC checkpoints), orchestration/templates/checkpoints.md:L489-L543 (Checks 2-7 and verdict section -- leave unchanged), any file other than orchestration/templates/checkpoints.md

## Focus
Your task is ONLY to update the CCB checkpoint header, individual reports list, document count, Check 0, and Check 1 for round-aware report counts.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
