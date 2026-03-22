# Implementer Skeleton Template

## Instructions for the Orchestrator

Fill in all `{PLACEHOLDER}` values (uppercase) and use the result as the Task tool `prompt` parameter.
The agent-facing text starts below the `---` separator. Do NOT include this instruction block.

**Model**: The Task tool call MUST include `model: "sonnet"`. This applies to ALL Implementers regardless of their `subagent_type` (python-pro, typescript-pro, general-purpose, etc.).

**Term definitions (canonical across all orchestration templates):**
- `{TASK_ID}` — full crumb ID including project prefix (e.g., `ant-farm-9oa`)
- `{TASK_SUFFIX}` — suffix portion only; extracted by splitting on the LAST hyphen (e.g., `9oa` from `ant-farm-9oa`, or `74g1` from `my-project-74g.1`)
- `{SESSION_DIR}` — session artifact directory path (e.g., `.crumbs/sessions/_session-abc123`)

Placeholders:
- {TASK_TYPE}: crumb type (bug/feature/task) — from the Recon Planner's briefing
- {TASK_ID}: full crumb ID including project prefix (e.g., ant-farm-9oa)
- {TASK_SUFFIX}: suffix only, no prefix (e.g., 9oa)
- {AGENT_TYPE}: subagent_type for Task tool — from the Prompt Composer verdict table (Agent Type column). See **Agent Type Selection Policy** below.
- {DATA_FILE_PATH}: from the Prompt Composer verdict table
- {SUMMARY_OUTPUT_PATH}: {SESSION_DIR}/summaries/{TASK_SUFFIX}.md

### Agent Type Selection Policy

**Authority chain**: Recon Planner recommends → Prompt Composer passes through unchanged → Orchestrator may override.

**Orchestrator override**: Allowed only when Recon Planner metadata is demonstrably wrong (e.g., wrong domain, agent type unavailable). Document the override reason in the Orchestrator's state file before spawning. Do NOT override based on preference or guesswork.

## Template (send everything below this line)

---

Execute {TASK_TYPE} for {TASK_ID}.

Step 0: Read your task context from {DATA_FILE_PATH}
(Format: markdown. Sections: Context, Scope Boundaries, Focus, Summary Doc Sections.)

Execute these 6 steps in order:

1. **Claim**: `crumb show {TASK_ID}` + `crumb update {TASK_ID} --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> ({TASK_ID})"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to {SUMMARY_OUTPUT_PATH} with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `crumb close {TASK_ID}`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

**Sentinel (final action)**: As your absolute last action, write your verdict summary:
```bash
echo "VERDICT: {PASS|FAIL}
COMMIT: {commit-hash|none}
FILES: {comma-separated changed files}
SUMMARY: {one-line task description}" > "{SESSION_DIR}/signals/{TASK_SUFFIX}.done"
```
This file signals completion to the Orchestrator. Do NOT skip this step.
