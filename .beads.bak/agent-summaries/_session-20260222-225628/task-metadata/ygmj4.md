# Task: ant-farm-ygmj.4
**Status**: success
**Title**: Update RULES.md for persistent team and fix inner loop
**Type**: task
**Priority**: P2
**Epic**: ant-farm-ygmj
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-ygmj.1, ant-farm-ygmj.2, ant-farm-ygmj.3]}
**Blocked by**: ant-farm-ygmj.1 (Wave 1), ant-farm-ygmj.2 (Wave 1), ant-farm-ygmj.3 (Wave 2)

## Affected Files
- orchestration/RULES.md:L157-301 — Steps 3b and 3c; rewrite for persistent team and fix inner loop
- orchestration/RULES.md:L416-435 — Model Assignments table; update CCB to sonnet, add fix-pc-wwd haiku, fix-pc-dmvdc sonnet
- orchestration/RULES.md:L530-546 — Error handling table; add fix DP stuck/crash, fix PC crash, reviewer failure, Big Head crash, CCB material fail

## Root Cause
RULES.md currently describes a Nitpicker team that is implicitly torn down after round 1 and a fix workflow that uses standalone Task agents. The persistent team design requires the team to stay alive across the full review-fix-review loop with fix agents spawning into it.

## Expected Behavior
Step 3b documents team persistence across the full loop. Step 3c documents the complete fix inner loop with in-team agents, Scout auto-approval, and SendMessage round transitions. Model assignments, error handling, team naming conventions, and progress log entries are all updated.

## Acceptance Criteria
1. Step 3b explicitly states team persists across the full loop (no teardown after round 1)
2. Step 3c documents: Big Head handoff -> Scout (outside team) -> SSV -> fix agents spawn into team -> inner loop -> round transition
3. Fix-cycle Scout is documented as auto-approved for the user with SSV gate as mechanical safety net
4. Model Assignments table updated: CCB sonnet, fix-pc-wwd haiku, fix-pc-dmvdc sonnet, fix DPs sonnet
5. Error handling covers fix DP stuck/crash, fix PC crash, reviewer failure, Big Head crash, CCB material fail
6. Team naming conventions documented (fix-dp-N, fix-pc-wwd, fix-pc-dmvdc with round suffixes)
7. Progress log format includes new milestones for fix cycle steps
