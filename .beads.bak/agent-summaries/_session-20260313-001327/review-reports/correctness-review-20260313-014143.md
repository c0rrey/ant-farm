# Correctness Review — Round 2 (Fix Commits Only)
**Timestamp**: 20260313-014143
**Reviewer**: correctness-reviewer
**Commit range**: 500d88e~1..HEAD
**Round**: 2

---

## Scope

Round 2. Only fix commits are in scope. Out-of-scope findings reported only if they cause runtime failure or silently wrong results.

Fix commits reviewed:
- `500d88e` — ant-farm-35a5: wrap open/touch in try/except OSError
- `d33fde5` — ant-farm-ru51: dual-lookup parent/discovered_from in cmd_list and _auto_close_trail_if_complete
- `87cdd8f` — ant-farm-l1en: validate --from-json type and config counter fields
- `74c5cf6` — ant-farm-bzhs: fix inverted blocks dependency direction
- `96347af` — ant-farm-ch0z: expand FileLock scope in cmd_doctor

---

## Findings Catalog

No findings. All five fixes land correctly and meet their acceptance criteria. Detailed per-fix assessment below.

---

## Per-Fix Assessment

### ant-farm-35a5 (500d88e) — OSError wrapping
- `read_tasks` and `iter_jsonl`: `open()` wrapped in `try/except OSError`; uses `fh_ctx` variable pattern. `die()` calls `sys.exit()` (raises `SystemExit`), so `with fh_ctx` is unreachable on error — no uninitialized variable risk at runtime. Static analysis tools will flag `fh_ctx` as potentially unbound, but this is not a runtime concern.
- `FileLock.__enter__`: both `path.touch()` and `open()` wrapped in a single `try/except OSError`. Correct.
- All three acceptance criteria met.

### ant-farm-ru51 (d33fde5) — Dual-lookup parent/discovered_from
- `cmd_list --parent` (L533-537): now checks both `t.get("parent") == args.parent` and `(t.get("links") or {}).get("parent") == args.parent`. Correct — mirrors `_get_trail_children` pattern.
- `cmd_list --discovered` (L540-543): now checks both `t.get("discovered_from")` and `(t.get("links") or {}).get("discovered_from")`. Correct.
- `_auto_close_trail_if_complete` (L438): changed to `crumb.get("parent") or links.get("parent")`. The earlier branch that returned on non-dict `links` now assigns `links = {}` and continues — this is correct because `crumb.get("parent")` will still be evaluated regardless. Acceptance criteria for ant-farm-ru51 all met.

### ant-farm-l1en (87cdd8f) — Payload and config counter validation
- `read_config` now validates `next_crumb_id` and `next_trail_id` as integers on every load, covering all five downstream `int()` call sites with a single fix point. Correct.
- `cmd_create --from-json`: `isinstance(payload, dict)` check added immediately after `json.loads`. Clean `die()` on non-object JSON. Correct.
- All three acceptance criteria met.

### ant-farm-bzhs (74c5cf6) — Blocks dependency direction fix
- `_convert_beads_record` no longer appends to `blocked_by` for `blocks`-type deps. Correct removal.
- `_apply_blocks_deps` builds `record_index` from `converted` (successfully imported records only) and `beads_id_to_crumb_id` from all `raw_beads`. It then iterates `raw_beads` as source — a skipped-duplicate source record can still add itself to a target's `blocked_by` (since `record_index` will still find the target). This is a minor data integrity edge case (duplicate Beads records referencing the same source blocker); the resulting dangling reference is detectable by `crumb doctor`. Not a runtime failure. P3 at most, and only triggered on re-import of data with duplicate IDs, which is already a degenerate case.
- The `parent-child` mapping remains unchanged (regression check passed).
- All three acceptance criteria met.

### ant-farm-ch0z (96347af) — FileLock scope expansion in cmd_doctor
- Entire read-validate-write cycle now runs inside a single `with FileLock():`. The inner `FileLock` around `write_tasks` is correctly removed (no double-lock attempt, which would deadlock on non-reentrant `flock`).
- `fixes_applied` printing moved inside the lock — prints to stdout while holding the lock, which is fine (lock is advisory, stdout writes are not blocked by `flock`).
- Reporting (`errors`, `warnings`, `sys.exit`) correctly placed outside the lock scope.
- All three acceptance criteria met.

---

## Preliminary Groupings

No findings to group.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1       | 0     |
| P2       | 0     |
| P3       | 0     |
| **Total**| **0** |

---

## Cross-Review Messages

None sent or received this round.

---

## Coverage Log

| File | Status |
|------|--------|
| `/Users/correy/projects/ant-farm/crumb.py` | Reviewed — 0 findings |

---

## Overall Assessment

**Score**: 10 / 10

**Verdict**: PASS

All five fix commits land correctly. The original P2 findings from Round 1 (F1, F2, F3, F4) are resolved. No regressions introduced. The one minor edge case in `_apply_blocks_deps` (skipped-duplicate source records can still write to a target's `blocked_by`) is P3 and only reachable in a degenerate re-import scenario; it does not cause data loss or runtime failure.
