Execute task for ant-farm-ha7a.9.

Step 0: Read your task context from .beads/agent-summaries/_session-50c2c6/prompts/task-ha7a.9.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-ha7a.9` + `bd update ant-farm-ha7a.9 --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-ha7a.9)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-50c2c6/summaries/ha7a.9.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-ha7a.9`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-ha7a.9
**Task**: Update pantry review mode for round-aware brief composition
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-50c2c6/summaries/ha7a.9.md

## Context
- **Affected files**: `orchestration/templates/pantry.md:L199-281` — 6 sections in review mode: Input spec (L201), Brief composition (L229), Files-to-write (L239-243), Step 4 Big Head brief (L245-254), Step 5 Previews (L257-265), Step 6 Return table (L268-281)
- **Root cause**: pantry.md's review mode describes a fixed 4-brief flow with no concept of review rounds. It must be updated to accept a round number as input and branch behavior (4 briefs round 1, 2 briefs round 2+) so that the Pantry agent correctly composes round-appropriate review packages.
- **Expected behavior**: Input spec includes "review round number (1, 2, 3, ...)". Brief composition has round-aware rules: Round 1 = 4 briefs (clarity, edge-cases, correctness, excellence); Round 2+ = 2 briefs (correctness, edge-cases only) with out-of-scope finding bar from reviews.md. Files-to-write section shows "Round 1:" (4 files) and "Round 2+:" (2 files). Step 4 mentions "Review round number", "P3 auto-filing", and "Polling loop adaptation". Step 5 mentions `{REVIEW_ROUND}` placeholder. Step 6 has "Round 1 return table:" (4 data rows) and "Round 2+ return table:" (2 data rows). Exact content specified in `docs/plans/2026-02-19-review-loop-convergence.md` Task 9.
- **Acceptance criteria**:
  1. Input spec includes "review round number (1, 2, 3, ...)"
  2. Brief composition has `**Round 1**: Compose 4 review briefs` and `**Round 2+**: Compose 2 review briefs`
  3. Files-to-write section shows "**Round 1**:" (4 files) and "**Round 2+**:" (2 files)
  4. Step 4 mentions "Review round number", "P3 auto-filing", and "**Polling loop adaptation**"
  5. Step 5 mentions `{REVIEW_ROUND}` placeholder
  6. Step 6 has "**Round 1 return table:**" (4 data rows) and "**Round 2+ return table:**" (2 data rows)

## Scope Boundaries
Read ONLY: `orchestration/templates/pantry.md:L197-289` (Section 2: Review Mode), `docs/plans/2026-02-19-review-loop-convergence.md` Task 9 (for exact replacement content), `orchestration/templates/reviews.md:L146-154` (Round 2+ Reviewer Instructions, referenced in brief composition)
Do NOT edit: Section 1 (Implementation Mode, L15-196), Section 3 (Error Handling, L283-289), or any content outside Section 2. Do not modify the term definitions or the Section 1/Section 2 separator.

## Focus
Your task is ONLY to update the 6 sections of pantry.md's review mode (Section 2) to support round-aware brief composition as specified in the implementation plan Task 9.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
