Execute bug for ant-farm-7kei.

Step 0: Read your task context from .beads/agent-summaries/_session-0ffcdc51/prompts/task-7kei.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-7kei` + `bd update ant-farm-7kei --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-7kei)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-0ffcdc51/summaries/7kei.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-7kei`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-7kei
**Task**: agents/big-head.md step ordering places bead filing before Pest Control checkpoint
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-0ffcdc51/summaries/7kei.md

## Context
- **Affected files**: `agents/big-head.md:L16-37` (full "When consolidating" step list)
- **Root cause**: When dedup and `--body-file` instructions were added to `agents/big-head.md` (during ant-farm-asdl.3), two new steps were inserted and existing steps renumbered, but the step ORDER was not updated to match the skeleton's required sequence. The result is that `big-head.md` says "file issues" (step 7) BEFORE "write consolidated report" (step 8), while `big-head-skeleton.md` requires writing the report first (step 8), sending to Pest Control (step 9), awaiting verdict (step 10), and filing only after PASS verdict. This means the agent definition contradicts the skeleton's Pest Control checkpoint gate.
- **Expected behavior**: The "When consolidating" steps in `agents/big-head.md` must follow the same sequence as `big-head-skeleton.md:L88-172`: (1) read reports, (2) build inventory, (3) group by root cause, (4) merge issues, (5) track severity, (6) dedup against existing beads, (7) write consolidated report, (8) send to Pest Control and await verdict, THEN (9) file issues via `bd create --body-file` only after PASS verdict.
- **Review finding reference**: RC-3 in consolidated review report at `.beads/agent-summaries/_session-0ffcdc51/review-reports/review-consolidated-20260222-143758.md:L74-94`
- **Acceptance criteria**:
  1. Step that writes the consolidated report appears BEFORE the step that files issues via `bd create --body-file`
  2. A step for sending the report to Pest Control and awaiting verdict exists BETWEEN writing the report and filing issues
  3. Filing issues step explicitly states it only proceeds after Pest Control PASS verdict
  4. All 8+ steps in the "When consolidating" list are present and in an order consistent with `big-head-skeleton.md:L88-172`
  5. No step references are broken or duplicated after reordering

## Scope Boundaries
Read ONLY:
- `agents/big-head.md:L1-37` (full file -- it is short)
- `orchestration/templates/big-head-skeleton.md:L88-172` (canonical step ordering reference)
- `.beads/agent-summaries/_session-0ffcdc51/review-reports/review-consolidated-20260222-143758.md:L74-94` (RC-3 finding detail)

Do NOT edit:
- `orchestration/templates/big-head-skeleton.md` (reference only -- the skeleton is correct)
- `orchestration/templates/reviews.md` (not in scope for this task)
- `orchestration/templates/pantry.md` (not in scope)
- Any file other than `agents/big-head.md`

## Focus
Your task is ONLY to reorder the "When consolidating" steps in `agents/big-head.md` so that bead filing occurs AFTER writing the consolidated report and receiving Pest Control's PASS verdict, matching the sequence in `big-head-skeleton.md`.
Do NOT fix adjacent issues you notice.
Do NOT change the content/wording of individual steps -- only reorder them and add the Pest Control checkpoint step if missing.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
