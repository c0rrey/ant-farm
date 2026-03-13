# Task Summary: ant-farm-jmvi

## Approaches Considered

1. **Helper functions + minimal cmd_close/cmd_link modification (selected)** — Define `_get_trail_children`, `_auto_close_trail_if_complete`, and `_auto_reopen_trail_if_needed` as module-level helpers. Add one-line hook calls to `cmd_close` (after its `write_tasks`) and `cmd_link` (after its `write_tasks` when `--parent` is set). `cmd_trail` dispatches to four private `_cmd_trail_*` sub-handlers. Clean separation of concerns, helpers defined once, minimal changes to existing code.

2. **All auto-close/reopen logic inside cmd_trail sub-handlers** — AC5 and AC6 are triggered by events in `cmd_close` and `cmd_link`, not by trail commands. There is no way to implement these purely inside `cmd_trail` handlers without either re-reading the file after those commands run (polling) or restructuring the architecture. Not feasible in a single-command CLI.

3. **Single monolithic cmd_trail function with nested dispatch** — Put all four sub-handler bodies directly inside `cmd_trail` as if/elif branches. Avoids adding new function names but creates a very long function (200+ lines) that's hard to read and test. No architectural benefit over helper functions.

4. **Event registration system** — Register post-hooks on `cmd_close` and `cmd_link` at startup so they call trail-related callbacks. Over-engineered for three functions in a single-file stdlib script.

## Selected Approach

Approach 1: helper functions plus minimal hook calls. The task spec explicitly permits "minimal modifications to cmd_close and cmd_link to add auto-close/auto-reopen hook calls." Each helper is clearly named, fully docstringed, and receives the already-modified task list plus path so they don't need to re-acquire the lock or re-read the file.

## Implementation Description

**New helper functions** (inserted before `cmd_list`):

- `_get_trail_children(tasks, trail_id)`: Returns all non-trail records whose `links.parent == trail_id`. Used by `_cmd_trail_show`, `_cmd_trail_list`, `_cmd_trail_close`, and the auto-close helper.
- `_auto_close_trail_if_complete(tasks, path, closed_crumb_id)`: Called from `cmd_close` inside the FileLock block. Looks up `closed_crumb_id`'s `links.parent`, checks if the parent is a trail, verifies all children are closed, and if so closes the trail with a second `write_tasks` call.
- `_auto_reopen_trail_if_needed(tasks, path, trail_id, crumb_status)`: Called from `cmd_link` inside the FileLock block when `--parent` is set. If the trail is closed and the crumb status is not closed, reopens the trail with a second `write_tasks` call.

**cmd_trail dispatcher**: Dispatches on `args.trail_command` to four private sub-handlers. Returns `die()` if trail_command is unrecognized.

**_cmd_trail_create**: Uses `FileLock`, reads `config.next_trail_id` for the T-prefixed ID (`{prefix}-T{n}`), increments counter in config, builds a record with `type="trail"`, and appends to `tasks.jsonl`.

**_cmd_trail_show**: Reads tasks without a lock (read-only). Finds the trail, prints its fields, then prints all children from `_get_trail_children` with completion count header.

**_cmd_trail_list**: Reads tasks without a lock. Filters by `type="trail"`, prints one line per trail with `{X}/{Y} closed` completion count.

**_cmd_trail_close**: Uses `FileLock`. Rejects with exit 1 if any children are not closed (lists them on stderr). Otherwise stamps `status=closed` and `closed_at`.

**cmd_close hook** (line ~822): After `write_tasks(path, tasks)`, iterates over the `closed` list and calls `_auto_close_trail_if_complete(tasks, path, crumb_id)` for each.

**cmd_link hook** (line ~939): After `write_tasks(path, tasks)`, calls `_auto_reopen_trail_if_needed(tasks, path, args.link_parent, crumb.get("status", "open"))` if `args.link_parent` is set.

## Correctness Review

**crumb.py** (all changed sections):

- AC1 (trail create with AF-T{n} ID): `_cmd_trail_create` uses `f"{prefix}-T{next_trail_id}"`. Confirmed: created AF-T1 and AF-T2.
- AC2 (trail show with child crumbs): `_cmd_trail_show` calls `_get_trail_children` and prints children table with completion count. Confirmed: showed AF-3 as open child of AF-T1.
- AC3 (trail list with X/Y closed): `_cmd_trail_list` computes `{closed_count}/{total} closed` per trail. Confirmed: showed `0/1 closed` and `0/0 closed`.
- AC4 (trail close exits 1 with open children): `_cmd_trail_close` checks `open_children` and calls `sys.exit(1)` with stderr list. Confirmed exit code 1 with open child listed.
- AC5 (auto-close on last child close): `_auto_close_trail_if_complete` called from `cmd_close` after its write. Confirmed: closing AF-3 printed "auto-closed trail AF-T1" and trail showed status=closed.
- AC6 (auto-reopen on new open child link): `_auto_reopen_trail_if_needed` called from `cmd_link` when `--parent` is set. Confirmed: linking AF-4 (open) to closed AF-T1 printed "auto-reopened trail AF-T1" and trail showed status=open.

No regressions: the only modifications to existing functions were two single-line hook call additions to `cmd_close` and `cmd_link`.

## Build/Test Validation

Smoke tested all 6 acceptance criteria manually against the temp `.crumbs/` directory. All passed. No test suite exists for crumb.py (adjacent issue, not fixed).

## Acceptance Criteria Checklist

- [x] `crumb trail create --title 'test trail'` creates trail entry with AF-T{n} ID format in tasks.jsonl — PASS
- [x] `crumb trail show <id>` displays trail fields plus list of all child crumbs with their statuses — PASS
- [x] `crumb trail list` shows all trails with 'X/Y closed' completion counts — PASS
- [x] `crumb trail close <id>` exits 1 with stderr listing open children if any exist — PASS
- [x] Closing the last open child of a trail auto-closes the trail (sets status=closed, closed_at) — PASS
- [x] Linking a new open crumb to a closed trail as parent auto-reopens the trail — PASS
