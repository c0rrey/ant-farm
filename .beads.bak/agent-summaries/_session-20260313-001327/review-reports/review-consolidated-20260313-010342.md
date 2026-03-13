# Big Head Consolidated Review Report
**Timestamp**: 2026-03-13T01:10:00Z
**Review round**: 1
**File under review**: `crumb.py`
**Status**: CONSOLIDATED

---

## Read Confirmation

| Report | Reviewer | Findings | P1 | P2 | P3 |
|--------|----------|----------|----|----|----|
| clarity-review-20260313-010342.md | clarity-reviewer | 8 | 0 | 1 | 7 |
| edge-cases-review-20260313-010342.md | edge-cases-reviewer | 9 | 0 | 4 | 5 |
| correctness-review-20260313-010342.md | correctness-reviewer | 5 | 0 | 4 | 1 |
| drift-review-20260313-010342.md | drift-reviewer | 4 | 0 | 2 | 2 |
| **Total raw findings** | | **26** | **0** | **11** | **15** |

---

## Consolidated Root Causes

### RC-1 [P2] — Inconsistent dual-storage field lookups in `cmd_list` filters and `_auto_close_trail_if_complete`

**Root cause**: The codebase stores parent/discovered_from linkage in two locations: top-level fields (e.g., `record["parent"]`) and the `links` sub-dict (e.g., `record["links"]["parent"]`). Some code paths (`_get_trail_children`, `cmd_doctor`, `_get_blocked_by`) correctly check both locations. Others check only one, producing silently wrong results.

**Affected surfaces**:
- `crumb.py:520` — `cmd_list --parent` checks only `t.get("parent")`, misses `links.parent` (from clarity F4, correctness F1, drift DRIFT-1)
- `crumb.py:523` — `cmd_list --discovered` checks only `t.get("discovered_from")`, misses `links.discovered_from` (from correctness F2, drift DRIFT-2)
- `crumb.py:425-430` — `_auto_close_trail_if_complete` reads only `links.get("parent")`, misses top-level `parent` (from correctness F3)

**Merge rationale**: All 6 raw findings share the same root cause: inconsistent handling of the dual-storage field pattern. The fix is a single audit of all field-access sites to ensure both locations are checked. The code already has a correct reference pattern in `_get_blocked_by` (line 861) and `_get_trail_children` (line 401).

**Suggested fix**: For each affected line, mirror the dual-lookup pattern from `_get_trail_children`. Consider extracting a helper `get_field(record, field_name)` that checks both locations, to prevent recurrence.

**Acceptance criteria**:
- `crumb list --parent AF-T1` returns crumbs linked via `crumb link --parent`
- `crumb list --discovered` returns crumbs linked via `crumb link --discovered-from`
- Closing the last open child of a trail auto-closes the trail for crumbs with top-level `parent` field

---

### RC-2 [P2] — `_convert_beads_record` inverts `blocks` dependency direction

**Root cause**: When converting a Beads record with a `blocks`-type dependency, the code adds the target to the source record's `blocked_by` list -- the semantic inverse of the actual relationship. Record A with `depends_on_id: B, type: "blocks"` means A blocks B (B is blocked by A), but the code interprets it as A is blocked by B.

**Affected surfaces**:
- `crumb.py:1483-1484` — `blocked_by.append(depends_on)` incorrectly adds B to A's blocked_by (from correctness F4)

**Merge rationale**: Single finding, standalone logic bug. No other findings share this code path.

**Suggested fix**: Build a reverse index during conversion: when processing record A with a `blocks` dep pointing to B, record that B should have A in its `blocked_by`. Apply the reverse index in a post-processing pass after all records are collected.

