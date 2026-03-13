# Task Brief: ant-farm-399a
**Task**: Design and write Surveyor agent (definition + template + skeleton)
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-20260313-021748/summaries/399a.md

## Context
- **Affected files**:
  - agents/surveyor.md (new file) — agent definition with frontmatter
  - orchestration/templates/surveyor.md (new file) — detailed workflow template
  - orchestration/templates/surveyor-skeleton.md (new file) — prompt skeleton
- **Root cause**: N/A — new feature. Surveyor agent needed for requirements gathering from freeform input.
- **Expected behavior**: Three files created: agent definition, workflow template, and prompt skeleton for the Surveyor agent that gathers requirements via AskUserQuestion, reads freeform input + existing codebase, and writes spec.md.
- **Acceptance criteria**:
  1. agents/surveyor.md exists with correct frontmatter (name, description, model: opus, tools list)
  2. orchestration/templates/surveyor.md contains detailed workflow: read input, ask questions, synthesize spec
  3. orchestration/templates/surveyor-skeleton.md contains prompt template with placeholder conventions
  4. Prompt includes explicit prohibitions: no questions with obvious answers, max 12 questions, no invented requirements, no vague criteria
  5. Output format specifies spec.md with Scope/Constraints/Requirements/Non-requirements sections
  6. Brownfield handling: reads existing codebase structure to avoid redundant questions
  7. Good/bad output examples included in the prompt

## Scope Boundaries
Read ONLY:
- agents/ directory — to understand existing agent definition format and conventions
- orchestration/templates/ directory — to understand existing template format and conventions (e.g., scout.md, pantry.md, implementation.md for structural patterns)
- orchestration/PLACEHOLDER_CONVENTIONS.md — for placeholder naming rules

Do NOT edit:
- Any existing agent definitions (agents/*.md)
- Any existing templates (orchestration/templates/*.md)
- CLAUDE.md, CHANGELOG.md, README.md
- orchestration/RULES.md

## Focus
Your task is ONLY to create the three Surveyor agent files (definition, template, skeleton).
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
