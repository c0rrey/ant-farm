# Task Brief: ant-farm-a5lq
**Task**: Write /ant-farm:plan skill definition
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-20260313-021748/summaries/a5lq.md

## Context
- **Affected files**:
  - skills/plan.md (new file) — skill definition for /ant-farm:plan slash command
- **Root cause**: N/A — new feature. /ant-farm:plan slash command needed to trigger decomposition workflow.
- **Expected behavior**: skills/plan.md exists with skill frontmatter, accepts spec path or inline text, classifies input, routes to RULES-decompose.md.
- **Acceptance criteria**:
  1. skills/plan.md exists with correct skill frontmatter and trigger pattern
  2. Accepts file path argument (reads file contents) or inline text
  3. Input classification heuristic documented (structured vs freeform detection)
  4. Routes to RULES-decompose.md workflow
  5. Creates DECOMPOSE_DIR with timestamp-based naming
  6. Error handling: missing file path, empty input, .crumbs/ not initialized

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
Your task is ONLY to create skills/plan.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