**Acceptance criteria**:
- `crumb import --from-beads` correctly maps `blocks` dependencies (if A blocks B, B's `blocked_by` contains A, not the reverse)
- Existing `parent-child` mapping remains correct (regression check)

---

### RC-3 [P2] — Missing `try/except OSError` on file open/touch operations

**Root cause**: Several functions call `open()` or `path.touch()` without catching `OSError`, causing raw Python tracebacks instead of clean `die()` messages when files are unreadable, missing (race), or on a read-only filesystem. `read_config()` (line 139) already demonstrates the correct pattern.

**Affected surfaces**:
- `crumb.py:181` — `read_tasks()` unguarded `open()` (from edge-cases F-01)
- `crumb.py:222` — `iter_jsonl()` unguarded `open()` (from edge-cases F-02)
- `crumb.py:258-260` — `FileLock.__enter__` unguarded `path.touch()` and `open()` (from edge-cases F-03)

**Merge rationale**: All three share the same root cause (missing OSError handling on file I/O) and the same fix pattern (wrap in `try/except OSError as exc: die(...)`). The existing `read_config()` at line 139 is the template.

**Suggested fix**: Add `try/except OSError as exc: die(f"cannot read/write ...: {exc}")` around each unguarded `open()` / `path.touch()` call, following `read_config()`'s pattern.

**Acceptance criteria**:
- `read_tasks()` produces a clean error message on permission error or missing file
- `FileLock.__enter__` produces a clean error message on read-only filesystem or permission error
- `iter_jsonl()` produces a clean error message on file access failure

---

### RC-4 [P2] — Missing type validation on parsed external data (`--from-json`, config counters)

**Root cause**: External inputs parsed via `json.loads` or `int()` are used directly without type validation. A non-dict JSON payload causes `AttributeError` on `.get()`, and a non-integer config counter causes `ValueError` on `int()`.

**Affected surfaces**:
- `crumb.py:645-649` — `cmd_create --from-json` does not check `isinstance(payload, dict)` (from edge-cases F-04)
- `crumb.py:679` — `int(config.get("next_crumb_id", 1))` unguarded `ValueError` (from edge-cases F-05)
- `crumb.py:1148` — `int(config.get("next_trail_id", 1))` same pattern (from edge-cases F-05)
- `crumb.py:1433` — import path same pattern (from edge-cases F-05)
- `crumb.py:1646-1647` — post-import counter update same pattern (from edge-cases F-09)

**Merge rationale**: F-04, F-05, and F-09 all stem from the same root cause: external data is parsed but not type-validated before use. F-05 and F-09 are the same `int()` pattern in different code paths. F-04 is the same category (parsed-but-unvalidated external input) in the JSON parsing path. The fix is a consistent validation layer.

**Suggested fix**: (a) Add `if not isinstance(payload, dict): die(...)` after `json.loads` in `cmd_create`. (b) Add a `read_config()` validator that type-checks counter fields on load, or wrap each `int()` conversion in `try/except ValueError: die(...)`.

**Acceptance criteria**:
- `crumb create --from-json '["a"]'` produces a clean error message, not a traceback
- Corrupted `next_crumb_id` in config.json produces a clean error pointing to the config field

---

### RC-5 [P2] — TOCTOU race in `cmd_doctor --fix` (read without lock)

**Root cause**: `cmd_doctor` reads `tasks.jsonl` at line 1714 without holding `FileLock`. The lock is only acquired at line 1816 for writing. Between read and lock acquisition, another process can modify `tasks.jsonl`, and the doctor's write will silently discard those changes.

**Affected surfaces**:
- `crumb.py:1714` — read without lock (from edge-cases F-06)
- `crumb.py:1816` — lock acquired only for write (from edge-cases F-06)

**Merge rationale**: Single finding, standalone concurrency bug.

**Suggested fix**: Move `FileLock` acquisition to wrap the entire read+validate+write sequence. The doctor already does a raw `open()` for malformed-line detection; restructure to acquire the lock first, then do both read passes inside it.

**Acceptance criteria**:
- `cmd_doctor --fix` holds the lock for the entire read-validate-write cycle
- Concurrent `crumb create` during `crumb doctor --fix` does not lose the created crumb

---

### RC-6 [P3] — Overly broad `*.tmp` glob in `cleanup_stale_tmp_files`

**Affected surfaces**:
- `crumb.py:298` — `crumbs.glob("*.tmp")` (from edge-cases F-07)

**Merge rationale**: Single finding, standalone boundary issue.

**Suggested fix**: Replace `crumbs.glob("*.tmp")` with explicit patterns: `["tasks.jsonl.tmp", "config.json.tmp"]`.

**Acceptance criteria**:
- Only crumb-owned temp files are cleaned up; unrelated `.tmp` files in `.crumbs/` are preserved

---

### RC-7 [P3] — Unvalidated `--after` date string in `cmd_list`

**Affected surfaces**:
- `crumb.py:527-531` — no validation of `args.after` (from edge-cases F-08)

**Merge rationale**: Single finding, standalone input validation gap.

**Suggested fix**: Validate `args.after` with `datetime.fromisoformat()` or a regex, calling `die()` on bad input.

**Acceptance criteria**:
- `crumb list --after foo` produces a clean error message

---

### RC-8 [P3] — Plain import accepts records missing required fields

**Affected surfaces**:
- `crumb.py:1622-1628` — missing field validation (from correctness F5)

**Merge rationale**: Single finding, standalone data quality gap.

**Suggested fix**: After checking `id`, validate that `title`, `type`, and `status` are present; `die()` or skip with a warning if missing.

**Acceptance criteria**:
- Plain import rejects or warns on records missing `title`, `type`, or `status`

---

### RC-9 [P3] — Redundant wrapper function `crumbs_dir`

**Affected surfaces**:
- `crumb.py:105-107` — one-line delegate to `find_crumbs_dir()` (from clarity F1)

**Merge rationale**: Single finding.

**Suggested fix**: Inline `crumbs_dir()` call sites to use `find_crumbs_dir()` directly, and remove the wrapper.

---

### RC-10 [P3] — Misleading variable name `seen` in `_get_blocked_by`

**Affected surfaces**:
- `crumb.py:884` — `seen` used as both dedup tracker and output (from clarity F2)

**Merge rationale**: Single finding.

**Suggested fix**: Rename to `result` or `merged`; use a separate `seen_set` for membership testing.

---

### RC-11 [P3] — Dead variable `all_trail_ids` in `cmd_tree`

**Affected surfaces**:
- `crumb.py:1349` — built but never referenced (from clarity F3)

**Merge rationale**: Single finding.

**Suggested fix**: Remove the `all_trail_ids` assignment.

---

### RC-12 [P3] — `getattr` with default on always-present argparse fields

**Affected surfaces**:
- `crumb.py:1558` — `getattr(args, "from_beads", False)` (from clarity F5)
- `crumb.py:1792` — `getattr(args, "fix", False)` (from clarity F5)

**Merge rationale**: Single finding (two instances of the same pattern within one clarity finding).

**Suggested fix**: Replace with direct attribute access: `args.from_beads`, `args.fix`.

---

### RC-13 [P3] — `FileLock._lock_file` typed as `Optional[Any]`

**Affected surfaces**:
- `crumb.py:253` — loses type information (from clarity F6)

**Merge rationale**: Single finding.

**Suggested fix**: Change to `Optional[IO[str]]`.

---

### RC-14 [P3] — Redundant `dep.get("depends_on_id", "")` lookup in `_convert_beads_record`

**Affected surfaces**:
- `crumb.py:1479-1482` — same lookup repeated (from clarity F7)

**Merge rationale**: Single finding.

**Suggested fix**: Replace `parent_id = dep.get("depends_on_id", "")` with `parent_id = depends_on`.

---

### RC-15 [P3] — `max_crumb_num` initialization opaque without comment

**Affected surfaces**:
- `crumb.py:1646-1647` — the `-1` adjustment not explained (from clarity F8)

**Merge rationale**: Single finding.

**Suggested fix**: Add comment: `# Seed with current config ceiling so we never go backwards`.

---

### RC-16 [P3] — Module docstring documents nonexistent `FIELD=VALUE` syntax

**Affected surfaces**:
- `crumb.py:15` — `[FIELD=VALUE ...]` not implemented (from drift DRIFT-3)

**Merge rationale**: Single finding.

**Suggested fix**: Remove `[FIELD=VALUE ...]` from the docstring or implement the feature.

---

### RC-17 [P3] — Error message wording diverges from spec

**Affected surfaces**:
- `crumb.py:649` — `"invalid JSON in --from-json"` vs spec's `"invalid JSON: <details>"` (from drift DRIFT-4)

**Merge rationale**: Single finding.

**Suggested fix**: Align error message to spec: `die(f"invalid JSON: {exc}")`.

---

## Deduplication Log

| Raw Finding | Source | Consolidated RC | Merge Rationale |
|-------------|--------|-----------------|-----------------|
| Clarity F4 | clarity | RC-1 | Same dual-storage blind spot as correctness F1/F2 and drift DRIFT-1/DRIFT-2; shares code pattern and root cause |
| Correctness F1 | correctness | RC-1 | `cmd_list --parent` filter checks wrong field; same root cause as clarity F4 and drift DRIFT-1 |
| Correctness F2 | correctness | RC-1 | `cmd_list --discovered` filter checks wrong field; same dual-storage pattern |
| Correctness F3 | correctness | RC-1 | `_auto_close_trail_if_complete` reads only one location; same systemic dual-storage inconsistency |
| Drift DRIFT-1 | drift | RC-1 | Same `cmd_list --parent` line 520 finding as correctness F1 and clarity F4 |
| Drift DRIFT-2 | drift | RC-1 | Same `cmd_list --discovered` line 523 finding as correctness F2 |
| Correctness F4 | correctness | RC-2 | Standalone: `_convert_beads_record` blocks inversion, unique code path |
| Edge Cases F-01 | edge-cases | RC-3 | Missing OSError on `open()` in `read_tasks()`; same pattern as F-02 and F-03 |
| Edge Cases F-02 | edge-cases | RC-3 | Missing OSError on `open()` in `iter_jsonl()`; same pattern as F-01 |
| Edge Cases F-03 | edge-cases | RC-3 | Missing OSError on `open()`/`touch()` in `FileLock`; same pattern as F-01 |
| Edge Cases F-04 | edge-cases | RC-4 | Missing type check after `json.loads`; same category as F-05/F-09 (unvalidated external data) |
| Edge Cases F-05 | edge-cases | RC-4 | Unguarded `int()` on config counter; same category as F-04/F-09 |
| Edge Cases F-09 | edge-cases | RC-4 | Same `int()` pattern as F-05 in import path |
| Edge Cases F-06 | edge-cases | RC-5 | Standalone TOCTOU race in `cmd_doctor` |
| Edge Cases F-07 | edge-cases | RC-6 | Standalone: overly broad glob |
| Edge Cases F-08 | edge-cases | RC-7 | Standalone: unvalidated date string |
| Correctness F5 | correctness | RC-8 | Standalone: missing field validation in import |
| Clarity F1 | clarity | RC-9 | Standalone: redundant wrapper function |
| Clarity F2 | clarity | RC-10 | Standalone: misleading variable name |
| Clarity F3 | clarity | RC-11 | Standalone: dead variable |
| Clarity F5 | clarity | RC-12 | Standalone: misleading getattr pattern |
| Clarity F6 | clarity | RC-13 | Standalone: imprecise type annotation |
| Clarity F7 | clarity | RC-14 | Standalone: redundant lookup |
| Clarity F8 | clarity | RC-15 | Standalone: missing comment |
| Drift DRIFT-3 | drift | RC-16 | Standalone: stale docstring |
| Drift DRIFT-4 | drift | RC-17 | Standalone: error message wording |

**Raw count**: 26 findings in -> **17 consolidated root causes** out (9 findings merged via dedup).

---

## Severity Conflicts

No severity conflicts of 2+ levels exist. All merged findings had severities within 1 level of each other:

- RC-1: Clarity F4 (P2), Correctness F1 (P2), Correctness F2 (P2), Correctness F3 (P2), Drift DRIFT-1 (P2), Drift DRIFT-2 (P2) -- unanimous P2
- RC-3: Edge Cases F-01 (P2), F-02 (P3), F-03 (P2) -- 1 level difference, highest P2 used
- RC-4: Edge Cases F-04 (P2), F-05 (P3), F-09 (P3) -- 1 level difference, highest P2 used

No calibration flags needed.

---

## Cross-Session Dedup Log

All 17 root causes were checked against 130+ open beads. No matches found:
- The open beads are entirely about orchestration files, documentation, shell scripts, and placeholder conventions
- No existing beads target `crumb.py` logic, edge cases, correctness, or clarity issues
- All 17 root causes are marked for filing (0 skipped)

Search queries executed: `cmd_list parent`, `crumb.py`, `blocks dependency`, `doctor TOCTOU` -- all returned no relevant matches.

---

## Priority Breakdown

| Priority | Root Causes | Count |
|----------|-------------|-------|
| P2 | RC-1, RC-2, RC-3, RC-4, RC-5 | 5 |
| P3 | RC-6 through RC-17 | 12 |
| **Total** | | **17** |

P1: 0, P2: 5, P3: 12. Distribution is reasonable -- majority P3, P2s are real correctness/robustness gaps.

---

## Traceability Matrix

All 26 raw findings accounted for:
- 26 findings mapped to 17 root causes (see Deduplication Log above)
- 0 findings excluded
- 0 findings skipped as cross-session duplicates

---

## Overall Verdict

**PASS WITH ISSUES**

No P1 findings. Five P2 root causes require fixes:
- RC-1: Dual-storage field lookup inconsistency (highest impact -- affects normal workflow)
- RC-2: Beads import `blocks` dependency inversion
- RC-3: Missing OSError handling on file operations
- RC-4: Missing type validation on external data
- RC-5: TOCTOU race in `cmd_doctor --fix`

Twelve P3 root causes are cosmetic/defensive improvements. Per Round 1 protocol, P3 disposition is handled by the Queen.
