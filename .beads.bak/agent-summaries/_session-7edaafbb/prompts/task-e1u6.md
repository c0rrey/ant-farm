# Task Brief: ant-farm-e1u6
**Task**: No tmux guard for dummy reviewer spawn
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/e1u6.md

## Context
- **Affected files**: orchestration/RULES.md:L183-214 -- dummy reviewer spawn section (Step 3b-v) uses tmux commands without checking for tmux session
- **Root cause**: RULES.md Step 3b-v runs tmux display-message (L198), tmux new-window (L201), and tmux send-keys (L202-206) without checking whether the Queen is inside a tmux session. Current single-Queen workflow does not require tmux.
- **Expected behavior**: Add if [ -z "$TMUX" ] guard before tmux commands.
- **Acceptance criteria**:
  1. Dummy reviewer section does not error outside tmux
  2. Inside tmux, behavior unchanged

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L183-214 (Step 3b-v dummy reviewer spawn section)
Do NOT edit: orchestration/templates/scout.md, orchestration/templates/pantry.md, scripts/, any other files

## Focus
Your task is ONLY to add a TMUX environment variable guard around the tmux commands in Step 3b-v.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
