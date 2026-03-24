---
description: This skill should be used when the user invokes "/ant-farm-work", says "let's get to work", "start execution", "run the pipeline", "execute tasks", or asks to begin running crumbs or executing queued tasks. Triggers the ant-farm execution workflow: reads .crumbs/tasks.jsonl, runs a startup coherence check, creates a SESSION_DIR, then launches the Orchestrator orchestration pipeline (RULES.md).
---

> **Tool invocation note**: Where this skill instructs the Orchestrator to call crumb operations directly
> (e.g., `crumb list`, `crumb doctor`), prefer the MCP tool equivalents (`crumb_list`, `crumb_show`,
> `crumb_update`, `crumb_create`, `crumb_query`, `crumb_doctor`, `crumb_trail_list`, `crumb_trail_show`,
> `crumb_trail_close`, `crumb_close`, `crumb_ready`, `crumb_blocked`, `crumb_link`). If the MCP server is unavailable, fall
> back to the equivalent `crumb <command>` CLI call via Bash.

# /ant-farm-work — Execution Session Skill

This skill governs the `/ant-farm-work` slash command. It reads `.crumbs/tasks.jsonl`, runs a startup coherence check, and launches the Orchestrator orchestration pipeline defined in `orchestration/RULES.md`.

## Trigger Conditions

Activate this skill when the user:
- Invokes `/ant-farm-work` (with or without arguments)
- Says "let's get to work" (case-insensitive)
- Asks to run, execute, or start the pipeline against existing crumbs

## Step 0 — Pre-flight Error Handling

Before doing anything else, check for these fatal conditions. Surface clear error messages and stop if any are true.

### Error: .crumbs/ not initialized

```bash
[ -f .crumbs/tasks.jsonl ] && [ -f .crumbs/config.json ] && echo "INITIALIZED" || echo "NOT_INITIALIZED"
```

If `.crumbs/tasks.jsonl` or `.crumbs/config.json` does not exist:

> **Error**: `.crumbs/tasks.jsonl` not found. Run `/ant-farm-init` to initialize the project, then `/ant-farm-plan` to create tasks before running `/ant-farm-work`.

Stop. Do not proceed.

### Error: crumb CLI not found

```bash
command -v crumb >/dev/null 2>&1 || echo "CRUMB_NOT_INSTALLED"
```

If `crumb` is not installed:

> **Error**: `crumb` CLI not found. Run `/ant-farm-init` to install it.

Stop. Do not proceed.

### Error: No tasks found

```bash
crumb list --short 2>/dev/null | grep -c . || echo 0
```

If the file exists but contains zero crumbs (trails only, or empty):

> **Error**: No crumbs found in `.crumbs/tasks.jsonl`. Run `/ant-farm-plan` to decompose a spec into executable tasks first.

Stop. Do not proceed.

### Error: All tasks closed

```bash
OPEN_OUTPUT=$(crumb list --open --short 2>&1) || { echo "ERROR: crumb list --open failed: ${OPEN_OUTPUT}"; exit 1; }
echo "${OPEN_OUTPUT}" | grep -c . || echo 0
```

If all crumbs are closed (open count = 0):

> **All tasks are closed.** Nothing to execute. If you have new work, run `/ant-farm-plan` to add tasks.

Stop. Do not proceed.

## Step 1 — Execution Startup Coherence Check

Run this lightweight check before spawning the Recon Planner. It catches structural issues caused by manual edits to `.crumbs/tasks.jsonl` between decomposition and execution sessions. Surface results as **warnings** (not hard blocks) — the user decides whether to fix or proceed.

### Check 1: blocked_by references resolve

Verify every ID listed in any crumb's `blocked_by` array exists somewhere in `.crumbs/tasks.jsonl`.

```bash
# Capture once; reused by both checks below
DOCTOR_OUTPUT=$(crumb doctor 2>&1) || { echo "ERROR: crumb doctor failed: ${DOCTOR_OUTPUT}"; exit 1; }
echo "${DOCTOR_OUTPUT}" | grep -i "dangling blocked_by" || echo "OK"
```

If dangling references are found:

> **Warning**: Some `blocked_by` references point to non-existent IDs: `[list them]`. The Recon Planner will treat these as resolved (following `crumb ready` semantics). Fix with `crumb link <id> --remove-blocked-by <missing-id>` if this is unintentional.

### Check 2: parent links resolve

Verify every crumb's `links.parent` value (if set) points to an existing trail ID.

```bash
echo "${DOCTOR_OUTPUT}" | grep -i "dangling parent" || echo "OK"
```

