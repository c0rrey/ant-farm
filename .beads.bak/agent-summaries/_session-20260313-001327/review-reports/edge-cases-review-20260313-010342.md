# Edge Cases Review — crumb.py
**Timestamp**: 20260313-010342
**Review round**: 1
**Commit range**: 25219ff..HEAD
**Reviewer**: edge-cases

---

## Findings Catalog

### F-01
**File:line**: `/Users/correy/projects/ant-farm/crumb.py:181`
**Severity**: P2
**Category**: File operations — unguarded open
**Description**: `read_tasks()` calls `open(path, "r")` with no `try/except OSError`. Callers upstream guard existence with `require_tasks_jsonl()` or an `if path.exists()` check, but a permission error, a broken symlink, or a file deleted between the existence check and the open will raise an unhandled `FileNotFoundError` / `PermissionError` instead of a clean `die()` message.
**Suggested fix**: Wrap the `open()` in a `try/except OSError as exc: die(...)` block, consistent with `read_config()` at L139.

---

### F-02
**File:line**: `/Users/correy/projects/ant-farm/crumb.py:222`
**Severity**: P3
**Category**: File operations — unguarded open
**Description**: `iter_jsonl()` has the same missing `try/except OSError` around `open()`. `iter_jsonl` is defined but not called by any current command (it appears unused), so the risk is latent rather than immediately exploitable.
**Suggested fix**: Same as F-01 — wrap in `try/except OSError` or add a guard before the open.

---

### F-03
**File:line**: `/Users/correy/projects/ant-farm/crumb.py:258-260`
**Severity**: P2
**Category**: File operations — unguarded OSError in FileLock.__enter__
**Description**: `FileLock.__enter__` calls `path.touch()` and then `open(path, "w", ...)` without catching `OSError`. If `.crumbs/` is not writable (read-only filesystem, permission change, disk full), both calls raise unhandled exceptions with a raw Python traceback instead of a clean error message. Every write command (`create`, `update`, `close`, `reopen`, `link`, `import`, `trail create`, `trail close`, `doctor --fix`) is affected.
**Suggested fix**: Wrap both `path.touch()` and `open(...)` in `try/except OSError as exc: die(f"cannot acquire lock: {exc}")`.

---

### F-04
**File:line**: `/Users/correy/projects/ant-farm/crumb.py:645-649`
**Severity**: P2
**Category**: Input validation — non-dict JSON in --from-json
**Description**: In `cmd_create`, when `--from-json` is supplied, `json.loads(args.from_json)` is called and the result assigned to `payload`. If the user passes a valid JSON value that is not a dict (e.g., `'["a","b"]'`, `'"just a string"'`, `'42'`), `json.loads` succeeds but `payload.get(...)` at L653 raises `AttributeError: 'list' object has no attribute 'get'`, producing a Python traceback instead of a user-friendly error.
**Suggested fix**: After `json.loads`, add: `if not isinstance(payload, dict): die("--from-json must be a JSON object, not a list or scalar")`.

---

### F-05
**File:line**: `/Users/correy/projects/ant-farm/crumb.py:679`
**Severity**: P3
**Category**: Input validation — non-integer config counter
**Description**: `int(config.get("next_crumb_id", 1))` in `cmd_create` raises unhandled `ValueError` if `config.json` has been manually edited and `next_crumb_id` is not a valid integer (e.g., `"next_crumb_id": "corrupted"`). Same pattern at `crumb.py:1148` (`next_trail_id`), `crumb.py:1433` (import), and `crumb.py:1646-1647` (post-import counter update).
**Suggested fix**: Wrap each `int(...)` conversion in a `try/except ValueError` and `die()` with a helpful message pointing to the config field. Or add a `read_config()` validator that type-checks counter fields on load.

---

### F-06
**File:line**: `/Users/correy/projects/ant-farm/crumb.py:1814-1817`
**Severity**: P2
**Category**: Race condition — TOCTOU in cmd_doctor --fix
**Description**: `cmd_doctor` reads `tasks.jsonl` at L1714 **without** holding the `FileLock`. The lock is only acquired at L1816 when writing fixes. Between the read (L1714) and the lock acquisition (L1816), another process could append or modify `tasks.jsonl`. The doctor then overwrites the file with its snapshot, silently discarding the interleaved writes.
**Suggested fix**: Move the `FileLock` acquisition to wrap the entire read+validate+write sequence in `cmd_doctor`. Since the doctor already does a raw `open()` on the path (for malformed-line detection), restructure to acquire the lock first, then do the two-pass read inside it.

---

