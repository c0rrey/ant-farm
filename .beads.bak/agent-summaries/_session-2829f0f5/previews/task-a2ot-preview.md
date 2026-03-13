Execute bug for ant-farm-a2ot.

Step 0: Read your task context from .beads/agent-summaries/_session-2829f0f5/prompts/task-a2ot.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-a2ot` + `bd update ant-farm-a2ot --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-a2ot)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-2829f0f5/summaries/a2ot.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-a2ot`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

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
