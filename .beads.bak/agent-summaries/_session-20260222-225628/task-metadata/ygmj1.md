# Task: ant-farm-ygmj.1
**Status**: success
**Title**: Upgrade CCB to sonnet and add root cause spot-check
**Type**: task
**Priority**: P2
**Epic**: ant-farm-ygmj
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [ant-farm-ygmj.3, ant-farm-ygmj.4], blockedBy: []}

## Affected Files
- orchestration/templates/checkpoints.md:L514-620 — CCB (Colony Census Bureau) checkpoint section; model assignment, checks 0-7
- orchestration/RULES.md:L429 — Model Assignments table, PC -- CCB row (haiku -> sonnet)

## Root Cause
CCB currently uses haiku model, but Checks 3 (bead quality) and 6 (dedup correctness) require judgment that haiku cannot reliably provide -- assessing whether root cause explanations are substantive and whether merged findings genuinely share a code path.

## Expected Behavior
CCB uses sonnet model. A new Check 3b (Root Cause Spot-Check) validates up to 2 beads by reading source files at referenced file:line locations. SUSPECT severity is distinguished as minor vs material, with material failures triggering escalation.

## Acceptance Criteria
1. CCB prompt in checkpoints.md specifies model as sonnet (grep for 'Model.*sonnet' in CCB section)
2. Check 3b exists between Check 3 and Check 4 with spot-check instructions for up to 2 beads
3. Check 3b includes SUSPECT severity distinction (minor vs material) with different actions for each
4. Material escalation path documented: PARTIAL verdict -> context-degradation-suspected flag -> fresh Big Head spawn -> full review -> re-run CCB -> user escalation
5. RULES.md Model Assignments table shows CCB as sonnet, not haiku
6. Existing CCB checks 0-7 are unchanged (no regression)
