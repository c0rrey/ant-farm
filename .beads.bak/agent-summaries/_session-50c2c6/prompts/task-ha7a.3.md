# Task Brief: ant-farm-ha7a.3
**Task**: Update Big Head verification and summary for round-aware report counts
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-50c2c6/summaries/ha7a.3.md

## Context
- **Affected files**:
  - `orchestration/templates/reviews.md:L339-370` -- Step 0: Verify All Reports Exist (MANDATORY GATE); hardcoded 4-report check to be replaced with round-aware version
  - `orchestration/templates/reviews.md:L356-410` -- Step 0a: Remediation Path for Missing Reports; polling loop with hardcoded 4-variable check to be made round-aware
  - `orchestration/templates/reviews.md:L475-560` -- Step 3: Write Consolidated Summary; hardcoded reviewer list and 4-row Read Confirmation table to be made dynamic
- **Root cause**: Big Head consolidation sections hardcode "4 reports" but the review loop convergence feature introduces round-aware report counts (4 reports in round 1, 2 reports in round 2+). These sections need to conditionally expect different reports per round.
- **Expected behavior**:
  - Step 0 says "The number of expected reports depends on the review round" with separate Round 1 and Round 2+ bash blocks
  - Step 0a polling loop uses `# <IF ROUND 1>` / `# </IF ROUND 1>` comment markers wrapping clarity/excellence checks
  - A `**Pantry responsibility**` note follows the Step 0a code block
  - Consolidated summary reviews-completed line shows `<Round 1: ... | Round 2+: ...>` format
  - Read Confirmation table uses `<for each report in this round>` (not fixed 4 rows)
- **Acceptance criteria**:
  1. Step 0 text says "The number of expected reports depends on the review round" with separate "**Round 1**" and "**Round 2+**" bash blocks
  2. Step 0a polling loop contains `# <IF ROUND 1>` and `# </IF ROUND 1>` comment markers wrapping the clarity/excellence variable checks
  3. A `**Pantry responsibility**` note follows the Step 0a code block
  4. Consolidated summary reviews-completed line shows `<Round 1: ... | Round 2+: ...>` format (not hardcoded 4 reviewers)
  5. Read Confirmation table uses `<for each report in this round>` (not fixed 4 rows)

## Scope Boundaries
Read ONLY: `orchestration/templates/reviews.md:L339-560` (Step 0, Step 0a, Step 3 sections), `docs/plans/2026-02-19-review-loop-convergence.md:L174-297` (Task 3 section of the implementation plan)
Do NOT edit: Any file other than `orchestration/templates/reviews.md`. Do NOT edit sections outside Step 0, Step 0a, and Step 3 of the Big Head Consolidation Protocol. Do NOT edit Queen's Step 3c, Handle P3 Issues, or the review type definitions (Review 1-4). Do NOT add the P3 Auto-Filing section (that is task ha7a.4).

## Focus
Your task is ONLY to update Big Head Step 0, Step 0a, and Step 3 for round-aware report counts.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
