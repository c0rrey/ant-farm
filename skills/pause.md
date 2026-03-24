---
description: This skill should be used when the user invokes "/ant-farm-pause". Pauses the current multi-agent session by writing a structured handoff.json and continue-here.md to the session directory, then performing a WIP commit of any staged/unstaged changes. Enables safe session resumption after context exhaustion or deliberate pause.
---

> **Tool invocation note**: Where this skill instructs the Orchestrator to call crumb operations directly
> (e.g., `crumb list`), prefer the MCP tool equivalents (`crumb_list`, `crumb_show`, `crumb_update`,
> `crumb_create`, `crumb_query`, `crumb_blocked`, `crumb_ready`, `crumb_link`). If the MCP server is
> unavailable, fall back to the equivalent `crumb <command>` CLI call via Bash.

# /ant-farm-pause — Session Pause Skill

This skill governs the `/ant-farm-pause` slash command. It captures the Orchestrator's current session state into a structured `handoff.json` and human-readable `continue-here.md`, then performs a WIP commit of any outstanding changes. This creates a safe, resumable snapshot of the session.

**Critical ordering constraint**: `handoff.json` and `continue-here.md` MUST be written BEFORE the WIP commit. If the process is killed between the commit and the file write, the session appears as a crash with no recovery data. Writing files first ensures the handoff artifacts survive even if the commit step is interrupted.

## Trigger Conditions

Activate this skill when the user:
- Invokes `/ant-farm-pause`
- Explicitly asks to pause, checkpoint, or save session state for later resumption

Do NOT activate for "let's get to work", `/ant-farm-work`, or `/ant-farm-quick` — those trigger execution workflows.

## Step 0 — Pre-flight Checks

Before doing anything else, verify these conditions. Surface clear errors and stop if any are true.

### Check: SESSION_DIR is set

`SESSION_DIR` must be set in the Orchestrator's context. If it is not set or the directory does not exist:

> **Error**: `/ant-farm-pause` requires an active session. `SESSION_DIR` is not set or does not exist.
> Start a session with `/ant-farm-work` before pausing.

Stop. Do not proceed.

### Check: .crumbs/ is initialized

```bash
[ -f .crumbs/tasks.jsonl ] && echo "OK" || echo "NOT_INITIALIZED"
```

If not initialized, surface the error and stop.

## Step 1 — Gather Session State

Collect all fields required for `handoff.json`. The Orchestrator must determine each value from its current context window.

### 1a. Uncommitted files

```bash
git status --porcelain
```

Capture the output as `UNCOMMITTED_FILES`. If the output is empty, `UNCOMMITTED_FILES` is empty (WIP commit will be skipped).

### 1b. Blocked crumbs

Use the `crumb_blocked` MCP tool (or `crumb blocked --short` CLI fallback) to get the list of currently blocked crumb IDs.

### 1c. Pending tasks

Use the `crumb_ready` MCP tool (or `crumb ready --short` CLI fallback) to get unblocked open crumbs still pending execution.

### 1d. Current step, completed steps, active wave, retry budget

These come from the Orchestrator's context. If unknown, record `"unknown"` rather than omitting the field.

## Step 2 — Write handoff.json (BEFORE WIP commit)

Construct and write `${SESSION_DIR}/handoff.json`. Use the values gathered in Step 1.

The JSON schema is fixed — include all fields even if their value is `null` or `[]`:

```
{
  "schema_version": "1",
  "session_id": "<SESSION_ID>",
  "paused_at": "<ISO 8601 UTC timestamp>",
  "current_step": "<step name or number, e.g. WAVE_SPAWNED or 3b>",
  "completed_steps": ["<step1>", "<step2>", ...],
  "pending_tasks": ["<crumb-id>", ...],
  "active_wave": <integer or null>,
  "retry_budget_remaining": <integer or null>,
  "uncommitted_files": ["<path>", ...],
  "blocked_crumbs": ["<crumb-id>", ...],
  "next_action": "<concise description of what to do when resuming>",
  "context_notes": "<Orchestrator's current understanding: approach, known issues, decisions made, anything needed for clean resumption>"
}
```

