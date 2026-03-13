# Task Brief: ant-farm-mmo3
**Task**: Migrate agent definitions (mechanical)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/mmo3.md

## Context
- **Affected files**:
  - ~/.claude/agents/scout-organizer.md:L3,L25,L33,L35 — bd command references in description and tool descriptions
  - ~/.claude/agents/nitpicker.md:L107,L124,L172 — bd show references in review instructions
- **Root cause**: Agent definition files contain bd command references needing mechanical substitution.
- **Expected behavior**: All bd command references replaced with crumb equivalents; agent descriptions remain functionally correct.
- **Acceptance criteria**:
  1. agents/scout-organizer.md: all bd command references replaced with crumb equivalents (L3, L25, L33, L35)
  2. agents/nitpicker.md: all 3 bd references replaced with crumb equivalents (L107, L124, L172)
  3. grep -c '\bbd\b' on both files returns 0
  4. Agent descriptions and tool references remain functionally correct after substitution

## Scope Boundaries
Read ONLY: ~/.claude/agents/scout-organizer.md (full file), ~/.claude/agents/nitpicker.md (full file)
Do NOT edit: Any other agent files, orchestration templates, or any file outside these two

## Focus
Your task is ONLY to replace bd command references with crumb equivalents in scout-organizer.md and nitpicker.md agent definitions.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
