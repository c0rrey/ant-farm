# Task Summary: ant-farm-l7pk

**Task**: Implement crumb create, show, list commands
**Commit**: `41004c4`
**File modified**: `crumb.py`

---

## 1. Approaches Considered

**Approach A: Inline imperative style (all logic in function bodies)**
Write every branch and loop directly inside `cmd_list`, `cmd_show`, and `cmd_create` with no helper extraction. Simple and self-contained, but causes code duplication: both `cmd_show` and `cmd_create` need to find a crumb by ID, leading to the same loop appearing twice. Sort key logic for `cmd_list` also becomes inline lambda spaghetti.

**Approach B: Private module-level helpers (selected)**
Extract `_find_crumb`, `_priority_sort_key`, and `_status_sort_key` as private functions immediately above the three command functions. Each command is short, readable, and calls helpers for shared operations. No duplication. Follows the existing procedural style of crumb.py. Helpers are prefixed with `_` to signal they are internal, not part of the public API.

**Approach C: Class-based command dispatcher**
Wrap all three commands in a `CrumbCommands` class with methods `list()`, `show()`, and `create()`. This adds OOP structure but doesn't fit the existing module-level function style used throughout crumb.py (every other command is a `def cmd_*` function). Diverging from the established convention would make the file inconsistent and mislead downstream task authors.

**Approach D: Generator pipeline for list filtering**
Use `functools.reduce` or chained `filter()` calls to build the list pipeline as a series of generator transformations. More declarative and Pythonic for large datasets, but the tasks.jsonl dataset is expected to be small (hundreds of records at most), and the functional style adds abstraction that obscures the simple conditional logic without any memory or performance benefit at this scale.

---

## 2. Selected Approach with Rationale

**Approach B** — private helpers + direct command function bodies.

Rationale:
- Shared ID lookup (`_find_crumb`) is needed in both `cmd_show` and `cmd_create`; extracting it avoids duplication and makes the contract explicit.
- Sort key helpers (`_priority_sort_key`, `_status_sort_key`) keep lambda bodies in `cmd_list` readable and individually testable.
- Consistent with the existing procedural, function-per-command style of the rest of the file.
- stdlib-only, minimum Python 3.8 constraint satisfied.
- All filter flags from the parser are used directly via `args.*` attributes, requiring no additional mapping layer.

---

## 3. Implementation Description

Three private helpers were added between the section comment and the `cmd_list` function:

- `_find_crumb(tasks, crumb_id)`: Linear search returning the first dict matching `id`, or `None`. Used in `cmd_show` and `cmd_create`.
- `_priority_sort_key(priority)`: Maps `P0`–`P4` to integers 0–4; unknown values return 5 (sort last).
- `_status_sort_key(status)`: Maps `open`/`in_progress`/`closed` to 0/1/2; unknown values return 3.

`cmd_list`:
- Calls `require_tasks_jsonl()` then `read_tasks()`.
- Excludes `type == "trail"` records from the result set.
- Applies composable OR-logic status filters (`--open`, `--closed`, `--in-progress`), then independent AND-logic filters: `--priority`, `--type`, `--agent-type`, `--parent`, `--discovered`, `--after`.
- `--after DATE` uses lexicographic comparison against `created_at` ISO 8601 strings.
- Sorts by one of `priority`/`status`/`created_at` (default `created_at` ascending).
- Applies `--limit` slice.
- `--short` mode: prints `{id:<12} {priority:<4} {status:<12} {title}`.
- Full mode: adds `type` and `created_at[:10]` columns.

`cmd_show`:
- Calls `require_tasks_jsonl()` then `read_tasks()`.
- Finds the crumb with `_find_crumb`; exits 1 if not found.
- Iterates a fixed ordered field list printing label-value pairs. Lists print multi-line with `  - item` format. Empty/None/`[]`/`{}` values are skipped.
- Any unexpected keys not in the known list are printed at the end with auto-generated labels.

`cmd_create`:
- Runs entirely inside a `FileLock()` context manager to prevent concurrent writes.
- Creates `tasks.jsonl` implicitly if it doesn't exist yet.
- `--from-json` path: parses the JSON string; CLI flags (`--title`, `--priority`, `--type`, `--description`) override JSON payload fields if provided.
- `--title` path: builds a minimal payload dict; requires `--title` unless `--from-json` is present.
- ID assignment: if `id` is present in payload and non-empty, use it and check for duplicates (exits 1 with `error: crumb 'X' already exists`). Otherwise, auto-increment `next_crumb_id` from config, skipping any IDs that already exist, then write the updated config.
- Builds final record with defaults (`type=task`, `status=open`, `priority=config.default_priority`), carries over all extra payload fields.
- Validates status/priority/type against the module constants.
- Calls `write_tasks()` for atomic JSONL write.
- Prints `created {id}` on success.

---

## 4. Correctness Review

**crumb.py (changed sections L340–619)**

All private helpers:
- `_find_crumb`: correct linear scan, returns `Optional[Dict]`, handles empty list.
- `_priority_sort_key`: handles `P0`–`P4` correctly; `"P0"[1] = "0"` → `int("0") = 0`. Guards against non-`P?` strings with `else 5`.
- `_status_sort_key`: `.get(status, 3)` correctly handles unknowns.

