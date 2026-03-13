# Task Summary: ant-farm-dhh8
**Task**: Implement crumb search and tree commands
**Status**: Complete

## Approaches Considered

1. **Inline substring matching** — Iterate all records, check `query.lower() in field.lower()` for title and description. Simple, no dependencies, exactly matches the spec.

2. **Regex-based search** — Use `re.search(pattern, text, re.IGNORECASE)` for pattern matching. More flexible but adds complexity beyond what the spec requires; the spec says keyword matching.

3. **Pre-built text corpus** — Concatenate all text fields per record into a single string for search. Overkill; checking two specific fields (title, description) is explicit and avoids false matches on other fields.

4. **Existing `_get_trail_children` helper for tree** — Use the existing `_get_trail_children` helper to get children per trail, then print orphans separately. Reuses existing logic without duplication.

## Selected Approach

**Approach 1 for search, Approach 4 for tree** — both inline with no new helpers.

Rationale: `cmd_search` is a one-liner filter + loop — no helper needed. `cmd_tree` is slightly more complex (needs to track which records have been claimed by a trail) but reuses `_get_trail_children` and stays under 60 lines. Adding helper functions would add indirection without benefit.

## Implementation Description

`cmd_search(args)`:
- Loads all tasks via `read_tasks`.
- `query_lower = args.query.lower()`.
- Filters records where `query_lower in title.lower() or query_lower in description.lower()`.
- Prints matching records in the standard one-line format (same as cmd_list).
- No output for empty results (prints nothing, exits 0).

`cmd_tree(args)`:
- Scoped mode (`args.id` is not None): finds the specified trail via `_find_crumb`, dies if not found or not type='trail'. Prints trail then indented children using `_get_trail_children`.
- Full mode (`args.id` is None): iterates all trails, prints each with `_get_trail_children` output (2-space indent). Tracks `child_ids` set. After all trails, prints orphan non-trail records (those not in `child_ids`) under an `(orphans)` header.

## Correctness Review

**crumb.py (cmd_search)**:
- Both title and description fields checked — AC1 PASS
- `str.lower()` on both query and field — AC2 (case-insensitive) PASS
- No output, no sys.exit call on empty results — AC5 PASS

**crumb.py (cmd_tree)**:
- Full tree shows all trails as parents, children indented — AC3 PASS
- Scoped `args.id` shows only that trail and children; dies on unknown or non-trail ID — AC4 PASS
- Orphan section added for records with no parent trail — covers completeness

## Build/Test Validation

Syntax check: `python3 -m py_compile crumb.py` — passed.

Integration tests:
- `search 'rate'`: matched AF-T1 (title), AF-1 (title), AF-3 (description "rate control") — correct.
- `search 'Rate'`: same results as 'rate' — case-insensitive confirmed.
- `search 'nonexistent_zzz'`: no output — correct.
- `tree` (full): AF-T1 trail → AF-1 child, AF-T2 trail → AF-2 child, orphans section → AF-3 — correct.
- `tree AF-T1`: shows only AF-T1 trail and AF-1 child — correct.
- `tree AF-T99`: error "not found", exit 1 — correct.
- `tree AF-1`: error "not a trail", exit 1 — correct.

## Acceptance Criteria Checklist

- [x] crumb search 'keyword' returns crumbs/trails matching keyword in title or description — PASS
- [x] Search is case-insensitive ('Rate' matches 'rate') — PASS
- [x] crumb tree displays hierarchical view with trails as parents and child crumbs indented — PASS
- [x] crumb tree <trail-id> shows only the specified trail and its children — PASS
- [x] Empty search results produce no output and exit 0 — PASS
