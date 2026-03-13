# Task Summary: ant-farm-izng
**Task**: Implement crumb doctor command
**Status**: Complete

## Approaches Considered

1. **Single-pass read_tasks + semantic checks** — Reuse `read_tasks()` for parsing, then do semantic validation. Fails criterion 1: `read_tasks()` silently skips bad lines without reporting line numbers.

2. **Raw line-by-line pass then semantic pass** — Two passes: first reads raw lines and detects malformed JSON with line numbers; second performs semantic checks on valid records. Clean separation of syntax vs semantic validation.

3. **Structured IssueReporter class** — Create a small class accumulating errors/warnings with add_error/add_warning methods. Clean API but unnecessary complexity for a single-file stdlib-only tool.

4. **Inline accumulation into two lists** — Use two lists (`errors`, `warnings`), populate inline during both passes, print at end, exit 1 if errors exist. Simplest approach, consistent with the codebase's stdlib-only style and no-classes preference for helpers.

## Selected Approach

**Approach 4 (inline accumulation with Approach 2's two-pass structure)**: Two passes using raw line read + two lists.

Rationale: The stdlib-only single-file constraint means no external dependencies. Using two named lists (errors, warnings) makes the exit-code logic trivial (`if errors: sys.exit(1)`) and clearly communicates severity distinction. The raw file open is required to detect malformed JSON with line numbers — `read_tasks()` cannot be reused for this.

## Implementation Description

`cmd_doctor(args)`:
- **Pass 1 (raw line read)**: Opens tasks.jsonl directly, iterates line-by-line, `json.loads()` each line. On `JSONDecodeError`, appends to `errors` with line number. Valid records collected in `valid_records`.
- **Lookup structures**: Builds `seen_ids` dict for duplicate detection and `id_to_record` dict for reference validation. Duplicate IDs → errors. `trail_ids` set built from records with `type == "trail"`.
- **Pass 2 (semantic checks)**: For each non-trail record:
  - Resolves parent from `record.get("parent")` (top-level) OR `links.parent` (nested). Dangling/non-trail parents → errors. No parent at all → orphan warning.
  - Resolves `blocked_by` via existing `_get_blocked_by()` helper. Non-existent blocker IDs → warnings.
  - If `--fix`: removes dangling IDs from both top-level and `links.blocked_by`.
- **Fix write**: Inside `FileLock`, calls `write_tasks(path, valid_records)`.
- **Exit**: Reports errors to stderr, warnings to stderr. Exits 1 if errors. Exits 0 if warnings-only or clean.

Added `p_doctor.add_argument("--fix", action="store_true", ...)` to parser.

## Correctness Review

**crumb.py (cmd_doctor)**:
- Malformed JSON: raw line-by-line, line numbers included in error message — AC1 PASS
- Dangling blocked_by: uses `_get_blocked_by()` helper (consistent with cmd_ready/blocked), appends to `warnings` — AC2 PASS
- Dangling parent: checks `parent_id not in id_to_record` OR `parent_id not in trail_ids`, appends to `errors` — AC3 PASS
- Duplicate IDs: `seen_ids` dict tracks first occurrence, second occurrence appends to `errors` — AC4 PASS
- Orphan crumbs: non-trail records with no parent → warnings — AC5 PASS
- --fix: only removes dangling blocked_by (not duplicates/dangling parents per spec), writes atomically via FileLock + write_tasks — AC6 PASS
- Clean data: prints "No issues found", returns without sys.exit → exit 0 — AC7 PASS

**Parser**: `p_doctor.add_argument("--fix", action="store_true")` added — correct.

## Build/Test Validation

Syntax check: `python3 -m py_compile crumb.py` — passed.

Integration tests:
- Mixed issues (malformed JSON, duplicate ID, dangling parent, orphan, dangling blocked_by): all reported correctly, exit 1.
- Clean data (trail + child with valid parent): "No issues found", exit 0.
- --fix with dangling blocked_by: dangling removed, existing blocker kept, file rewritten, exit 0 (warnings only after fix).
- Warnings only: exit 0 confirmed.

## Acceptance Criteria Checklist

- [x] crumb doctor reports malformed JSON lines with line numbers — PASS
- [x] Dangling blocked_by references are flagged as warnings (not errors) — PASS
- [x] Dangling parent links (pointing to non-existent trail) are flagged as errors — PASS
- [x] Duplicate IDs are flagged as errors — PASS
- [x] Orphan crumbs (no parent trail) are flagged as warnings — PASS
- [x] crumb doctor --fix removes dangling blocked_by references and reports fixes applied — PASS
- [x] Clean data produces 'No issues found' and exits 0 — PASS
