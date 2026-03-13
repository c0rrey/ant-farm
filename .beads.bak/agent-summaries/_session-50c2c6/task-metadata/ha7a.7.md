# Task: ant-farm-ha7a.7
**Status**: success
**Title**: Update big-head-skeleton for round-aware consolidation
**Type**: task
**Priority**: P2
**Epic**: ant-farm-ha7a
**Agent Type**: technical-writer
**Dependencies**: blocks: [ant-farm-ha7a.11, ant-farm-ha7a.9], blockedBy: [ant-farm-ha7a.2]

## Affected Files
- `orchestration/templates/big-head-skeleton.md:1-80` — Entire file; add {REVIEW_ROUND} placeholder, replace single TeamCreate example with two round-dependent examples, update agent-facing template with round-aware language and Step 10 for P3 auto-filing

## Root Cause
big-head-skeleton.md hardcodes "4 Nitpicker reports" and a single 6-member TeamCreate example. With the review loop convergence feature, round 2+ uses only 2 reviewers and requires P3 auto-filing as step 10. The skeleton needs to support both round 1 and round 2+ scenarios.

## Expected Behavior
- Placeholder list includes `{REVIEW_ROUND}` with description mentioning "review round number (1, 2, 3, ...)"
- File contains two TeamCreate examples — "**Round 1**:" (6 members) and "**Round 2+**:" (4 members)
- Agent template says "Consolidate the Nitpicker reports" (no hardcoded "4") followed by `**Review round**: {REVIEW_ROUND}` with round-dependent report count explanation
- Step 10 exists with heading "**Round 2+ only — P3 auto-filing**" and contains `bd dep add <id> <epic-id> --type parent-child`

## Acceptance Criteria
1. Placeholder list includes `{REVIEW_ROUND}` with description mentioning "review round number (1, 2, 3, ...)"
2. File contains two TeamCreate examples — verify both "**Round 1**:" (6 members) and "**Round 2+**:" (4 members) exist
3. Agent template says "Consolidate the Nitpicker reports" (no hardcoded "4") followed by `**Review round**: {REVIEW_ROUND}` with round-dependent report count explanation
4. Step 10 exists with heading "**Round 2+ only — P3 auto-filing**" and contains `bd dep add <id> <epic-id> --type parent-child`
