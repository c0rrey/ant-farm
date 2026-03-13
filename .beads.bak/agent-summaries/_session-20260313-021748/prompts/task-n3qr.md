# Task Brief: ant-farm-n3qr
**Task**: Write /ant-farm:status skill definition
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-20260313-021748/summaries/n3qr.md

## Context
- **Affected files**:
  - skills/status.md (new file) — skill definition for /ant-farm:status slash command
- **Root cause**: N/A — new feature. /ant-farm:status slash command needed for quick view dashboard.
- **Expected behavior**: skills/status.md exists with skill frontmatter, displays trail completion counts, crumb status summary, last session summary.
- **Acceptance criteria**:
  1. skills/status.md exists with correct skill frontmatter and trigger pattern
  2. Displays trail completion counts using crumb trail list output
  3. Displays crumb status summary: open count, blocked count, in_progress count, closed count
  4. Shows last session summary from most recent .crumbs/history/exec-summary-*.md
  5. Handles edge case: no tasks exist, no sessions completed yet
  6. Output is concise and scannable (dashboard format, not raw command output)

## Scope Boundaries
Read ONLY:
- skills/ directory — to understand existing skill definition format (if any exist)
- orchestration/SETUP.md — for context on project structure

Do NOT edit:
- orchestration/RULES.md
- orchestration/templates/*.md
- agents/*.md
- CLAUDE.md, CHANGELOG.md, README.md

## Focus
Your task is ONLY to create skills/status.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