**Field guidelines:**
- `paused_at`: Use `$(date -u +%Y-%m-%dT%H:%M:%SZ)` to generate.
- `context_notes`: This is the most important field. Write a dense summary of the Orchestrator's current understanding — active decisions, known edge cases, why the current approach was chosen, any deferred issues. This is the Orchestrator's memory for the next session.
- `next_action`: One sentence. What is the very first thing the resuming session should do?
- `uncommitted_files`: List each file on its own line from `git status --porcelain` output.

Write the file:

```bash
cat > "${SESSION_DIR}/handoff.json" << 'HANDOFF_EOF'
<constructed JSON here>
HANDOFF_EOF
```

Verify the file was written:

```bash
[ -f "${SESSION_DIR}/handoff.json" ] && echo "handoff.json written OK" || echo "ERROR: handoff.json write failed"
```

If the write failed, stop and surface the error. Do NOT proceed to the WIP commit.

## Step 3 — Write continue-here.md (BEFORE WIP commit)

Write a human-readable summary alongside `handoff.json`. This is the file a human or resuming Orchestrator reads first to understand what was happening.

```bash
cat > "${SESSION_DIR}/continue-here.md" << 'CONTINUE_EOF'
# Session Pause — Continue Here

**Session ID**: <SESSION_ID>
**Paused at**: <timestamp>

## What Was Happening

<1-3 sentences: what the session was doing when paused>

## Resume Point

**Current step**: <current_step>
**Next action**: <next_action>

## Pending Tasks

<bulleted list of pending_tasks with crumb IDs>

## Active Wave

<active_wave or "None">

## Retry Budget Remaining

<retry_budget_remaining or "Unknown">

## Known Issues / Context Notes

<context_notes — copy from handoff.json but prose-formatted>

## Blocked Crumbs

<bulleted list of blocked_crumbs, or "None">

## Uncommitted Files at Pause Time

<bulleted list of uncommitted_files, or "None (clean working tree)">

---

*To resume: start a new session and refer to `handoff.json` in this directory for structured state.*
*Session artifacts: `${SESSION_DIR}/`*
CONTINUE_EOF
```

Verify the file was written:

```bash
[ -f "${SESSION_DIR}/continue-here.md" ] && echo "continue-here.md written OK" || echo "ERROR: continue-here.md write failed"
```

If the write failed, stop and surface the error.

## Step 4 — WIP Commit (AFTER handoff files are written)

Check whether there are any uncommitted changes (including the handoff files just written):

```bash
git status --porcelain
```

If the output is empty (nothing to commit), skip the WIP commit and note it:

> No uncommitted changes. WIP commit skipped.

If there are changes, stage and commit:

```bash
git add -A
git commit -m "wip: ant-farm pause -- session ${SESSION_ID}"
```

**Note**: The handoff files (`handoff.json`, `continue-here.md`) are inside `.crumbs/sessions/` which is gitignored. They will NOT appear in `git status` and will NOT be staged by `git add -A`. The WIP commit captures code changes only — handoff files live in the session directory as local artifacts. This is correct behavior: handoff files are session-local, not version-controlled.

If the commit fails, surface the error but do NOT retry in a loop. Report the failure and continue to Step 5 — the handoff files are already written and the session is safely paused.

## Step 5 — Confirm and Summarize

Report completion to the user:

> **Session paused.**
>
> - `handoff.json` written to `${SESSION_DIR}/handoff.json`
> - `continue-here.md` written to `${SESSION_DIR}/continue-here.md`
> - WIP commit: [committed as `wip: ant-farm pause -- session ${SESSION_ID}` | skipped — clean working tree | failed — see error above]
>
> **Resume point**: <current_step> — <next_action>
>
> To resume this session later, start a new `/ant-farm-work` session and reference `${SESSION_DIR}` for prior context. The Orchestrator will read `handoff.json` via Step 0a crash recovery.

## Error Reference

| Condition | Behavior |
|---|---|
| `SESSION_DIR` not set | Hard stop — instruct user to start a session first |
| `.crumbs/` not initialized | Hard stop — instruct user to run `/ant-farm-init` |
| `handoff.json` write failed | Hard stop — do NOT proceed to WIP commit |
| `continue-here.md` write failed | Hard stop — do NOT proceed to WIP commit |
| WIP commit failed | Surface error, continue to Step 5 (handoff files are safe) |
| `crumb blocked` or `crumb ready` unavailable | Record `null` / `[]` for those fields; note in `context_notes` |
