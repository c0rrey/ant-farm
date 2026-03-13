# Task Brief: ant-farm-3imu
**Task**: Write /ant-farm:init skill definition
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-20260313-021748/summaries/3imu.md

## Context
- **Affected files**:
  - skills/init.md (new file) — skill definition for /ant-farm:init slash command
- **Root cause**: N/A — new feature. /ant-farm:init slash command needed to scaffold .crumbs/ in target projects.
- **Expected behavior**: skills/init.md exists with skill frontmatter, scaffolds .crumbs/ directory structure, installs crumb.py, detects project language/stack.
- **Acceptance criteria**:
  1. skills/init.md exists with correct skill frontmatter (name, description, trigger pattern)
  2. Skill creates .crumbs/tasks.jsonl, .crumbs/config.json, .crumbs/sessions/, .crumbs/history/
  3. config.json populated with prefix (prompted or auto-derived), default_priority P2, counters at 1
  4. .crumbs/sessions/ added to .gitignore (not the whole .crumbs/)
  5. crumb.py installation step included with PATH verification
  6. Idempotent: re-running on existing .crumbs/ doesn't overwrite data

## Scope Boundaries
Read ONLY:
- skills/ directory — to understand existing skill definition format (if any exist)
- orchestration/SETUP.md — for context on project structure and .crumbs/ layout

Do NOT edit:
- orchestration/RULES.md
- orchestration/templates/*.md
- agents/*.md
- CLAUDE.md, CHANGELOG.md, README.md

## Focus
Your task is ONLY to create skills/init.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
