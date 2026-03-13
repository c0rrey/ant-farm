Execute bug for ant-farm-a87o.

Step 0: Read your task context from .beads/agent-summaries/_session-79d4200e/prompts/task-a87o.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-a87o` + `bd update ant-farm-a87o --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-a87o)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-79d4200e/summaries/a87o.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-a87o`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-a87o
**Task**: fix: CCO artifact naming uses session-wide format in practice but checkpoints.md specifies per-task
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-79d4200e/summaries/a87o.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L179 -- CCO naming convention (per-task format)
  - orchestration/templates/checkpoints.md:L28 -- example naming
- **Root cause**: CCO specification assumed one CCO run per task. In practice, Queen batches all wave prompts into a single CCO audit producing session-scoped artifacts (pc-session-cco-{timestamp}.md) rather than per-task artifacts.
- **Expected behavior**: checkpoints.md should document both per-task and session-wide CCO naming patterns.
- **Acceptance criteria**:
  1. checkpoints.md documents both per-task and session-wide CCO naming patterns
  2. Example on L28 reflects actual practice
  3. Naming convention matches actual artifacts in recent sessions

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md:L20-35 (naming conventions), orchestration/templates/checkpoints.md:L170-185 (CCO naming section)
Do NOT edit: Any other section of checkpoints.md, any other file

## Focus
Your task is ONLY to update CCO artifact naming documentation to cover both per-task and session-wide patterns.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
