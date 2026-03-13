# fix-sync-script.md

## Task
Fix 3 review findings in `scripts/sync-to-claude.sh` (RC-4, RC-6, RC-11).

## Changes Applied

### RC-11 (P2) — Backup cp error guard (line 15)
Added an explicit `|| { echo "[ant-farm] ERROR: backup failed" >&2; exit 1; }` guard on the
`cp ~/.claude/CLAUDE.md "$BACKUP_PATH"` call. Previously the script relied solely on `set -e`
to catch a failed backup, which provides no actionable error message and can be suppressed in
subshell contexts. The explicit guard surfaces a clear error and guarantees exit on failure.

### RC-6 (P3) — Replace single-item for-loop with direct cp (lines 36-42)
Replaced the `for script in "$REPO_ROOT/scripts/build-review-prompts.sh"; do ... done` construct
with a straightforward `if [ ! -f ... ]; then ... else cp ... && chmod ... fi` block. A for-loop
over a single hardcoded path adds syntactic noise and obscures intent. The direct if/else is
easier to read, audits more cleanly, and eliminates the misleading implication that the loop
might iterate over multiple items.

### RC-4 (P2) — Empty agents/ warning (lines 49-61)
Added an `agents_synced` counter inside the agent sync loop. After the loop completes, if the
`agents/` directory exists but `agents_synced` is still 0 (i.e., the glob matched nothing or
every match was skipped by the `[ -f ]` guard), a WARNING is emitted to stderr:
`[ant-farm] WARNING: agents/ directory exists but contains no .md files — no agents synced.`
This makes the silent-skip case visible so operators notice misconfigured or accidentally empty
agent directories.

## Commit
`b2fdfee` — fix: sync-to-claude.sh edge cases — empty agents warning, direct cp, backup guard (RC-4, RC-6, RC-11)

## Files Modified
- `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh`
