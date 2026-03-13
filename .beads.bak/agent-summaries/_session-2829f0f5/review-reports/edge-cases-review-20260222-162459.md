# Edge Cases Review — Round 1
**Timestamp**: 20260222-162459
**Reviewer**: Edge Cases Nitpicker
**Commit range**: b9260b5~1..HEAD

---

## Findings Catalog

### EC-01
**File**: `orchestration/RULES.md:156-176`
**Severity**: P3
**Category**: Input validation — incomplete guard for TASK_IDS
**Description**: The TASK_IDS validation at line 172-176 uses a `tr | sed` pipeline to strip whitespace before checking emptiness:
```bash
if [ -z "$(echo "${TASK_IDS}" | tr -s ' \n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')" ]; then
```
This uses a subprocess pipeline with `echo`, `tr`, and `sed`. The comment above the CHANGED_FILES check (lines 163-168) explicitly notes that bash parameter expansion (`${CHANGED_FILES//[[:space:]]/}`) is "simpler and more portable than the tr+sed pipeline (no subprocesses, no platform-specific tr/sed behavior differences)." Yet the TASK_IDS check immediately below uses exactly the `tr+sed` pipeline that the comment warns against. The inconsistency means TASK_IDS validation relies on the less-robust approach while the rationale for a better approach sits two lines above it. On platforms where `tr` or `sed` behaves differently (e.g., macOS vs. GNU), the TASK_IDS check may fail or silently pass an empty/whitespace-only value.
**Suggested fix**: Apply the same bash parameter expansion pattern:
```bash
if [[ -z "${TASK_IDS//[[:space:]]/}" ]]; then
```
This matches the explicitly preferred pattern documented in the comment above.

---

### EC-02
**File**: `orchestration/RULES.md:227-237`
**Severity**: P3
**Category**: Conditional execution without error path for partial tmux failure
**Description**: The dummy reviewer launch block in Step 3b-v wraps the entire tmux invocation in a guard:
```bash
if command -v tmux > /dev/null 2>&1 && [ -n "$TMUX" ]; then
```
This is correct — it skips the block when tmux is absent or the user is not inside a tmux session. However, the inner `tmux new-window` and `tmux send-keys` calls have no error handling. If `tmux new-window` succeeds but `tmux send-keys` fails (e.g., the new window closed before the send-keys reached it), the error is silently swallowed. The notes section (line 244) does acknowledge "The output report may not materialize" as acceptable, which mitigates the risk. No fix is required for the report non-materialization case. However, a `tmux new-window` failure (e.g., tmux session limit hit) would also go undetected and unlogged, leaving no trace in the progress log that the dummy reviewer was attempted but failed to launch. Impact is low given the sunset clause.
**Suggested fix**: P3 — acceptable as-is given the sunset clause. If the dummy reviewer instrumentation is extended past ~30 sessions, add `|| true` with a stderr note, or log a "DUMMY_LAUNCH_FAILED" entry to the progress log so failures are visible.

---

### EC-03
**File**: `orchestration/RULES.md:381`
**Severity**: P2
**Category**: Race condition / non-unique session ID
**Description**: The session ID generation command is:
```bash
SESSION_ID=$(echo "$$-$(date +%s%N)-$RANDOM" | shasum | head -c 8)
```
`$$` is the current process PID, `$(date +%s%N)` is nanosecond timestamp, and `$RANDOM` is a 0-32767 integer. On macOS (Darwin, which is the documented platform), `date +%s%N` is not supported by the BSD `date` command — `%N` is a GNU extension. On macOS, `$(date +%s%N)` outputs the literal string `%N` rather than nanoseconds, reducing the entropy of the session ID to PID + literal "%N" + RANDOM. This makes collisions more likely when multiple sessions are started rapidly (e.g., two Queens starting in the same second on the same machine). The `_session-` prefix note at line 412-413 states it "prevents collisions when multiple Queens run in the same repo" — but this guarantee is weakened on macOS.
**Suggested fix**: Use a macOS-compatible approach:
```bash
SESSION_ID=$(echo "$$-$(date +%s)-$(python3 -c 'import time; print(int(time.time_ns()))' 2>/dev/null || date +%s)-$RANDOM" | shasum | head -c 8)
```
Or more simply, use `uuidgen | head -c 8` which is available on macOS and produces reliably unique values:
```bash
SESSION_ID=$(uuidgen | tr -d '-' | head -c 8 | tr '[:upper:]' '[:lower:]')
```

