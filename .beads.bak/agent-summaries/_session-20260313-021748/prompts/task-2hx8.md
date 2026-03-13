# Task Brief: ant-farm-2hx8
**Task**: Write /ant-farm:work skill definition
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-20260313-021748/summaries/2hx8.md

## Context
- **Affected files**:
  - skills/work.md (new file) — skill definition for /ant-farm:work slash command
- **Root cause**: N/A — new feature. /ant-farm:work slash command needed to trigger execution workflow.
- **Expected behavior**: skills/work.md exists with skill frontmatter, reads .crumbs/tasks.jsonl, routes to RULES.md, includes execution startup coherence check.
- **Acceptance criteria**:
  1. skills/work.md exists with correct skill frontmatter and trigger pattern
  2. Reads .crumbs/tasks.jsonl for task data
  3. Routes to RULES.md workflow (Queen orchestration)
  4. Execution startup coherence check documented: blocked_by validation, parent validation, stale in_progress detection
  5. Creates SESSION_DIR with timestamp-based naming
  6. Error handling: .crumbs/ not initialized, no tasks found, all tasks closed

## Scope Boundaries
Read ONLY:
- skills/ directory — to understand existing skill definition format (if any exist)
- orchestration/RULES.md — to understand the workflow this skill routes to
- orchestration/SETUP.md — for context on project structure

Do NOT edit:
- orchestration/RULES.md
- orchestration/templates/*.md
- agents/*.md
- CLAUDE.md, CHANGELOG.md, README.md

## Focus
Your task is ONLY to create skills/work.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
