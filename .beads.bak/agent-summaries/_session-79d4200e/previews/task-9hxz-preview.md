Execute bug for ant-farm-9hxz.

Step 0: Read your task context from .beads/agent-summaries/_session-79d4200e/prompts/task-9hxz.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-9hxz` + `bd update ant-farm-9hxz --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-9hxz)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-79d4200e/summaries/9hxz.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-9hxz`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-9hxz
**Task**: SETUP.md references wrong path for SESSION_PLAN_TEMPLATE.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-79d4200e/summaries/9hxz.md

## Context
- **Affected files**:
  - orchestration/SETUP.md:L42 -- "Project: SESSION_PLAN_TEMPLATE.md" (potentially wrong path)
  - orchestration/SETUP.md:L61 -- "cp orchestration/SESSION_PLAN_TEMPLATE.md ." (copy command reference)
  - orchestration/SETUP.md:L93 -- "Project: SESSION_PLAN_TEMPLATE.md" (recipe card repeat)
  - orchestration/SETUP.md:L116-121 -- Full Setup section SESSION_PLAN_TEMPLATE.md references
- **Root cause**: SETUP.md contains an incorrect file path reference for SESSION_PLAN_TEMPLATE.md. The file path(s) need to be verified against the actual location of SESSION_PLAN_TEMPLATE.md in the repository.
- **Expected behavior**: SETUP.md should reference the correct path for SESSION_PLAN_TEMPLATE.md.
- **Acceptance criteria**:
  1. SETUP.md references the correct path for SESSION_PLAN_TEMPLATE.md

## Scope Boundaries
Read ONLY: orchestration/SETUP.md:L1-200 (all SESSION_PLAN_TEMPLATE.md references), orchestration/SESSION_PLAN_TEMPLATE.md (verify actual location)
Do NOT edit: Any file other than orchestration/SETUP.md

## Focus
Your task is ONLY to fix the SESSION_PLAN_TEMPLATE.md path reference(s) in SETUP.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
