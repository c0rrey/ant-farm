Execute task for ant-farm-dhh8.

Step 0: Read your task context from .beads/agent-summaries/_session-20260313-001327/prompts/task-dhh8.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-dhh8` + `bd update ant-farm-dhh8 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-dhh8)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-20260313-001327/summaries/dhh8.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-dhh8`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-dhh8
**Task**: Implement crumb search and tree commands
**Agent Type**: python-pro
**Summary output path**: .beads/agent-summaries/_session-20260313-001327/summaries/dhh8.md

## Context
- **Affected files**: crumb.py:L652-654 (cmd_search stub), crumb.py:L662-664 (cmd_tree stub), crumb.py:L792-794 (search parser), crumb.py:L823-825 (tree parser)
- **Root cause**: N/A (new feature) -- cmd_search and cmd_tree are unimplemented stubs that die with "not yet implemented"
- **Expected behavior**: Search and visualization: crumb search performs case-insensitive full-text search across titles and descriptions. crumb tree shows all trails and children as indented hierarchy, optionally scoped to a single trail.
- **Acceptance criteria**:
  1. crumb search 'keyword' returns crumbs/trails matching keyword in title or description
  2. Search is case-insensitive ('Rate' matches 'rate')
  3. crumb tree displays hierarchical view with trails as parents and child crumbs indented
  4. crumb tree <trail-id> shows only the specified trail and its children
  5. Empty search results produce no output and exit 0

## Scope Boundaries
Read ONLY:
- crumb.py:L1-42 (module docstring, imports)
- crumb.py:L44-62 (constants)
- crumb.py:L66-73 (die helper)
- crumb.py:L105-123 (path helpers)
- crumb.py:L171-193 (read_tasks)
- crumb.py:L320-332 (require_tasks_jsonl)
- crumb.py:L340-368 (_find_crumb, _priority_sort_key)
- crumb.py:L384-470 (cmd_list -- reference for output format)
- crumb.py:L652-654 (cmd_search stub to replace)
- crumb.py:L662-664 (cmd_tree stub to replace)
- crumb.py:L792-794 (search parser -- has "query" positional arg)
- crumb.py:L823-825 (tree parser -- has optional "id" positional arg)

Do NOT edit:
- crumb.py:L384-650 (cmd_list through cmd_link implementations)
- crumb.py:L656-660 (cmd_trail -- Wave 3 implementation)
- crumb.py:L667-674 (cmd_import, cmd_doctor -- other Wave 4 tasks)
- crumb.py:L714-790 (parser sections for other commands)
- crumb.py:L796-842 (trail, import, doctor parsers)
- crumb.py:L850-866 (main entry point)

## Focus
Your task is ONLY to implement cmd_search and cmd_tree in crumb.py.
Do NOT fix adjacent issues you notice.

Important implementation details:
- Search: iterate all records (both crumbs and trails), check if query appears in title or description (case-insensitive). Use str.lower() or similar for comparison.
- Search output: use a compact format similar to cmd_list output (crumb.py:L454-469) showing ID, priority, status, and title for each match
- Tree display: group records by parent trail. For each trail (type == "trail"), print the trail, then print its children (records where parent == trail_id) indented with 2-4 spaces
- Tree with ID argument: show only the specified trail and its children; die with error if trail not found
- Records with no parent (orphan crumbs) should appear under a special section or at the top level
- The tree parser at crumb.py:L823-825 already has an optional "id" positional argument (nargs="?")
- The search parser at crumb.py:L792-794 already has a "query" positional argument
- Empty search results: print nothing and exit 0 (do NOT print "no results found")
- Note: Earlier waves may have expanded crumb.py beyond these line numbers. Read the full file first to locate the actual current positions of stubs and parser code.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
