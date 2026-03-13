# Task Brief: ant-farm-ygmj.4
**Task**: Update RULES.md for persistent team and fix inner loop
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-20260222-225628/summaries/ygmj4.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L157-305 -- Steps 3b and 3c; rewrite for persistent team and fix inner loop
  - orchestration/RULES.md:L416-435 -- Model Assignments table; update CCB to sonnet (already done by ygmj.1), add fix-pc-wwd haiku, fix-pc-dmvdc sonnet, fix DPs sonnet
  - orchestration/RULES.md:L533-548 -- Retry Limits / Error handling table; add fix DP stuck/crash, fix PC crash, reviewer failure, Big Head crash, CCB material fail
- **Root cause**: RULES.md currently describes a Nitpicker team that is implicitly torn down after round 1 and a fix workflow that uses standalone Task agents. The persistent team design requires the team to stay alive across the full review-fix-review loop with fix agents spawning into it.
- **Expected behavior**: Step 3b documents team persistence across the full loop. Step 3c documents the complete fix inner loop with in-team agents, Scout auto-approval, and SendMessage round transitions. Model assignments, error handling, team naming conventions, and progress log entries are all updated.
- **Acceptance criteria**:
  1. Step 3b explicitly states team persists across the full loop (no teardown after round 1)
  2. Step 3c documents: Big Head handoff -> Scout (outside team) -> SSV -> fix agents spawn into team -> inner loop -> round transition
  3. Fix-cycle Scout is documented as auto-approved for the user with SSV gate as mechanical safety net
  4. Model Assignments table updated: CCB sonnet, fix-pc-wwd haiku, fix-pc-dmvdc sonnet, fix DPs sonnet
  5. Error handling covers fix DP stuck/crash, fix PC crash, reviewer failure, Big Head crash, CCB material fail
  6. Team naming conventions documented (fix-dp-N, fix-pc-wwd, fix-pc-dmvdc with round suffixes)
  7. Progress log format includes new milestones for fix cycle steps

## Scope Boundaries
Read ONLY:
- orchestration/RULES.md:L1-590 (full file for context, especially Steps 3b-3c at L157-305, Model Assignments at L416-435, Retry Limits at L533-548)
- orchestration/templates/reviews.md (read-only reference for fix workflow design that ygmj.3 rewrote; do NOT edit)
- orchestration/templates/big-head-skeleton.md (read-only reference for bead-list handoff step that ygmj.2 added; do NOT edit)
- orchestration/templates/checkpoints.md (read-only reference for CCB upgrade that ygmj.1 added; do NOT edit)

Do NOT edit:
- orchestration/templates/reviews.md (owned by ygmj.3)
- orchestration/templates/big-head-skeleton.md (owned by ygmj.2)
- orchestration/templates/checkpoints.md (owned by ygmj.1)
- orchestration/RULES.md sections outside L157-305, L416-435, L533-548 (e.g., Steps 0-2, Step 4-6, Concurrency Rules, Session Directory, Anti-Patterns)
- Any files not listed above

## Focus
Your task is ONLY to update RULES.md Steps 3b, 3c, Model Assignments table, and Error Handling table to document the persistent team design and fix inner loop.
Do NOT fix adjacent issues you notice.

**Important predecessor context**: This task depends on work done by three predecessor tasks:
- ygmj.1 (Wave 1): Upgraded CCB to sonnet in checkpoints.md and updated the Model Assignments table row for PC-CCB (L429). Your Model Assignments edits must preserve this change and add new rows for fix agents.
- ygmj.2 (Wave 1): Added bead-list handoff step 12 to big-head-skeleton.md. Your Step 3c fix workflow documentation should reference this handoff mechanism.
- ygmj.3 (Wave 2): Rewrote the fix workflow section in reviews.md for in-team agents. Your RULES.md Steps 3b/3c must be consistent with the fix workflow as documented in reviews.md. Read reviews.md after ygmj.3's changes to ensure consistency.

Run `git pull --rebase` before reading RULES.md to ensure you have all predecessor commits.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
