Execute bug for ant-farm-auas.

Step 0: Read your task context from .beads/agent-summaries/_session-cd9866/prompts/task-auas.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-auas` + `bd update ant-farm-auas --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-auas)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-cd9866/summaries/auas.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-auas`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-auas
**Task**: Missing input validation guards on Queen-owned review path (REVIEW_ROUND, CHANGED_FILES, TASK_IDS)
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/auas.md

## Context
- **Affected files**: orchestration/RULES.md:L280-298 (Queen review path logic, no validation of review inputs before passing to subagents), orchestration/templates/pantry.md:L260-286 (receives REVIEW_ROUND, CHANGED_FILES, TASK_IDS from Queen but no validation on receipt), orchestration/templates/checkpoints.md:L198 (references {REVIEW_ROUND} without validation), orchestration/templates/nitpicker-skeleton.md:L13,21 (receives {REVIEW_ROUND} without validation), orchestration/templates/big-head-skeleton.md:L13,69 (receives {REVIEW_ROUND} without validation)
- **Root cause**: The Queen passes REVIEW_ROUND, CHANGED_FILES, and TASK_IDS to various subagents in the review path, but none of these variables are validated before use. If REVIEW_ROUND is missing, non-numeric, or zero, downstream templates will produce malformed prompts. If CHANGED_FILES is empty, reviews will have nothing to review. If TASK_IDS is empty, the correctness reviewer cannot verify acceptance criteria.
- **Expected behavior**: All Queen-owned review path variables are validated before being passed to subagents, with actionable error messages for missing or malformed values.
- **Acceptance criteria**:
  1. REVIEW_ROUND, CHANGED_FILES, and TASK_IDS are validated before use (type checks, non-empty checks)
  2. Missing or malformed values produce actionable error messages identifying the specific variable and expected format

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L270-310, orchestration/templates/pantry.md:L251-290, orchestration/templates/checkpoints.md:L190-205, orchestration/templates/nitpicker-skeleton.md:L1-43, orchestration/templates/big-head-skeleton.md:L1-105
Do NOT edit: orchestration/templates/reviews.md, orchestration/templates/implementation.md, any scripts/ files, agents/ files

## Focus
Your task is ONLY to add input validation guards for REVIEW_ROUND, CHANGED_FILES, and TASK_IDS on the Queen-owned review path.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
