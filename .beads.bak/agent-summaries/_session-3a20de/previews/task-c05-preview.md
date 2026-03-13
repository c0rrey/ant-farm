Execute bug for ant-farm-c05.

Step 0: Read your task context from .beads/agent-summaries/_session-3a20de/prompts/task-c05.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-c05` + `bd update ant-farm-c05 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-c05)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-3a20de/summaries/c05.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-c05`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-c05
**Task**: Checkpoint A.5 relies on Queen-provided file list with no independent scope validation
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/c05.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L189 -- Checkpoint A.5 expected file list placeholder (inside the CCO Nitpickers template)
- **Root cause**: Checkpoint A.5 uses {list files from task description} as the expected file list, provided by the Queen. If the Queen passes an incomplete or incorrect list, A.5 will produce false positives or false negatives.
- **Expected behavior**: Either A.5 has an independent scope reference, or the limitation is explicitly documented.
- **Acceptance criteria**:
  1. Either A.5 has an independent scope reference, or the limitation is explicitly documented

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md:L165-225 (CCO Nitpickers section)
Do NOT edit: CCO Dirt Pushers section (L97-163), WWD section (L235-303), DMVDC section (L306-454), CCB section (L457-572)

## Focus
Your task is ONLY to add independent scope validation to Checkpoint A.5 or document its limitation.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
