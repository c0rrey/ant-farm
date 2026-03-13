Execute bug for ant-farm-bi3.

Step 0: Read your task context from .beads/agent-summaries/_session-cd9866/prompts/task-bi3.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-bi3` + `bd update ant-farm-bi3 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-bi3)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-cd9866/summaries/bi3.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-bi3`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-bi3
**Task**: Pantry template lacks fail-fast for missing task-metadata dir and empty file list
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/bi3.md

## Context
- **Affected files**: orchestration/templates/pantry.md:L44 (Step 2 reads task-metadata files without dir existence check), orchestration/templates/pantry.md:L251-286 (Section 2 review mode receives file list without empty guard), orchestration/templates/pantry.md:L37 (uses ambiguous 'Read this file' instead of explicit filename)
- **Root cause**: orchestration/templates/pantry.md has two fail-fast gaps: (1) Step 2 (implementation mode) reads task-metadata/{TASK_SUFFIX}.md but does not check if the task-metadata/ directory itself exists before iterating. (2) Section 2 (review mode) receives a changed-file list from the Queen but has no guard against an empty list (the guard at L275-286 exists but AC requires verification it covers all entry points). Additionally, the phrase 'Read this file' at L37 is ambiguous and should use the explicit filename.
- **Expected behavior**: Missing task-metadata/ produces actionable error. Empty file list produces immediate failure. 'Read this file' replaced with explicit file name reference.
- **Acceptance criteria**:
  1. Missing task-metadata/ directory produces an actionable error message before any per-task iteration
  2. Empty file list in Section 2 produces immediate failure with descriptive message
  3. 'Read this file' at L37 replaced with explicit file name reference (e.g., 'Read `~/.claude/orchestration/templates/implementation.md`')
  4. Introduce {REVIEW_TIMESTAMP} placeholder or equivalent for timestamp consistency

## Scope Boundaries
Read ONLY: orchestration/templates/pantry.md:L1-557
Do NOT edit: orchestration/RULES.md, orchestration/templates/implementation.md, orchestration/templates/reviews.md, any scripts/ files

## Focus
Your task is ONLY to add fail-fast guards for missing task-metadata directory and empty file list, replace ambiguous 'Read this file' with explicit filename, and introduce a REVIEW_TIMESTAMP placeholder.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
