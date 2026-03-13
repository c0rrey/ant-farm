Execute task for ant-farm-ha7a.8.

Step 0: Read your task context from .beads/agent-summaries/_session-50c2c6/prompts/task-ha7a.8.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-ha7a.8` + `bd update ant-farm-ha7a.8 --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-ha7a.8)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-50c2c6/summaries/ha7a.8.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-ha7a.8`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-ha7a.8
**Task**: Add round-aware scope instructions to nitpicker-skeleton
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-50c2c6/summaries/ha7a.8.md

## Context
- **Affected files**: orchestration/templates/nitpicker-skeleton.md:L8-L11 (placeholder list -- add `{REVIEW_ROUND}` after last existing placeholder), orchestration/templates/nitpicker-skeleton.md:L17 (agent-facing template -- update "Perform a {REVIEW_TYPE} review" line with round-aware scope instructions)
- **Root cause**: The nitpicker-skeleton has no `{REVIEW_ROUND}` placeholder, so the Pantry agent cannot inject round information into reviewer prompts. Round 2+ reviewers need scope constraints limiting them to fix commits only.
- **Expected behavior**: `{REVIEW_ROUND}` is added to the placeholder list after the last existing placeholder (L11). In the agent-facing template, the "Perform a {REVIEW_TYPE} review" line (L17) is kept, `**Review round**: {REVIEW_ROUND}` is added after it, and round 2+ scope instructions follow (scope limited to fix commits only, out-of-scope findings only for runtime failures or silently wrong results). Exact content in docs/plans/2026-02-19-review-loop-convergence.md Task 8.
- **Acceptance criteria**:
  1. `grep "REVIEW_ROUND" orchestration/templates/nitpicker-skeleton.md` returns matches in both the placeholder list and the agent template
  2. Placeholder entry reads `{REVIEW_ROUND}: 1, 2, 3, ... (determines scope instructions; filled by Pantry)`
  3. Agent template contains `**Review round**: {REVIEW_ROUND}` after the "Perform a {REVIEW_TYPE} review" line
  4. Round 2+ scope text mentions "fix commits only", "runtime failure", and "silently wrong results"

## Scope Boundaries
Read ONLY: orchestration/templates/nitpicker-skeleton.md:L1-L38 (entire file), docs/plans/2026-02-19-review-loop-convergence.md:L585-L614 (Task 8 specification)
Do NOT edit: orchestration/templates/nitpicker-skeleton.md:L1-L7 (header and instructions block before placeholders), orchestration/templates/nitpicker-skeleton.md:L19-L38 (workflow steps and report sections below the insertion point -- keep them intact), any file other than orchestration/templates/nitpicker-skeleton.md

## Focus
Your task is ONLY to add the REVIEW_ROUND placeholder and round-aware scope instructions to the nitpicker-skeleton template.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
