# Edge Cases Review — crumb.py (Round 2)
**Timestamp**: 20260313-014143
**Review round**: 2
**Commit range**: 500d88e~1..HEAD (fix commits only)
**Reviewer**: edge-cases

---

## Scope Note

Round 2 scope is fix commits only. Each fix is evaluated against: (a) did the fix land correctly, and (b) did the fix introduce a new boundary failure? Out-of-scope findings (naming, style, docs) are suppressed.

Fix commits reviewed:
- `500d88e` ant-farm-35a5: wrap open/touch in try/except OSError
- `d33fde5` ant-farm-ru51: dual-lookup parent/discovered_from in cmd_list and _auto_close_trail_if_complete
- `87cdd8f` ant-farm-l1en: validate --from-json type and config counter fields
- `74c5cf6` ant-farm-bzhs: fix inverted blocks dependency direction in _convert_beads_record
- `96347af` ant-farm-ch0z: expand FileLock scope in cmd_doctor to cover read-validate-write

---

## Findings Catalog

### F-R2-01
**File:line**: `/Users/correy/projects/ant-farm/crumb.py:1590-1591`
**Severity**: P2
**Category**: Input validation — non-dict `links` value not guarded in `_apply_blocks_deps`
**Description**: In the new `_apply_blocks_deps` function (introduced by ant-farm-bzhs fix), the line:
```python
links = target_record.setdefault("links", {})
blocked_by: List[str] = links.setdefault("blocked_by", [])
```
`dict.setdefault` returns the *existing value* if the key is already present — it does not coerce the type. If a target record has `"links": null`, `"links": []`, or any non-dict value (possible in plain-import records that came from hand-edited or third-party JSONL), `setdefault` returns that non-dict value, and the subsequent `.setdefault("blocked_by", [])` call raises `AttributeError`, crashing `cmd_import --from-beads`. This is a new edge case introduced by the fix: the pre-fix code had the same gap in `_convert_beads_record`, but that path also had no `setdefault` — it would simply skip the dict entirely. The new post-pass is more aggressive and doesn't guard the type.
**Suggested fix**: Replace the two `setdefault` calls with an explicit type guard:
```python
existing = target_record.get("links")
if not isinstance(existing, dict):
    existing = {}
    target_record["links"] = existing
links = existing
blocked_by: List[str] = links.setdefault("blocked_by", [])
```

---

## Fix Verification Summary

| Commit | Fix | Landed Correctly? | New Issues? |
|--------|-----|-------------------|-------------|
| ant-farm-35a5 | `read_tasks`/`iter_jsonl`/`FileLock` OSError guards | Yes — exceptions caught and routed to `die()`. Note: `fh_ctx` is technically unbound if `die()` ever returned (it never does), but not exploitable in practice. | No new P-level issues. |
| ant-farm-ru51 | Dual-lookup parent/discovered_from | Yes — both `cmd_list` filters and `_auto_close_trail_if_complete` now check top-level and `links` sub-dict. | No. |
| ant-farm-l1en | `--from-json` dict check + config counter coercion | Yes — `isinstance(payload, dict)` check at L672 is correctly placed. `read_config()` coercion at L147-151 covers all callers including the import counter path (F-09 from round 1). | No. |
| ant-farm-bzhs | Inverted blocks direction fix via `_apply_blocks_deps` | Mostly yes — direction is corrected. New `_apply_blocks_deps` function has a type-guard gap (F-R2-01 above) when `links` is non-dict. | **Yes — F-R2-01 (P2).** |
| ant-farm-ch0z | FileLock scope expanded to cover full read-validate-write in `cmd_doctor` | Yes — entire doctor body now inside `with FileLock()`. Nested `with FileLock()` for the fix write correctly removed. | No. |

---

## Preliminary Groupings

### Group A: Introduced by ant-farm-bzhs — non-dict `links` guard missing (F-R2-01)
Sole finding. Root cause: `setdefault` does not coerce existing values to the expected type. The fix assumed `links` is always absent or a dict, but import paths can produce non-dict `links` values from external JSONL.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1       | 0     |
| P2       | 1 (F-R2-01) |
| P3       | 0     |
| **Total** | **1** |

---

## Cross-Review Messages

No cross-domain issues identified. No messages sent or received during this round.

---

## Coverage Log

| File | Reviewed | Issues Found |
|------|----------|--------------|
| `/Users/correy/projects/ant-farm/crumb.py` | Yes — all fix hunks reviewed in full | F-R2-01 |

---

## Overall Assessment

**Score**: 9 / 10
**Verdict**: PASS WITH ISSUES

Four of the five fixes landed cleanly and correctly address the round-1 findings. The ant-farm-bzhs fix (blocks direction) introduces one new P2 edge case: if a target record in a beads import has a non-dict `links` value, the new `_apply_blocks_deps` function will crash with `AttributeError` rather than handling it gracefully. This is a narrow but real path — malformed or hand-edited JSONL can produce it. The fix is one type-guard check.
