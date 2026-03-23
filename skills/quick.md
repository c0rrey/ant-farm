---
description: This skill should be used when the user invokes "/ant-farm-quick" or "/ant-farm-quick <crumb-id>". Triggers lite mode execution for a single crumb: validates the crumb, then runs the RULES-lite.md workflow. If no crumb-id is provided, lists unblocked open crumbs and prompts user to pick one (or auto-selects if exactly one exists).
---

> **Tool invocation note**: Where this skill instructs the Orchestrator to call crumb operations directly
> (e.g., `crumb show`, `crumb list`, `crumb ready`, `crumb update`), prefer the MCP tool equivalents
> (`crumb_list`, `crumb_show`, `crumb_update`, `crumb_create`, `crumb_query`, `crumb_doctor`). If the MCP
> server is unavailable, fall back to the equivalent `crumb <command>` CLI call via Bash.

# /ant-farm-quick — Lite Mode Execution Skill

This skill governs the `/ant-farm-quick` slash command. It validates the target crumb, then launches the lite mode orchestration workflow defined in `~/.claude/orchestration/RULES-lite.md`.

Lite mode is opt-in. Full mode (`/ant-farm-work`) remains the default for multi-crumb sessions.

## Trigger Conditions

Activate this skill when the user:
- Invokes `/ant-farm-quick` (with or without a crumb-id argument)
- Invokes `/ant-farm-quick <crumb-id>` (e.g., `/ant-farm-quick AF-42`)

Do NOT activate for "let's get to work" — that phrase triggers full-mode `/ant-farm-work` only.

## Step 0 — Pre-flight Error Handling

Before doing anything else, check for fatal conditions. Surface clear error messages and stop if any are true.

### Error: .crumbs/ not initialized

```bash
[ -f .crumbs/tasks.jsonl ] && [ -f .crumbs/config.json ] || echo "NOT_INITIALIZED"
```

If `.crumbs/tasks.jsonl` or `.crumbs/config.json` does not exist:

> **Error**: `.crumbs/tasks.jsonl` not found. Run `/ant-farm-init` to initialize the project, then `/ant-farm-plan` to create tasks before running `/ant-farm-quick`.

Stop. Do not proceed.

## Step 1 — Crumb Selection

### Case A: crumb-id provided (`/ant-farm-quick <crumb-id>`)

Run `crumb show <crumb-id>` to read the crumb's details.

**If the crumb does not exist:**

```bash
crumb list --short 2>/dev/null
```

> **Error**: Crumb `<crumb-id>` not found. Available crumb IDs:
> `[list all crumb IDs from crumb list --short]`

Stop. Do not proceed.

**If the crumb status is `completed`:**

> **Refused**: Crumb `<crumb-id>` is already completed. Nothing to do.
> If this is incorrect, reset it with: `crumb update <crumb-id> --status open`

Stop. Do not proceed.

**If the crumb status is `in_progress`:**

> **Refused**: Crumb `<crumb-id>` is already in progress. A previous session may still be running it.
> To reset to open: `crumb update <crumb-id> --status open`
> To force execution anyway: `/ant-farm-quick <crumb-id> --force`

Stop. Do not proceed (unless `--force` flag was provided, in which case warn and continue).

**If the crumb has unmet `blocked_by` dependencies:**

Check whether all IDs listed in the crumb's `blocked_by` array are `completed`:

```bash
crumb show <crumb-id> 2>/dev/null   # inspect blocked_by field
# For each blocked_by ID, run: crumb show <dep-id> 2>/dev/null | grep "Status:"
```

If any `blocked_by` dependency is NOT `completed`:

> **Warning**: Crumb `<crumb-id>` is blocked by unmet dependencies: `[list unmet IDs and their status]`.
> Running a blocked crumb may produce incorrect or conflicting results.
> To proceed anyway: `/ant-farm-quick <crumb-id> --force`

Stop. Do not proceed (unless `--force` flag was provided).

**If the crumb passes all checks:** Store the crumb ID as `TASK_ID`. Proceed to Step 2.

### Case B: no crumb-id provided (`/ant-farm-quick`)

List all unblocked open crumbs:

```bash
crumb ready --short 2>/dev/null
```

**If zero unblocked open crumbs exist:**

```bash
crumb list --open --short 2>/dev/null
```

> **No unblocked crumbs available.**
> Open crumbs exist but all are blocked by unmet dependencies: `[list them]`.
> Resolve dependencies first, or use `/ant-farm-work` for full multi-crumb execution.

Stop. Do not proceed.

**If exactly one unblocked open crumb exists:**

> Auto-selecting the only available crumb: `<crumb-id>` — `<crumb-title>`.
> Proceeding with lite mode execution. (Run `/ant-farm-quick <other-id>` to target a different crumb.)

Store the crumb ID as `TASK_ID`. Proceed to Step 2.

**If two or more unblocked open crumbs exist:**

> **Select a crumb to run in lite mode:**
> `[numbered list of unblocked open crumbs with ID + title]`
>
> Run `/ant-farm-quick <crumb-id>` to execute one.

Stop. Wait for user to re-invoke with a specific crumb-id.

## Step 2 — Launch Lite Mode Workflow

Read `~/.claude/orchestration/RULES-lite.md` FIRST and ALONE — no parallel tool calls. Then follow it from **Step 0** (Session setup) onward, using `TASK_ID` as the crumb to execute.

Pass `TASK_ID` explicitly into the RULES-lite.md workflow at Step 1 (Task selection — skip the selection sub-step since TASK_ID is already determined).

**Carry the affected files list into RULES-lite.md Step 3:** When you ran `crumb show <TASK_ID>` in Step 1, the crumb's `Scope.files` field contains the list of affected files (with optional line ranges). Store this as `AFFECTED_FILES_LIST` (space-separated strings, e.g., `"src/foo.py:10-50" "src/bar.py"`). RULES-lite.md Step 3 uses `AFFECTED_FILES_LIST` to write `.ant-farm-scope.json` before spawning the implementer. If the crumb has no `Scope.files`, set `AFFECTED_FILES_LIST=""` and the sidecar will be written with an empty `allowed_files` array.

All orchestration rules from `~/.claude/orchestration/RULES-lite.md` apply without exception: pre-spawn-check gate, claims-vs-code gate, retry limits, progress log format, sidecar write at spawn, and sidecar cleanup at close.

## Error Reference

| Condition | Behavior |
|---|---|
| `.crumbs/` not initialized | Hard stop — instruct user to run `/ant-farm-init` |
| Crumb ID not found | Hard stop — list available crumb IDs |
| Crumb already completed | Hard stop — refuse with reset instructions |
| Crumb in_progress (no --force) | Hard stop — refuse with reset and --force instructions |
| Unmet blocked_by deps (no --force) | Hard stop — warn with dependency list and --force instructions |
| No unblocked open crumbs | Hard stop — explain, suggest `/ant-farm-work` |
| Multiple unblocked crumbs, none specified | Soft stop — list choices, wait for re-invocation |
