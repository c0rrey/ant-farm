Execute task for ant-farm-7hgn.

Step 0: Read your task context from .beads/agent-summaries/_session-54996f/prompts/task-7hgn.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-7hgn` + `bd update ant-farm-7hgn --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-7hgn)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-54996f/summaries/7hgn.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-7hgn`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-7hgn
**Task**: Delay Big Head bead filing until after Pest Control checkpoint validation
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-54996f/summaries/7hgn.md

## Context
- **Affected files**:
  - orchestration/templates/reviews.md:L321-325 (Big Head Consolidation Protocol header and model spec), L460-470 (Step 3: File Beads section), L535-542 (Big Head Consolidation Checklist) -- Update Big Head Consolidation Protocol to add checkpoint gate before bead filing
  - orchestration/templates/big-head-skeleton.md:L67-80 (steps 5-8: consolidation to bead filing workflow) -- Add wait-for-PC step between consolidation and bead filing
  - orchestration/RULES.md:L97-103 (Nitpicker team composition and post-team Pest Control spawning) -- Update review team composition to include Pest Control coordination step
  - orchestration/templates/pantry.md:L137-145 (Section 2, Step 4: Big Head data file composition) -- Big Head data file needs to reference the PC coordination step
- **Root cause**: Big Head currently files beads for review findings before CCD and DMVDC checkpoints run. If checkpoints identify invalid findings (hallucinated, misattributed, does not match actual diff), those beads already exist and require manual cleanup. This pollutes the issue tracker with unvalidated findings.
- **Expected behavior**: Big Head consolidates and writes the report but holds off on bd create calls until Pest Control confirms the findings pass checkpoints. On PASS: Big Head files all beads. On FAIL: Big Head flags failures to the Queen; only validated findings are filed.
- **Acceptance criteria**:
  1. Big Head does not file any beads until Pest Control confirms checkpoint validation
  2. Pest Control is spawned as part of the Nitpicker team, not as a separate Queen-orchestrated agent
  3. On checkpoint pass, all consolidated findings are filed as beads
  4. On checkpoint fail, only validated findings are filed; failures are escalated to Queen with specifics
  5. No review report content enters the Queen's context window during this process

## Scope Boundaries
Read ONLY: orchestration/templates/reviews.md:L321-542, orchestration/templates/big-head-skeleton.md:L1-80, orchestration/RULES.md:L88-110, orchestration/templates/pantry.md:L137-145
Do NOT edit: orchestration/templates/scout.md; orchestration/templates/implementation.md; orchestration/templates/checkpoints.md (read-only reference for checkpoint definitions); orchestration/templates/nitpicker-skeleton.md; orchestration/templates/dirt-pusher-skeleton.md; any agent files in agents/

## Focus
Your task is ONLY to add a checkpoint gate so Big Head delays bead filing until after Pest Control validates the consolidated findings. Update the four affected files to implement this gating mechanism.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
