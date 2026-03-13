# Task Brief: ant-farm-lajv
**Task**: Research tmux + iTerm2 control mode integration for spawning Claude Code sessions
**Agent Type**: data-researcher
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/lajv.md

## Context
- **Affected files**:
  - docs/plans/2026-02-19-meta-orchestration-plan.md:L34-49 -- tmux-Based Spawning section with current tmux examples
  - docs/plans/2026-02-19-meta-orchestration-plan.md:L239-241 -- iTerm2 alternative note (currently TBD)
  - NOTE: Scout metadata had bare filename (no line numbers). Lines identified by Pantry via grep.
- **Root cause**: Meta-orchestration design and dummy reviewer instrumentation require spawning Claude Code sessions in tmux windows visible within iTerm2. The exact commands for creating windows and sending keystrokes within iTerm2's control mode may differ from standard tmux usage.
- **Expected behavior**: Document exact commands for tmux control mode session management within iTerm2.
- **Acceptance criteria**:
  1. Document the exact commands needed to: start a tmux control mode session, create a new window, send a prompt to that window, and check window status
  2. Verify whether tmux send-keys works as expected in control mode or if an alternative is needed
  3. Update the dummy reviewer bead's description with correct iTerm2-compatible commands
  4. Update the meta-orchestration plan tmux examples with correct iTerm2 control mode commands

## Scope Boundaries
Read ONLY: docs/plans/2026-02-19-meta-orchestration-plan.md (full file -- research task requires understanding the complete plan)
Do NOT edit: orchestration/RULES.md, orchestration/templates/*.md (any orchestration template)

## Focus
Your task is ONLY to research tmux + iTerm2 control mode integration and update the meta-orchestration plan with correct commands.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
