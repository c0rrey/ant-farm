# Task Brief: ant-farm-qoig
**Task**: RULES.md tmux dependency without availability check
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/qoig.md

## Context
- **Affected files**: orchestration/RULES.md:L183-214 -- tmux-dependent section (Step 3b-v) assumes tmux binary is available
- **Root cause**: Step 3b-v dummy reviewer spawn assumes tmux is available (L198-206) and Queen is running inside tmux. No availability check with 'command -v tmux' or fallback.
- **Expected behavior**: Add command -v tmux and TMUX check before the tmux block.
- **Acceptance criteria**:
  1. tmux availability checked before use
  2. Graceful fallback when tmux is unavailable

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L183-214 (Step 3b-v dummy reviewer spawn section)
Do NOT edit: orchestration/templates/scout.md, orchestration/templates/pantry.md, scripts/, any other files

## Focus
Your task is ONLY to add tmux availability checking and fallback in the Step 3b-v section.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
