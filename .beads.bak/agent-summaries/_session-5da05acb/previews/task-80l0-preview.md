Execute bug for ant-farm-80l0.

Step 0: Read your task context from .beads/agent-summaries/_session-5da05acb/prompts/task-80l0.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-80l0` + `bd update ant-farm-80l0 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-80l0)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-5da05acb/summaries/80l0.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-80l0`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-80l0
**Task**: README Hard Gates table missing SSV checkpoint
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-5da05acb/summaries/80l0.md

## Context
- **Affected files**:
  - README.md:L258-263 — Hard Gates table missing SSV row
- **Root cause**: When SSV (Scout Strategy Verification) was added as the fifth hard gate, the README Hard Gates table was not updated. It still lists only 4 gates while RULES.md and GLOSSARY correctly list 5 including SSV.
- **Expected behavior**: README Hard Gates table should list 5 checkpoints matching RULES.md (SSV, CCO, WWD, DMVDC, CCB).
- **Acceptance criteria**:
  1. README Hard Gates table lists 5 checkpoints matching RULES.md (SSV, CCO, WWD, DMVDC, CCB)
  2. SSV row includes correct gate target (Pantry spawn) and model (haiku)

## Scope Boundaries
Read ONLY: README.md:L250-270, orchestration/RULES.md (SSV checkpoint definition for reference)
Do NOT edit: orchestration/RULES.md, orchestration/GLOSSARY.md, orchestration/templates/checkpoints.md

## Focus
Your task is ONLY to add the missing SSV row to the README Hard Gates table.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
