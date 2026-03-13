Execute task for ant-farm-vxpr.

Step 0: Read your task context from .beads/agent-summaries/_session-20260313-001327/prompts/task-vxpr.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-vxpr` + `bd update ant-farm-vxpr --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-vxpr)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-20260313-001327/summaries/vxpr.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-vxpr`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-vxpr
**Task**: Implement crumb ready and blocked commands
**Agent Type**: python-pro
**Summary output path**: .beads/agent-summaries/_session-20260313-001327/summaries/vxpr.md

## Context
- **Affected files**: crumb.py:L637-644 (cmd_ready and cmd_blocked stubs), crumb.py:L769-780 (ready and blocked parser registration)
- **Root cause**: N/A (new feature) -- cmd_ready and cmd_blocked are unimplemented stubs that die with "not yet implemented"
- **Expected behavior**: Dependency-aware queries: crumb ready lists open crumbs with no unresolved blockers, crumb blocked lists open crumbs with unresolved blockers. The two commands produce disjoint sets covering all open crumbs.
- **Acceptance criteria**:
  1. crumb ready returns only open crumbs whose blocked_by entries are all closed or non-existent
  2. crumb ready --limit 5 --sort priority returns at most 5 results sorted by priority (P0 first)
  3. crumb blocked returns only open crumbs with at least one blocker that is open/in_progress and exists
  4. Crumbs with blocked_by references to non-existent IDs appear in ready (treated as resolved)
  5. For any set of open crumbs, ready union blocked = all open crumbs and ready intersect blocked = empty
  6. Both commands exclude closed and in_progress crumbs from their output

## Scope Boundaries
Read ONLY:
- crumb.py:L1-42 (module docstring, imports)
- crumb.py:L44-62 (constants: VALID_STATUSES, VALID_PRIORITIES, VALID_TYPES)
- crumb.py:L66-73 (die helper)
- crumb.py:L105-123 (path helpers: crumbs_dir, tasks_path, config_path, lock_path)
- crumb.py:L171-193 (read_tasks)
- crumb.py:L320-332 (require_tasks_jsonl)
- crumb.py:L340-368 (_find_crumb, _priority_sort_key)
- crumb.py:L384-470 (cmd_list for output format reference)
- crumb.py:L637-644 (cmd_ready and cmd_blocked stubs to replace)
- crumb.py:L769-780 (ready and blocked parser sections)

Do NOT edit:
- crumb.py:L384-470 (cmd_list -- read only for output format reference)
- crumb.py:L524-619 (cmd_create)
- crumb.py:L622-650 (cmd_update, cmd_close, cmd_reopen, cmd_link -- other stubs being implemented by prior waves)
- crumb.py:L652-674 (cmd_search, cmd_trail, cmd_tree, cmd_import, cmd_doctor -- other Wave 4 tasks)
- crumb.py:L682-842 (build_parser -- except parser registration for ready/blocked which likely already exists at L769-780)

## Focus
Your task is ONLY to implement cmd_ready and cmd_blocked functions in crumb.py.
Do NOT fix adjacent issues you notice.

Important implementation details:
- The blocked_by field on crumbs is a list of ID strings (e.g., ["AF-1", "AF-3"])
- A crumb is "ready" if status == "open" AND all IDs in its blocked_by list either (a) refer to closed crumbs, or (b) refer to non-existent IDs (treated as resolved)
- A crumb is "blocked" if status == "open" AND at least one ID in its blocked_by list refers to an existing crumb with status != "closed"
- Use _priority_sort_key (crumb.py:L356-368) for --sort priority
- Use the same output format as cmd_list (crumb.py:L454-469) for consistency
- The ready parser already supports --limit and --sort at crumb.py:L770-776
- Note: Earlier waves may have expanded crumb.py beyond these line numbers. Read the full file first to locate the actual current positions of stubs and parser code.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