`cmd_list` correctness:
- `args.filter_open` matches argparse `dest="filter_open"` at L449. Confirmed.
- `args.filter_closed` matches `dest="filter_closed"` at L450. Confirmed.
- `args.filter_in_progress` matches `dest="filter_in_progress"` at L451. Confirmed.
- `args.filter_type` matches `dest="filter_type"` at L454. Confirmed.
- `args.sort` has choices `["priority","created_at","status"]` with default `"created_at"`. Implementation handles all three. Confirmed.
- `--after` comparison: `"2026-03-13T04:00:00Z" > "2026-03-12"` → True (correct). `"2026-03-12T23:59:59Z" > "2026-03-13"` → False (correct, since `"2" < "3"` at the 9th character).
- Trail exclusion: filters `type != "trail"` before any other filter; trails won't appear in `crumb list` output.

`cmd_show` correctness:
- `args.id` matches `p_show.add_argument("id", metavar="ID")` at L469. Confirmed.
- Field list covers all acceptance criteria fields: title, status, priority, description, acceptance_criteria, scope, links, notes, created_at, updated_at.

`cmd_create` correctness:
- `args.crumb_type` matches `dest="crumb_type"` at L477. Confirmed.
- `args.from_json` matches `dest="from_json"` at L475. Confirmed.
- Lock acquired before reading tasks; config read inside lock; config written before tasks written — prevents TOCTOU race.
- `path.parent.mkdir(parents=True, exist_ok=True)` handles the case where `.crumbs/` doesn't exist yet (though `FileLock` would have failed first — minor defense-in-depth).
- Validation rejects invalid status/priority/type from `--from-json` payloads.
- `crumb_id` is assigned before the `print(f"created {crumb_id}")` line, which is outside the lock context (lock released on `write_tasks` return). Correct.

**Unmodified sections (L1–339, L621–end)**: not touched; downstream stubs, parser, and entry point intact.

---

## 5. Build/Test Validation

Manual functional tests run in `/tmp/crumb_test/` with a fresh `.crumbs/config.json`:

```
python3 crumb.py create --title 'test task'
  → created AF-1  (config.json next_crumb_id: 2)

python3 crumb.py create --from-json '{"title":"test","priority":"P1","type":"task"}'
  → created AF-2

python3 crumb.py show AF-1
  → ID / Type / Title / Status / Priority / Created At / Updated At all printed

python3 crumb.py create --from-json '{"title":"rich task",...all fields...}'
python3 crumb.py show AF-3
  → All fields including lists (acceptance_criteria, links, notes, blocked_by) shown correctly

python3 crumb.py list --open --priority P1 --sort priority --limit 5
  → Returns only P1 open crumbs, sorted by priority, max 5

python3 crumb.py list --short
  → Compact one-line output: ID, priority, status, title

python3 crumb.py list --after 2026-03-12
  → Returns all March 13 crumbs; crumbs with earlier dates would be excluded

python3 crumb.py create --from-json '{"id":"AF-1","title":"duplicate attempt"}'
  → error: crumb 'AF-1' already exists  (exit code 1)

python3 crumb.py show AF-99
  → error: crumb 'AF-99' not found  (exit code 1)

python3 crumb.py create
  → error: --title is required unless --from-json is provided  (exit code 1)

python3 crumb.py list --open --closed --sort status
  → Returns open AND closed crumbs (OR logic), sorted by status

python3 -m py_compile crumb.py
  → Syntax OK
```

---

## 6. Acceptance Criteria Checklist

- [x] `crumb create --title 'test task'` creates entry in tasks.jsonl with auto-assigned ID matching config prefix (AF-1). **PASS**
- [x] `crumb create --from-json '{"title":"test","priority":"P1","type":"task"}'` creates with explicit fields, auto-assigns ID if omitted (AF-2). **PASS**
- [x] `crumb show <id>` displays all fields (title, status, priority, description, acceptance_criteria, scope, links, notes, timestamps). **PASS**
- [x] `crumb list --open --priority P1 --sort priority --limit 5` correctly applies all filters, sorts, and limits. **PASS**
- [x] `crumb list --short` shows compact one-line-per-crumb output (ID, title, status, priority only). **PASS**
- [x] `crumb list --after 2026-03-12` returns only crumbs created after the specified ISO 8601 date. **PASS**
- [x] Creating a crumb with a duplicate ID exits 1 with stderr `error: crumb 'AF-1' already exists`. **PASS**

---

## Adjacent Issues Found

1. **`.beads/hooks/pre-commit` shim used stale `bd hook` API**: The `.beads/hooks/pre-commit` shim (generated by an older `bd` version) called `bd hook pre-commit` (singular). The current `bd` v0.56.1 uses `bd hooks run pre-commit` (plural). This caused every `git commit` to fail with `Error: unknown command "hook" for "bd"`. Fixed during this session by running `bd hooks install --beads --force` which regenerated the shim to v2. This is a `bd` version migration bug, not a crumb.py issue.
