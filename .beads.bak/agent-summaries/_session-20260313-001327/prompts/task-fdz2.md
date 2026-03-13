# Task Brief: ant-farm-fdz2
**Task**: Implement crumb import and --from-beads migration
**Agent Type**: python-pro
**Summary output path**: .beads/agent-summaries/_session-20260313-001327/summaries/fdz2.md

## Context
- **Affected files**: crumb.py:L667-669 (cmd_import stub), crumb.py:L828-836 (import parser registration with --from-beads flag already defined)
- **Root cause**: N/A (new feature) -- cmd_import is an unimplemented stub that dies with "not yet implemented"
- **Expected behavior**: Bulk import and migration: crumb import validates and imports JSONL entries with duplicate detection and counter updates. crumb import --from-beads converts Beads format with priority mapping, epic-to-trail conversion, and dependency mapping.
- **Acceptance criteria**:
  1. crumb import file.jsonl imports valid JSONL entries and reports count of imported items
  2. Malformed JSON lines are skipped with stderr warning including line number
  3. Duplicate IDs against existing entries are skipped with stderr warning
  4. crumb import --from-beads .beads/issues.jsonl converts beads format to crumb format
  5. Beads priority mapping: 0 to P0, 1 to P1, 2 to P2, 3 to P3, 4 to P4
  6. Beads type 'epic' becomes type 'trail' with T-prefixed ID
  7. next_crumb_id/next_trail_id in config.json updated to exceed highest imported ID

## Scope Boundaries
Read ONLY:
- crumb.py:L1-42 (module docstring, imports)
- crumb.py:L44-62 (constants: VALID_STATUSES, VALID_PRIORITIES, VALID_TYPES)
- crumb.py:L66-73 (die helper)
- crumb.py:L105-123 (path helpers)
- crumb.py:L130-163 (read_config, write_config -- needed for counter updates)
- crumb.py:L171-210 (read_tasks, write_tasks)
- crumb.py:L236-267 (FileLock -- needed for atomic import writes)
- crumb.py:L320-332 (require_tasks_jsonl)
- crumb.py:L340-353 (_find_crumb -- for duplicate detection)
- crumb.py:L524-619 (cmd_create -- reference for record structure and ID assignment patterns)
- crumb.py:L667-669 (cmd_import stub to replace)
- crumb.py:L828-836 (import parser -- --from-beads flag already registered)
- .beads/issues.jsonl (read-only reference for Beads format during --from-beads development)

Do NOT edit:
- crumb.py:L384-519 (cmd_list, cmd_show)
- crumb.py:L524-664 (other command implementations)
- crumb.py:L672-674 (cmd_doctor -- other Wave 4 task)
- crumb.py:L714-825 (parser sections for other commands)
- crumb.py:L839-866 (doctor parser and main)

## Focus
Your task is ONLY to implement cmd_import in crumb.py with both plain JSONL import and --from-beads migration mode.
Do NOT fix adjacent issues you notice.

Important implementation details:
- The import parser at crumb.py:L828-836 already has the --from-beads flag and file positional argument
- For plain JSONL import: read input file line-by-line, parse each as JSON, skip malformed lines with stderr warning, skip duplicate IDs with stderr warning, append valid entries to tasks.jsonl
- For --from-beads: Beads JSONL has fields like "id", "title", "description", "type", "priority" (integer 0-4), "status", "labels", "created", "updated"
- Priority mapping: Beads uses integers (0=P0, 1=P1, 2=P2, 3=P3, 4=P4) -- map to string format
- Type mapping: Beads type "epic" becomes crumb type "trail"; Beads type "task"/"bug"/"feature" stay the same
- ID mapping for epics: when Beads type is "epic", generate a T-prefixed trail ID (e.g., "T-1", "T-2") using next_trail_id from config
- For non-epic types: use the Beads ID as-is or generate from next_crumb_id if it conflicts
- After import: update next_crumb_id and next_trail_id in config.json to exceed the highest imported numeric ID
- Use FileLock (crumb.py:L241-267) for all writes
- Reference cmd_create (crumb.py:L524-619) for record creation patterns
- Note: Earlier waves may have expanded crumb.py beyond these line numbers. Read the full file first to locate the actual current positions of stubs and parser code.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
