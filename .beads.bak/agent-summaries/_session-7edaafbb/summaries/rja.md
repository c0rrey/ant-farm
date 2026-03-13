# Task Summary: ant-farm-rja

**Task**: sync-to-claude.sh agent glob fails silently when agents/ directory missing
**Commit**: 4c2f963

## 1. Approaches Considered

1. **Explicit directory guard (if/else)** — wrap the for-loop in `if [ ! -d "$REPO_ROOT/agents" ]; then warn; else loop; fi`. Clear separation of the two paths. Readable. Consistent with the if-block style used elsewhere in this file after g29r changes.

2. **nullglob shell option** — `shopt -s nullglob` before the loop makes a non-matching glob expand to nothing (empty string list) instead of the literal pattern. The loop body then never executes for a missing directory. Bash-specific, works with the existing shebang. However, a missing-directory scenario still produces no warning without additional detection logic, and nullglob must be restored after to avoid side effects on the rest of the script.

3. **One-liner guard before the glob** — `[ -d "$REPO_ROOT/agents" ] || { echo ... >&2; }` followed by the original loop unchanged. Concise but leaves the glob line exposed — if the directory check passes but no .md files match (empty agents/ dir), the loop still runs with the literal glob pattern as a "file" and the `[ -f "$agent" ] || continue` guard silently swallows it. This is an existing behavior, not in scope to fix here, but the explicit if-else is cleaner.

4. **Switch to `find`** — replace the glob with `find "$REPO_ROOT/agents" -name '*.md'` inside an if-directory-exists check. Eliminates the glob-expansion issue entirely. More complex than necessary; find is not needed when the directory is known.

## 2. Selected Approach

**Option 1: Explicit directory guard with if/else.**

Rationale: Most readable. Clearly separates the warning-and-skip path from the normal iteration path. The else-branch preserves the loop exactly as it was, minimizing change scope. Consistent style with the fix introduced for g29r (if-block with stderr warn). AGENTS_CHANGED is initialized before the if-guard so it still drives the reload message correctly in both branches.

## 3. Implementation Description

Changed `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh` lines 47-60:

Before:
```sh
# Sync custom agents to ~/.claude/agents/
AGENTS_CHANGED=false
for agent in "$REPO_ROOT/agents/"*.md; do
    [ -f "$agent" ] || continue
    ...
done
```

After:
```sh
# Sync custom agents to ~/.claude/agents/
AGENTS_CHANGED=false
if [ ! -d "$REPO_ROOT/agents" ]; then
    echo "[ant-farm] WARNING: agents/ directory not found, skipping agent sync: $REPO_ROOT/agents" >&2
else
    for agent in "$REPO_ROOT/agents/"*.md; do
        [ -f "$agent" ] || continue
        ...
    done
fi
```

The warning includes the full expected path to make it actionable for the operator.

## 4. Correctness Review

**File: scripts/sync-to-claude.sh**

- Lines 49-60: if-else correctly checks for directory absence, emits warning to stderr, and otherwise executes the unchanged loop.
- AGENTS_CHANGED is initialized at line 48, before the if-guard, so the reload message at lines 64-67 behaves correctly regardless of whether the agents/ directory exists.
- `bash -n` syntax check passes.
- No unintended changes to any other section.

**Acceptance criteria verification:**
1. Missing agents/ directory produces a warning — PASS (line 50, `>&2`, WARNING prefix, full path included)
2. Script continues normally when agents/ is absent — PASS (no exit call; script reaches "Sync complete." in all branches)

## 5. Build/Test Validation

- `bash -n scripts/sync-to-claude.sh` passes (syntax OK).
- Functional: when `$REPO_ROOT/agents` does not exist, the condition on line 49 is true, the warning fires, the else-branch is skipped, and script execution continues to line 62 ("Sync complete."). AGENTS_CHANGED remains false so the reload message is not printed.
- No automated test suite for shell scripts in this repo.

## 6. Acceptance Criteria Checklist

- [x] Missing agents/ directory produces a warning — PASS
- [x] Script continues normally when agents/ is absent — PASS