If dangling parent links are found:

> **Warning**: Some crumbs reference non-existent trails as their parent: `[list them]`. These crumbs are orphaned. Fix with `crumb link <id> --parent <trail-id>` or create the missing trail.

### Check 3: stale in_progress crumbs

Detect crumbs left in `in_progress` state from a previous crashed or abandoned execution session.

```bash
INPROGRESS_OUTPUT=$(crumb list --in-progress --short 2>&1) || { echo "ERROR: crumb list --in-progress failed: ${INPROGRESS_OUTPUT}"; exit 1; }
echo "${INPROGRESS_OUTPUT}"
```

If any in_progress crumbs are found:

> **Warning**: The following crumbs are still marked `in_progress` from a previous session: `[list them]`. This may indicate a crashed or abandoned session. Options:
> - Reset to open: `crumb update <id> --status open` (recommended if the work was not completed)
> - Keep as-is: the Recon Planner will skip these and work around them

Wait for user decision before proceeding if in_progress crumbs are found.

### Check 4: existing paused or crashed sessions

Detect prior sessions that did not complete so the user can choose to resume or start fresh.

```bash
SESSIONS_JSON=$(crumb session-list --json 2>&1)
```

Parse the JSON array. Filter for sessions with `status` of `paused` or `crashed` (exclude `completed`). If any non-completed sessions exist, present them to the user:

> **Prior sessions detected**:
>
> | ID | Status | Last Activity |
> |----|--------|---------------|
> | `<session-id>` | `<status>` | `<last_activity>` |
>
> Options:
> - **Resume** a prior session: reply `resume <session-id>`. The Orchestrator will run `scripts/parse-progress-log.sh <SESSION_DIR>` to generate a resume plan from `progress.log` (and `handoff.json` if present), then present the plan for approval before taking any action.
> - **Start fresh**: reply `fresh start` to create a new session directory and proceed normally.

**If the user chooses resume**:

1. Set `SESSION_DIR` to the chosen session directory path (from the `path` field in the JSON output).
2. Run `scripts/parse-progress-log.sh "${SESSION_DIR}"` to generate `${SESSION_DIR}/resume-plan.md`.
   - Exit code 2 means the session already completed — inform the user and fall back to fresh start.
   - Exit code 1 means an error — surface it to the user.
3. Read and present `${SESSION_DIR}/resume-plan.md` verbatim to the user for approval.
4. After the user approves, delete `handoff.json` if it exists:
   ```bash
   rm -f "${SESSION_DIR}/handoff.json"
   ```
5. Proceed to Step 3 (Launch Orchestrator), passing the existing `SESSION_DIR` rather than creating a new one.

Wait for user decision before proceeding if non-completed sessions are found.

## Step 2 — Session Directory Setup

Generate a session ID and create the session artifact directory:

```bash
SESSION_ID=$(date +%Y%m%d-%H%M%S)
SESSION_DIR=".crumbs/sessions/_session-${SESSION_ID}"
mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts,pc,summaries,signals}  # pc = checkpoint artifacts (legacy: "pest control")
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SESSION_INIT|complete|session_dir=${SESSION_DIR}" >> "${SESSION_DIR}/progress.log"
```

Store `SESSION_ID` and `SESSION_DIR` in context. Pass `SESSION_DIR` explicitly to every downstream agent.

## Step 3 — Launch Orchestrator

Read `orchestration/RULES.md`. Follow its workflow from **Step 1** (Recon / Recon Planner spawn) onward. The Recon Planner reads `.crumbs/tasks.jsonl` via the `crumb` CLI.

All other orchestration rules from `orchestration/RULES.md` apply without exception: wave management, concurrency limits, hard gates (startup-check, pre-spawn-check, scope-verify, claims-vs-code, session-complete), model assignments, and landing-the-plane protocol.

## Error Reference

| Condition | Behavior |
|---|---|
| `.crumbs/` not initialized | Hard stop — instruct user to run `/ant-farm-init` |
| No crumbs in tasks.jsonl | Hard stop — instruct user to run `/ant-farm-plan` |
| All crumbs closed | Hard stop — nothing to do |
| Dangling `blocked_by` reference | Warning — surface to user, offer fix command, proceed after acknowledgment |
| Dangling `parent` link | Warning — surface to user, offer fix command, proceed after acknowledgment |
| Stale `in_progress` crumbs | Warning — list crumbs, offer reset command, **wait for user decision** before proceeding |
| `crumb doctor` command not found | Assume crumb CLI not installed — instruct user to run `/ant-farm-init` to install it |
