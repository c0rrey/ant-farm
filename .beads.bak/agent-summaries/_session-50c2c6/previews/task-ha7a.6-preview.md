Execute task for ant-farm-ha7a.6.

Step 0: Read your task context from .beads/agent-summaries/_session-50c2c6/prompts/task-ha7a.6.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-ha7a.6` + `bd update ant-farm-ha7a.6 --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-ha7a.6)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-50c2c6/summaries/ha7a.6.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-ha7a.6`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-ha7a.6
**Task**: Update RULES.md Step 3b/3c for round-aware review loop
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-50c2c6/summaries/ha7a.6.md

## Context
- **Affected files**: `orchestration/RULES.md:L89-135` -- Step 3b and Step 3c sections and Hard Gates table; replace with round-aware versions that read review round from session state and support termination check and re-run path
- **Root cause**: RULES.md Step 3b/3c contain stale hardcoded review protocol (always 6-member team, no round tracking, no termination path). Must be updated so the Queen reads review round from session state, passes it to Pantry, and handles termination (0 P1/P2 = proceed) vs. fix-and-rerun path.
- **Expected behavior**:
  - Step 3b contains `**Review round**: read from session state (default: 1)` and both `**Round 1**:` and `**Round 2+**:` team composition instructions
  - Step 3c contains `**Termination check**: If zero P1 and zero P2 findings:` with round-specific P3 handling
  - Step 3c fix-now path says `re-run Step 3b with round N+1` and mentions `increment review round, record fix commit range`
  - `grep "L631" orchestration/RULES.md` returns NO match (stale reference removed)
  - Hard Gates Reviews row contains "re-runs after fix cycles with reduced scope (round 2+)"
- **Acceptance criteria**:
  1. Step 3b contains `**Review round**: read from session state (default: 1)` and both `**Round 1**:` and `**Round 2+**:` team composition instructions
  2. Step 3c contains `**Termination check**: If zero P1 and zero P2 findings:` with round-specific P3 handling
  3. Step 3c fix-now path says `re-run Step 3b with round N+1` and mentions `increment review round, record fix commit range`
  4. `grep "L631" orchestration/RULES.md` returns NO match (stale reference removed)
  5. Hard Gates Reviews row contains "re-runs after fix cycles with reduced scope (round 2+)"

## Scope Boundaries
Read ONLY: `orchestration/RULES.md:L89-135`, `docs/plans/2026-02-19-review-loop-convergence.md:L436-500` (Task 6 section of the implementation plan)
Do NOT edit: Any file other than `orchestration/RULES.md`. Do NOT edit lines outside L89-135 (Step 3b, Step 3c, and Hard Gates table). Do NOT edit Step 4, Step 5, Step 6, or any content above Step 3b.

## Focus
Your task is ONLY to update RULES.md Step 3b/3c for round-aware review loop with termination.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
