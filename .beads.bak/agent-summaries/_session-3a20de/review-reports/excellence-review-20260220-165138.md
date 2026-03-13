# Report: Excellence Review

**Scope**: docs/plans/2026-02-19-meta-orchestration-plan.md, orchestration/RULES.md, orchestration/templates/checkpoints.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md, scripts/parse-progress-log.sh
**Reviewer**: Excellence Review (code-reviewer / nitpicker)

---

## Findings Catalog

### Finding 1: Hardcoded 30-Second Polling Timeout With No Configurability
- **File(s)**: `orchestration/templates/pantry.md:382-416`, `orchestration/templates/reviews.md:466-545`
- **Severity**: P3
- **Category**: excellence
- **Description**: The polling loop timeout is hardcoded to 30 seconds in two separate places (pantry.md and reviews.md) with the same value and logic. If the timeout needs adjustment (e.g., in a slow-network environment or with a large reviewer team), it requires editing two files. The two specs are slightly inconsistent: pantry.md's loop uses `{PANTRY_ROUND_1_CHECK_START}` / `{PANTRY_ROUND_1_CHECK_END}` markers while reviews.md uses `<IF ROUND 1>` / `</IF ROUND 1>` markers — two different placeholder conventions for the same conditional construct.
- **Suggested fix**: Document the timeout value as a single named constant at the top of the section, e.g., `TIMEOUT=30  # seconds — adjust if reviewers are slow to start`. Standardize the round-conditional marker syntax across both files to the same convention (`{PANTRY_ROUND_1_CHECK_START}` or `<IF ROUND 1>`, not both).

### Finding 2: parse-progress-log.sh Silently Overwrites resume-plan.md
- **File(s)**: `scripts/parse-progress-log.sh:157-224`
- **Severity**: P3
- **Category**: excellence
- **Description**: The script writes unconditionally to `${SESSION_DIR}/resume-plan.md` using `> "$OUT_FILE"`. If a prior run wrote a resume-plan.md that the user approved and acted on, and the script is called again (e.g., after partial re-crash), the old plan is silently overwritten with no warning. The script header says "never read or overwritten during normal operation" about progress.log, but resume-plan.md has no such protection.
- **Suggested fix**: Before writing, check whether `$OUT_FILE` already exists and log a notice to stderr: `"NOTICE: Overwriting existing resume-plan.md at ${OUT_FILE}"`. This makes re-runs detectable without blocking them.

### Finding 3: Script Uses bash 4+ Associative Arrays — Fails Catastrophically on macOS Default bash 3.2
- **File(s)**: `scripts/parse-progress-log.sh:25,113-115`
- **Severity**: P1
- **Category**: excellence
- **Description**: The script uses `declare -A` (bash 4+ associative arrays) but ships with `#!/usr/bin/env bash`. macOS ships bash 3.2 as the system default; `/usr/bin/env bash` resolves to bash 3.2 on a standard macOS system unless Homebrew bash is installed and first in PATH. The failures are not graceful errors — they are silent functional failures that corrupt the crash-recovery feature:
  - **Under bash 3.2 + `set -euo pipefail`**: `declare -A` is not recognized and causes the script to exit with code 2 (the `set -e` + syntax error path). RULES.md Step 0 interprets exit code 2 as "session already completed — proceed with fresh start", silently discarding all crash recovery data and presenting a new session as if nothing happened.
  - **Under zsh** (macOS default shell): `declare -A` runs without error but associative array lookups return empty strings. The step6 completion check (`[ "${STEP_COMPLETED[step6]+set}" = "set" ]`) never triggers, so completed sessions get offered as "resume" to the user instead of triggering a fresh start.
  Both failure modes mean the entire crash recovery feature (ant-farm-0b4k) is non-functional on a standard macOS developer machine.
