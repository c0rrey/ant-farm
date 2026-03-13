# Task Brief: ant-farm-jmvi
**Task**: Implement trail commands
**Agent Type**: python-pro
**Summary output path**: .beads/agent-summaries/_session-20260313-001327/summaries/jmvi.md

## Context
- **Affected files**: crumb.py:L390-392 (stub function cmd_trail), crumb.py:L529-553 (argparse registration for trail subcommands: list, show, create, close)
- **Root cause**: N/A (new feature) -- trail subcommand is a single stub function that calls die("not yet implemented"), but the parser already routes to four sub-subcommands (list, show, create, close) via trail_command
- **Expected behavior**: Trail (epic) management: crumb trail create with T-prefixed auto-ID, crumb trail show with child crumb listing, crumb trail list with completion summaries, crumb trail close with open-children rejection. Auto-close when last child closes, auto-reopen when new open crumb linked.
- **Acceptance criteria**:
  1. crumb trail create --title 'test trail' creates trail entry with AF-T{n} ID format in tasks.jsonl
  2. crumb trail show <id> displays trail fields plus list of all child crumbs with their statuses
  3. crumb trail list shows all trails with 'X/Y closed' completion counts
  4. crumb trail close <id> exits 1 with stderr listing open children if any exist
  5. Closing the last open child of a trail auto-closes the trail (sets status=closed, closed_at)
  6. Linking a new open crumb to a closed trail as parent auto-reopens the trail

## Scope Boundaries
Read ONLY:
- crumb.py:L1-63 (module docstring, imports, constants -- VALID_TYPES at L62 includes "trail")
- crumb.py:L70-73 (die() helper)
- crumb.py:L130-164 (read_config, write_config -- needed for next_trail_id counter)
- crumb.py:L171-234 (read_tasks, write_tasks, iter_jsonl -- JSONL I/O utilities)
- crumb.py:L241-268 (FileLock context manager)
- crumb.py:L310-312 (now_iso() timestamp helper)
- crumb.py:L320-332 (require_tasks_jsonl() guard)
- crumb.py:L390-392 (current stub function you will replace)
- crumb.py:L529-553 (argparse registration -- already complete, with trail_command dispatching)
- cmd_close implementation (implemented by ant-farm-cmcd earlier in this wave -- understand how close sets status/closed_at for auto-close behavior)
- cmd_link implementation (implemented by ant-farm-h7af earlier in this wave -- understand how --parent sets links.parent for auto-reopen trigger)

Do NOT edit:
- crumb.py:L340-382 (cmd_list, cmd_show, cmd_create, cmd_update, cmd_close, cmd_reopen, cmd_ready, cmd_blocked, cmd_link implementations)
- crumb.py:L385-388 (cmd_search stub)
- crumb.py:L395-408 (cmd_tree, cmd_import, cmd_doctor stubs)
- crumb.py:L415-528 (build_parser -- non-trail parser sections)
- crumb.py:L555-599 (tree/import/doctor parser + main entry point)

## Focus
Your task is ONLY to implement the cmd_trail function in crumb.py, replacing the stub at L390-392.

Do NOT fix adjacent issues you notice. Do NOT add or modify argparse arguments (they are already registered at L529-553). Do NOT modify any other stub functions.

The cmd_trail function must dispatch on args.trail_command to handle four sub-subcommands:
- **trail create**: Generate a new trail record with type="trail", auto-ID using AF-T{n} format from config.next_trail_id, write to tasks.jsonl, increment next_trail_id in config.json
- **trail show**: Find trail by ID, list all child crumbs (records whose links.parent == trail ID), display trail fields plus child listing with statuses
- **trail list**: Filter all records with type="trail", display each with completion counts (X/Y closed children)
- **trail close**: Reject if any child crumbs are still open (exit 1 with stderr listing them); otherwise set status=closed and closed_at

**Auto-close behavior (AC #5)**: When cmd_close closes a crumb, check if the crumb has a links.parent pointing to a trail. If so, check if all other children of that trail are also closed. If yes, auto-close the trail. This requires modifying the cmd_close function (implemented by ant-farm-cmcd). Since you cannot edit cmd_close directly, implement the auto-close check as a helper function that cmd_close can call. Document this cross-cutting concern in your summary doc.

**IMPORTANT**: The auto-close (AC #5) and auto-reopen (AC #6) behaviors cross-cut with cmd_close and cmd_link from earlier tasks. You have two options:
1. Add a helper function (e.g., `check_trail_auto_close(records, crumb)`) that the existing cmd_close can be updated to call, and similarly for cmd_link auto-reopen. You MAY minimally modify cmd_close and cmd_link to add these hook calls since the behavior is specified in YOUR acceptance criteria.
2. Implement the auto-close/reopen logic entirely within cmd_trail's sub-handlers if architecturally feasible.

Document your choice in the Design step. Minimal modifications to cmd_close/cmd_link are acceptable ONLY for adding auto-close/auto-reopen hook calls as specified in AC #5 and #6.

All operations must use FileLock (L241-268) for concurrency safety and write_tasks (L196-210) for atomic persistence. Trail creation must also use read_config/write_config (L130-164) for next_trail_id.

**Serial execution note**: This task runs third (last) in Wave 3, after ant-farm-cmcd and ant-farm-h7af. Both cmd_close and cmd_link will already be implemented. Read the updated crumb.py to get accurate line numbers before implementing.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
