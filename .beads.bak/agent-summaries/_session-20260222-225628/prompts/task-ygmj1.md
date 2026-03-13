# Task Brief: ant-farm-ygmj.1
**Task**: Upgrade CCB to sonnet and add root cause spot-check
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-20260222-225628/summaries/ygmj1.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L514-620 -- CCB (Colony Census Bureau) checkpoint section; model assignment, checks 0-7
  - orchestration/RULES.md:L429 -- Model Assignments table, PC -- CCB row (haiku -> sonnet)
- **Root cause**: CCB currently uses haiku model, but Checks 3 (bead quality) and 6 (dedup correctness) require judgment that haiku cannot reliably provide -- assessing whether root cause explanations are substantive and whether merged findings genuinely share a code path.
- **Expected behavior**: CCB uses sonnet model. A new Check 3b (Root Cause Spot-Check) validates up to 2 beads by reading source files at referenced file:line locations. SUSPECT severity is distinguished as minor vs material, with material failures triggering escalation.
- **Acceptance criteria**:
  1. CCB prompt in checkpoints.md specifies model as sonnet (grep for 'Model.*sonnet' in CCB section)
  2. Check 3b exists between Check 3 and Check 4 with spot-check instructions for up to 2 beads
  3. Check 3b includes SUSPECT severity distinction (minor vs material) with different actions for each
  4. Material escalation path documented: PARTIAL verdict -> context-degradation-suspected flag -> fresh Big Head spawn -> full review -> re-run CCB -> user escalation
  5. RULES.md Model Assignments table shows CCB as sonnet, not haiku
  6. Existing CCB checks 0-7 are unchanged (no regression)

## Scope Boundaries
Read ONLY:
- orchestration/templates/checkpoints.md:L514-620 (CCB section)
- orchestration/RULES.md:L425-435 (Model Assignments table)

Do NOT edit:
- Any CCB checks outside of inserting 3b (checks 0-7 must remain unchanged)
- Any other sections of checkpoints.md outside the CCB block (L514-620)
- Any other rows in the Model Assignments table besides the CCB row
- big-head-skeleton.md, reviews.md, pantry.md, or any other template files

## Focus
Your task is ONLY to upgrade the CCB model from haiku to sonnet and add the root cause spot-check (Check 3b).
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