- **Cross-reference**: Verified as P1 by edge-cases reviewer (empirically tested on this system). Defer to edge-cases report for deduplication — this finding should merge with edge-cases P1 findings 1 and 2 under a single root cause.
- **Suggested fix**: Add an explicit bash version guard at the top of the script, before any `declare` statements:
  ```bash
  if [ "${BASH_VERSINFO[0]:-0}" -lt 4 ]; then
      echo "ERROR: parse-progress-log.sh requires bash 4+. Current: ${BASH_VERSION:-unknown}" >&2
      echo "On macOS: install bash via Homebrew (brew install bash) and ensure it is first in PATH." >&2
      exit 1
  fi
  ```
  This exits with code 1 (surfaced to user as an error), not code 2 (misread as "session complete").

### Finding 4: parse-progress-log.sh Line 149 — Fallback Resume Logic Has a Reachable Dead Branch
- **File(s)**: `scripts/parse-progress-log.sh:148-151`
- **Severity**: P3
- **Category**: excellence
- **Description**: Lines 148-151 read:
  ```bash
  # If every step except step6 is done but step6 is absent, resume at step6
  if [ -z "$RESUME_STEP" ]; then
      RESUME_STEP="step6"
  fi
  ```
  But the earlier loop already iterates over `STEP_KEYS` which includes `step6`. If step6 is NOT in `STEP_COMPLETED` (which is the only code path to reach lines 148-151 — if step6 were completed, we'd have exited with code 2 at line 130), the loop would have set `RESUME_STEP="step6"` already. The fallback at 148-151 can only be reached if step6 IS the first incomplete step, which the loop would have caught. So the fallback comment "every step except step6 is done but step6 is absent" cannot actually be true at that point — it's a reachable statement but logically redundant, and the comment is misleading.
- **Suggested fix**: Remove the comment or rewrite it. If the logic is intentionally defensive, comment it as "defensive: belt-and-suspenders in case STEP_KEYS is reordered" rather than stating a condition that cannot logically occur.

### Finding 5: Big Head Consolidation Brief Polling Loop Uses Template Markers Not Resolved at Runtime
- **File(s)**: `orchestration/templates/pantry.md:399-419`
- **Severity**: P3
- **Category**: excellence
- **Description**: The polling loop specification in pantry.md uses `{PANTRY_ROUND_1_CHECK_START}` and `{PANTRY_ROUND_1_CHECK_END}` markers (lines 402-405). These are instructions TO the Pantry, not runtime code — the Pantry must substitute or remove them when composing the Big Head brief. However, if the Pantry fails to process these markers (e.g., due to a prompt misunderstanding or hallucination), they will appear verbatim in the Big Head brief, causing Big Head to include them in the bash script it runs — which will produce an error or no-op bash lines. There is no validation step that checks the composed brief for leftover marker strings.
- **Suggested fix**: Add a Pantry self-check step: after composing the Big Head brief, scan it for any remaining `{PANTRY_*}` or `<IF ROUND>` marker patterns and report a SUBSTANCE FAILURE if any are found. This is consistent with the existing placeholder-contamination check for task briefs (pantry.md lines 66-81).

### Finding 6: RULES.md Step 3b-v Dummy Reviewer — TIMESTAMP Variable May Be Unset
- **File(s)**: `orchestration/RULES.md:176`
- **Severity**: P2
- **Category**: excellence
- **Description**: The tmux send-keys command for the dummy reviewer references `${TIMESTAMP}` in the shell string:
  ```bash
  tmux send-keys -t "${TMUX_SESSION}:${DUMMY_WINDOW}" \
    "Perform a correctness review ... Write your report to ${SESSION_DIR}/review-reports/dummy-review-${TIMESTAMP}.md" Enter
  ```
  The `TIMESTAMP` variable must have been set by the Queen earlier in Step 3b (Step 3b-i says "The Queen generates ONE timestamp ... using `date +%Y%m%d-%H%M%S` format"). However, RULES.md does not define a variable name for this timestamp — it describes the Queen generating it but never assigns it to a variable name. The dummy reviewer step uses `${TIMESTAMP}` without establishing that this is the variable name the Queen uses. If the Queen stores the timestamp under a different name (e.g., `REVIEW_TS`), the `${TIMESTAMP}` reference in the send-keys string will expand to empty or error under `set -u`, silently sending a malformed command to the tmux pane.
- **Suggested fix**: Explicitly define the variable name in Step 3b-i: "Store this timestamp as `TIMESTAMP` in your shell context: `TIMESTAMP=$(date +%Y%m%d-%H%M%S)`". This ensures the Step 3b-v reference to `${TIMESTAMP}` resolves correctly.

### Finding 7: SSV Prompt Template Embeds Specific Task IDs From a Different Project
- **File(s)**: `orchestration/templates/checkpoints.md:670-683`
- **Severity**: P3
- **Category**: excellence
- **Description**: The SSV FAIL verdict example in checkpoints.md uses `ant-farm-abc`, `ant-farm-def`, `ant-farm-xyz`, `ant-farm-uvw` as task IDs in the example. While these look like placeholders, they use the `ant-farm-` prefix which could be confused with real ant-farm beads (which also use `ant-farm-` prefix). A reader could mistake these for real bead IDs. This is a minor documentation quality issue but could mislead future maintainers.
- **Suggested fix**: Use clearly fictional IDs in examples, e.g., `project-xxx`, `project-yyy`, or `<task-A>`, `<task-B>` in angle brackets to signal they are placeholders.

### Finding 8: parse-progress-log.sh Has No Handling for Corrupted / Non-Pipe-Delimited Lines
- **File(s)**: `scripts/parse-progress-log.sh:117-124`
- **Severity**: P3
- **Category**: excellence
- **Description**: The progress.log parser reads each line with `IFS='|' read -r timestamp step_key rest`. If a log line is malformed (e.g., a partial write from a crash mid-echo, or contains no pipe character), `step_key` will be empty and the `[ -z "$step_key" ] && continue` guard skips it. However, `timestamp` will contain the entire malformed line. The guard only checks `step_key`, not `timestamp`. If a corrupted line happens to produce a non-empty `step_key` (e.g., the line is `2026-02-19T14:00:00Z` with no pipes at all, making `timestamp="2026-02-19T14:00:00Z"` and `step_key=""`), it is correctly skipped. But if a line has only one pipe (e.g., `garbage|step3`), it would be treated as a valid step3 entry with `rest=""` — potentially marking a step as complete that never actually ran.
- **Suggested fix**: Add a minimum-field validation: require `timestamp` to match ISO 8601 format before treating the line as valid: `[[ "$timestamp" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T ]] || continue`. This rejects lines where the timestamp field doesn't look like a timestamp.

---

## Preliminary Groupings

### Group A: Template Inconsistency — Dual Placeholder Conventions
- Finding 1 (hardcoded timeout / dual marker syntax), Finding 5 (PANTRY_ROUND_1_CHECK markers)
- Root cause: Two different placeholder/marker conventions were introduced at different times (`{PANTRY_*}` braces vs `<IF ROUND>` angle brackets) without a unified convention. This affects maintainability — future editors must know which convention applies where.
- Suggested combined fix: Standardize on one marker style throughout pantry.md and reviews.md for round-conditional blocks.

### Group B: parse-progress-log.sh — bash Version Incompatibility Breaks Crash Recovery (P1)
- Finding 3 (bash 3.2 / zsh incompatibility — P1)
- Root cause: Script uses bash 4+ associative arrays without a version guard, causing silent functional failures (wrong exit code, empty lookups) on macOS default bash 3.2 and zsh. The crash recovery feature (ant-farm-0b4k) is entirely non-functional on a standard macOS system.
- Cross-reference: Edge-cases reviewer independently found and empirically verified this as P1 (edge-cases findings 1 and 2). Big Head should merge under one root cause.
- Suggested combined fix: Add bash version guard (see Finding 3 for exact code).

### Group C: parse-progress-log.sh — Minor Hardening Gaps (P3)
- Finding 2 (silent overwrite of resume-plan.md), Finding 4 (redundant dead branch with misleading comment), Finding 8 (corrupted log line handling)
- Root cause: First-pass implementation; several defensive hardening gaps that don't affect the happy path.
- Suggested combined fix: A single hardening pass on parse-progress-log.sh addressing all three items.

### Group C: Runtime Variable Contract Not Formally Established
- Finding 6 (TIMESTAMP variable name undefined in Step 3b-i)
- Standalone finding. The Step 3b dummy reviewer step references a shell variable that is described but not named in the preceding instructions.

---

## Summary Statistics

- **Total findings**: 8
- **By severity**: P1: 1, P2: 1, P3: 6
- **Preliminary groups**: 4 (Group A: template inconsistency; Group B: bash P1 crash recovery failure; Group C: parse-progress-log.sh hardening; Group D: runtime variable contract)

---

## Cross-Review Messages

### Sent
- To edge-cases-reviewer: "Found bash 3.2 portability issue in scripts/parse-progress-log.sh — `declare -A` requires bash 4+, may be an edge cases boundary condition worth flagging." — Action: flagged for their domain review.

### Received
- From edge-cases-reviewer: "Already covered as P1 findings 1 and 2 — verified empirically. Under bash 3.2, `declare -A` causes script to exit code 2 (misread by RULES.md Step 0 as 'session completed'). Under zsh, lookups return empty so step6 check never fires. Entire crash recovery feature non-functional. Upgrade my Finding 3 to P1." — Action: upgraded Finding 3 from P3 to P1; added cross-reference note; Big Head should merge under one root cause with edge-cases findings 1 and 2.

### Deferred Items
- Finding 3 (bash P1): Reported in both excellence and edge-cases reviews. Deferred to Big Head for deduplication — should result in one root-cause bead.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `docs/plans/2026-02-19-meta-orchestration-plan.md` | Reviewed — no issues | ~280 lines; 6 sections reviewed (Architecture, tmux-Based Spawning, Rolling Pool, Dependency DAG, Worktrees, SSV); all content is documentation/planning prose with no executable components. Diff adds tmux command examples and resolves two open questions. |
| `orchestration/RULES.md` | Findings: #6 | ~396 lines; all workflow steps reviewed; new SSV gate (Step 1b), progress log entries, dummy reviewer instructions (Step 3b-v), stuck-agent diagnostic, wave failure threshold all reviewed. |
| `orchestration/templates/checkpoints.md` | Findings: #7 | ~710 lines; full checkpoint specifications reviewed: SSV (new section, 114 lines), CCO, WWD, DMVDC, CCB. All "Agent type" label clarifications, worked examples table, CCB Check 0 simplification reviewed. |
| `orchestration/templates/pantry.md` | Findings: #1, #5 | ~557 lines; Section 1 (Implementation Mode), Section 2 (Review Mode, deprecated), Section 3 (Error Handling) reviewed. New Step 3.5 (dummy reviewer data file) and polling loop marker system reviewed. |
| `orchestration/templates/reviews.md` | Findings: #1 | ~890 lines; transition gate checklist, team protocol, round-aware protocol, all review type specs, Big Head consolidation protocol (Steps 0-4), Queen checklists reviewed. Diff is small (one line change to DMVDC artifact selection). |
| `scripts/parse-progress-log.sh` | Findings: #2, #3, #4, #8 | 230 lines; complete new file. All sections reviewed: argument validation, step key definitions, progress.log parsing, session-completed check, resume point determination, resume plan output generation. |

---

## Overall Assessment

**Score**: 6.5/10
**Verdict**: NEEDS WORK

The changes implement meaningful workflow improvements (crash recovery, SSV gate, dummy reviewer instrumentation, DMVDC retry artifact selection clarification) but the core deliverable — `scripts/parse-progress-log.sh` — is non-functional on a standard macOS developer machine due to a bash version incompatibility (Finding 3, P1). Under the system default bash 3.2, the script exits with code 2 (misinterpreted by RULES.md Step 0 as "session already completed"), silently discarding all crash recovery. Under zsh, associative array lookups return empty, causing completed sessions to be offered as "resume". A bash version guard is the required fix. The P2 finding (Finding 6, undefined `TIMESTAMP` variable name) is a secondary blocker for the dummy reviewer feature. Fix the P1 first.
