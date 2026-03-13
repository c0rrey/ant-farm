# Task Brief: ant-farm-3bz5
**Task**: Write setup script replacing sync-to-claude.sh
**Agent Type**: python-pro
**Summary output path**: .beads/agent-summaries/_session-20260313-021748/summaries/3bz5.md

## Context
- **Affected files**:
  - scripts/setup.sh (new file) — replacement for scripts/sync-to-claude.sh
- **Root cause**: N/A — new feature. Setup script needed to install plugin files to correct locations.
- **Expected behavior**: Setup script copies agent definitions, orchestration files, crumb.py to PATH, skill files. Backs up existing files. Warns about CC restart. Idempotent.
- **Acceptance criteria**:
  1. Setup script copies agent definitions to ~/.claude/agents/
  2. Setup script copies orchestration/ to ~/.claude/orchestration/
  3. crumb.py installed to ~/.local/bin/crumb with executable permissions
  4. Existing files backed up with timestamped .bak suffix before overwrite
  5. Warning message about Claude Code restart requirement for new agents displayed
  6. Script is idempotent: re-running updates files without duplicating backups
  7. Script validates PATH includes ~/.local/bin and warns if not

## Scope Boundaries
Read ONLY:
- scripts/sync-to-claude.sh — to understand current installation behavior being replaced
- scripts/ directory — to understand existing script conventions
- agents/ directory — to understand what files need to be installed
- orchestration/ directory — to understand directory structure to copy

Do NOT edit:
- scripts/sync-to-claude.sh (read only, do not modify the old script)
- agents/*.md
- orchestration/**/*.md
- CLAUDE.md, CHANGELOG.md, README.md

## Focus
Your task is ONLY to create scripts/setup.sh (or similar).
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
