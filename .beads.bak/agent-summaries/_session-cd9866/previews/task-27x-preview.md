Execute bug for ant-farm-27x.

Step 0: Read your task context from .beads/agent-summaries/_session-cd9866/prompts/task-27x.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-27x` + `bd update ant-farm-27x --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-27x)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-cd9866/summaries/27x.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-27x`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-27x
**Task**: big-head.md includes Edit tool unnecessarily, violating least-privilege
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/27x.md

## Context
- **Affected files**: agents/big-head.md:L4 (tools list includes `Edit` alongside Read, Write, Bash, Glob, Grep)
- **Root cause**: agents/big-head.md:L4 declares `tools: Read, Write, Edit, Bash, Glob, Grep`. Big Head's role is to read reviewer reports, consolidate findings, write a consolidated summary, and file beads via `bd create` (bash). The Edit tool allows modifying existing files in-place, which Big Head should never need to do -- it reads reports (Read), writes new files (Write), runs bd commands (Bash), and searches (Glob, Grep). Including Edit violates the least-privilege principle and could allow Big Head to accidentally modify source files or review reports.
- **Expected behavior**: big-head.md only includes tools it actually needs. Edit tool removed since Big Head does not need to edit existing files in-place.
- **Acceptance criteria**:
  1. Edit tool removed from big-head.md tools list (L4)
  2. Least-privilege principle maintained (only tools Big Head actually uses are listed)

## Scope Boundaries
Read ONLY: agents/big-head.md:L1-36
Do NOT edit: orchestration/templates/big-head-skeleton.md, orchestration/templates/reviews.md, orchestration/RULES.md, any other agents/ files

## Focus
Your task is ONLY to remove the Edit tool from big-head.md's tools list.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
