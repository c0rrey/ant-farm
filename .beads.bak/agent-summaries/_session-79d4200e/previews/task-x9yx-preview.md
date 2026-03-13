Execute bug for ant-farm-x9yx.

Step 0: Read your task context from .beads/agent-summaries/_session-79d4200e/prompts/task-x9yx.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-x9yx` + `bd update ant-farm-x9yx --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-x9yx)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-79d4200e/summaries/x9yx.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-x9yx`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-x9yx
**Task**: fix: SSV checkpoint missing from RULES.md Model Assignments table
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-79d4200e/summaries/x9yx.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L297 -- insert SSV row in Model Assignments table
- **Root cause**: When SSV was added as a checkpoint, it was documented inline in Step 1b but the Model Assignments table was not updated.
- **Expected behavior**: Model Assignments table should include PC -- SSV row with model haiku.
- **Acceptance criteria**:
  1. Model Assignments table includes PC -- SSV row with model haiku
  2. All 5 PC checkpoint types (SSV, CCO, WWD, DMVDC, CCB) have table entries
  3. Table row note matches checkpoints.md:L612 rationale

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L303-320 (Model Assignments table), orchestration/templates/checkpoints.md:L606-613 (SSV rationale)
Do NOT edit: Any other section of RULES.md, any other file besides RULES.md

## Focus
Your task is ONLY to add the missing SSV row to the RULES.md Model Assignments table.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
