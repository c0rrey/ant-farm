# Task Brief: ant-farm-hlv6
**Task**: Create decomposition orchestration template
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-20260313-021748/summaries/hlv6.md

## Context
- **Affected files**: orchestration/templates/decomposition.md (new file, shared with ant-farm-xtu9)
- **Root cause**: N/A — new feature. Decomposition orchestration template needed for Architect workflow.
- **Expected behavior**: orchestration/templates/decomposition.md contains the Architect's complete workflow orchestration template with crumb CLI examples and decomposition brief output template.
- **Acceptance criteria**:
  1. orchestration/templates/decomposition.md exists with clear step-by-step workflow
  2. Input reading order defined: spec.md first, then research briefs, then codebase structure
  3. crumb trail create and crumb create --from-json command examples with full JSON payloads
  4. blocked_by wiring guidance: when to add dependencies, how to detect data/API dependencies
  5. scope.files and scope.agent_type assignment guidance with examples
  6. decomposition-brief.md output template included

## Scope Boundaries
Read ONLY: orchestration/templates/ directory for context on existing template patterns
Do NOT edit: Any existing templates (implementation.md, pantry.md, reviews.md, etc.), RULES.md, CLAUDE.md, CHANGELOG.md

## Focus
Your task is ONLY to create orchestration/templates/decomposition.md with the Architect's decomposition workflow template.
Do NOT fix adjacent issues you notice.

NOTE: This file is shared with ant-farm-xtu9 (which creates the initial file). This task adds the orchestration template content. If xtu9 has already created the file, build on its content. If not, create the file from scratch.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
