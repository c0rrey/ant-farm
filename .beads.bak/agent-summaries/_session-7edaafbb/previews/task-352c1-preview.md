Execute bug for ant-farm-352c.1.

Step 0: Read your task context from .beads/agent-summaries/_session-7edaafbb/prompts/task-352c1.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-352c.1` + `bd update ant-farm-352c.1 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-352c.1)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-7edaafbb/summaries/352c1.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-352c.1`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-352c.1
**Task**: Strengthen IF ROUND 1 markers from interpretive to executable
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/352c1.md

## Context
- **Affected files**:
  - orchestration/templates/reviews.md:L527-541 -- IF ROUND 1 placeholder guard block
  - orchestration/templates/reviews.md:L560-563 -- IF ROUND 1 polling loop body block
- **Root cause**: IF ROUND 1 / /IF ROUND 1 markers are bash comments interpreted by LLM (Big Head/Pantry) rather than executed by a script. If LLM fails to strip in round 2+, placeholder guard falsely flags clarity/excellence paths.
- **Expected behavior**: Conditional blocks should be processed by a script rather than relying on LLM interpretation.
- **Acceptance criteria**:
  1. Conditional blocks are executable (script-processed) rather than LLM-interpreted
  2. Round 2+ behavior is reliable regardless of LLM interpretation

## Scope Boundaries
Read ONLY:
- orchestration/templates/reviews.md:L490-580 (polling loop and placeholder guard sections)
- scripts/fill-review-slots.sh (the script that processes these templates at runtime)

Do NOT edit:
- Any review content sections (Review 1-4, L209-366)
- Big Head Consolidation Protocol narrative sections (L443-487)
- scripts/compose-review-skeletons.sh
- orchestration/RULES.md

## Focus
Your task is ONLY to strengthen IF ROUND 1 markers from interpretive comments to executable constructs.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
