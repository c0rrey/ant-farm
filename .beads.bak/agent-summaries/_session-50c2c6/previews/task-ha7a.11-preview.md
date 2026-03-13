Execute task for ant-farm-ha7a.11.

Step 0: Read your task context from .beads/agent-summaries/_session-50c2c6/prompts/task-ha7a.11.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-ha7a.11` + `bd update ant-farm-ha7a.11 --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-ha7a.11)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-50c2c6/summaries/ha7a.11.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-ha7a.11`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-ha7a.11
**Task**: Verify cross-file consistency of round-aware review convergence patterns
**Agent Type**: code-reviewer
**Note**: No Scout metadata file exists for ha7a.11. Agent Type set to `code-reviewer` based on audit/verification nature of this task. The Queen may override.
**Summary output path**: .beads/agent-summaries/_session-50c2c6/summaries/ha7a.11.md

## Context
- **Affected files (read-only verification)**:
  - `orchestration/templates/queen-state.md:L33-37` (Review Rounds section)
  - `orchestration/templates/reviews.md:L49-96` (Team Setup, round-aware), `reviews.md:L110-154` (Round-Aware Review Protocol), `reviews.md:L394-488` (Big Head Step 0/0a), `reviews.md:L564-611` (Consolidated Summary template), `reviews.md:L671-699` (P3 Auto-Filing), `reviews.md:L701-729` (Checklists), `reviews.md:L740-809` (Queen's Step 3c + Handle P3 Issues)
  - `orchestration/RULES.md:L89-121` (Step 3b/3c round-aware review loop), `RULES.md:L138` (Hard Gates row for Reviews)
  - `orchestration/templates/big-head-skeleton.md:L13` (REVIEW_ROUND placeholder), `big-head-skeleton.md:L26-54` (TeamCreate round 1 and round 2+ examples), `big-head-skeleton.md:L67-71` (agent-facing round-aware text), `big-head-skeleton.md:L93-98` (P3 auto-filing step 10)
  - `orchestration/templates/nitpicker-skeleton.md:L12` (REVIEW_ROUND placeholder), `nitpicker-skeleton.md:L18-21` (agent-facing round-aware scope)
  - `orchestration/templates/pantry.md:L201` (review round in input spec), `pantry.md:L229-251` (round-aware composition + files to write), `pantry.md:L253-267` (Big Head brief round-awareness), `pantry.md:L269-278` (preview composition round note), `pantry.md:L286-308` (round-dependent return tables)
  - `orchestration/templates/checkpoints.md:L453` (CCB header round-aware), `checkpoints.md:L467-478` (Individual reports Round 1/2+), `checkpoints.md:L479` (document count line), `checkpoints.md:L481-494` (Check 0 round-aware), `checkpoints.md:L497-500` (Check 1 round-aware math)
- **Root cause**: Tasks 1-10 each modified a separate file or section to add round-aware review patterns. These changes must be mutually consistent across all 7 files: team member counts, report counts, placeholder names, termination semantics, P3 handling paths, and cross-references must all agree.
- **Expected behavior**: All 11 invariants from the implementation plan (Task 11, Step 1 table) hold across the 7 modified files. No stale hardcoded counts remain. No stale line-number references survive. All round-aware patterns use consistent terminology.
- **Acceptance criteria**:
  1. Invariant: Round 1 = 6 team members confirmed in reviews.md:L53 Team Setup, RULES.md:L100 Step 3b, big-head-skeleton.md:L26 TeamCreate example; Round 2+ = 4 team members confirmed in reviews.md:L75, RULES.md:L103, big-head-skeleton.md:L42
  2. Invariant: Round 1 = 4 reports confirmed in reviews.md:L410 Step 0, checkpoints.md:L484 Check 0, big-head-skeleton.md:L70 template, pantry.md:L230 composition; Round 2+ = 2 reports confirmed in reviews.md:L419, checkpoints.md:L491, big-head-skeleton.md:L71, pantry.md:L231
  3. Invariant: Termination = 0 P1/P2 leads to RULES.md Step 4 confirmed in both reviews.md:L744-753 (Queen's Step 3c Termination Check) and RULES.md:L112-116 (Step 3c termination check)
  4. Invariant: Round 1 P3s flow to Queen's "Handle P3 Issues" confirmed in reviews.md:L792-807 and RULES.md:L114
  5. Invariant: Round 2+ P3s auto-filed by Big Head confirmed in reviews.md:L671-699 (P3 Auto-Filing section) and big-head-skeleton.md:L93-98 (step 10)
  6. Invariant: REVIEW_ROUND placeholder exists in both nitpicker-skeleton.md:L12 and big-head-skeleton.md:L13, and pantry.md:L276 references filling it
  7. Invariant: queen-state.md:L33-37 has review round counter, RULES.md:L92 reads it, RULES.md:L120 updates it
  8. Invariant: Pantry adapts polling loop per round per pantry.md:L267, matching reviews.md:L453-488 polling loop template
  9. Invariant: CCB expects round-dependent report count per checkpoints.md:L481-494 (Check 0) and checkpoints.md:L497-500 (Check 1), matching reviews.md:L406-429 (Step 0)
  10. Invariant: Re-review is MANDATORY (not optional) after fixes per reviews.md:L782-785 and RULES.md:L119
  11. Invariant: "Handle P3 Issues" section marked "Round 1 only" at reviews.md:L794 does not conflict with P3 Auto-Filing at reviews.md:L671
  12. No stale hardcoded line-number references in any of the 7 files (search for patterns like `L\d+`, `line \d+`)
  13. No stale member/report counts remaining: every instance of "all 4", "4 report", "5 member", "4 individual" is either in a round 1 context or has been made round-aware

## Scope Boundaries
Read ONLY: orchestration/templates/queen-state.md, orchestration/templates/reviews.md, orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/checkpoints.md
Do NOT edit: any file (this is a read-only audit). If inconsistencies are found, document them in the summary and fix them in a separate commit.

## Focus
Your task is ONLY to verify cross-file consistency of the round-aware review convergence patterns across all 7 modified files.
Do NOT fix adjacent issues you notice -- document them under "Adjacent Issues Found" in your summary.
If you find inconsistencies, fix them and commit with message "fix: resolve cross-file inconsistencies in review convergence implementation (ant-farm-ha7a.11)".

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
