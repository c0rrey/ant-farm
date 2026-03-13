# Report: Edge Cases Review

**Scope**: docs/plans/2026-02-19-meta-orchestration-plan.md, orchestration/RULES.md, orchestration/templates/checkpoints.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md, scripts/parse-progress-log.sh
**Reviewer**: Edge Cases Review (code-reviewer)

---

## Findings Catalog

### Finding 1: parse-progress-log.sh fails completely under bash 3.2 (macOS default) — exit code collision masks crash
- **File(s)**: `scripts/parse-progress-log.sh:25,113-115`
- **Severity**: P1
- **Category**: edge-case
- **Description**: The script uses `declare -A` (bash 4+ associative arrays) but ships with `#!/usr/bin/env bash`. On macOS, `/usr/bin/env bash` resolves to bash 3.2 (the macOS system bash), which does not support `declare -A`. Under `set -euo pipefail` (line 25), the `declare -A` failure at line 113 exits with code 2. This is exactly the exit code the Queen interprets as "session already completed — proceed with fresh start" (per RULES.md Step 0 and the script's own exit code documentation). As a result, ANY crash recovery attempt on macOS silently discards the recovery plan and starts a new session instead of offering to resume. The script's core function (crash recovery) is completely broken on the primary target platform.

  Verified by running:
  ```
  /usr/bin/env bash scripts/parse-progress-log.sh /tmp/test-session4 → exit 2 (WRONG: was a partial session, not complete)
  ```
- **Suggested fix**: Add a bash version check at the top of the script and exit 1 with an actionable error if bash < 4 is detected. Or rewrite the associative arrays using positional arrays + grep-based lookup (POSIX-compatible). Or update the shebang to `#!/usr/bin/env zsh` (zsh is available on macOS and supports associative arrays, but with `typeset -A` not `declare -A`, requiring additional changes). A simpler fix is to switch to a Python-based implementation or use `awk` for the parse-and-report logic.

  Example bash version guard:
  ```bash
  if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
      echo "ERROR: parse-progress-log.sh requires bash 4+. System has bash ${BASH_VERSINFO[0]}." >&2
      echo "       Install bash 4+ via homebrew: brew install bash" >&2
      exit 1
  fi
  ```
- **Cross-reference**: Blocking correctness issue — correctness reviewer should also see this (wrong exit code from crash recovery means data loss risk: recovery metadata never presented to user).

---

### Finding 2: parse-progress-log.sh fails silently under zsh — step detection broken, wrong exit code for completed sessions
- **File(s)**: `scripts/parse-progress-log.sh:113-115,130-133`
- **Severity**: P1
- **Category**: edge-case
- **Description**: When the script is run via `zsh` (the macOS default shell and the shell used by Claude Code's Bash tool), `declare -A` creates the variable but associative array lookups via bash-style `${arr[key]+set}` syntax always return empty — zsh uses different internal semantics for `declare -A` vs `typeset -A`. The consequence is that ALL array lookups fail silently:
  1. The step6 completion check (`if [ "${STEP_COMPLETED[step6]+set}" = "set" ]`) never triggers, so completed sessions exit with code 0 (resume) instead of code 2 (fresh start). Resume-plan.md is written for already-completed sessions — incorrectly presenting recovery to the user.
  2. All `STEP_COMPLETED[$key]` lookups return empty, so `RESUME_STEP` always equals `step0` (first key not found), regardless of how many steps actually completed.
  3. The resume plan's step status table always shows all steps as "pending" and "RESUME HERE: Step 0" regardless of actual session progress.

  Verified by running:
  ```
  zsh scripts/parse-progress-log.sh /tmp/test-session7 (session with only step6 complete) → exit 0 + resume-plan.md written (WRONG: should be exit 2, no resume-plan)
  zsh scripts/parse-progress-log.sh /tmp/test-session4-complete (step0+step1 complete) → exit 0, resume-plan says "RESUME HERE: Step 0" (WRONG: should say "RESUME HERE: Step 2")
  ```
- **Suggested fix**: Replace `declare -A` with POSIX-compatible parallel arrays, or use a grep-based step detection approach. Example replacement for the three arrays:
  ```bash
  STEP_COMPLETED_KEYS=""
  step_is_completed() { echo "$STEP_COMPLETED_KEYS" | grep -qF "|$1|"; }
  mark_completed() { STEP_COMPLETED_KEYS="${STEP_COMPLETED_KEYS}|$1|"; }
  ```
  Or add `typeset -A` as a zsh compatibility alias before `declare -A`.

---

### Finding 3: progress.log step3b template references non-existent file path
- **File(s)**: `orchestration/RULES.md:186`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The step3b progress log template in RULES.md reads:
  ```
  echo "...|step3b|round=<N>|team=complete|report=${SESSION_DIR}/review-reports/big-head-summary.md"
  ```
  The filename `big-head-summary.md` does not exist — the actual Big Head consolidated report is written to `review-consolidated-{timestamp}.md` (confirmed in reviews.md:632, reviews.md:801, and reviews.md:138). If crash recovery logic were to attempt to read the reported path from the progress log (e.g., a future version of `parse-progress-log.sh` that uses STEP_DETAILS for file-based recovery), it would fail to find the file.

  Currently, `parse-progress-log.sh` only displays the details field as metadata in the resume plan (line 215) and does not validate or open the path. So this is a documentation inaccuracy rather than a runtime failure, but it will mislead any future implementation that reads the path.
- **Suggested fix**: Update the step3b progress log template to reference the correct filename:
  ```
  report=${SESSION_DIR}/review-reports/review-consolidated-${TIMESTAMP}.md
  ```
  This requires the Queen to know the TIMESTAMP at the point of writing the step3b log entry, which it does (TIMESTAMP is generated once at the start of Step 3b).

---

### Finding 4b: Unbound TIMESTAMP variable in dummy reviewer tmux send-keys command
- **File(s)**: `orchestration/RULES.md:176`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The `tmux send-keys` command at line 176 interpolates `${TIMESTAMP}` in a double-quoted string, which expands in the Queen's shell at call time. Step 3b-i instructs the Queen to generate one timestamp per review cycle but contains no `TIMESTAMP=...` shell assignment — the timestamp is only threaded as a positional literal into `fill-review-slots.sh` (line 138: `"<timestamp>"`). If `TIMESTAMP` is unset in the Queen's shell when the tmux command runs, the dummy reviewer is told: "Write your report to `${SESSION_DIR}/review-reports/dummy-review-.md`" (timestamp portion empty). This produces a file with a malformed name (`dummy-review-.md`) on every round, silently colliding if Step 3b-v runs for round 2+. The dummy reviewer also has no way to distinguish this from a legitimate round-1 run.

  Forwarded by clarity-reviewer; confirmed as an edge-case issue (unset variable in shell expansion).
- **Suggested fix**: Add an explicit assignment at the top of the Step 3b-v code block, either deriving from `date` again or capturing the value produced in Step 3b-i:
  ```bash
  # At the top of Step 3b (Step 3b-i), store as a shell variable:
  TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  # Then Step 3b-v's tmux send-keys can reference ${TIMESTAMP} safely.
  ```
  Step 3b-i currently says "The Queen generates ONE timestamp" but does not specify storing it as `$TIMESTAMP`. Adding `TIMESTAMP=$(date +%Y%m%d-%H%M%S)` to Step 3b-i's instructions closes this gap for both the `fill-review-slots.sh` call and the tmux command.

---

### Finding 4: No guard for tmux unavailability in dummy reviewer spawn (RULES.md)
- **File(s)**: `orchestration/RULES.md:168-177`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The dummy reviewer instrumentation block runs `TMUX_SESSION=$(tmux display-message -p '#S')` without checking whether the Queen is running inside a tmux session first. If the Queen is running outside tmux (e.g., during development, testing, or in a CI-like environment), `tmux display-message` exits with an error, which will surface as a command failure in the Queen's context. The `tmux new-window` and `tmux send-keys` calls that follow will also fail.

  There is no `if [ -n "$TMUX" ]` guard or fallback instruction. The meta-orchestration plan documents tmux as a hard architectural requirement, but the current single-Queen workflow (triggered by "Let's get to work") does not require tmux and is the primary workflow users run today.

  The dummy reviewer section has a "Sunset clause" (remove after ~30 sessions), so this is a temporary gap. However, during the measurement period, a Queen running outside tmux will encounter a series of confusing failures.
- **Suggested fix**: Add a guard before the tmux block:
  ```bash
  if [ -z "$TMUX" ]; then
      echo "Note: Not running in tmux — dummy reviewer skipped (instrumentation only)"
  else
      TMUX_SESSION=$(tmux display-message -p '#S')
      DUMMY_WINDOW="dummy-reviewer-round-<N>"
      tmux new-window ...
      sleep 5
      tmux send-keys ...
  fi
  ```

---

### Finding 5: DMVDC Check 2 fallback has no guard for missing acceptance criteria in summary doc
- **File(s)**: `orchestration/templates/checkpoints.md:362-366`
- **Severity**: P3
- **Category**: edge-case
- **Description**: When `bd show {TASK_ID}` fails (infrastructure failure), the DMVDC check instructs Pest Control to "use the acceptance criteria listed in the agent's summary doc instead." However, there is no specified handling for the scenario where the summary doc also lacks an acceptance criteria section (e.g., if the agent wrote a truncated summary or if the summary doc is empty). In this case, Check 2 would have no criteria to verify from either source, but the checkpoint protocol doesn't specify whether to PASS, PARTIAL, or FAIL Check 2 under this double-failure condition.
- **Suggested fix**: Add a clarifying sentence to the fallback instruction:
  > If the summary doc also lacks acceptance criteria (empty or absent section), mark Check 2 as PARTIAL with reason: "Could not retrieve acceptance criteria from either `bd show` or summary doc."

---

## Preliminary Groupings

### Group A: Associative array incompatibility makes crash recovery non-functional
- Finding 1 (bash 3.2 failure) + Finding 2 (zsh failure)
- **Root cause**: `parse-progress-log.sh` uses bash 4+ associative array syntax (`declare -A` with `${arr[key]+set}` lookup) without a version guard. macOS ships bash 3.2 and uses zsh as default shell. Both environments break the script's core functionality, but in different ways (bash 3.2 exits with wrong exit code; zsh runs but all lookups fail silently).
- **Suggested combined fix**: Rewrite step detection without associative arrays, or add an explicit `bash --version` guard at line 25 before `set -euo pipefail`.

### Group B: Documentation template inaccuracies with limited runtime impact
- Finding 3 (wrong filename in step3b progress log template) + Finding 5 (missing guard in DMVDC fallback)
- These are specification gaps that could cause confusion in edge situations but don't cause immediate runtime failures in the current implementation.

### Group C: Missing guards and unbound variables in dummy reviewer launch (RULES.md Step 3b-v)
- Finding 4b (unbound `${TIMESTAMP}` in tmux send-keys) + Finding 4 (no `$TMUX` guard)
- Both findings are in the same Step 3b-v code block. Root cause: Step 3b-v was written without cross-checking what shell variables the Queen has in scope at that point, and without a defensive check for the tmux environment assumption.
- **Suggested combined fix**: Add `TIMESTAMP=$(date +%Y%m%d-%H%M%S)` to Step 3b-i, and wrap the Step 3b-v block in `if [ -n "$TMUX" ]; then ... fi`.

---

## Summary Statistics
- Total findings: 6
- By severity: P1: 2, P2: 1, P3: 3
- Preliminary groups: 3

---

## Cross-Review Messages

### Sent
- To correctness-reviewer: "Finding 1 has a correctness dimension — the wrong exit code from `scripts/parse-progress-log.sh:113` (exit 2 instead of exit 1 on bash 3.2) means the Queen receives false 'session completed' signal. This violates the RULES.md Step 0 contract where exit 2 means 'session completed' and the Queen should proceed with fresh start. May want to note this as an acceptance criteria violation for ant-farm-b219 (crash recovery bead)."

### Received
- From clarity-reviewer: "orchestration/RULES.md:176 — `${TIMESTAMP}` in tmux send-keys is never bound in Step 3b-v. If unset, produces malformed report path." — Action taken: verified at line 176, confirmed variable is not assigned in Step 3b-v scope. Added as Finding 4b (P2).

### Deferred Items
- None

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `docs/plans/2026-02-19-meta-orchestration-plan.md` | Reviewed — no issues | 5 major sections (Architecture, Design Decisions, Task Complexity Scoring, Meta-Scout Behavior, Incremental Delivery Phases), ~270 lines. All shell examples are illustrative bash snippets, not executable code. No input validation or error handling required. Related beads table references valid bead IDs. |
| `orchestration/RULES.md` | Findings: #3, #4b, #4 | 9 workflow steps, 6 tables (Hard Gates, Agent Types, Model Assignments, Concurrency, Template Lookup, Retry Limits), ~395 lines. Finding #3: step3b progress log template references wrong filename. Finding #4b: unbound `${TIMESTAMP}` in tmux send-keys at line 176. Finding #4: no tmux guard for dummy reviewer spawn. |
| `orchestration/templates/checkpoints.md` | Findings: #5 | 5 checkpoint types (SSV, CCO, WWD, DMVDC, CCB), ~710 lines. All checkpoint templates reviewed. Finding #5: DMVDC Check 2 fallback lacks guard for missing criteria in summary doc. SSV infrastructure failure handling (Check 2 and Check 3) includes "more than half" threshold — borderline case at exactly 50% is acceptable by design. |
| `orchestration/templates/pantry.md` | Reviewed — no issues | 3 sections (Implementation Mode, Review Mode/deprecated, Error Handling), ~557 lines. Fail-fast checks (Condition 1, 2, 3) are thorough. The deprecated Section 2 review mode is clearly marked and contains a polling loop that is correct. The Section 1 compose-review-skeletons.sh call has appropriate error handling. |
| `orchestration/templates/reviews.md` | Reviewed — no issues | Big Head consolidation protocol, 4 review type templates, polling loop, P3 auto-filing, ~890 lines. Polling loop timeout logic is correct (30s, 2s interval). The `<IF ROUND 1>` conditional markers are clearly structured for agent implementation. Big Head timeout-and-retry protocol for Pest Control SendMessage response is well-specified. |
| `scripts/parse-progress-log.sh` | Findings: #1, #2 | Single script, ~231 lines. Argument validation (line 31-53) is thorough and handles all invalid input cases correctly. Step key matching logic, resume point detection, and resume-plan.md generation are all correct in their design — but broken at the platform layer due to bash 4+ dependency. |

---

## Overall Assessment
**Score**: 4/10
**Verdict**: NEEDS WORK

Two P1 findings make this NEEDS WORK. The crash recovery script (`parse-progress-log.sh`) is non-functional on both macOS bash 3.2 (wrong exit code) and macOS zsh (silent array failures). Since crash recovery is the primary raison d'être of this script, and the target platform is macOS, this is a blocking issue. The script cannot fulfill its contract on any macOS system without homebrew bash 4+ installed. The one P2 finding (unbound `${TIMESTAMP}` in the dummy reviewer tmux command) will silently produce malformed report filenames every session until fixed. The three P3 findings are minor documentation inaccuracies without immediate runtime impact.
