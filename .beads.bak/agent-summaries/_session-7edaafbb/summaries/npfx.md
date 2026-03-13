# Summary: ant-farm-npfx

**Task**: parse-progress-log.sh hardening gaps (overwrite, dead branch, corruption)
**Commit**: b5bf26b

## Approaches Considered

### Issue 1: Malformed line / timestamp validation (L164-177)

1. **ISO 8601 prefix regex (selected)**: Validate timestamp with `[[ "$timestamp" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2} ]]`. Emits a WARNING to stderr naming the bad timestamp and skips the line. Bash-native, matches observed log format, minimal change.
2. **Non-empty check only**: `[ -z "$timestamp" ] && continue`. Too permissive — rejects truly empty timestamps but accepts any non-empty garbage like "BADDATA".
3. **Field count validation**: Check that at least 2 pipe-delimited fields exist. Coarser than a timestamp check; would still allow malformed timestamps like "BADDATA" as long as there's a pipe.
4. **Strict full-timestamp regex**: Validate full ISO 8601 including seconds, timezone. More precise but also more brittle for edge cases. The prefix match is sufficient since progress.log is internally generated.

### Issue 2: Dead branch comment (L202-207)

1. **Accurate "UNREACHABLE" comment (selected)**: Replace the misleading comment with an accurate explanation: the branch is unreachable because SESSION_COMPLETE is always in STEP_KEYS, and if SESSION_COMPLETE were completed the early-exit guard (exit 2) would have already fired. Minimal change, maximum clarity.
2. **Remove dead branch entirely**: Cleaner but riskier — if a future refactor removes the SESSION_COMPLETE early-exit guard, the fallback would be silently missing. Retaining the branch with accurate comment is safer.
3. **Add runtime assertion**: `echo "BUG: unreachable" >&2; exit 1` inside the branch. More robust but heavyhanded for a dead branch that should never execute.
4. **Restructure RESUME_STEP logic**: Move SESSION_COMPLETE check inside the for loop instead of a pre-check. Over-engineering for a comment fix.

### Issue 3: Silent overwrite (L213-219)

1. **stderr warning before overwrite (selected)**: Check `[ -f "$OUT_FILE" ]` before writing; emit `WARNING: Overwriting existing resume plan` to stderr. Continues with the overwrite (useful when re-running after partial failure). Matches acceptance criterion exactly.
2. **Fail-fast if file exists**: `exit 1` on existing file. Safer for strict environments but breaks valid re-run use cases.
3. **Backup old file**: `mv "$OUT_FILE" "${OUT_FILE}.bak"` before writing. Preserves data but adds complexity not requested.
4. **Append mode**: Append a new plan to the existing file with a separator. Changes output format and would confuse the Queen reading the file.

## Selected Approach with Rationale

- **Timestamp validation**: Regex check against the ISO 8601 prefix used in all progress.log entries. Rejects corruption clearly with a named WARNING. Zero false positives for valid entries.
- **Dead branch comment**: "UNREACHABLE" comment explaining the invariant (SESSION_COMPLETE in STEP_KEYS + early-exit guard). Code is retained as a defensive fallback, comment is now accurate.
- **Overwrite warning**: Pre-write existence check emitting a WARNING to stderr. The overwrite proceeds (correct behavior for re-runs); the caller is informed.

## Implementation Description

Three targeted edits to `scripts/parse-progress-log.sh`:

**1. Timestamp validation (L164-177)** — Added a 4-line guard inside the parse loop:
```bash
if ! [[ "$timestamp" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2} ]]; then
    echo "WARNING: Skipping malformed log line (invalid timestamp '${timestamp}'): ${step_key}|${rest}" >&2
    continue
fi
```

**2. Dead branch comment (L202-207)** — Replaced:
```
# If every step except SESSION_COMPLETE is done but SESSION_COMPLETE is absent, resume at SESSION_COMPLETE
```
with:
```
# UNREACHABLE: RESUME_STEP is always set by the loop above because SESSION_COMPLETE is in
# STEP_KEYS. If SESSION_COMPLETE were completed, the early-exit guard above (exit 2) would
# have already terminated the script. This branch can never be reached during normal execution.
```

**3. Overwrite notice (L215-218)** — Added before the `{...} > "$OUT_FILE"` block:
```bash
if [ -f "$OUT_FILE" ]; then
    echo "WARNING: Overwriting existing resume plan: $OUT_FILE" >&2
fi
```

## Correctness Review

**scripts/parse-progress-log.sh (L164-177)**:
- Timestamp regex `^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}` matches all valid progress.log timestamps (format from `date -u +%Y-%m-%dT%H:%M:%S`) — CORRECT
- The guard is placed AFTER the `[ -z "$step_key" ]` blank-line skip, preserving existing blank-line handling — CORRECT
- WARNING message names the bad timestamp value and the step_key, giving enough context to diagnose corruption — CORRECT

**scripts/parse-progress-log.sh (L202-207)**:
- Comment accurately identifies the branch as unreachable and explains why — CORRECT
- Code branch is retained as a defensive fallback — CORRECT
- The invariant stated (SESSION_COMPLETE in STEP_KEYS + exit 2 guard) is verified by reading L62-72 and L183-188 — CORRECT

**scripts/parse-progress-log.sh (L215-218)**:
- Check uses `[ -f "$OUT_FILE" ]` (file existence), not `-e` (any path type) — appropriate since OUT_FILE is always a regular file path — CORRECT
- Warning goes to stderr, normal output continues to stdout — CORRECT
- Overwrite still proceeds; script exits 0 on success — CORRECT

## Build/Test Validation

Bash syntax check:
```
bash -n scripts/parse-progress-log.sh  # exits 0
```

Integration test — first run (no warning):
```
parse-progress-log.sh: resume plan written to /tmp/.../resume-plan.md
Resume point: Scout Complete: ...
```

Integration test — second run on same directory (overwrite warning):
```
WARNING: Overwriting existing resume plan: /tmp/.../resume-plan.md
parse-progress-log.sh: resume plan written to /tmp/.../resume-plan.md
```

Integration test — malformed timestamp line:
```
WARNING: Skipping malformed log line (invalid timestamp 'BADDATA'): SCOUT_COMPLETE|
parse-progress-log.sh: resume plan written to /tmp/.../resume-plan.md
```
(SCOUT_COMPLETE correctly excluded from completed steps; resume point remains at SCOUT_COMPLETE)

## Acceptance Criteria

- [x] Overwrite produces stderr notice — PASS: `WARNING: Overwriting existing resume plan: <path>` emitted to stderr when file exists
- [x] Dead branch comment is accurate — PASS: comment now reads "UNREACHABLE" and explains the invariant that makes the branch unreachable
- [x] Malformed lines rejected with timestamp validation — PASS: lines whose timestamp field does not match ISO 8601 prefix are skipped with a WARNING naming the bad value
