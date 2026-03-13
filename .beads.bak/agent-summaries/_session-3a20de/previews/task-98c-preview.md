Execute bug for ant-farm-98c.

Step 0: Read your task context from .beads/agent-summaries/_session-3a20de/prompts/task-98c.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-98c` + `bd update ant-farm-98c --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-98c)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-3a20de/summaries/98c.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-98c`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-98c
**Task**: RULES.md retry counter interaction between per-checkpoint and session-total limits is unspecified
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/98c.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L269-278 -- Retry Limits table, specifically the Checkpoint C row and session total row
- **Root cause**: The retry limits table says Checkpoint C failures allow 1 retry, and a session total of 5 retries. But it does not specify whether a Checkpoint C re-run counts toward the session total. The interaction between per-checkpoint limits and the global session cap is ambiguous.
- **Expected behavior**: Retry table explicitly states how per-checkpoint retries interact with the session total.
- **Acceptance criteria**:
  1. Retry table explicitly states: Each Checkpoint C re-run counts as 1 toward both the per-checkpoint limit (1) and the session total (5)

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L269-278 (Retry Limits section)
Do NOT edit: Workflow section (L53-150), Hard Gates (L152-162), Session Directory (L216-234), any other section

## Focus
Your task is ONLY to clarify the retry counter interaction in the Retry Limits table.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