---

### EC-04
**File**: `orchestration/RULES.md:383`
**Severity**: P3
**Category**: Missing error check on directory creation
**Description**: Session directory creation:
```bash
mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts,pc,summaries}
```
If `SESSION_DIR` is empty (e.g., if the SESSION_ID generation fails and SESSION_DIR is unset), this expands to `mkdir -p /{task-metadata,previews,...}` — creating directories at the filesystem root. On macOS with SIP enabled, this would fail with a permission error, which would surface the issue. But in environments where root creation is possible (e.g., running as root in a container), this could create unintended directories. Additionally, the progress log written at Step 0 includes `session_dir=${SESSION_DIR}` — if SESSION_DIR is empty, this would log a malformed entry.
**Suggested fix**: Add a guard before the mkdir:
```bash
[[ -z "${SESSION_DIR}" ]] && { echo "ERROR: SESSION_DIR is empty — SESSION_ID generation may have failed." >&2; exit 1; }
mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts,pc,summaries}
```

---

### EC-05
**File**: `orchestration/templates/scout.md:266-289`
**Severity**: P3
**Category**: Error handling gap — partial `bd show` failure not fully documented
**Description**: The error handling section states: "If `bd show` fails for a task: Write a metadata file with `**Status**: error`." This is correct. However, the error metadata template at line 278-287 includes fields like `**Title**: {title from bd list, or "unknown — not in listing"}` and `**Type**: {type from bd list, or "unknown"}`. This means the Scout is expected to cross-reference `bd list` output even when `bd show` fails. But Step 2 only runs `bd list` in `filter` mode — for `ready`, `epic`, or `tasks` modes, `bd list` is not called. If `bd show` fails in `ready` mode, the Scout has no `bd list` output to fall back on for title/type, and would need to use `"unknown"` for all fallback fields. The instructions do not clarify this — a Scout could either silently guess or over-eagerly run `bd list` to populate fallback fields. In `ready` mode, `bd ready` output may contain title summaries, but the template does not reference that.
**Suggested fix**: Clarify the fallback source per mode. For example: "For `ready` mode, use data from `bd ready` output if available; for `tasks` mode, there may be no listing output — use `unknown` for all fields."

---

### EC-06
**File**: `orchestration/SETUP.md:39-42`
**Severity**: P2
**Category**: Missing validation / silent failure path for required external file
**Description**: SETUP.md documents that `code-reviewer` is a required agent type that is NOT deployed by `sync-to-claude.sh`, and must be manually copied:
```
you must copy or create ~/.claude/agents/code-reviewer.md manually.
Without this file, the Nitpicker team members will fail to spawn
```
This is a hard dependency with a manual installation step that has no automated verification. There is no mention of a check users can run to confirm the file is present before starting a session. If a user follows the Quick Setup steps (Step 1 in SETUP.md) and restarts Claude Code, they will not discover the missing `code-reviewer.md` until the review phase fails at runtime — which may be hours into a session.
**Suggested fix**: Add a preflight check to the Quick Setup section or to `sync-to-claude.sh`:
```bash
[ -f ~/.claude/agents/code-reviewer.md ] || echo "WARNING: ~/.claude/agents/code-reviewer.md missing — Nitpicker team will fail to spawn. Copy it manually before starting a session."
```
This is a P2 because the failure mode is not silent (the team spawn will fail with an error message), but the error will occur late and after significant work has already been done, making recovery disruptive.

---

### EC-07
**File**: `orchestration/RULES.md:157-159`
**Severity**: P3
**Category**: Regex pattern does not guard against non-integer inputs with leading zeros
**Description**: The REVIEW_ROUND validation regex is:
```bash
if ! echo "${REVIEW_ROUND}" | grep -qE '^[1-9][0-9]*$'; then
```
This correctly requires a positive integer with no leading zeros (first digit must be 1-9). However, `echo` with double quotes may behave unexpectedly if REVIEW_ROUND contains newlines or shell metacharacters. Using `printf '%s\n'` or a `[[ =~ ]]` bash regex test would be safer. This is a very minor issue — REVIEW_ROUND is set by the Queen from its own state file, so malformed values are unlikely.
**Suggested fix**: Replace with a bash-native test to avoid subprocess:
```bash
if [[ ! "${REVIEW_ROUND}" =~ ^[1-9][0-9]*$ ]]; then
```

---

