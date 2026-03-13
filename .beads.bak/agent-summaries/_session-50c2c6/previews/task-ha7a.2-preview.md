Execute task for ant-farm-ha7a.2.

Step 0: Read your task context from .beads/agent-summaries/_session-50c2c6/prompts/task-ha7a.2.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-ha7a.2` + `bd update ant-farm-ha7a.2 --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-ha7a.2)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-50c2c6/summaries/ha7a.2.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-ha7a.2`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-ha7a.2
**Task**: Add round-aware review protocol and team setup to reviews.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-50c2c6/summaries/ha7a.2.md

## Context
- **Affected files**: orchestration/templates/reviews.md:L49-L75 (Team Setup section), orchestration/templates/reviews.md:L89 (insert new section before `## Review 1: Clarity (P3)`)
- **Root cause**: The reviews.md file defines a fixed 4-reviewer, 6-member-team pipeline with no concept of review rounds, causing the review loop to run full reviews on every fix cycle instead of narrowing scope.
- **Expected behavior**: A `## Round-Aware Review Protocol` section is inserted before the first review type heading (`## Review 1: Clarity (P3)` at L89), containing subsections for Round 1 (Full Review), Round 2+ (Fix Verification), Termination Rule, and Round 2+ Reviewer Instructions. Team Setup (L49-L75) is updated to show round-dependent team sizes (6 for round 1, 4 for round 2+).
- **Acceptance criteria**:
  1. `grep "## Round-Aware Review Protocol" orchestration/templates/reviews.md` returns a match
  2. The section appears before `## Review 1: Clarity (P3)` -- verify heading order
  3. The section contains all 4 subsections: Round 1 (Full Review), Round 2+ (Fix Verification), Termination Rule, Round 2+ Reviewer Instructions
  4. Team Setup shows "**Round 1**: The Queen creates the Nitpicker team with **6 members**" and "**Round 2+**: The Queen creates the Nitpicker team with **4 members**"
  5. `### Messaging Guidelines` section still exists immediately after Team Setup

## Scope Boundaries
Read ONLY: orchestration/templates/reviews.md:L1-L120 (from top through Review 1 heading area), docs/plans/2026-02-19-review-loop-convergence.md:L53-L170 (Task 2 specification)
Do NOT edit: orchestration/templates/reviews.md:L89-L689 (Review 1 through end of file -- only insert before L89, do not modify existing review sections), any file other than orchestration/templates/reviews.md

## Focus
Your task is ONLY to add the Round-Aware Review Protocol section and update the Team Setup section in reviews.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
