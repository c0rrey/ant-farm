# Task Brief: ant-farm-ha7a.7
**Task**: Update big-head-skeleton for round-aware consolidation
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-50c2c6/summaries/ha7a.7.md

## Context
- **Affected files**: `orchestration/templates/big-head-skeleton.md:L1-80` -- Entire file; add {REVIEW_ROUND} placeholder, replace single TeamCreate example with two round-dependent examples, update agent-facing template with round-aware language and Step 10 for P3 auto-filing
- **Root cause**: big-head-skeleton.md hardcodes "4 Nitpicker reports" and a single 6-member TeamCreate example. With the review loop convergence feature, round 2+ uses only 2 reviewers and requires P3 auto-filing as step 10. The skeleton needs to support both round 1 and round 2+ scenarios.
- **Expected behavior**:
  - Placeholder list includes `{REVIEW_ROUND}` with description mentioning "review round number (1, 2, 3, ...)"
  - File contains two TeamCreate examples -- "**Round 1**:" (6 members) and "**Round 2+**:" (4 members)
  - Agent template says "Consolidate the Nitpicker reports" (no hardcoded "4") followed by `**Review round**: {REVIEW_ROUND}` with round-dependent report count explanation
  - Step 10 exists with heading "**Round 2+ only -- P3 auto-filing**" and contains `bd dep add <id> <epic-id> --type parent-child`
- **Acceptance criteria**:
  1. Placeholder list includes `{REVIEW_ROUND}` with description mentioning "review round number (1, 2, 3, ...)"
  2. File contains two TeamCreate examples -- verify both "**Round 1**:" (6 members) and "**Round 2+**:" (4 members) exist
  3. Agent template says "Consolidate the Nitpicker reports" (no hardcoded "4") followed by `**Review round**: {REVIEW_ROUND}` with round-dependent report count explanation
  4. Step 10 exists with heading "**Round 2+ only -- P3 auto-filing**" and contains `bd dep add <id> <epic-id> --type parent-child`

## Scope Boundaries
Read ONLY: `orchestration/templates/big-head-skeleton.md:L1-80`, `docs/plans/2026-02-19-review-loop-convergence.md:L504-581` (Task 7 section of the implementation plan)
Do NOT edit: Any file other than `orchestration/templates/big-head-skeleton.md`. Do NOT edit `orchestration/templates/reviews.md` or `orchestration/RULES.md`.

## Focus
Your task is ONLY to update big-head-skeleton.md for round-aware consolidation and P3 auto-filing.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
