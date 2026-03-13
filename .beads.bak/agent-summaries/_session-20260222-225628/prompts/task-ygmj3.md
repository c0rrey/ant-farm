# Task Brief: ant-farm-ygmj.3
**Task**: Rewrite fix workflow for in-team agents
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-20260222-225628/summaries/ygmj3.md

## Context
- **Affected files**: orchestration/templates/reviews.md:L975-1070 — Fix Workflow section; rewrite for persistent team design with in-team fix agents
- **Root cause**: The current fix workflow in reviews.md describes standalone Task agents for fixes. The persistent team design requires fix DPs and fix PCs to spawn into the Nitpicker team for direct reviewer communication and tight DMVDC inner loop.
- **Expected behavior**: Fix Workflow section describes fix DPs and fix PCs spawning into the persistent team, documents the fix inner loop protocol (DP -> fix-pc-wwd -> fix-pc-dmvdc -> iterate), Pantry/CCO skip rationale, round transition via SendMessage, and fix-cycle Scout auto-approval.
- **Acceptance criteria**:
  1. Fix workflow section describes fix DPs and fix PCs spawning into the persistent team via Task with team_name parameter
  2. Fix inner loop protocol documented: DP -> fix-pc-wwd -> fix-pc-dmvdc -> iterate on fail (with max 2 retries)
  3. Pantry/CCO skip rationale documented with clear explanation of why beads + CCB + SSV are sufficient
  4. Round transition protocol uses SendMessage to re-task Correctness and Edge Cases reviewers
  5. Fix-cycle Scout documented as auto-approved with SSV gate
  6. Fix DP prompt structure shown (lean prompt, bead as source of truth, message fix-pc-wwd after commit)
  7. Naming convention for fix team members documented (fix-dp-N, fix-pc-wwd, fix-pc-dmvdc, round suffixes)

## Scope Boundaries
Read ONLY: orchestration/templates/reviews.md:L975-1070 (Fix Workflow section and surrounding context for P1/P2 handling and P3 handling)
Do NOT edit: orchestration/templates/reviews.md:L1-974 (all sections before the Fix Workflow), orchestration/templates/checkpoints.md, orchestration/templates/big-head-skeleton.md, orchestration/RULES.md, orchestration/templates/implementation.md

## Focus
Your task is ONLY to rewrite the Fix Workflow section (L983-1070) in reviews.md for in-team agents using the persistent team design.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
