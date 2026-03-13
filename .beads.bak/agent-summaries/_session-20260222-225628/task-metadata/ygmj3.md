# Task: ant-farm-ygmj.3
**Status**: success
**Title**: Rewrite fix workflow for in-team agents
**Type**: task
**Priority**: P2
**Epic**: ant-farm-ygmj
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [ant-farm-ygmj.4], blockedBy: [ant-farm-ygmj.1]}
**Blocked by**: ant-farm-ygmj.1 (expected to complete in Wave 1)

## Affected Files
- orchestration/templates/reviews.md:L975-1070 — Fix Workflow section; rewrite for persistent team design with in-team fix agents

## Root Cause
The current fix workflow in reviews.md describes standalone Task agents for fixes. The persistent team design requires fix DPs and fix PCs to spawn into the Nitpicker team for direct reviewer communication and tight DMVDC inner loop.

## Expected Behavior
Fix Workflow section describes fix DPs and fix PCs spawning into the persistent team, documents the fix inner loop protocol (DP -> fix-pc-wwd -> fix-pc-dmvdc -> iterate), Pantry/CCO skip rationale, round transition via SendMessage, and fix-cycle Scout auto-approval.

## Acceptance Criteria
1. Fix workflow section describes fix DPs and fix PCs spawning into the persistent team via Task with team_name parameter
2. Fix inner loop protocol documented: DP -> fix-pc-wwd -> fix-pc-dmvdc -> iterate on fail (with max 2 retries)
3. Pantry/CCO skip rationale documented with clear explanation of why beads + CCB + SSV are sufficient
4. Round transition protocol uses SendMessage to re-task Correctness and Edge Cases reviewers
5. Fix-cycle Scout documented as auto-approved with SSV gate
6. Fix DP prompt structure shown (lean prompt, bead as source of truth, message fix-pc-wwd after commit)
7. Naming convention for fix team members documented (fix-dp-N, fix-pc-wwd, fix-pc-dmvdc, round suffixes)
