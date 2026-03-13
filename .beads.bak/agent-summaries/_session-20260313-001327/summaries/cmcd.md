# Task Summary: ant-farm-cmcd

## Approaches Considered

1. **In-place dict mutation inside FileLock (selected)** — Read tasks into a list, find the target record by ID using `_find_crumb`, mutate the dict in place, then call `write_tasks` for atomic rename. Directly mirrors how `cmd_create` works. Minimal code, zero new abstractions.

2. **Functional map() with new dicts** — Instead of mutating in place, build new dicts via `{**old, **changes}` for each record. Avoids aliasing bugs but makes the ID-lookup pattern more awkward (must reconstruct the entire list even for a single change).

3. **Shared `_mutate_task` helper** — Extract a single mutation helper called by all three commands. Good for DRY if the three commands had shared logic, but they have mostly distinct mutation patterns (status transition guard, note append, closed_at stamp). Would add indirection without reducing code.

4. **Class-based TaskEditor context manager** — A context manager that loads tasks on `__enter__` and saves on `__exit__`, letting commands just mutate records without calling `write_tasks` explicitly. Elegant but over-engineered for a single-file stdlib script with only three new functions.

## Selected Approach

Approach 1: in-place dict mutation inside `FileLock`. Rationale: matches the existing codebase pattern (see `cmd_create`), requires no new abstractions, and keeps the code minimal and readable. The FileLock + read + mutate + write_tasks pattern is already the established idiom.

## Implementation Description

Three functions replaced the stub implementations at crumb.py L622-634:

- `cmd_update`: Acquires FileLock, reads tasks, finds crumb by ID. Applies status (with transition guard that rejects closed->non-open), title, priority, description changes. Appends timestamped note entries to the `notes` array. Skips write if nothing changed. Always stamps `updated_at`.

- `cmd_close`: Acquires FileLock once for all IDs, collects `closed` and `skipped` lists. Unknown IDs exit 1 immediately via `die()`. Already-closed IDs are silently skipped (idempotent). Closed crumbs get `status="closed"`, `closed_at=now_iso()`, `updated_at=now_iso()`. Only writes if at least one crumb was actually closed.

- `cmd_reopen`: Acquires FileLock, finds crumb, rejects non-closed crumbs with an informative error, then sets `status="open"`, removes `closed_at` via `dict.pop`, and stamps `updated_at`.

## Correctness Review

**crumb.py** (changed sections L622-755):

- AC1 (update --status in_progress): `cmd_update` applies `args.status` after the transition guard; sets `changed=True`; calls `write_tasks`. Confirmed by smoke test showing status field updated.
- AC2 (update --note): Note entry formatted as `"{iso}: {note}"`, appended to `notes` list (created if absent). Confirmed by smoke test showing Notes list with timestamp.
- AC3 (close multi-ID): `args.ids` is a list; loop closes each independently, stamps `closed_at` on each. Confirmed by smoke test showing both AF-1 and AF-2 closed with `Closed At` field.
- AC4 (close idempotent): Already-closed check before mutation; skipped IDs print "already closed" but return exit 0. Confirmed.
- AC5 (reopen clears closed_at): `crumb.pop("closed_at", None)` removes the field; `status` set to `"open"`. Confirmed by smoke test showing no `Closed At` field after reopen.
- AC6 (closed->in_progress exits 1): Transition guard: `if current_status == "closed" and args.status != "open": die(...)`. Confirmed exit code 1 with correct stderr message.

No regressions: functions outside scope (cmd_ready, cmd_blocked, cmd_link, cmd_search, cmd_trail, cmd_tree, cmd_import, cmd_doctor, build_parser, main) were not modified.

## Build/Test Validation

Smoke tested all 6 acceptance criteria manually against a temp `.crumbs/` directory using the actual crumb.py binary. All passed. No test suite exists for crumb.py yet (noted as adjacent issue, not fixed).

## Acceptance Criteria Checklist

- [x] `crumb update <id> --status in_progress` changes status field in tasks.jsonl entry — PASS
- [x] `crumb update <id> --note 'test note'` appends timestamped entry to notes array — PASS
- [x] `crumb close <id1> <id2>` closes both crumbs, each gets closed_at timestamp — PASS
- [x] `crumb close <already-closed-id>` exits 0 without error (idempotent) — PASS
- [x] `crumb reopen <id>` sets status back to open and clears closed_at field — PASS
- [x] Attempting closed to in_progress exits 1 with stderr guidance to use reopen first — PASS
