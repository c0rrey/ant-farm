Execute task for ant-farm-ha7a.1.

Step 0: Read your task context from .beads/agent-summaries/_session-50c2c6/prompts/task-ha7a.1.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-ha7a.1` + `bd update ant-farm-ha7a.1 --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-ha7a.1)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-50c2c6/summaries/ha7a.1.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-ha7a.1`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-ha7a.1
**Task**: Add review round counter to queen-state template
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-50c2c6/summaries/ha7a.1.md

## Context
- **Affected files**: orchestration/templates/queen-state.md:L23-L37 (between `## Pest Control` table ending and `## Queue Position` section)
- **Root cause**: The queen-state template has no field to track which review round is active, so the Queen has no persistent state to distinguish round 1 (full review) from round 2+ (fix verification).
- **Expected behavior**: A `## Review Rounds` section with 4 placeholder fields (current round, round 1 commit range, fix commit range, termination status) is inserted between `## Pest Control` (table ends around L31) and `## Queue Position` (L33). Exact markdown content is specified in docs/plans/2026-02-19-review-loop-convergence.md Task 1 Step 1.
- **Acceptance criteria**:
  1. `grep "## Review Rounds" orchestration/templates/queen-state.md` returns a match
  2. The section appears between `## Pest Control` and `## Queue Position` -- verify section order: Pest Control then Review Rounds then Queue Position
  3. The template includes all 4 placeholder fields: "Current round", "Round 1 commit range", "Fix commit range", "Termination"
  4. Existing `## Pest Control` and `## Queue Position` sections remain intact and unmodified

## Scope Boundaries
Read ONLY: orchestration/templates/queen-state.md:L1-L41 (entire file), docs/plans/2026-02-19-review-loop-convergence.md:L23-L49 (Task 1 specification)
Do NOT edit: orchestration/templates/queen-state.md:L1-L31 (everything before the insertion point), orchestration/templates/queen-state.md:L33-L41 (Queue Position through end), any file other than orchestration/templates/queen-state.md

## Focus
Your task is ONLY to insert the Review Rounds section into the queen-state template between Pest Control and Queue Position.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
