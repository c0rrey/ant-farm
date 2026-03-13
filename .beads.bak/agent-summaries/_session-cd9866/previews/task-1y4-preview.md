Execute bug for ant-farm-1y4.

Step 0: Read your task context from .beads/agent-summaries/_session-cd9866/prompts/task-1y4.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-1y4` + `bd update ant-farm-1y4 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-1y4)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-cd9866/summaries/1y4.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-1y4`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-1y4
**Task**: SETUP.md hardcoded personal path ~/projects/hs_website/ blocks new adopters
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/1y4.md

## Context
- **Affected files**: orchestration/SETUP.md:L61,121 (originally reported as `cp ~/projects/hs_website/SESSION_PLAN_TEMPLATE.md .` but now reads `cp orchestration/SESSION_PLAN_TEMPLATE.md .`)
- **Root cause**: The bead reports that orchestration/SETUP.md:L61 and L121 contain hardcoded personal path `~/projects/hs_website/`. However, current inspection shows these lines have already been changed to `cp orchestration/SESSION_PLAN_TEMPLATE.md .`. The agent must verify whether (1) the fix is complete and this task can be closed as already-fixed, or (2) there are other residual personal path references elsewhere in SETUP.md or related files that the bead's title describes. The agent should search the entire file for any remaining personal machine paths (e.g., `/Users/`, `~/projects/`, hardcoded usernames).
- **Expected behavior**: Step is executable by a new adopter with no personal machine paths in documentation.
- **Acceptance criteria**:
  1. No personal machine paths remain in SETUP.md (e.g., ~/projects/hs_website/, /Users/username/, or other hardcoded personal paths)
  2. Step is executable by a new adopter without modification

## Scope Boundaries
Read ONLY: orchestration/SETUP.md:L1-269
Do NOT edit: docs/installation-guide.md, README.md, orchestration/RULES.md, any scripts/ files

## Focus
Your task is ONLY to verify and remove any remaining personal machine paths from SETUP.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
