Execute task for ant-farm-ha7a.4.

Step 0: Read your task context from .beads/agent-summaries/_session-50c2c6/prompts/task-ha7a.4.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-ha7a.4` + `bd update ant-farm-ha7a.4 --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-ha7a.4)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-50c2c6/summaries/ha7a.4.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-ha7a.4`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-ha7a.4
**Task**: Add P3 auto-filing, termination check, and mandatory re-review to reviews.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-50c2c6/summaries/ha7a.4.md

## Context
- **Affected files**: `orchestration/templates/reviews.md:L475-688` -- Big Head consolidation block and Queen's Step 3c/4 sections; adds P3 Auto-Filing section, Termination Check subsection, changes "optional" to "MANDATORY", and adds Round 1 only blockquote
- **Root cause**: The review loop has no termination condition and no automatic P3 filing for round 2+. Round 2+ P3 findings need to be auto-filed without user involvement, and the loop needs a termination check (zero P1/P2 = done). Also, re-running reviews after fixes is currently "optional" but must be mandatory.
- **Expected behavior**:
  - `### P3 Auto-Filing (Round 2+ Only)` section exists after the bead filing block, contains `bd epic create` and `bd dep add ... --type parent-child`
  - `### Termination Check (zero P1/P2 findings)` subsection exists in Queen's Step 3c, positioned before `### If P1 or P2 issues found:`
  - "Re-run reviews" changed from "(optional)" to "(MANDATORY)"
  - `### Handle P3 Issues (Queen's Step 4)` is followed immediately by `> **Round 1 only.**` blockquote
- **Acceptance criteria**:
  1. `grep "### P3 Auto-Filing (Round 2+ Only)" orchestration/templates/reviews.md` returns a match
  2. P3 Auto-Filing section contains both `bd epic create` and `bd dep add` with `--type parent-child`
  3. `grep "### Termination Check" orchestration/templates/reviews.md` returns a match, positioned before `### If P1 or P2 issues found:`
  4. `grep "Re-run reviews.*MANDATORY" orchestration/templates/reviews.md` returns a match (not "optional")
  5. `### Handle P3 Issues (Queen's Step 4)` is followed immediately by a `> **Round 1 only.**` blockquote

## Scope Boundaries
Read ONLY: `orchestration/templates/reviews.md:L475-755` (Big Head consolidation bead filing through Handle P3 Issues section), `docs/plans/2026-02-19-review-loop-convergence.md:L300-383` (Task 4 section of the implementation plan)
Do NOT edit: Any file other than `orchestration/templates/reviews.md`. Do NOT edit Step 0, Step 0a, or Step 3 of the Big Head Consolidation Protocol (those are task ha7a.3). Do NOT edit the review type definitions (Review 1-4), Team Setup, or Round-Aware Review Protocol sections. Do NOT edit the Nitpicker Checklist or Big Head Consolidation Checklist.

## Focus
Your task is ONLY to add P3 auto-filing, termination check, and mandatory re-review to reviews.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
