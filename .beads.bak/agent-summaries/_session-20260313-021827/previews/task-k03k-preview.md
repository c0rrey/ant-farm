Execute task for ant-farm-k03k.

Step 0: Read your task context from .beads/agent-summaries/_session-20260313-021827/prompts/task-k03k.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-k03k` + `bd update ant-farm-k03k --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-k03k)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-20260313-021827/summaries/k03k.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-k03k`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-k03k
**Task**: Migrate reference and setup documentation (mechanical)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/k03k.md

## Context
- **Affected files**:
  - orchestration/reference/dependency-analysis.md:L59-60,L195 — bd show, bd blocked references
  - orchestration/SETUP.md:L87,L93,L226 — bd create, bd show references
- **Root cause**: Reference and setup documentation contain bd references needing mechanical substitution.
- **Expected behavior**: All bd references replaced with crumb equivalents; .beads/ paths updated to .crumbs/.
- **Acceptance criteria**:
  1. dependency-analysis.md: 4 bd references replaced with crumb equivalents (L59, L60, L195, plus any others found)
  2. SETUP.md: 3 bd references replaced with crumb equivalents (L87, L93, L226)
  3. grep -c '\bbd\b' on both files returns 0
  4. .beads/ paths updated to .crumbs/ where present

## Scope Boundaries
Read ONLY: orchestration/reference/dependency-analysis.md (full file), orchestration/SETUP.md (full file)
Do NOT edit: Any other reference files, RULES.md, templates/, or any file outside these two

## Focus
Your task is ONLY to replace bd command references with crumb equivalents and .beads/ paths with .crumbs/ in dependency-analysis.md and SETUP.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
