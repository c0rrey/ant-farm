Execute task for ant-farm-6d3f.

Step 0: Read your task context from .beads/agent-summaries/_session-20260313-021827/prompts/task-6d3f.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-6d3f` + `bd update ant-farm-6d3f --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-6d3f)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-20260313-021827/summaries/6d3f.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-6d3f`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-6d3f
**Task**: Migrate build-review-prompts.sh (semantic)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/6d3f.md

## Context
- **Affected files**:
  - scripts/build-review-prompts.sh:L247 — bd show reference in echo statement
- **Root cause**: Shell script contains bd command references requiring semantic migration to crumb equivalents.
- **Expected behavior**: bd show replaced with crumb show; .beads/ session paths updated; script remains executable and functional.
- **Acceptance criteria**:
  1. bd show reference replaced with crumb show (L247)
  2. Any .beads/ session path references updated to .crumbs/
  3. grep -c '\bbd\b' scripts/build-review-prompts.sh returns 0
  4. Script remains executable and functional (bash -n syntax check passes)

## Scope Boundaries
Read ONLY: scripts/build-review-prompts.sh (full file)
Do NOT edit: Any other scripts, orchestration templates, or any file outside this one

## Focus
Your task is ONLY to replace bd command references with crumb equivalents and .beads/ paths with .crumbs/ in build-review-prompts.sh.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
