# Dirt Pusher Skeleton Template

## Instructions for The Queen

Fill in all `{PLACEHOLDER}` values (uppercase) and use the result as the Task tool `prompt` parameter.
The agent-facing text starts below the `---` separator. Do NOT include this instruction block.

**Term definitions (canonical across all orchestration templates):**
- `{TASK_ID}` — full bead ID including project prefix (e.g., `ant-farm-9oa`)
- `{TASK_SUFFIX}` — suffix portion only, no project prefix (e.g., `9oa` from `ant-farm-9oa`, or `74g1` from `hs_website-74g.1`)
- `{EPIC_ID}` — epic suffix only (e.g., `74g` from `hs_website-74g`), or `_standalone` for tasks with no epic parent

Placeholders:
- {TASK_TYPE}: bead type (bug/feature/task) — from the Scout's briefing
- {TASK_ID}: full bead ID including project prefix (e.g., ant-farm-9oa)
- {TASK_SUFFIX}: suffix only, no prefix (e.g., 9oa)
- {AGENT_TYPE}: subagent_type for Task tool — from the Pantry verdict table (Agent Type column). The Queen MAY override if strategy context warrants it.
- {DATA_FILE_PATH}: from the Pantry verdict table
- {SUMMARY_OUTPUT_PATH}: .beads/agent-summaries/{EPIC_ID}/{TASK_SUFFIX}.md

## Template (send everything below this line)

---

Execute {TASK_TYPE} for {TASK_ID}.

Step 0: Read your task context from {DATA_FILE_PATH}
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show {TASK_ID}` + `bd update {TASK_ID} --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> ({TASK_ID})"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to {SUMMARY_OUTPUT_PATH} with all required sections
   (see data file for section list).

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.
After committing: `bd close {TASK_ID}`
