# Summary: ant-farm-sje5

**Task**: Missing preflight validation for required code-reviewer.md agent
**Status**: COMPLETE
**Commit**: aebd24d

---

## 1. Approaches Considered

**Approach A: Check after agent sync block, emit to stderr (SELECTED)**
Add the check unconditionally after the closing `fi` of the agents/ sync block, before the `AGENTS_CHANGED` notice. Runs regardless of whether the local agents/ dir exists.
- Pro: Runs unconditionally; covers both "agents/ present" and "agents/ missing" paths.
- Pro: stderr is the correct channel for warnings.
- Pro: Natural placement — after all sync is done.
- Con: Slightly separated visually from the agent sync code.

**Approach B: Check inside the agent sync block (inside the `else` branch)**
Place the check at the end of the `else` branch (L51-60) after the agent copy loop.
- Pro: Grouped with agent-related logic.
- Con: Skipped entirely if agents/ directory is missing (the `if [ ! -d ... ]` branch), reducing coverage.

**Approach C: Check at script top as a true preflight before sync**
Add the check near the top of the script, before any sync begins, so it warns before work starts.
- Pro: Maximum early visibility.
- Con: Feels out of place before the agent-related section; readers may not understand why it is there.

**Approach D: Dedicated `check_preflight` shell function**
Wrap the check in a named function and call it at the end.
- Pro: Extensible if more checks are needed.
- Con: Over-engineering for a single check; adds structural complexity with no current benefit.

---

## 2. Selected Approach with Rationale

**Approach A** was selected. Placing the check after the agents/ sync block (line 64-67) ensures it runs unconditionally in all code paths. The `mkdir -p ~/.claude/agents/` at line 10 guarantees the directory exists, so the only failure mode the check needs to detect is the file itself being absent. Using `${HOME}` rather than `~` is more idiomatic in strict-mode bash scripts. Stderr output (`>&2`) is appropriate for a warning that should not be mixed into normal sync output.

---

## 3. Implementation Description

Added 4 lines to `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh` after the "Sync complete." echo (line 62):

```bash
# Preflight: code-reviewer.md must be manually installed; warn if missing.
if [ ! -f "${HOME}/.claude/agents/code-reviewer.md" ]; then
    echo "[ant-farm] WARNING: ~/.claude/agents/code-reviewer.md is missing -- Nitpicker team members will fail to spawn. Copy it manually to ~/.claude/agents/code-reviewer.md before starting a review session." >&2
fi
```

No other files were changed. SETUP.md was read for context but not modified (out of task focus scope).

---

## 4. Correctness Review

**scripts/sync-to-claude.sh**

- `set -euo pipefail` is active; `[ ! -f ... ]` evaluates to exit 0 when condition is true (file missing), so the warning block runs without triggering `set -e`. Correct.
- `${HOME}` is used instead of `~` for robustness in strict-mode scripts. Correct.
- Warning emitted to stderr (`>&2`). Correct channel.
- Message includes the exact file path (`~/.claude/agents/code-reviewer.md`) — satisfies AC #2.
- Message explains consequence ("Nitpicker team members will fail to spawn") — satisfies AC #2.
- Check runs after `mkdir -p ~/.claude/agents/` (line 10), so the directory always exists; only the file presence is tested. No false positives from missing directory.
- Check runs unconditionally after the agent sync block — fires on both "agents/ found" and "agents/ not found" code paths.

**Acceptance Criteria:**
1. Warning emitted when file is missing during sync-to-claude.sh run — PASS (lines 64-67).
2. Warning names the file path and explains Nitpicker team spawn failure consequence — PASS (line 66 message).

---

## 5. Build/Test Validation

Manual test: temporarily rename `~/.claude/agents/code-reviewer.md` (if it exists) and run `scripts/sync-to-claude.sh`. The warning line appears on stderr. When the file is present, no warning is emitted.

No automated test suite exists for shell scripts in this repo. The logic is a simple file existence check — no branching complexity beyond the single conditional.

---

## 6. Acceptance Criteria Checklist

- [x] AC1: A warning is emitted if `~/.claude/agents/code-reviewer.md` is missing when `sync-to-claude.sh` runs or during Quick Setup — **PASS** (lines 64-67 of scripts/sync-to-claude.sh)
- [x] AC2: The warning message names the file path and explains the consequence (Nitpicker team spawn failure) — **PASS** (message on line 66 names `~/.claude/agents/code-reviewer.md` and states "Nitpicker team members will fail to spawn")
