# Task Summary: ant-farm-vxpr
**Task**: Implement crumb ready and blocked commands
**Status**: Complete

## Approaches Considered

1. **Inline filter logic in each command** — Duplicate the blocker-resolution logic directly in both `cmd_ready` and `cmd_blocked`. Simple to read but violates DRY; any future logic change requires updating two places.

2. **Single helper `_is_ready(crumb, id_to_record)`** — A single helper returning True/False for readiness. `cmd_blocked` would call `not _is_ready(...)`. Names the concept from one direction only; slightly awkward for the blocked case.

3. **Shared helper `_is_crumb_blocked` plus `_get_blocked_by`** — Two helpers: `_get_blocked_by` resolves where blocked_by data lives (top-level or nested in links), and `_is_crumb_blocked` does the lookup logic. Both commands use the same pair. Best separation of concerns.

4. **Generator pipeline approach** — Chain filter generators: `(t for t in tasks if t.get("status") == "open")` then another `(t for t in open_tasks if not _is_crumb_blocked(...))`. Memory-efficient for large datasets but adds complexity with no real benefit at this scale.

## Selected Approach

**Approach 3**: `_get_blocked_by` + `_is_crumb_blocked` helpers.

Rationale: The two commands share identical blocking logic (only the True/False sense differs). A shared helper eliminates duplication. Splitting into two focused helpers (`_get_blocked_by` for field resolution, `_is_crumb_blocked` for lookup logic) follows the existing project pattern of single-responsibility helpers like `_find_crumb` and `_priority_sort_key`. The dict-based lookup (`id_to_record`) is O(1) per blocker check vs O(n) linear scan.

## Implementation Description

Added three new functions before `cmd_link`:

- **`_get_blocked_by(crumb)`**: Returns a deduplicated list of blocker ID strings, checking both `crumb["blocked_by"]` (top-level, used by `--from-json` imports) and `crumb["links"]["blocked_by"]` (set by `cmd_link`). Handles malformed values (non-list types) gracefully.

- **`_is_crumb_blocked(crumb, id_to_record)`**: Returns True if any blocker ID in `_get_blocked_by(crumb)` exists in `id_to_record` AND has status != "closed". Non-existent IDs return False (treated as resolved).

- **`cmd_ready(args)`**: Filters `status == "open"` and `type != "trail"` and `not _is_crumb_blocked`. Supports `--sort` (priority/created_at/status) and `--limit`. Uses same output format as `cmd_list`.

- **`cmd_blocked(args)`**: Filters `status == "open"` and `type != "trail"` and `_is_crumb_blocked`. Sorted by `created_at` ascending. Same output format.

## Correctness Review

**crumb.py (changed functions)**:
- `_get_blocked_by`: handles None, empty list, string (non-list), top-level, and nested links locations. Fixed operator precedence issue in ternary expression. Correct.
- `_is_crumb_blocked`: iterates `_get_blocked_by`, checks `id_to_record.get(bid)` returns non-None AND status != "closed". Non-existent IDs correctly ignored. Correct.
- `cmd_ready`: builds `id_to_record` dict from all tasks, applies three-clause filter. Sort and limit match `cmd_list` pattern. Correct.
- `cmd_blocked`: same dict build, inverted filter. Correct.

## Build/Test Validation

Syntax check: `python3 -m py_compile crumb.py` — passed.

Manual integration test with 8 synthetic records (open ready, open blocked by open, open blocker, open blocked by closed, closed blocker, open blocked by nonexistent, in_progress, trail):
- Ready output: AF-1, AF-3, AF-4, AF-6 — all 4 correct
- Blocked output: AF-2 — correct
- `--sort priority --limit 2`: AF-3 (P0), AF-1 (P2) — correct

## Acceptance Criteria Checklist

- [x] crumb ready returns only open crumbs whose blocked_by entries are all closed or non-existent — PASS
- [x] crumb ready --limit 5 --sort priority returns at most 5 results sorted by priority (P0 first) — PASS
- [x] crumb blocked returns only open crumbs with at least one blocker that is open/in_progress and exists — PASS
- [x] Crumbs with blocked_by references to non-existent IDs appear in ready (treated as resolved) — PASS
- [x] For any set of open crumbs, ready union blocked = all open crumbs and ready intersect blocked = empty — PASS
- [x] Both commands exclude closed and in_progress crumbs from their output — PASS
