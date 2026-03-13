# Task Brief: ant-farm-cmcd
**Task**: Implement crumb update, close, reopen commands
**Agent Type**: python-pro
**Summary output path**: .beads/agent-summaries/_session-20260313-001327/summaries/cmcd.md

## Context
- **Affected files**: crumb.py:L355-367 (stub functions cmd_update, cmd_close, cmd_reopen), crumb.py:L482-499 (argparse registration for update, close, reopen)
- **Root cause**: N/A (new feature) -- mutation commands are currently stub functions that call die("not yet implemented")
- **Expected behavior**: Mutation commands: crumb update for field changes and note appending, crumb close for multi-ID closing with closed_at stamps (idempotent), crumb reopen for closed-to-open transitions. Invalid transitions exit 1 with guidance.
- **Acceptance criteria**:
  1. crumb update <id> --status in_progress changes status field in tasks.jsonl entry
  2. crumb update <id> --note 'test note' appends timestamped entry to notes array
  3. crumb close <id1> <id2> closes both crumbs, each gets closed_at timestamp
  4. crumb close <already-closed-id> exits 0 without error (idempotent)
  5. crumb reopen <id> sets status back to open and clears closed_at field
  6. Attempting closed to in_progress exits 1 with stderr guidance to use reopen first

## Scope Boundaries
Read ONLY:
- crumb.py:L1-63 (module docstring, imports, constants -- VALID_STATUSES at L60)
- crumb.py:L70-73 (die() helper)
- crumb.py:L171-234 (read_tasks, write_tasks, iter_jsonl -- JSONL I/O utilities)
- crumb.py:L241-268 (FileLock context manager)
- crumb.py:L310-312 (now_iso() timestamp helper)
- crumb.py:L320-332 (require_tasks_jsonl() guard)
- crumb.py:L355-367 (current stub functions you will replace)
- crumb.py:L482-499 (argparse registration -- already complete, do not modify)

Do NOT edit:
- crumb.py:L340-352 (cmd_list, cmd_show, cmd_create -- other task's stubs or implementations)
- crumb.py:L370-408 (cmd_ready, cmd_blocked, cmd_link, cmd_search, cmd_trail, cmd_tree, cmd_import, cmd_doctor stubs)
- crumb.py:L415-575 (build_parser function -- parser args are already registered)
- crumb.py:L583-599 (main() entry point)

## Focus
Your task is ONLY to implement the cmd_update, cmd_close, and cmd_reopen functions in crumb.py, replacing the stub implementations at L355-367.

Do NOT fix adjacent issues you notice. Do NOT add or modify argparse arguments (they are already registered at L482-499). Do NOT modify any other stub functions. If the existing argparse registration for update includes --title, --priority, --description flags (L486-488), your cmd_update implementation should handle those fields as well.

All three commands must use FileLock (L241-268) for concurrency safety and write_tasks (L196-210) for atomic persistence. Use now_iso() (L310-312) for timestamps.

**Serial execution note**: This task runs first in Wave 3. After you commit, the same agent session will proceed to ant-farm-h7af (link command) and then ant-farm-jmvi (trail commands). Your implementation of cmd_close will be used by the trail auto-close feature in ant-farm-jmvi, so ensure cmd_close correctly sets status="closed" and adds a closed_at timestamp to each record.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
