Execute task for ant-farm-vjhe.

Step 0: Read your task context from .beads/agent-summaries/_session-20260313-021827/prompts/task-vjhe.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-vjhe` + `bd update ant-farm-vjhe --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-vjhe)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-20260313-021827/summaries/vjhe.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-vjhe`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-vjhe
**Task**: Migrate project documentation (mechanical)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/vjhe.md

## Context
- **Affected files**:
  - README.md:L29,L78-79,L128,L249,L322-336 — bd references, beads terminology, .beads/ paths
  - AGENTS.md:L3,L8-12,L28 — bd references in quick reference section
  - CONTRIBUTING.md:L132 — bd create reference
  - docs/installation-guide.md:L41 — bd sync reference, .beads/ path
- **Root cause**: Project documentation contains bd references and beads terminology needing mechanical substitution.
- **Expected behavior**: All bd references replaced; beads -> crumbs terminology; .beads/ -> .crumbs/ paths; installation instructions updated.
- **Acceptance criteria**:
  1. README.md: all 10+ bd references replaced, beads -> crumbs terminology, .beads/ -> .crumbs/ paths
  2. AGENTS.md: all 7 bd references replaced with crumb equivalents
  3. CONTRIBUTING.md: bd reference replaced with crumb equivalent
  4. docs/installation-guide.md: bd reference replaced with crumb equivalent
  5. grep -rl '\bbd\b' across all four files returns 0
  6. No broken links or references to removed Beads/Dolt tools

## Scope Boundaries
Read ONLY: README.md (full file), AGENTS.md (full file), CONTRIBUTING.md (full file), docs/installation-guide.md (full file)
Do NOT edit: CLAUDE.md, orchestration/, scripts/, or any file outside these four

## Focus
Your task is ONLY to replace bd command references with crumb equivalents, beads terminology with crumbs, and .beads/ paths with .crumbs/ in the four project documentation files.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
