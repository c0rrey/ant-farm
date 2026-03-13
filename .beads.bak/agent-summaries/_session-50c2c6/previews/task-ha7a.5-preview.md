Execute task for ant-farm-ha7a.5.

Step 0: Read your task context from .beads/agent-summaries/_session-50c2c6/prompts/task-ha7a.5.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-ha7a.5` + `bd update ant-farm-ha7a.5 --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-ha7a.5)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-50c2c6/summaries/ha7a.5.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-ha7a.5`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-ha7a.5
**Task**: Update review checklists for round-aware team composition
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-50c2c6/summaries/ha7a.5.md

## Context
- **Affected files**: `orchestration/templates/reviews.md:L703-725` — both operational checklists: Nitpicker Checklist and Big Head Consolidation Checklist
- **Root cause**: The Nitpicker Checklist and Big Head Consolidation Checklist in reviews.md were written for a single-round review flow and do not include round-aware checks. They need to be updated so orchestrators can verify round-dependent behavior (team size, prompt count, out-of-scope bar, P3 auto-filing) at runtime.
- **Expected behavior**: The Nitpicker Checklist contains: review round number check, round-dependent prompt count (4 round 1 / 2 round 2+), out-of-scope finding bar for round 2+, round-dependent team size (6 round 1 / 4 round 2+), Big Head P3 auto-filing instructions for round 2+. The Big Head Consolidation Checklist first item is round-aware report count; contains P3 auto-filing check for round 2+. Exact checklist items are specified in `docs/plans/2026-02-19-review-loop-convergence.md` Task 5.
- **Acceptance criteria**:
  1. Nitpicker Checklist contains `Review round number passed to Pantry` item
  2. Nitpicker Checklist contains item mentioning both "6 members" and "4 members" in round-dependent format
  3. Nitpicker Checklist contains `Round 2+ reviewers include out-of-scope finding bar` item
  4. Big Head Checklist first item says `Round 1: Read all 4 Nitpicker reports; Round 2+: Read 2 reports`
  5. Big Head Checklist contains `Round 2+ on PASS: P3 beads auto-filed to "Future Work" epic` item

## Scope Boundaries
Read ONLY: `orchestration/templates/reviews.md:L700-730` (the two checklist sections), `docs/plans/2026-02-19-review-loop-convergence.md` Task 5 (for exact replacement content)
Do NOT edit: Any section outside the two checklists (Nitpicker Checklist and Big Head Consolidation Checklist). Do not touch the Round-Aware Review Protocol, Big Head Consolidation Protocol, Agent Teams Protocol, review type sections (Review 1-4), P3 Auto-Filing, or Queen's Step 3c sections.

## Focus
Your task is ONLY to replace the Nitpicker Checklist and Big Head Consolidation Checklist items with round-aware versions as specified in the implementation plan Task 5.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
