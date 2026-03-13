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
