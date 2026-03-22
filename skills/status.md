---
description: This skill should be used when the user invokes "/ant-farm-status", says "show project status", "what's the status", "show dashboard", "how many tasks are open", or asks for a quick overview of the current project's crumb task state. Displays a concise dashboard: trail completion counts, crumb status summary, and last session summary.
---

# /ant-farm-status — Quick View Dashboard Skill

This skill governs the `/ant-farm-status` slash command. It renders a concise, scannable dashboard showing trail completion counts, crumb status totals by state, and the last session summary. It does not modify any data.

## Trigger Conditions

Activate this skill when the user:
- Invokes `/ant-farm-status` (with or without arguments)
- Asks for project status, task counts, or a dashboard overview
- Asks how many tasks are open, blocked, or completed

## Step 0 — Pre-flight Check

Before gathering any data, verify the project is initialized.

```bash
[ -f .crumbs/tasks.jsonl ] && [ -f .crumbs/config.json ] && echo "INITIALIZED" || echo "NOT_INITIALIZED"
```

If `NOT_INITIALIZED`:

> **Error**: `.crumbs/` is not initialized in this project. Run `/ant-farm-init` to set up the task system.

Stop. Do not proceed.

## Step 1 — Gather Trail Completion Counts

List all trails and compute a completion fraction for each.

```bash
crumb trail list 2>/dev/null
```

For each trail in the output, compute:
- `TRAIL_CLOSED` — count of crumbs in that trail with status `closed`
- `TRAIL_TOTAL` — total crumb count in that trail (all statuses)

Store as a list of `(trail_id, title, TRAIL_CLOSED, TRAIL_TOTAL)` tuples. If the command returns no trails or fails, store an empty list and set `HAS_TRAILS=false`. Otherwise set `HAS_TRAILS=true`.

To get per-trail counts, run:

```bash
crumb list --trail <TRAIL_ID> --short 2>/dev/null | wc -l
crumb list --trail <TRAIL_ID> --closed --short 2>/dev/null | wc -l
```

Repeat for each trail.

## Step 2 — Gather Crumb Status Summary

Collect status counts across all crumbs.

```bash
crumb list --open     --short 2>/dev/null | wc -l
crumb list --blocked  --short 2>/dev/null | wc -l
crumb list --in-progress --short 2>/dev/null | wc -l
crumb list --closed   --short 2>/dev/null | wc -l
```

Store results as:
- `COUNT_OPEN`
- `COUNT_BLOCKED`
- `COUNT_IN_PROGRESS`
- `COUNT_CLOSED`

If all commands fail or return empty output, set all counts to `0` and set `HAS_CRUMBS=false`. Otherwise set `HAS_CRUMBS=true`.

## Step 3 — Retrieve Last Session Summary

Find the most recent exec-summary file under `.crumbs/sessions/` (full-mode sessions). Session directories are named `_session-YYYYMMDD-HHMMSS`.

```bash
ls -t .crumbs/sessions/*/exec-summary.md 2>/dev/null | head -1
```

Store the path as `LAST_SUMMARY_PATH`. If no files are found, set `LAST_SUMMARY_PATH=""` and `HAS_SESSION=false`. Otherwise set `HAS_SESSION=true`.

If `HAS_SESSION=true`, read a brief excerpt (first 20 lines) of `LAST_SUMMARY_PATH`:

```bash
head -20 "${LAST_SUMMARY_PATH}"
```

Store as `LAST_SUMMARY_EXCERPT`.

Extract the session date from the directory name (e.g., `.crumbs/sessions/_session-20260313-021748/exec-summary.md` → `2026-03-13 02:17`). Store as `LAST_SESSION_DATE`.

**Also scan for lite-mode sessions:**

```bash
grep -rl "mode=lite" .crumbs/sessions/*/progress.log 2>/dev/null | sort -r | head -5
```

For each matching `progress.log`, extract the most recent `SESSION_COMPLETE` or `WAVE_VERIFIED` entry (whichever is latest) and store as a lite-mode session record:

- `LITE_SESSION_DIR` — the session directory (e.g., `.crumbs/sessions/_session-20260313-120000`)
- `LITE_TASK_ID` — value of the `task=` field in the `SESSION_COMPLETE` entry (or `tasks_verified=` from `WAVE_VERIFIED`)
- `LITE_SESSION_DATE` — timestamp from the matched entry, formatted as `YYYY-MM-DD HH:MM`
- `LITE_STATUS` — `complete` if a `SESSION_COMPLETE` entry exists, `in_progress` if only `WAVE_SPAWNED` or `WAVE_VERIFIED` exist

