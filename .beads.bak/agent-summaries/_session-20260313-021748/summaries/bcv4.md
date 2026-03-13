# Summary: ant-farm-bcv4

## Approaches

Four approaches were considered for each fix:

### Fix 1: CODEBASE_ROOT unsubstituted placeholder guard

1. **Prose-only warning (rejected)**: Keep the existing inline note ("substitute `{CODEBASE_ROOT}` before running") and rely on agent compliance. Rejected — this is exactly what already existed and failed; a text note has no enforcement.
2. **Pre-flight variable check with `[ -n "$CODEBASE_ROOT" ]` (rejected)**: Check that the variable is non-empty before running `find`. Rejected — a non-empty string could still be a non-existent path, causing `find` to silently return 0 and trigger the same misclassification bug.
3. **Directory existence guard with `[ -d "$CODEBASE_ROOT" ]` + `exit 1` (chosen)**: Check that the variable resolves to an actual directory on disk. If not, emit a clear `ERROR:` message and exit. This catches both unset variables and invalid paths, producing an explicit failure instead of a silent wrong result.
4. **Wrap `find` in a subshell with `set -u` (rejected)**: Enable `set -u` so an unset variable causes an immediate error. Rejected — `set -u` would affect the entire bash block and could interfere with other optional variables used elsewhere in the workflow; also produces a less readable error message than the explicit guard.

### Fix 2: Forager 100-line cap enforcement

1. **Trust Forager instruction compliance (rejected)**: Leave the cap as a stated rule in the Forager prompt and rely on the agent following it. Rejected — this is the current state and is explicitly what the bug report identifies as having no enforcement mechanism.
2. **Planner reads each file and checks line count before passing to Architect (rejected)**: Have the Planner read each research file post-gate and truncate inline. Rejected — the Planner is explicitly forbidden from reading Forager research files (`orchestration/RULES-decompose.md` Read Permissions section); this would be a scope violation.
3. **Add truncation step in a bash block immediately after gate PASS (chosen)**: After the Research complete gate PASS, run a shell loop with `wc -l` to detect overlong files and `head -100 > .tmp && mv` to truncate them in-place, logging each truncation. This enforces the cap mechanically without requiring the Planner to read file content, and runs before the Architect is spawned.
4. **Add a post-write hook in the Forager instruction to self-truncate (rejected)**: Modify `forager.md` to add a self-truncation step at the end of each Forager's run. Rejected — this fix is scoped to `RULES-decompose.md` only; modifying agent instruction files is out of scope for this bead, and self-truncation in the Forager still leaves the Planner with no fallback if the Forager omits the step.

## Files Changed

- `orchestration/RULES-decompose.md` — 18 insertions, 2 deletions (commit 6766723)

## Implementation

**Change 1 — CODEBASE_ROOT guard (line 129):**
Added `[ -d "${CODEBASE_ROOT}" ] || { echo "ERROR: CODEBASE_ROOT is not set or does not exist"; exit 1; }` as the first line of the brownfield detection bash block. Also corrected the `find` argument from the literal-string form `"{CODEBASE_ROOT}"` to the proper shell variable form `"${CODEBASE_ROOT}"`.

**Change 2 — Post-research line cap enforcement (lines 257–272):**
Added a bash loop after the Research complete gate PASS that iterates over `stack`, `architecture`, `pitfall`, and `pattern` research files. For each file exceeding 100 lines, it logs a `FORAGER_TRUNCATED` entry to `progress.log` and truncates the file in-place via `head -100 ... > .tmp && mv .tmp`.

## Correctness Notes

Re-read: yes

- The guard uses `[ -d ... ]` (directory existence) rather than `[ -n ... ]` (non-empty string), which correctly catches both an unset variable and a path that does not exist on disk.
- The `find` argument fix (removing outer quotes around `{CODEBASE_ROOT}`) is necessary for the guard to be meaningful — without it the guard would pass but `find` would still receive the literal string.
- The truncation loop runs on all four files regardless of `CODEBASE_MODE`. The greenfield skip-notice file for `pattern.md` will be ≤ 100 lines in practice, so the loop is safe to run unconditionally.
- Truncation uses a `.tmp` intermediary and atomic `mv` to avoid leaving a partially-written file if interrupted.
- The `FORAGER_TRUNCATED` log entry captures both the focus area and the original line count, giving downstream diagnostics enough context.
