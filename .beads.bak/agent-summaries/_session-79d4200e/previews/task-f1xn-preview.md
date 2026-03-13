Execute bug for ant-farm-f1xn.

Step 0: Read your task context from .beads/agent-summaries/_session-79d4200e/prompts/task-f1xn.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-f1xn` + `bd update ant-farm-f1xn --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-f1xn)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-79d4200e/summaries/f1xn.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-f1xn`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-f1xn
**Task**: fix: CLAUDE.md Landing the Plane annotation says Step 6 but content spans Steps 4-6 with gaps
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-79d4200e/summaries/f1xn.md

## Context
- **Affected files**:
  - CLAUDE.md:L54 -- annotation says "Step 6" but spans Steps 4-6
  - CLAUDE.md (Landing the Plane section, L52-75) -- missing documentation commit and cross-reference verification steps
  - orchestration/RULES.md (Steps 4-6) -- missing quality gates, issue management, git status verification
- **Root cause**: CLAUDE.md and RULES.md evolved independently. CLAUDE.md was extended with operational steps that RULES.md does not cover, while RULES.md has documentation and verification steps that CLAUDE.md does not include.
- **Expected behavior**: Both files should cover the same complete set of landing steps with correct cross-references.
- **Acceptance criteria**:
  1. CLAUDE.md annotation correctly references Steps 4-6
  2. Both files cover the same complete set of landing steps
  3. No step present in one file is absent from the other
  4. git status verification appears in both files

## Scope Boundaries
Read ONLY: CLAUDE.md:L50-75 (Landing the Plane section), orchestration/RULES.md Steps 4-6
Do NOT edit: Any section of CLAUDE.md outside Landing the Plane, any section of RULES.md outside Steps 4-6, any other file

## Focus
Your task is ONLY to synchronize the Landing the Plane steps between CLAUDE.md and RULES.md so both cover the same complete set of steps.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
