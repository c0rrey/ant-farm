Execute bug for ant-farm-txw.

Step 0: Read your task context from .beads/agent-summaries/_session-cd9866/prompts/task-txw.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-txw` + `bd update ant-farm-txw --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-txw)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-cd9866/summaries/txw.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-txw`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-txw
**Task**: Templates lack failure artifact specification for error paths
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/txw.md

## Context
- **Affected files**: orchestration/templates/big-head-skeleton.md:L73-99 (Step 0 says 'Do NOT proceed' when reports missing but writes no failure artifact), orchestration/templates/pantry.md:L45-90 (has failure artifacts for some conditions but convention not documented), orchestration/templates/reviews.md:L465-590 (Step 0/0a specifies FAIL conditions and error return but no artifact written to output path)
- **Root cause**: Multiple templates specify FAIL conditions but do not specify what artifact to write on failure. Big Head Step 0 (big-head-skeleton.md:L77-79) says 'Do NOT proceed to read reports or perform consolidation' but does not instruct writing a failure artifact to the consolidated output path. Reviews.md Step 0a (L552-588) specifies an error return message format but does not write a failure file. Downstream consumers have no written record of the failure, making debugging and recovery harder.
- **Expected behavior**: When any template reaches a FAIL condition, it writes a brief failure artifact to the expected output path explaining the failure, the timestamp, and the recovery action.
- **Acceptance criteria**:
  1. Big Head Step 0 in big-head-skeleton.md writes a failure artifact to the consolidated output path when reports are missing after timeout
  2. Failure artifact convention documented (standard format: Status, Reason, Recovery) applicable to all templates

## Scope Boundaries
Read ONLY: orchestration/templates/big-head-skeleton.md:L1-105, orchestration/templates/reviews.md:L455-600, orchestration/templates/pantry.md:L45-90 (existing failure artifact examples)
Do NOT edit: orchestration/templates/pantry.md (pantry already has failure artifacts), orchestration/RULES.md, orchestration/templates/checkpoints.md, any scripts/ files

## Focus
Your task is ONLY to add failure artifact specifications to Big Head Step 0 and document the failure artifact convention.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
