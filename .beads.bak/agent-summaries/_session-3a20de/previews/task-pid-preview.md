Execute task for ant-farm-pid.

Step 0: Read your task context from .beads/agent-summaries/_session-3a20de/prompts/task-pid.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-pid` + `bd update ant-farm-pid --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-pid)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-3a20de/summaries/pid.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-pid`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-pid
**Task**: AGG-038: Clarify wildcard artifact path matching in reviews.md transition gate
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/pid.md

## Context
- **Affected files**:
  - orchestration/templates/reviews.md:L4-17 -- Transition Gate Checklist section
  - orchestration/templates/reviews.md:L11 -- DMVDC artifact verification using wildcard * for timestamp portion
  - NOTE: Scout metadata had bare filename (no line numbers). Lines identified by Pantry via content analysis.
- **Root cause**: reviews.md specifies verifying artifacts with wildcard * for the timestamp portion. Multiple files could match due to retries, and the instruction does not specify which to check.
- **Expected behavior**: Clarified: Verify at least one DMVDC artifact exists with PASS verdict. If multiple exist, the most recent by timestamp must show PASS.
- **Acceptance criteria**:
  1. reviews.md transition gate specifies which artifact to check when multiple match the wildcard
  2. The most-recent-by-timestamp rule is documented for retry scenarios
  3. The PASS verdict requirement is explicit (not just file existence)

## Scope Boundaries
Read ONLY: orchestration/templates/reviews.md:L1-28 (Transition Gate Checklist and Pre-Spawn Directory Setup sections)
Do NOT edit: Agent Teams Protocol (L30+), Review type sections (L215+), Nitpicker Report Format (L374+), Big Head Consolidation Protocol (L449+), Queen's Checklists (L767+)

## Focus
Your task is ONLY to clarify wildcard artifact path matching in the transition gate checklist.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
