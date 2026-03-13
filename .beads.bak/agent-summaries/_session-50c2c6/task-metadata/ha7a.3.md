# Task: ant-farm-ha7a.3
**Status**: success
**Title**: Update Big Head verification and summary for round-aware report counts
**Type**: task
**Priority**: P2
**Epic**: ant-farm-ha7a
**Agent Type**: technical-writer
**Dependencies**: blocks: [ant-farm-ha7a.11, ant-farm-ha7a.5], blockedBy: [ant-farm-ha7a.2]

## Affected Files
- `orchestration/templates/reviews.md:339-370` — Step 0: Verify All Reports Exist (MANDATORY GATE); hardcoded 4-report check to be replaced with round-aware version
- `orchestration/templates/reviews.md:356-410` — Step 0a: Remediation Path for Missing Reports; polling loop with hardcoded 4-variable check to be made round-aware
- `orchestration/templates/reviews.md:475-560` — Step 3: Write Consolidated Summary; hardcoded reviewer list and 4-row Read Confirmation table to be made dynamic

## Root Cause
Big Head consolidation sections hardcode "4 reports" but the review loop convergence feature introduces round-aware report counts (4 reports in round 1, 2 reports in round 2+). These sections need to conditionally expect different reports per round.

## Expected Behavior
- Step 0 says "The number of expected reports depends on the review round" with separate Round 1 and Round 2+ bash blocks
- Step 0a polling loop uses `# <IF ROUND 1>` / `# </IF ROUND 1>` comment markers wrapping clarity/excellence checks
- A `**Pantry responsibility**` note follows the Step 0a code block
- Consolidated summary reviews-completed line shows `<Round 1: ... | Round 2+: ...>` format
- Read Confirmation table uses `<for each report in this round>` (not fixed 4 rows)

## Acceptance Criteria
1. Step 0 text says "The number of expected reports depends on the review round" with separate "**Round 1**" and "**Round 2+**" bash blocks
2. Step 0a polling loop contains `# <IF ROUND 1>` and `# </IF ROUND 1>` comment markers wrapping the clarity/excellence variable checks
3. A `**Pantry responsibility**` note follows the Step 0a code block
4. Consolidated summary reviews-completed line shows `<Round 1: ... | Round 2+: ...>` format (not hardcoded 4 reviewers)
5. Read Confirmation table uses `<for each report in this round>` (not fixed 4 rows)
