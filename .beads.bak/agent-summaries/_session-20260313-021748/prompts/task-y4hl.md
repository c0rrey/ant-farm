# Task Brief: ant-farm-y4hl
**Task**: Design and write Forager agent (definition + template + skeleton)
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-20260313-021748/summaries/y4hl.md

## Context
- **Affected files**:
  - agents/forager.md (new file) — agent definition with frontmatter
  - orchestration/templates/forager.md (new file or replacement) — workflow template for 4 parallel focus areas
  - orchestration/templates/forager-skeleton.md (new file) — prompt skeleton
- **Root cause**: N/A — new feature. Forager agent needed for parallel research across 4 focus areas.
- **Expected behavior**: Three files created: agent definition, workflow template, and prompt skeleton for the Forager agent that runs 4 parallel instances (Stack, Architecture, Pitfall, Pattern) with 100-line hard cap.
- **Acceptance criteria**:
  1. agents/forager.md exists with correct frontmatter (name, description, model: sonnet, tools list)
  2. orchestration/templates/forager.md contains workflow for all 4 focus areas with clear scope boundaries
  3. orchestration/templates/forager-skeleton.md contains prompt template with {FOCUS_AREA} placeholder
  4. Prompt includes explicit prohibitions: no cross-reading, max 100 lines, no contradicting spec decisions, no alternative recommendations
  5. Pattern Forager skip logic documented for greenfield projects
  6. Source hierarchy (official docs > web > training data) explicitly stated in prompt
  7. Each focus area has concrete examples of good/bad research output

## Scope Boundaries
Read ONLY:
- agents/ directory — to understand existing agent definition format and conventions
- orchestration/templates/ directory — to understand existing template format and conventions
- orchestration/templates/forager.md — if it exists, read current content before replacing
- orchestration/PLACEHOLDER_CONVENTIONS.md — for placeholder naming rules

Do NOT edit:
- Any existing agent definitions other than forager-related files
- Any non-forager templates (orchestration/templates/*.md)
- CLAUDE.md, CHANGELOG.md, README.md
- orchestration/RULES.md

## Focus
Your task is ONLY to create the three Forager agent files (definition, template, skeleton).
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
