# Task Brief: ant-farm-l7pk
**Task**: Implement crumb create, show, list commands
**Agent Type**: python-pro
**Summary output path**: .beads/agent-summaries/_session-20260313-001327/summaries/l7pk.md

## Context
- **Affected files**:
  - `crumb.py:L340-352` -- stub functions to replace: `cmd_list` (L340-342), `cmd_show` (L345-347), `cmd_create` (L350-352). Each currently calls `die("crumb <cmd> not yet implemented")`.
  - `crumb.py:L415-575` -- `build_parser()` already registers all three subcommands with argparse flags: list (L448-465), show (L468-470), create (L473-479). Parser wiring is complete; do NOT modify parser registration.
- **Root cause**: N/A (new feature) -- crumb.py exists with CLI framework scaffolding (created by Wave 1 task ant-farm-mg0r) but the three stub functions only print "not yet implemented" and exit.
- **Expected behavior**: Core CRUD read commands: crumb create with auto-ID and --from-json, crumb show for full detail display, crumb list with composable filter flags (--open, --closed, --priority, --type, --sort, --limit, --short, etc.).
- **Acceptance criteria**:
  1. `crumb create --title 'test task'` creates entry in tasks.jsonl with auto-assigned ID matching config prefix
  2. `crumb create --from-json '{"title":"test","priority":"P1","type":"task"}'` creates with explicit fields, auto-assigns ID if omitted
  3. `crumb show <id>` displays all fields (title, status, priority, description, acceptance_criteria, scope, links, notes, timestamps)
  4. `crumb list --open --priority P1 --sort priority --limit 5` correctly applies all filters, sorts, and limits
  5. `crumb list --short` shows compact one-line-per-crumb output (ID, title, status, priority only)
  6. `crumb list --after 2026-03-12` returns only crumbs created after the specified ISO 8601 date
  7. Creating a crumb with a duplicate ID exits 1 with stderr error message

## Existing Infrastructure (Read ONLY -- do NOT modify)
The following utilities in crumb.py are available for your implementations:
- `crumb.py:L48-62` -- Constants: VALID_STATUSES, VALID_PRIORITIES, VALID_TYPES, DEFAULT_CONFIG (prefix, default_priority, next_crumb_id)
- `crumb.py:L70-73` -- `die(message, code=1)` -- print to stderr and sys.exit
- `crumb.py:L130-146` -- `read_config()` -- returns dict with keys: prefix, default_priority, next_crumb_id, next_trail_id
- `crumb.py:L149-163` -- `write_config(config)` -- atomic write of config.json
- `crumb.py:L171-193` -- `read_tasks(path)` -- returns List[Dict] from JSONL
- `crumb.py:L196-210` -- `write_tasks(path, records)` -- atomic write records to JSONL
- `crumb.py:L213-233` -- `iter_jsonl(path)` -- lazy iterator over JSONL records
- `crumb.py:L241-267` -- `FileLock` -- context manager for exclusive flock on tasks.lock
- `crumb.py:L310-312` -- `now_iso()` -- returns UTC ISO 8601 timestamp string
- `crumb.py:L320-332` -- `require_tasks_jsonl()` -- returns Path to tasks.jsonl or exits

## Scope Boundaries
Read ONLY: `crumb.py:L1-599` (full file for context), with particular attention to the infrastructure listed above
Edit ONLY: `crumb.py:L340-352` (replace the three stub function bodies: cmd_list, cmd_show, cmd_create)
Do NOT edit: `crumb.py:L1-339` (directory discovery, config I/O, JSONL utilities, file locking, cleanup, timestamp helpers), `crumb.py:L355-408` (other stub functions for downstream tasks), `crumb.py:L415-599` (argument parser, entry point -- parser wiring is already complete)

## Focus
Your task is ONLY to implement the crumb create, crumb show, and crumb list subcommands by replacing the stub function bodies at `crumb.py:L340-352`.
Do NOT fix adjacent issues you notice.
Do NOT refactor the CLI framework or infrastructure code from Wave 1.
Do NOT modify the argument parser -- all flags are already registered at `crumb.py:L448-479`.
If you find issues in the Wave 1 scaffolding, document them in your summary doc under "Adjacent Issues Found" but do NOT fix them.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
