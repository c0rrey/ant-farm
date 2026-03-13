# Edge Cases Review Report

**Review type**: Edge Cases
**Round**: 1
**Commit range**: aebd24d^..HEAD
**Timestamp**: 20260222-181124
**Reviewer**: Nitpicker (Edge Cases specialization)

---

## Findings Catalog

### EC-001

**File**: `scripts/sync-to-claude.sh:52`
**Severity**: P2
**Category**: Input validation / glob expansion
**Description**: The agent loop `for agent in "$REPO_ROOT/agents/"*.md` will include the literal string `"$REPO_ROOT/agents/*.md"` as a single iteration if the `agents/` directory contains no `.md` files (glob does not expand). The guard on line 53 (`[ -f "$agent" ] || continue`) is meant to catch this, but it operates inside the loop body and silently skips without any notice to the operator. If the `agents/` directory exists but is empty or contains only non-.md files, the loop body still executes once with the unexpanded pattern string, the `-f` test fails, `continue` fires, and `AGENTS_CHANGED` is never set to `true` — which is correct but silent. More importantly, the `cp` on line 57 is never reached, which is safe. However, there is **no user-facing warning** when the `agents/` directory exists but yields no `.md` files, leaving the operator with no signal that the sync silently skipped all agents. Unlike the missing-directory case (lines 49-51, which prints a WARNING), the zero-agent case produces no diagnostic output.
**Suggested fix**: After the loop, check whether any `.md` files were actually found and processed; emit a WARNING if the directory exists but no agents were synced:
```bash
AGENTS_SYNCED=0
for agent in "$REPO_ROOT/agents/"*.md; do
    [ -f "$agent" ] || continue
    AGENTS_SYNCED=$((AGENTS_SYNCED + 1))
    ...
done
if [ "$AGENTS_SYNCED" -eq 0 ] && [ -d "$REPO_ROOT/agents" ]; then
    echo "[ant-farm] WARNING: agents/ directory exists but contains no .md files; no agents were synced." >&2
fi
```

---

### EC-002

**File**: `scripts/sync-to-claude.sh:13-17`
**Severity**: P3
**Category**: File operation without error handling
**Description**: The backup of `~/.claude/CLAUDE.md` (lines 13-17) uses `cp` without checking whether the copy succeeded. If the copy fails (e.g., disk full, target directory not writable after `mkdir -p`), the script continues and overwrites the original with no valid backup in place. Under `set -euo pipefail`, a `cp` failure would abort the script — but this is only safe if the backup is not needed further into the script. In this case the original is overwritten on line 20 regardless. If the `cp` on line 16 fails, `set -e` will abort before line 20, so the original is preserved. This is technically safe due to `set -e`, but the error message from bash's implicit exit would be cryptic. The condition is unlikely in practice but worth noting.
**Suggested fix**: P3 — the `set -euo pipefail` on line 2 provides adequate protection. No change strictly required, but an explicit check with a clearer message would improve operability:
```bash
cp ~/.claude/CLAUDE.md "$BACKUP_PATH" || { echo "[ant-farm] ERROR: backup failed, aborting sync." >&2; exit 1; }
```

---

### EC-003

**File**: `scripts/sync-to-claude.sh:36`
**Severity**: P3
**Category**: Boundary condition — single-item for-loop
**Description**: The loop `for script in "$REPO_ROOT/scripts/build-review-prompts.sh"` is a single hardcoded path in a `for` loop construct. If the path contains spaces or special shell characters, the expansion is safe here because it is double-quoted. However, if someone adds a second script to the list (as the code structure invites), they must remember to quote correctly. The current construct is an unusual idiom for a single-file operation. The script comment on line 30-34 explains the intent ("only build-review-prompts.sh is synced"), which mitigates the risk, but the loop form introduces a false affordance suggesting the list is extensible.
**Suggested fix**: P3 — replace with a direct single-file copy for clarity, or leave as-is with the comment. No functional edge case is currently present.

---

### EC-004

**File**: `orchestration/RULES.md:154-173`
**Severity**: P3
**Category**: Input validation — shell variable whitespace stripping
**Description**: The validation block strips whitespace from `CHANGED_FILES` and `TASK_IDS` using `${VAR//[[:space:]]/}` — a bash-specific parameter expansion. The script that runs this block is invoked by the Queen in a bash shell (`bash ~/.claude/orchestration/scripts/build-review-prompts.sh`), so bash is guaranteed. However, the validation block is expressed as inline prose-embedded shell code intended to be run by the Queen itself (not by a script), and the comment on line 162 notes "simpler and more portable than the tr+sed pipeline." If this validation code is ever copy-pasted into a `#!/bin/sh` context or run with `sh` instead of `bash`, `[[:space:]]` in `${VAR//...}` behaves differently (it is a bash extension). This is a documentation/environment assumption issue rather than an active bug.
**Suggested fix**: P3 — the comment documents the bash dependency, and the Queen runs bash. No functional risk under current conditions.

---

### EC-005

