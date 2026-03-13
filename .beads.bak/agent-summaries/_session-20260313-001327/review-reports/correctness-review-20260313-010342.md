# Correctness Review — crumb.py
**Timestamp**: 20260313-010342
**Reviewer**: correctness-reviewer
**Commit range**: 25219ff..HEAD
**Round**: 1

---

## Findings Catalog

### F1 — P2 — `cmd_list --parent` checks wrong field; filter always misses linked crumbs
**File**: `/Users/correy/projects/ant-farm/crumb.py:520`
**Severity**: P2
**Category**: Logic correctness / Data integrity

`cmd_list` with `--parent` runs:
```python
results = [t for t in results if t.get("parent") == args.parent]
```
But `crumb link <id> --parent <trail-id>` stores the parent in `links["parent"]`, not at the top-level `parent` key (see L1029-1030). Any crumb linked via `crumb link` will never appear in `crumb list --parent <trail-id>`. Only crumbs created with an explicit top-level `parent` key (e.g., via `--from-json {"parent": "AF-T1", ...}`) would match.

**Criterion**: ant-farm-l7pk criterion 4 — "crumb list ... --parent AF-T1 ... correctly applies all filters" — this criterion is unmet for the normal workflow.

**Suggested fix**: Mirror the pattern used elsewhere (e.g., `_get_trail_children` at L398-403 and `cmd_doctor` at L1758-1765) that checks both `record.get("parent")` and `record.get("links", {}).get("parent")`.

---

### F2 — P2 — `cmd_list --discovered` checks wrong field; filter always misses linked crumbs
**File**: `/Users/correy/projects/ant-farm/crumb.py:523`
**Severity**: P2
**Category**: Logic correctness

`cmd_list` with `--discovered` runs:
```python
results = [t for t in results if t.get("discovered_from")]
```
But `crumb link <id> --discovered-from <other-id>` stores the value in `links["discovered_from"]` (L1057-1058), not at the top-level `discovered_from` key. The filter will never return crumbs linked via `crumb link`.

**Suggested fix**: Check both `t.get("discovered_from")` and `(t.get("links") or {}).get("discovered_from")`.

---

### F3 — P2 — `_auto_close_trail_if_complete` only reads `links.parent`; misses top-level `parent`
**File**: `/Users/correy/projects/ant-farm/crumb.py:425-430`
**Severity**: P2
**Category**: Logic correctness / Data integrity

When `cmd_close` calls `_auto_close_trail_if_complete`, the function reads:
```python
links = crumb.get("links") or {}
parent_id = links.get("parent")
```
But `cmd_doctor` at L1758-1765 explicitly checks both `record.get("parent")` and `links.get("parent")` when resolving the parent, because crumbs can have the parent set in either location (e.g., via `--from-json` with a top-level `parent` field). If a crumb's parent is stored at the top-level `parent` key, `_auto_close_trail_if_complete` will return early without checking whether all trail children are now closed — the trail auto-close will silently not fire.

**Criterion**: ant-farm-jmvi criterion 5 — "Closing the last open child of a trail auto-closes the trail" — unmet for crumbs with top-level `parent` field.

**Suggested fix**: Read parent from both locations:
```python
links = crumb.get("links") or {}
parent_id = (crumb.get("parent") or "") or (links.get("parent") if isinstance(links, dict) else "")
```

---

### F4 — P2 — `_convert_beads_record` inverts `blocks` dependency direction
**File**: `/Users/correy/projects/ant-farm/crumb.py:1483-1484`
**Severity**: P2
**Category**: Data integrity / Algorithm correctness

In Beads, a dependency record `{issue_id: A, depends_on_id: B, type: "blocks"}` means "A blocks B" (B cannot proceed until A is done, so B is blocked by A). When converting record A, the code does:

```python
elif dep_type == "blocks" and depends_on:
    blocked_by.append(depends_on)  # adds B to A's blocked_by
```

This says "A is blocked by B" — the reverse of the actual relationship. The correct transformation is: when processing record A with a `blocks` dep pointing to B, it is B (not A) that should have A added to its `blocked_by` list.

Since the conversion is one-pass per record, the correct approach is to either:
1. Build a reverse index during the two-pass conversion and assign `blocked_by` to the correct records after all records are collected, or
2. Skip `blocks` type deps entirely during per-record conversion and emit them as a post-processing step using the reverse index.

**Criterion**: ant-farm-fdz2 criterion 4 — "crumb import --from-beads converts beads format to crumb format" — the blocked_by mapping is logically inverted.

**Note**: This only affects users who import from Beads with `blocks`-type deps. The `parent-child` mapping is correct. Confirmed via inspection of `.beads/issues.jsonl` which has real `blocks`-type dep entries (e.g., `ant-farm-1jo` blocks `ant-farm-x0m`).

---

### F5 — P3 — `cmd_import` (plain mode) accepts records missing required fields silently
**File**: `/Users/correy/projects/ant-farm/crumb.py:1622-1628`
**Severity**: P3
**Category**: Data integrity

Plain import mode checks for missing `id` but does not validate that required fields (`title`, `type`, `status`) are present. Records with `id` but missing `title` or `status` are imported without error and stored in tasks.jsonl. This can produce records that display incorrectly in `crumb show` and `crumb list`. The description says "checks JSON parse, required fields (id, title, type, status)" but only `id` is actually checked.

This is P3 because the failure mode is silent data quality degradation, not a crash or wrong output for already-valid records.

---

## Preliminary Groupings

### Group A: Inconsistent `links` vs top-level field access (root cause: dual storage locations)
- F1 (`cmd_list --parent` filter)
- F2 (`cmd_list --discovered` filter)
- F3 (`_auto_close_trail_if_complete`)

These three share the same root cause: the code was incrementally built, with some paths (doctor, get_trail_children) correctly checking both storage locations, and others checking only one. The inconsistency is systemic across the codebase for any field that can live at either `record[field]` or `record["links"][field]`.

### Group B: Beads migration data integrity
- F4 (`_convert_beads_record` blocks direction)

Standalone: the `blocks` dep type is semantically inverted during migration.

### Group C: Import validation gaps
- F5 (plain import missing field validation)

Minor standalone gap, P3 only.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1       | 0     |
| P2       | 4     |
| P3       | 1     |
| **Total**| **5** |

---

## Cross-Review Messages

- Sent to **edge-cases-reviewer**: "Unvalidated fields in plain import at crumb.py:1622 — records missing `title`/`type`/`status` are silently accepted. Could be edge case territory. I'm filing as P3 correctness; you may want to evaluate as boundary condition."

---

## Coverage Log

| File | Status |
|------|--------|
| `/Users/correy/projects/ant-farm/crumb.py` | Reviewed — 5 findings |

---

## Overall Assessment

**Score**: 7 / 10

**Verdict**: PASS WITH ISSUES

The core logic — create, show, update, close, reopen, ready, blocked, trail CRUD, search, tree, doctor, locking, atomic writes — is correct for the primary happy path. The acceptance criteria for most tasks are met.

Four P2 findings exist, none of which cause a crash or data loss in the most common paths:
- F1 and F2 mean two filters in `crumb list` silently return empty results for the normal linked workflow. These affect usability but not data integrity.
- F3 means trail auto-close doesn't fire for crumbs created with a top-level `parent` via `--from-json`; the normal `crumb link --parent` workflow is unaffected.
- F4 is a semantic inversion in Beads migration for `blocks`-type deps — wrong but only triggered by the migration path.

No P1 findings. No acceptance criteria are entirely unimplemented.
