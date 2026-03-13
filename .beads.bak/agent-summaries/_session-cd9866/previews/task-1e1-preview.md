Execute bug for ant-farm-1e1.

Step 0: Read your task context from .beads/agent-summaries/_session-cd9866/prompts/task-1e1.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-1e1` + `bd update ant-farm-1e1 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-1e1)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-cd9866/summaries/1e1.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-1e1`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-1e1
**Task**: Incomplete 'data file' to 'task brief' rename from ant-farm-0o4
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/1e1.md

## Context
- **Affected files**: orchestration/templates/dirt-pusher-skeleton.md:L43 (still says 'see data file for section list'), orchestration/templates/big-head-skeleton.md:L20 (still says 'Big Head consolidation data file'), README.md:L18,45,59,60,61,72,92,101,174,176,226 (multiple occurrences still use 'data file' for Pantry output)
- **Root cause**: Task ant-farm-0o4 required renaming Pantry output from 'data file' to 'task brief' across all files. The rename was applied to pantry.md but missed three other files: (1) dirt-pusher-skeleton.md:L43 says 'see data file for section list' -- should be 'see task brief for section list'. (2) big-head-skeleton.md:L20 says 'Big Head consolidation data file' -- should be 'Big Head consolidation brief'. (3) README.md has multiple occurrences (~8-11) still using 'data file' when referring to Pantry output.
- **Expected behavior**: No 'data file' references to Pantry output remain. Use 'task brief' for dirt-pusher context and README references, 'consolidation brief' for big-head-skeleton.
- **Acceptance criteria**:
  1. No 'data file' references to Pantry output remain in dirt-pusher-skeleton.md, big-head-skeleton.md, or README.md
  2. ant-farm-0o4 AC#3 fully met (all Pantry output references use 'task brief' or 'consolidation brief' as appropriate)

## Scope Boundaries
Read ONLY: orchestration/templates/dirt-pusher-skeleton.md:L1-48, orchestration/templates/big-head-skeleton.md:L1-105, README.md:L1-230
Do NOT edit: orchestration/templates/pantry.md (already renamed), orchestration/templates/reviews.md, orchestration/RULES.md, any scripts/ files

## Focus
Your task is ONLY to rename remaining 'data file' references to 'task brief' (dirt-pusher, README) or 'consolidation brief' (big-head-skeleton).
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
