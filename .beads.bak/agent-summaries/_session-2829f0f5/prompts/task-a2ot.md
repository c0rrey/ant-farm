# Task Brief: ant-farm-a2ot
**Task**: fix: CONTRIBUTING.md cross-file update checklist omits GLOSSARY.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2829f0f5/summaries/a2ot.md

## Context
- **Affected files**:
  - CONTRIBUTING.md:L37-41 -- cross-file update checklist
- **Root cause**: CONTRIBUTING.md lists files to update when adding an agent (README.md, RULES.md, scout.md) but omits GLOSSARY.md which contains an "Ant Metaphor Roles" table (lines 77-85) listing all agents.
- **Expected behavior**: CONTRIBUTING.md checklist includes GLOSSARY.md Ant Metaphor Roles table.
- **Acceptance criteria**:
  1. CONTRIBUTING.md checklist includes GLOSSARY.md Ant Metaphor Roles table

## Scope Boundaries
Read ONLY: CONTRIBUTING.md:L30-50, GLOSSARY.md:L70-90 (reference only, to confirm table exists)
Do NOT edit: GLOSSARY.md or any file other than CONTRIBUTING.md.

## Focus
Your task is ONLY to add GLOSSARY.md to the cross-file update checklist in CONTRIBUTING.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