**File**: `orchestration/RULES.md:224-234`
**Severity**: P2
**Category**: Race condition / missing guard
**Description**: The dummy reviewer launch block (Step 3b-v, lines 224-234) uses `sleep 5` after opening a new tmux window to give Claude Code time to start, before sending the review prompt via `tmux send-keys`. The 5-second sleep is a fixed wait with no verification that Claude Code actually started and is ready to receive input. On a slow machine, containerized environment, or when Claude Code takes longer than 5 seconds to initialize, the `send-keys` command will send the prompt to an incomplete session (e.g., mid-startup shell or before the Claude Code REPL is ready). The sent keystrokes may be lost, partially consumed by the shell initialization, or sent to the wrong process. The notes on line 241 acknowledge that the report may not materialize — but a premature `send-keys` means the prompt is lost silently rather than the agent legitimately not completing.
**Suggested fix**: This is a "measurement only" path (noted in the sunset clause), so P2 rather than P1. A more robust approach would be to poll for the tmux pane to reach a known ready state before sending keys, or to increase the sleep. Since the feature has a sunset clause, a P3 note may be more proportionate; however, the 5-second assumption is a real timing boundary that can fail silently.

---

### EC-006

**File**: `orchestration/RULES.md:378-380`
**Severity**: P3
**Category**: Platform assumption
**Description**: The session ID generation command on line 378 (`SESSION_ID=$(echo "$$-$(date +%s)-$RANDOM" | shasum | head -c 8)`) uses `shasum`, which is a macOS/BSD tool. On Linux systems, `shasum` may not be installed by default (the equivalent is `sha1sum`). If this project is used on a Linux host, the session ID generation will fail with "command not found". The README and SETUP.md don't document a macOS-only constraint.
**Suggested fix**: Use a more portable command: `sha1sum` with a fallback, or use `shasum -a 1` (available on both platforms if `shasum` is installed). Or document the macOS-only constraint explicitly. P3 because the primary target appears to be macOS (`darwin` platform noted in env), but adopters on Linux would hit this.

---

## Preliminary Groupings

### Group A: Silent failure in shell script operations (EC-001, EC-002)

Both findings involve `scripts/sync-to-claude.sh` operations that complete without producing diagnostic output when something unexpected occurs. EC-001 is the more impactful because an empty agents directory could leave the orchestration system in a broken state with no operator warning. EC-002 is mitigated by `set -e` but the error message is implicit. Root cause: the script has good coverage for the directory-missing case but weaker coverage for the directory-exists-but-empty or copy-failure cases.

### Group B: Platform and environment assumptions (EC-003, EC-004, EC-006)

Three findings share the root cause of implicit platform or runtime-environment assumptions. EC-003 is a false affordance in code structure. EC-004 assumes bash when documented as bash but the code is expressed as inline instructions. EC-006 uses a macOS-only tool without documentation. Root cause: the codebase was developed on macOS and some assumptions have not been made explicit for cross-platform adopters.

### Group C: Timing boundary in dummy reviewer launch (EC-005)

The fixed `sleep 5` is a classic timing assumption that creates a race condition between Claude Code startup and the `send-keys` command. This is isolated to Step 3b-v (sunset clause path) and has a known mitigation (the report may not materialize is acceptable). Root cause: tmux-based automation without a readiness check.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1 | 0 |
| P2 | 2 (EC-001, EC-005) |
| P3 | 4 (EC-002, EC-003, EC-004, EC-006) |
| **Total** | **6** |

---

## Cross-Review Messages

**Sent:**

- To Clarity: "Inconsistent warning coverage in `scripts/sync-to-claude.sh` — the missing-directory case (L49) produces a WARNING but the directory-exists-but-empty case produces no output. Consider flagging for documentation/comment clarity."

**Received:** None at time of writing.

---

## Coverage Log

| File | Status | Notes |
|------|--------|-------|
| `CONTRIBUTING.md` | Reviewed — no edge case issues found | Documentation-only file; no I/O, no validation, no boundaries. |
| `README.md` | Reviewed — no edge case issues found | Documentation-only file; no I/O, no validation, no boundaries. |
| `orchestration/GLOSSARY.md` | Reviewed — no edge case issues found | Reference document; no executable code, no boundaries. |
| `orchestration/RULES.md` | Reviewed — 3 findings (EC-004, EC-005, EC-006) | Shell code blocks embedded in instructions; timing boundary; platform assumption; input validation note. |
| `orchestration/templates/SESSION_PLAN_TEMPLATE.md` | Reviewed — no edge case issues found | Template/planning document; no executable code, no I/O, no boundaries. |
| `scripts/sync-to-claude.sh` | Reviewed — 3 findings (EC-001, EC-002, EC-003) | Shell script; glob expansion, backup error handling, single-item loop form. |

---

## Overall Assessment

**Score**: 7/10

**Verdict**: PASS WITH ISSUES

The codebase is a documentation and shell-script orchestration framework. There are no data-loss or crash-risk edge cases in the current change set. The two P2 findings (EC-001, EC-005) are meaningful:

- EC-001 is a silent-failure gap in the sync script — an operators running `sync-to-claude.sh` with an empty `agents/` directory get no signal that nothing was synced. This is the most actionable finding.
- EC-005 is a timing race in the dummy reviewer launch, but it is self-contained in a sunset-clause path with documented tolerance for non-materialization.

The P3 findings are polish-level. No P1 blockers were identified.
