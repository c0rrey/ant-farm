# Task Brief: ant-farm-z3j
**Task**: Checkpoint thresholds undefined: small file, sampling N<3, CCB bd list unbounded
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/z3j.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L121-128 -- CCO WARN verdict uses "small file" without a concrete line-count threshold in the WARN definition block (L87 and L123 mention <100 lines but the threshold is inconsistently stated)
  - orchestration/templates/checkpoints.md:L76,L424-437 -- DMVDC sampling formula `max(3, min(5, ceil(N/3)))` returns 3 when N=1 or N=2 (more samples than findings exist); the plain-English guard at L426 says "verify all of them" but the formula itself has no min(N,...) guard
  - orchestration/templates/checkpoints.md:L572 -- CCB Check 7 runs `bd list --status=open` with no date scope or limit, pulling every open bead in the database rather than only session-relevant ones
- **Root cause**: checkpoints.md uses three undefined or broken thresholds: (1) CCO Check 7 uses "small file" without defining a concrete line count in the verdict threshold section. (2) DMVDC sampling formula `max(3, min(5, ceil(N/3)))` returns 3 when N=1 or N=2, requesting more samples than findings exist; there is a plain-English caveat at L426 but the formula lacks a min(N,...) wrapper. (3) CCB Check 7 runs `bd list --status=open` with no limit or date scope, pulling the entire open-bead set instead of session-relevant beads only.
- **Expected behavior**: All three thresholds explicitly defined with concrete values: "small file" gets a numeric threshold, the sampling formula gets a min(N,...) guard, and the CCB bead list gets scoped to the session start date.
- **Acceptance criteria**:
  1. Define "small file" = fewer than 100 lines at every usage site in checkpoints.md (L87, L121-128, L158, L163)
  2. Fix sampling formula to `min(N, max(3, min(5, ceil(N/3))))` at L76 and L424, and update the worked-examples table at L430-437 to reflect the corrected formula (N=1 yields 1, N=2 yields 2)
  3. Scope CCB Check 7 bead list at L572 to session-start date (e.g., `bd list --status=open --after=<session-start-date>` or equivalent)

## Scope Boundaries
Read ONLY:
- orchestration/templates/checkpoints.md (full file -- all three fixes are in this single file)

Do NOT edit:
- orchestration/templates/implementation.md
- orchestration/templates/pantry.md
- orchestration/templates/reviews.md
- orchestration/templates/dirt-pusher-skeleton.md
- orchestration/RULES.md
- Any file outside orchestration/templates/checkpoints.md

## Focus
Your task is ONLY to fix the three undefined/broken thresholds in checkpoints.md:
1. Define "small file" with a concrete numeric threshold at all usage sites.
2. Add a min(N,...) guard to the DMVDC sampling formula and update the worked-examples table.
3. Scope the CCB Check 7 bead-list command to session-start date.

Do NOT fix adjacent issues you notice. Document them in your summary doc under "Adjacent Issues Found" instead.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
