# Task Summary: ant-farm-fdz2
**Task**: Implement crumb import and --from-beads migration
**Status**: Complete

## Approaches Considered

1. **Single function, inline branching** — One `cmd_import` with `if args.from_beads: ... else: ...`. Straightforward but risks a large monolithic function with tangled concerns.

2. **Two helper functions: `_import_plain` and `_import_beads`** — Clean separation of the two import paths, dispatched from cmd_import. Adds indirection without much gain given the two paths don't share logic.

3. **Transform-then-validate pipeline** — For beads mode: convert all records to crumb format, then pass through the same plain import validator. Maximizes reuse but requires the crumb validator to accept already-valid records; the beads → crumb conversion is a clean mapping anyway.

4. **Inline cmd_import with dedicated conversion helpers** — Single function dispatching on `from_beads`, with `_convert_beads_record` and `_resolve_beads_epic_refs` as focused helpers for the complex parts. The main function stays readable; helpers are small and testable.

## Selected Approach

**Approach 4**: Single cmd_import with dedicated beads conversion helpers.

Rationale: The two modes (plain vs beads) don't share data structures, so merging them into one pipeline adds accidental complexity. The beads conversion has two distinct sub-problems (single-record conversion, cross-record epic ID resolution) that map cleanly to two helpers. This keeps `cmd_import` under 100 lines while the helpers are individually testable.

## Implementation Description

Added constants `_BEADS_PRIORITY_MAP` (int→P-string) and `_BEADS_STATUS_MAP` (string→string) above `cmd_import`.

`_convert_beads_record(beads_rec, epic_id_map, config)`:
- Maps `issue_type` to crumb type; "epic" → "trail".
- For epics: generates T-prefixed trail ID using `config["next_trail_id"]`, records the mapping in `epic_id_map`, advances the counter.
- Maps priority integers 0-4 to P0-P4 via `_BEADS_PRIORITY_MAP`.
- Maps `dependencies` array: `parent-child` → `links.parent`, `blocks` → `links.blocked_by`.

`_resolve_beads_epic_refs(records, epic_id_map)`:
- After all records are converted, replaces original Beads epic IDs with generated trail IDs in `links.parent` and `links.blocked_by`.

`cmd_import(args)`:
- Plain mode: opens file, reads line-by-line, skips malformed JSON with line number warning, skips duplicates with warning, appends valid records.
- Beads mode: sorts epics before non-epics (so `epic_id_map` is fully populated before children are converted), calls `_convert_beads_record` for each, then `_resolve_beads_epic_refs` once.
- Both modes: scan all imported IDs to advance `next_crumb_id`/`next_trail_id` counters; write tasks + config atomically inside `FileLock`.

## Correctness Review

**crumb.py (cmd_import and helpers)**:
- AC1 (import count reported): `imported_count` tracked, printed at end — PASS
- AC2 (malformed JSON with line numbers): line-by-line read, `json.JSONDecodeError` caught with lineno — PASS
- AC3 (duplicate IDs skipped with warning): `existing_ids` set checked before append — PASS
- AC4 (--from-beads converts format): `_convert_beads_record` maps all fields — PASS
- AC5 (priority mapping 0→P0...4→P4): `_BEADS_PRIORITY_MAP` dict — PASS
- AC6 (epic → trail with T-prefixed ID): `if is_epic: crumb_type = "trail"`, trail ID generated — PASS
- AC7 (counter update): max numeric scan over all tasks after import, `+1` written to config — PASS

## Build/Test Validation

Syntax check: `python3 -m py_compile crumb.py` — passed.

Integration tests:
- Plain JSONL: 2 valid records imported, 1 malformed skipped, 1 duplicate skipped. `next_crumb_id` advanced to 11 (max was 10). Correct.
- Beads synthetic: epic → AF-T1 (trail, P0), task child → links.parent: AF-T1, bug → P4. Correct.
- Real `.beads/issues.jsonl`: 531 records imported (21 epics → trails), `next_trail_id` = 22. No errors. Correct.

## Acceptance Criteria Checklist

- [x] crumb import file.jsonl imports valid JSONL entries and reports count of imported items — PASS
- [x] Malformed JSON lines are skipped with stderr warning including line number — PASS
- [x] Duplicate IDs against existing entries are skipped with stderr warning — PASS
- [x] crumb import --from-beads .beads/issues.jsonl converts beads format to crumb format — PASS
- [x] Beads priority mapping: 0→P0, 1→P1, 2→P2, 3→P3, 4→P4 — PASS
- [x] Beads type 'epic' becomes type 'trail' with T-prefixed ID — PASS
- [x] next_crumb_id/next_trail_id in config.json updated to exceed highest imported ID — PASS
