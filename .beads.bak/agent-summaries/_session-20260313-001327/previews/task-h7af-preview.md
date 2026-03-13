Execute task for ant-farm-h7af.

Step 0: Read your task context from .beads/agent-summaries/_session-20260313-001327/prompts/task-h7af.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-h7af` + `bd update ant-farm-h7af --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-h7af)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-20260313-001327/summaries/h7af.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-h7af`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-h7af
**Task**: Implement crumb link command
**Agent Type**: python-pro
**Summary output path**: .beads/agent-summaries/_session-20260313-001327/summaries/h7af.md

## Context
- **Affected files**: crumb.py:L380-382 (stub function cmd_link), crumb.py:L516-522 (argparse registration for link subcommand)
- **Root cause**: N/A (new feature) -- link command is a stub function that calls die("not yet implemented")
- **Expected behavior**: Link management: crumb link for setting/changing parent trail links, appending/removing blocked_by entries, and setting discovered_from provenance. All operations use flock + atomic write. Dangling references allowed (caught by doctor).
- **Acceptance criteria**:
  1. crumb link <id> --parent <trail-id> sets links.parent field in the crumb's JSONL entry
  2. crumb link <id> --blocked-by <other-id> appends to links.blocked_by array (no duplicates)
  3. crumb link <id> --remove-blocked-by <other-id> removes the specified ID from links.blocked_by
  4. crumb link <id> --discovered-from <other-id> sets links.discovered_from field
  5. Running crumb show <id> after link operations reflects the updated link fields
  6. All link operations acquire flock and use atomic write

## Scope Boundaries
Read ONLY:
- crumb.py:L1-63 (module docstring, imports, constants)
- crumb.py:L70-73 (die() helper)
- crumb.py:L171-234 (read_tasks, write_tasks, iter_jsonl -- JSONL I/O utilities)
- crumb.py:L241-268 (FileLock context manager)
- crumb.py:L310-312 (now_iso() timestamp helper)
- crumb.py:L320-332 (require_tasks_jsonl() guard)
- crumb.py:L380-382 (current stub function you will replace)
- crumb.py:L516-522 (argparse registration -- already complete, verify flag names match your implementation)
- cmd_show implementation (wherever it exists after Wave 2 -- read to understand how show displays link fields for AC #5)

Do NOT edit:
- crumb.py:L340-367 (cmd_list, cmd_show, cmd_create, cmd_update, cmd_close, cmd_reopen -- other tasks' implementations)
- crumb.py:L370-378 (cmd_ready, cmd_blocked stubs)
- crumb.py:L385-408 (cmd_search, cmd_trail, cmd_tree, cmd_import, cmd_doctor stubs)
- crumb.py:L415-575 (build_parser function -- parser args are already registered)
- crumb.py:L583-599 (main() entry point)

## Focus
Your task is ONLY to implement the cmd_link function in crumb.py, replacing the stub at L380-382.

Do NOT fix adjacent issues you notice. Do NOT add or modify argparse arguments (they are already registered at L516-522). Do NOT modify any other stub functions.

The link command manages the `links` dict within each crumb's JSONL record. The expected structure is:
```json
{
  "links": {
    "parent": "<trail-id or null>",
    "blocked_by": ["<id1>", "<id2>"],
    "discovered_from": "<id or null>"
  }
}
```

Multiple flags can be combined in one invocation (e.g., --parent and --blocked-by together). Dangling references are allowed -- do NOT validate that referenced IDs exist (the doctor command handles that).

All operations must use FileLock (L241-268) for concurrency safety and write_tasks (L196-210) for atomic persistence.

**Serial execution note**: This task runs second in Wave 3, after ant-farm-cmcd. The cmd_update, cmd_close, cmd_reopen implementations will already be in place when you start. Read the updated crumb.py to get accurate line numbers before implementing.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
