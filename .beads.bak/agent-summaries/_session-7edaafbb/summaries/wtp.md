# Task Summary: ant-farm-wtp
**Task**: scrub-pii.sh does not re-stage issues.jsonl when run standalone outside pre-commit
**Commit**: 9673c91

## 1. Approaches Considered

**A — Detect standalone context via `GIT_INDEX_FILE` env var (selected)**
Git sets `GIT_INDEX_FILE` before invoking any hook. If the variable is absent, the script is running standalone. Check at the end of a successful scrub and print the reminder. No subprocess, no fragile parent-process inspection, no changes to install-hooks.sh.

**B — Check `$0` or `BASH_SOURCE` path for hook directory**
Fragile — the script can be symlinked or called from many paths. Does not reliably distinguish hook vs. standalone invocation.

**C — Add `--hook` flag and pass it from the generated pre-commit script**
Requires modifying install-hooks.sh, which is explicitly out of scope for this task.

**D — Print the reminder unconditionally after every successful scrub**
Simplest implementation. Produces noisy output during git commits (where the hook already handles re-staging). Could mislead users who see the reminder even when running `git commit` normally.

## 2. Selected Approach

Approach A — `GIT_INDEX_FILE` detection. It is the canonical environment variable that git sets for index-modifying hooks (pre-commit, post-commit, etc.). Absence means the script is not running under git's hook dispatcher. This cleanly separates hook context from standalone context without requiring any changes to the generated hook or install-hooks.sh.

## 3. Implementation Description

Added seven lines at the end of `scripts/scrub-pii.sh` (L73-78), after the success echo at L71:

```bash
# When run standalone (outside a git hook), git will not re-stage the modified
# file automatically. Remind the user to stage it before committing.
# GIT_INDEX_FILE is set by git when invoking hooks; its absence means standalone.
if [[ -z "${GIT_INDEX_FILE:-}" ]]; then
    echo "[scrub-pii] Reminder: run 'git add .beads/issues.jsonl' to stage the scrubbed file before committing." >&2
fi
```

The reminder uses stderr (consistent with all warning/error messages), includes the `[scrub-pii]` prefix, and specifies the exact command to run.

The reminder appears only after a successful scrub (after L71). The warning/exit paths at L67-69 exit before reaching the reminder, so users who see a failed scrub are not confused by an additional message.

## 4. Correctness Review

**scripts/scrub-pii.sh**

- L48-56: `--check` mode path exits at L54 or L51 before reaching L73-78 — pre-commit hook behavior in check mode unchanged — PASS
- L67-69: failed/incomplete scrub exits before L73-78 — reminder not shown on failure — PASS
- L71: success echo unchanged — PASS
- L76: `${GIT_INDEX_FILE:-}` uses parameter expansion with empty default to avoid unbound variable error under `set -u` — PASS
- L76-78: block only executes when `GIT_INDEX_FILE` is unset or empty (i.e., standalone run) — PASS
- When git invokes the pre-commit hook it sets `GIT_INDEX_FILE`, so the `[[ -z ... ]]` test is false and no reminder is printed — pre-commit hook behavior unchanged — PASS

Acceptance criteria:
1. "Standalone execution prints reminder about re-staging" — PASS (L76-78)
2. "Pre-commit hook behavior unchanged" — PASS (`GIT_INDEX_FILE` is set by git; reminder block skipped)

## 5. Build/Test Validation

`bash -n scripts/scrub-pii.sh` exits 0 — syntax valid.

Manual test of the condition logic:
```bash
unset GIT_INDEX_FILE
[[ -z "${GIT_INDEX_FILE:-}" ]] && echo "standalone" || echo "hook"
# Output: standalone

export GIT_INDEX_FILE=".git/index"
[[ -z "${GIT_INDEX_FILE:-}" ]] && echo "standalone" || echo "hook"
# Output: hook
```

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| Standalone execution prints reminder about re-staging | PASS — L76-78 prints `[scrub-pii] Reminder: run 'git add .beads/issues.jsonl'...` when `GIT_INDEX_FILE` is absent |
| Pre-commit hook behavior unchanged | PASS — git sets `GIT_INDEX_FILE` before invoking hooks; the reminder block is skipped |
