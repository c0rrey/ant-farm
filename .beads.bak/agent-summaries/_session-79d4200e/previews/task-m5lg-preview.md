Execute bug for ant-farm-m5lg.

Step 0: Read your task context from .beads/agent-summaries/_session-79d4200e/prompts/task-m5lg.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-m5lg` + `bd update ant-farm-m5lg --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-m5lg)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-79d4200e/summaries/m5lg.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-m5lg`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-m5lg
**Task**: fix: review-skeletons/ and review-reports/ missing from Step 0 session directory setup
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-79d4200e/summaries/m5lg.md

## Context
- **Affected files**:
  - orchestration/RULES.md (after L336) -- add note about review-skeletons/ and review-reports/ lazy creation
- **Root cause**: review-skeletons/ and review-reports/ directories were introduced after the original Step 0 setup. They are created lazily but the Session Directory section gives no hint they will exist.
- **Expected behavior**: RULES.md Session Directory section should document all 7 subdirectories including the lazily-created review dirs.
- **Acceptance criteria**:
  1. RULES.md Session Directory section documents all 7 subdirectories that appear in practice
  2. Note clarifies lazy creation (review dirs created by their respective phases, not at Step 0)
  3. Crash recovery documentation accounts for directories that may not yet exist

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L330-370 (Session Directory section and crash recovery)
Do NOT edit: Any section of RULES.md outside Session Directory, any other file

## Focus
Your task is ONLY to document the review-skeletons/ and review-reports/ lazy-created directories in the RULES.md Session Directory section.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
