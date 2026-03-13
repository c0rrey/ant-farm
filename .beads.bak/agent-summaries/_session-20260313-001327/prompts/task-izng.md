# Task Brief: ant-farm-izng
**Task**: Implement crumb doctor command
**Agent Type**: python-pro
**Summary output path**: .beads/agent-summaries/_session-20260313-001327/summaries/izng.md

## Context
- **Affected files**: crumb.py:L672-674 (cmd_doctor stub), crumb.py:L839-840 (doctor parser registration -- note: currently has NO --fix argument)
- **Root cause**: N/A (new feature) -- cmd_doctor is an unimplemented stub that dies with "not yet implemented"
- **Expected behavior**: Data validation and repair: crumb doctor checks for malformed JSON lines, dangling blocked_by references (warning), dangling parent links (error), duplicate IDs (error), orphan crumbs (warning). Optional --fix removes dangling references.
- **Acceptance criteria**:
  1. crumb doctor reports malformed JSON lines with line numbers
  2. Dangling blocked_by references are flagged as warnings (not errors)
  3. Dangling parent links (pointing to non-existent trail) are flagged as errors
  4. Duplicate IDs are flagged as errors
  5. Orphan crumbs (no parent trail) are flagged as warnings
  6. crumb doctor --fix removes dangling blocked_by references and reports fixes applied
  7. Clean data produces 'No issues found' and exits 0

## Scope Boundaries
Read ONLY:
- crumb.py:L1-42 (module docstring, imports)
- crumb.py:L44-62 (constants: VALID_STATUSES, VALID_PRIORITIES, VALID_TYPES)
- crumb.py:L66-73 (die helper)
- crumb.py:L105-123 (path helpers)
- crumb.py:L171-233 (read_tasks, write_tasks, iter_jsonl -- especially iter_jsonl for line-level parsing)
- crumb.py:L236-267 (FileLock -- needed for --fix writes)
- crumb.py:L320-332 (require_tasks_jsonl)
- crumb.py:L340-353 (_find_crumb)
- crumb.py:L672-674 (cmd_doctor stub to replace)
- crumb.py:L839-840 (doctor parser -- must add --fix argument here)

Do NOT edit:
- crumb.py:L384-619 (cmd_list, cmd_show, cmd_create)
- crumb.py:L622-669 (cmd_update through cmd_import -- other command implementations)
- crumb.py:L714-836 (parser sections for other commands)
- crumb.py:L850-866 (main entry point)

## Focus
Your task is ONLY to implement cmd_doctor in crumb.py and add the --fix argument to the doctor parser.
Do NOT fix adjacent issues you notice.

Important implementation details:
- The doctor parser at crumb.py:L839-840 currently has NO --fix argument -- you must add `p_doctor.add_argument("--fix", ...)` to the parser
- For malformed JSON detection: do NOT reuse read_tasks() (it silently skips bad lines). Instead, read the file line-by-line yourself and track line numbers for reporting
- The "parent" field on crumbs links to a trail ID. A "dangling parent" means parent points to an ID that either does not exist or is not type "trail"
- "Orphan crumbs" are non-trail records with no "parent" field (or parent is empty/null)
- Duplicate IDs: two or more records with the same "id" value
- For --fix: use FileLock (crumb.py:L241-267) and write_tasks (crumb.py:L196-210) for atomic writes
- --fix should only remove dangling blocked_by references (not fix other issues like duplicates or dangling parents, which require manual intervention)
- Exit code: 0 if no issues found, 1 if errors found (warnings alone should still exit 0)
- Note: Earlier waves may have expanded crumb.py beyond these line numbers. Read the full file first to locate the actual current positions of stubs and parser code.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
