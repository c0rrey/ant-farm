# Task Summary: ant-farm-i2zd

**Task**: fill-review-slots.sh temp files not cleaned up on abnormal exit
**Commit**: 2b7990a

## Approaches Considered

1. **Per-function ERR trap** — Add `trap 'rm -f ...' ERR` inside `fill_all_slots`. Problem: ERR traps in bash with `set -e` are unreliable across subshells and don't fire on signals (SIGINT, SIGTERM). Does not cover the case where the awk redirect succeeds but mv fails. Rejected.

2. **Subshell isolation** — Run `fill_all_slots` in a subshell; subshell EXIT trap handles local cleanup. Problem: `fill_all_slots` modifies the output file in place; the mv result is a side effect that would be lost when the subshell exits normally. Only abnormal exits would clean up. Not practical.

3. **RETURN trap inside fill_all_slots** — Use `trap 'cleanup' RETURN` (bash-specific) to clean up on both normal and abnormal return from the function. Problem: RETURN trap fires on every return, including successful ones, so it doubles as the normal cleanup path. The `${file}.tmp` file name is not in scope at RETURN trap setup time unless captured beforehand. Feasible but more complex than a top-level EXIT trap.

4. **Top-level EXIT trap with global temp-file registry** — Declare a global `_TMPFILES=()` array. Each `mktemp` result is appended to it. A `_cleanup_tmpfiles` function registered with `trap ... EXIT` removes all registered files. The EXIT trap fires on normal exit, set-e failure, and signals. Normal execution also calls `rm -f` directly so files are not held open for the entire script lifetime. This is the canonical shell scripting cleanup pattern.

5. **mktemp wrapper function** — Define `make_temp()` that calls mktemp and auto-appends to the registry. Reduces boilerplate at each mktemp call site. However, since there is only one call site (`fill_all_slots`), the added indirection is not worth it. Rejected in favor of explicit registration at each mktemp call.

## Selected Approach

**Approach 4 — Top-level EXIT trap with global `_TMPFILES` registry.**

Rationale: Fires on all exit paths (normal, set-e, signal). Normal path still does prompt cleanup via explicit `rm -f`, so the trap is a zero-cost safety net on success. Simple, auditable, and the standard pattern for bash scripts that create temp files.

## Implementation Description

Three additions to `fill-review-slots.sh`:

1. **Global registry and trap setup** (after `set -euo pipefail`, before argument validation):
   ```bash
   _TMPFILES=()
   _cleanup_tmpfiles() {
       if [ ${#_TMPFILES[@]} -gt 0 ]; then
           rm -f "${_TMPFILES[@]}"
       fi
   }
   trap '_cleanup_tmpfiles' EXIT
   ```

2. **Registration in `fill_all_slots`**:
   - `_TMPFILES+=("$mapfile")` immediately after `mapfile="$(mktemp)"`
   - `_TMPFILES+=("$tmpval")` immediately after each per-value `tmpval="$(mktemp)"`
   - `_TMPFILES+=("${file}.tmp")` before the awk invocation (covers the atomic-write temp)

3. **Normal-exit cleanup unchanged**: `rm -f "$mapfile" "${tmpfiles[@]}"` at end of `fill_all_slots` still runs on success; the trap's `rm -f` is a no-op for already-deleted files.

## Correctness Review

**scripts/fill-review-slots.sh** (full file reviewed):

- L46-55: `_TMPFILES=()` initialized before any functions are called; trap registered before argument validation so it fires even on early exit (wrong arg count). Correct.
- L48-53: `_cleanup_tmpfiles` guards with `${#_TMPFILES[@]} -gt 0` before expanding the array — safe under `set -u` even when the array is empty (e.g., if the script exits before `fill_all_slots` is ever called). Correct.
- L187: mapfile registered immediately after creation, before any operation that could fail. Correct.
- L202: each tmpval registered immediately after creation. Correct.
- L208: `${file}.tmp` registered before the awk command that creates it. If awk fails before creating the file, `rm -f` is a no-op. Correct.
- L244: Normal-exit `rm -f "$mapfile" "${tmpfiles[@]}"` still present. The `${file}.tmp` has been consumed by `mv` at this point, so it is no longer in `/tmp`. Correct.
- No other code paths create temp files; resolve_arg, write_filled_review, write_big_head_brief do not call mktemp. Correct.

Acceptance criteria verification:
- AC1 (no orphaned temp files after script failure): EXIT trap fires on all exit paths. PASS.
- AC2 (normal execution still cleans up properly): explicit `rm -f` still runs on success path; EXIT trap is a no-op for already-deleted files. PASS.

## Build/Test Validation

- `bash -n scripts/fill-review-slots.sh` — syntax check passed.
- Manual trap test: confirmed trap fires and cleans up two registered temp files when the script exits abnormally via `false` (simulating set-e exit).
- Normal-exit test: confirmed rm -f in function runs, EXIT trap fires, rm -f on already-deleted files is silent.

## Acceptance Criteria Checklist

- [x] No orphaned temp files after script failure — PASS (EXIT trap registered before any mktemp calls, fires on all exit paths)
- [x] Normal execution still cleans up properly — PASS (explicit rm -f still runs; trap is silent no-op for deleted files)
