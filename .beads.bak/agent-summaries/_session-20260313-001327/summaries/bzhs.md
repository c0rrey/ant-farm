---
bead: ant-farm-bzhs
title: _convert_beads_record inverts blocks dependency direction
commit: 74c5cf6
---

## Files Changed

- `crumb.py` — removed incorrect `blocked_by.append(depends_on)` from `_convert_beads_record`; added `_apply_blocks_deps` post-processing function; called it from `cmd_import` after `_resolve_beads_epic_refs`

## Implementation

The bug: a Beads dep `{issue_id: A, depends_on_id: B, type: "blocks"}` means "A blocks B", so B's `blocked_by` should contain A. The old code added B to A's `blocked_by` — the semantic inverse.

The fix has three parts:

1. **`_convert_beads_record` cleanup (L1507)**: Removed `blocked_by: List[str] = []` and `blocked_by.append(depends_on)` and the `if blocked_by: links["blocked_by"] = blocked_by` assignment. Added a comment noting blocks deps are handled in the post-pass. Also removed the now-unnecessary `blocked_by` variable initialisation.

2. **New `_apply_blocks_deps` function (L1544-1592)**: Added between `_resolve_beads_epic_refs` and `cmd_import`. It:
   - Builds `record_index` (crumb ID → record) from the converted records list for O(1) target lookup.
   - Builds `beads_id_to_crumb_id` mapping by iterating `raw_beads` and applying `epic_id_map` for epics (whose IDs were rewritten to trail IDs), using the beads ID directly for non-epics.
   - Iterates `raw_beads` again; for each `blocks` dep on source record A pointing to target B, looks up B's converted record and appends A's crumb ID to `B.links.blocked_by`, using `setdefault` to create `links` and `blocked_by` if absent.
   - Deduplicates with `if source_crumb_id not in blocked_by` guard.

3. **`cmd_import` call site (L1673)**: Added `_apply_blocks_deps(raw_beads, converted, epic_id_map)` immediately after `_resolve_beads_epic_refs(converted, epic_id_map)`. `raw_beads` is already in scope as the list of all parsed Beads records.

## Approaches Considered

1. **Fix in-place inside `_convert_beads_record` by passing a `reverse_index` dict**: Pass a mutable `Dict[str, List[str]]` into `_convert_beads_record` and accumulate `reverse_index[B].append(A)` there, then apply it in `cmd_import` after the conversion loop. Functionally equivalent but splits the logic across two places (accumulation in `_convert_beads_record`, application in `cmd_import`) making it harder to reason about. The standalone `_apply_blocks_deps` function is more cohesive.

2. **Change `_convert_beads_record` to return side-channel data**: Return a tuple `(record, blocks_deps)` where `blocks_deps` is a list of `(source_id, target_id)` pairs. Accumulate in `cmd_import` and apply after. Rejected because it changes the function signature and the existing call site, and the `raw_beads` list is already available in `cmd_import` making the raw dep data accessible without any signature change.

3. **Two-pass conversion: first pass builds all records with no deps, second pass applies all deps**: Cleaner conceptually but requires iterating `raw_beads` twice already being done (epics-first sort + main loop). Adding a third pass just for deps is structurally similar to the chosen approach but without the benefit of reusing the already-separated `_apply_blocks_deps` function.

4. **Fix the semantic model: store blocks as `blocks` not `blocked_by`**: Instead of converting "A blocks B" to "B.blocked_by = [A]", store it as "A.blocks = [B]" on the source record. This avoids needing a reverse index entirely. Rejected because the rest of crumb.py (e.g., `_get_blocked_by` at L861, `cmd_show`) consistently uses `blocked_by` on the target record as the canonical representation. Changing the model would break existing code.

5. **Re-read `raw_beads` inside `_apply_blocks_deps` from the original file**: Pass the file path instead of `raw_beads`. Rejected because `raw_beads` is already parsed and in memory in `cmd_import`; re-reading the file is wasteful and introduces a second file handle.

## Per-File Correctness Notes

### crumb.py

- **`_convert_beads_record` (L1495-1515)**: After removing `blocked_by`, the `links` dict is only populated with `parent` (for `parent-child` deps). The `if links:` guard ensures no empty `links: {}` is written to the record. The `depends_on` variable is still read in the loop (used by `parent-child` branch) — no unused variable.
- **`_apply_blocks_deps` `beads_id_to_crumb_id` mapping**: Epics get their mapped trail ID via `epic_id_map`; non-epics use their beads ID directly (which equals their crumb ID since `_convert_beads_record` sets `crumb_id = beads_id` for non-epics at L1464). This correctly handles the case where A or B is an epic.
- **`record_index` keyed by crumb ID**: `_apply_blocks_deps` looks up the target by `target_crumb_id` (after epic remapping), which matches the `id` field written into each converted record. If the target was skipped as a duplicate in `cmd_import`, it won't be in `converted` and `record_index.get(target_crumb_id)` returns `None` — the `if target_record is None: continue` guard handles this safely.
- **`setdefault` usage**: `target_record.setdefault("links", {})` creates `links` only if absent, preserving any existing `links` dict (e.g., one that already has a `parent` key from `parent-child` dep processing). `links.setdefault("blocked_by", [])` similarly preserves any pre-existing `blocked_by` list, though in practice none exists since `_convert_beads_record` no longer writes `blocked_by`.
- **Call order in `cmd_import`**: `_apply_blocks_deps` is called after `_resolve_beads_epic_refs`. This means epic IDs in `links.parent` are already rewritten to trail IDs before `_apply_blocks_deps` runs. `_apply_blocks_deps` independently applies `epic_id_map` to source and target IDs, so the order doesn't create a conflict — both functions are idempotent with respect to each other's output fields (`parent` vs `blocked_by`).
