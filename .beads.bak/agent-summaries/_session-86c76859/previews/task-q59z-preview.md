Execute bug for ant-farm-q59z.

Step 0: Read your task context from .beads/agent-summaries/_session-86c76859/prompts/task-q59z.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-q59z` + `bd update ant-farm-q59z --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-q59z)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-86c76859/summaries/q59z.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-q59z`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-q59z
**Task**: Big Head cannot receive Pest Control messages -- timeout on every CCB exchange
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-86c76859/summaries/q59z.md

## Context
- **Affected files**:
  - orchestration/templates/reviews.md:L774-805 -- Step 4 timeout/retry protocol using wall-clock seconds and sleep-based waiting
  - orchestration/templates/big-head-skeleton.md:L121-124 -- Step 10 await instructions referencing 60s wait, retry, 120s escalation
- **Root cause**: After sending the consolidated report path to Pest Control, Big Head runs `sleep 60` in Bash to "wait" for the reply. Messages in Claude Code teams are delivered as new conversation turns. While Big Head is blocked inside a Bash sleep, it cannot process incoming turns. Pest Control's reply arrives during the sleep window but Big Head has no way to see it. When the sleep completes, Big Head is already in the timeout branch and declares failure.
- **Expected behavior**: Big Head should end its turn immediately after sending the report to Pest Control. Pest Control's reply arrives as a new teammate message on Big Head's next turn. No sleep calls, no wall-clock polling.
- **Acceptance criteria**:
  1. Big Head receives Pest Control's CCB verdict without timeout in a test session
  2. No `sleep` calls used for message waiting in Big Head's workflow
  3. No Queen intervention required to relay CCB verdicts
  4. reviews.md Step 4 timeout protocol uses turn-count language, not wall-clock seconds
  5. big-head-skeleton.md Step 10 explicitly instructs "end your turn" after sending to Pest Control

## Scope Boundaries
Read ONLY:
- orchestration/templates/reviews.md:L770-810 (Step 4 timeout/retry protocol and surrounding context)
- orchestration/templates/big-head-skeleton.md:L115-135 (Step 10 await instructions and surrounding context)

Do NOT edit:
- orchestration/RULES.md (Queen workflow -- not relevant)
- orchestration/templates/pantry.md (Pantry workflow -- not relevant)
- orchestration/templates/nitpicker-skeleton.md (reviewer skeleton -- not relevant)
- orchestration/templates/checkpoints.md (CCO/DMVDC checkpoints -- not relevant)
- Any scripts/ files

## Focus
Your task is ONLY to replace the sleep-based timeout/retry protocol in reviews.md and big-head-skeleton.md with turn-based messaging that ends the turn after sending to Pest Control.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