### F-07
**File:line**: `/Users/correy/projects/ant-farm/crumb.py:298`
**Severity**: P3
**Category**: File operations — overly broad cleanup
**Description**: `cleanup_stale_tmp_files()` globs for `*.tmp` in `.crumbs/` and unlinks every match. This pattern would silently delete any user-created `.tmp` file in `.crumbs/` that is unrelated to crumb's own atomic writes. The only legitimate tmp files are `tasks.jsonl.tmp` and `config.json.tmp`. Globbing for all `*.tmp` is broader than necessary.
**Suggested fix**: Replace `crumbs.glob("*.tmp")` with explicit patterns: `["tasks.jsonl.tmp", "config.json.tmp"]`. Alternatively, glob for `*.jsonl.tmp` and `*.json.tmp` to exactly match the patterns used by `write_tasks` and `write_config`.

---

### F-08
**File:line**: `/Users/correy/projects/ant-farm/crumb.py:527-531`
**Severity**: P3
**Category**: Input validation — unvalidated date string in --after filter
**Description**: `cmd_list --after DATE` accepts any string from the CLI and compares it lexicographically against `created_at` ISO timestamps. If the user passes an invalid date (e.g., `--after foo` or `--after 2026-13-99`), the filter silently returns wrong results (either no tasks or all tasks) with no error message. The failure mode is non-obvious.
**Suggested fix**: Validate `args.after` against a simple pattern (e.g., `YYYY-MM-DD` regex or `datetime.fromisoformat`) before using it as a filter, calling `die()` on bad input.

---

### F-09
**File:line**: `/Users/correy/projects/ant-farm/crumb.py:1646-1647`
**Severity**: P3
**Category**: Input validation — unguarded int() in import counter update
**Description**: The post-import counter update at L1646-1647 calls `int(config.get("next_crumb_id", 1))` without guarding against a non-integer stored value. This is the same root cause as F-05 but in a separate code path (import, not create). Flagged separately because the import path has no prior user interaction that would surface the config corruption earlier.
**Suggested fix**: Same as F-05 — handled at `read_config()` validation level, or individual `try/except ValueError` wraps.

---

## Preliminary Groupings

### Group A: Missing OSError handling on file operations (F-01, F-02, F-03)
All three findings share the root cause of calling `open()` (or `path.touch()`) without a `try/except OSError`. The fix pattern is consistent: wrap in `try/except OSError as exc: die(...)`. `read_config()` (L139) already demonstrates the correct pattern and should be used as the template for the fixes.

### Group B: Missing type validation on parsed external data (F-04, F-05, F-09)
`--from-json` JSON not type-checked after parsing (F-04), and `int()` conversions of config values not guarded against non-integer stored values (F-05, F-09). Root cause: config and CLI inputs are read and immediately used without defensive type assertions. `read_config()` would be the right place to add counter type validation.

### Group C: Concurrency gap in doctor --fix (F-06)
Standalone issue. The TOCTOU race in `cmd_doctor --fix` is the only concurrency finding. The fix requires refactoring the lock scope in `cmd_doctor`.

### Group D: Brittle boundaries in utility functions (F-07, F-08)
Overly broad glob pattern in cleanup (F-07) and no validation of the `--after` date string (F-08). Both are low-impact individually but reflect missing defensive checks at input/output boundaries.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1       | 0     |
| P2       | 4 (F-01, F-03, F-04, F-06) |
| P3       | 5 (F-02, F-05, F-07, F-08, F-09) |
| **Total** | **9** |

---

## Cross-Review Messages

No cross-domain issues identified that require messaging other reviewers. The dependency-type mapping logic in `_convert_beads_record` (L1479-1484) looked potentially suspect for correctness, but on close reading it correctly maps the "parent-child" dep type to a parent link and "blocks" dep type to a blocked_by entry, which aligns with the beads schema described in project memory. No message sent.

---

## Coverage Log

| File | Reviewed | Issues Found |
|------|----------|--------------|
| `/Users/correy/projects/ant-farm/crumb.py` | Yes — all 2029 lines | F-01 through F-09 |

---

## Overall Assessment

**Score**: 7 / 10
**Verdict**: PASS WITH ISSUES

The file is generally well-structured for robustness: atomic writes via temp-rename, flock-based concurrency safety, malformed JSON tolerance, idempotent close, and defensive `_get_blocked_by` merging. The P2 findings (F-01, F-03, F-04, F-06) are real gaps that will surface as Python tracebacks or silent data overwrites in observable scenarios — particularly F-06 (TOCTOU in `doctor --fix`) and F-03 (unguarded `FileLock` open). None of these are P1 because they don't corrupt the persisted data under normal single-user operation. The P3 findings are defensive improvements.