### EC-08
**File**: `orchestration/RULES.md:88-98`
**Severity**: P3
**Category**: SSV failure path missing retry limit guard
**Description**: Step 1b documents: "On SSV FAIL: Re-run Scout with the specific violations from the SSV report (do NOT present a failed strategy to the user). After Scout revises briefing.md, re-run SSV." The retry logic says to re-run Scout, but no retry count is specified for the SSV→Scout→SSV loop. The Retry Limits table (line 455) lists "Scout fails or returns no tasks: 1 retry" but does not address the SSV FAIL → Scout retry cycle. If the Scout keeps producing a strategy that fails SSV, the Queen could loop indefinitely. This contrasts with DMVDC (2 retries explicitly) and CCB (1 retry explicitly).
**Suggested fix**: Add an explicit SSV retry limit to the Retry Limits table, e.g., "SSV fails after Scout revision: 1" with the same escalation path as other retries.

---

## Preliminary Groupings

### Group A: Platform-Specific Shell Behavior (Root cause: macOS/BSD vs. GNU tooling mismatch)
- **EC-01**: `tr+sed` pipeline used for TASK_IDS when bash expansion is explicitly preferred
- **EC-03**: `date +%s%N` is GNU-only; macOS produces literal `%N`
- **EC-07**: `echo` for regex matching vs. bash-native `[[ =~ ]]`

These share a root cause: shell commands in RULES.md assume GNU tooling behavior but the documented platform (darwin) uses BSD tooling. The most serious is EC-03 (P2) because it weakens session ID uniqueness guarantees. EC-01 and EC-07 are P3 styling/portability issues.

### Group B: Missing Guards on Critical Setup (Root cause: insufficient fail-fast before downstream work begins)
- **EC-04**: No guard on empty SESSION_DIR before mkdir
- **EC-06**: No automated check for required `code-reviewer.md` before session begins
- **EC-08**: No retry limit for SSV→Scout loop

These share the root cause that failures in setup/initialization are either silent or discovered only after significant downstream work. EC-06 (P2) is the most actionable because it affects all adopters doing a fresh install.

### Group C: Incomplete Error Documentation (Root cause: error handling spec is ambiguous about fallback data sources)
- **EC-02**: tmux send-keys failure path undocumented (low impact, sunset clause applies)
- **EC-05**: `bd show` failure fallback references `bd list` output that may not exist in all modes

These are documentation gaps in error handling specs, not code bugs per se.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1       | 0     |
| P2       | 2     |
| P3       | 6     |
| **Total** | **8** |

---

## Cross-Review Messages

**Received** from clarity-reviewer: "CONTRIBUTING.md:165 — comment says bash parameter expansion preferred over tr+sed, but adjacent TASK_IDS block at lines 172-173 uses tr+sed. May be worth flagging as an inconsistency in defensive handling."

**Response sent to clarity-reviewer**: Already captured as EC-01 (orchestration/RULES.md:156-176, P3). No separate filing needed.

---

## Coverage Log

| File | Status |
|------|--------|
| `CLAUDE.md` | Reviewed — no edge case issues found (instructional text only, no executable code) |
| `CONTRIBUTING.md` | Reviewed — no edge case issues found (documentation/instructions, shell commands are illustrative with no validation gaps beyond what already exists in RULES.md) |
| `orchestration/GLOSSARY.md` | Reviewed — no edge case issues found (definitions only, no executable code or I/O paths) |
| `orchestration/RULES.md` | Reviewed — EC-01, EC-02, EC-03, EC-04, EC-07, EC-08 found |
| `orchestration/SETUP.md` | Reviewed — EC-06 found |
| `orchestration/templates/scout.md` | Reviewed — EC-05 found |
| `orchestration/templates/SESSION_PLAN_TEMPLATE.md` | Reviewed — no edge case issues found (planning template only; code blocks are illustrative pseudocode, not executed directly) |
| `README.md` | Reviewed — no edge case issues found (documentation only; all shell commands are illustrative and match guidance in RULES.md) |

---

## Overall Assessment

**Score**: 7/10
**Verdict**: PASS WITH ISSUES

The orchestration system has solid structural edge case handling (REVIEW_ROUND validation, CHANGED_FILES validation, error metadata format for failed `bd show` calls, wave failure thresholds). The findings are concentrated in two areas: platform portability of shell commands (most critical: `date +%s%N` failing silently on macOS) and missing preflight validation for a required external dependency (`code-reviewer.md`). No P1 blockers. Two P2 issues warrant attention before broad adoption on macOS systems or by new adopters setting up fresh installations.