Store as a list `LITE_SESSIONS`. If no lite-mode sessions are found, set `LITE_SESSIONS=[]` and `HAS_LITE_SESSIONS=false`. Otherwise set `HAS_LITE_SESSIONS=true`.

## Step 4 — Render Dashboard

Compose and print the status dashboard using the data gathered in Steps 1–3. Format must be concise and scannable — use fixed sections with clear headings, not raw command output.

### No-data edge case

If `HAS_TRAILS=false` AND `HAS_CRUMBS=false` AND `HAS_SESSION=false`:

> **ant-farm status**
>
> No tasks found. Run `/ant-farm-plan` to decompose a spec into tasks.

Stop. Do not render further.

### Standard dashboard

Render the following block (substitute values; omit any section where data is unavailable):

```
ant-farm status
───────────────────────────────────────────
TRAILS
```

For each trail in the list from Step 1, render one line:

```
  <TRAIL_ID>  <TRAIL_TITLE truncated to 40 chars>  <TRAIL_CLOSED>/<TRAIL_TOTAL> closed
```

Example:

```
  trail-001  Auth system                              5/8 closed
  trail-002  API endpoints                            2/2 closed  ✓
```

Mark fully-complete trails with `✓`.

If `HAS_TRAILS=false`:

```
  (no trails)
```

Then render:

```
───────────────────────────────────────────
CRUMBS
  open         <COUNT_OPEN>
  in_progress  <COUNT_IN_PROGRESS>
  blocked      <COUNT_BLOCKED>
  closed       <COUNT_CLOSED>
───────────────────────────────────────────
LAST SESSION
```

If `HAS_SESSION=true`:

```
  <LAST_SESSION_DATE>  <LAST_SUMMARY_PATH>

<LAST_SUMMARY_EXCERPT>
```

If `HAS_SESSION=false`:

```
  (no sessions completed yet)
───────────────────────────────────────────
```

After the full-mode last session block, render lite-mode sessions if `HAS_LITE_SESSIONS=true`:

```
───────────────────────────────────────────
LITE MODE SESSIONS  (last 5)
```

For each entry in `LITE_SESSIONS` (most-recent first):

```
  <LITE_SESSION_DATE>  <LITE_TASK_ID>  [mode=lite]  <LITE_STATUS>
```

Example:

```
───────────────────────────────────────────
LITE MODE SESSIONS  (last 5)
  2026-03-13 12:00  AF-42   [mode=lite]  complete
  2026-03-13 11:45  AF-39   [mode=lite]  in_progress
```

If `HAS_LITE_SESSIONS=false`, omit the `LITE MODE SESSIONS` section entirely.

### Partial-data edge cases

- If `HAS_CRUMBS=false` but trails exist: show trails, show `CRUMBS` section with all zeros, show session section normally.
- If `HAS_SESSION=false` but crumbs exist: show trails and crumbs normally, show `(no sessions completed yet)` in last session section.
- If `HAS_TRAILS=false` but crumbs exist: show `(no trails)` in trails section, show crumb counts normally.
- If `HAS_LITE_SESSIONS=false`: omit the `LITE MODE SESSIONS` section — do not render a placeholder.

## Error Reference

| Condition | Behavior |
|---|---|
| `.crumbs/` not initialized | Hard stop — instruct user to run `/ant-farm-init` |
| `crumb` CLI not found | Hard stop — instruct user to run `/ant-farm-init` to install it |
| No trails, no crumbs, no sessions | Show minimal "no tasks" message with `/ant-farm-plan` hint |
| `crumb trail list` fails | Set `HAS_TRAILS=false`, render `(no trails)` |
| `crumb list` fails for any status | Treat count as `0` for that status |
| No exec-summary files in `.crumbs/sessions/` | Set `HAS_SESSION=false`, render `(no sessions completed yet)` |
| exec-summary file found but unreadable | Set `HAS_SESSION=false`, render `(no sessions completed yet)` |
| `grep` for lite-mode sessions fails or finds none | Set `HAS_LITE_SESSIONS=false`, omit `LITE MODE SESSIONS` section |
| Lite-mode `progress.log` found but missing `SESSION_COMPLETE` | Infer status from latest entry (`WAVE_SPAWNED` → `in_progress`, `WAVE_VERIFIED` → `in_progress`) |
