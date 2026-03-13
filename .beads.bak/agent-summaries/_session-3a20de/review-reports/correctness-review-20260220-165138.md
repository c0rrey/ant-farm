# Report: Correctness Review

**Scope**: docs/plans/2026-02-19-meta-orchestration-plan.md, orchestration/RULES.md, orchestration/templates/checkpoints.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md, scripts/parse-progress-log.sh
**Reviewer**: Correctness Review (code-reviewer)
**Commit range**: dc5082c..HEAD
**Review round**: 1

---

## Findings Catalog

### Finding 1: SSV PASS still requires human approval — contradicts ant-farm-s0ak criterion 3

- **File(s)**: `orchestration/RULES.md:94`, `orchestration/templates/checkpoints.md:698`
- **Severity**: P2
- **Category**: correctness
- **Description**: ant-farm-s0ak acceptance criterion 3 states "PASS allows workflow to continue without human approval." But the current implementation in both RULES.md and checkpoints.md explicitly preserves user approval after SSV PASS:
  - RULES.md:94: "**On SSV PASS**: Present the recommended strategy to the user for approval."
  - checkpoints.md:698: "**On PASS**: Present the recommended strategy to the user for approval (Step 1b in RULES.md). Only after user approval, proceed to spawn Pantry (Step 2)."

  This was introduced as a deliberate fix (commit 3510d66) that re-aligned checkpoints.md to RULES.md. The fix commit message justifies this as aligning with "RULES.md Step 1b which requires user strategy approval." However, the original bead's acceptance criterion 3 explicitly says the human gate should be removed. The resolution leaves one of two contracts unsatisfied: either the bead criterion or the RULES.md design. As filed, the bead's explicit acceptance criterion is unmet.
- **Suggested fix**: If the design decision is to retain user approval post-SSV (reasonable for safety), update the bead description to reflect the final decision, or add a clarifying note in RULES.md Step 1b explaining why user approval is preserved even when SSV passes. If the original criterion should be honored, remove the user approval gate.
- **Cross-reference**: This is a design decision that may be intentional; confirm with project owner whether ant-farm-s0ak criterion 3 has been intentionally superseded by the RULES.md design.

### Finding 2: Progress log step3b entry references wrong consolidated report filename

- **File(s)**: `orchestration/RULES.md:186`
- **Severity**: P2
- **Category**: correctness
- **Description**: The step3b progress log entry in RULES.md embeds a hardcoded report path `big-head-summary.md`, which does not exist. The actual consolidated report is written to `review-consolidated-{timestamp}.md` (documented in reviews.md lines 138, 632 and pantry.md line 464). When a recovery session reads the progress log, the embedded `report=` field will point to a non-existent file.

  RULES.md line 186:
  ```
  echo "...step3b|round=<N>|team=complete|report=${SESSION_DIR}/review-reports/big-head-summary.md"
  ```

  Actual filename pattern (reviews.md line 632):
  ```
  review-consolidated-<timestamp>.md
  ```

  Since the recovery script (`parse-progress-log.sh`) reads this field to "reveal how far it progressed" and the field directly embeds an incorrect file path, any recovery logic that attempts to locate the Big Head report using this field will fail to find the file.
- **Suggested fix**: Change the embedded path to `review-consolidated-${TIMESTAMP}.md` (where TIMESTAMP is the review cycle's timestamp, generated at Step 3b start). If a static path is more practical, reference a symlink or index file that Big Head writes.

### Finding 3: Progress log milestone names diverge from ant-farm-0b4k specification

- **File(s)**: `orchestration/RULES.md:59,98,115,123,186,207,210,213,216`
- **Severity**: P2
- **Category**: correctness
- **Description**: ant-farm-0b4k acceptance criterion 1 states: "Queen appends exactly one log entry after each workflow milestone listed above." The milestone list in the bead is:
  - SCOUT_COMPLETE, PANTRY_IMPL_COMPLETE, DIRT_PUSHER_COMPLETE (one per dirt-pusher), REVIEW_SLOTS_FILLED, NITPICKER_TEAM_SPAWNED, BIG_HEAD_CONSOLIDATED, PC_CHECKPOINT_VERDICT, BEADS_FILED, SESSION_CLOSE_STARTED

  The implementation uses workflow-step keys instead (`step0`, `step1`, `step2`, `step3`, `step3b`, `step3c`, `step4`, `step5`, `step6`) and writes one entry per wave rather than one per dirt-pusher for Step 3. Key divergences:
  1. "one entry per dirt-pusher" (with individual task ID and status) is not implemented — Step 3 logs one entry per wave covering all tasks: `tasks_verified=<ids>`.
  2. SESSION_CLOSE_STARTED milestone is not implemented — the current log writes `step6|complete|pushed=true` after the push, not a "started" marker for landing the plane.
  3. BEADS_FILED, PC_CHECKPOINT_VERDICT, REVIEW_SLOTS_FILLED, NITPICKER_TEAM_SPAWNED — none of these milestones have corresponding progress log entries.

  The per-dirt-pusher granularity was explicitly specified so a recovery session can identify which agents completed and which need re-running. The current per-wave entry does not support individual-agent resume.
- **Suggested fix**: Either (a) add per-dirt-pusher log entries at DIRT_PUSHER_COMPLETE (one per agent, with task ID and summary path), or (b) update the bead to reflect the chosen design (per-wave logging with task ID lists). If the per-wave design was an accepted alternative approach, the bead criterion should be updated to say so.
- **Cross-reference**: This may represent a deliberate simplification; if so, the bead's acceptance criteria text needs updating.

### Finding 4: parse-progress-log.sh completion check uses step6, but bead specifies SESSION_CLOSE_STARTED

- **File(s)**: `scripts/parse-progress-log.sh:130`, `orchestration/RULES.md:216`
- **Severity**: P3
- **Category**: correctness
- **Description**: ant-farm-0b4k specifies "SESSION_CLOSE_STARTED — (marks landing-the-plane initiated)" as the completion signal. The parse-progress-log.sh script checks for `step6` in the log to determine if the session completed (line 130: `if [ "${STEP_COMPLETED[step6]+set}" = "set" ]`). The RULES.md writes `step6|complete|pushed=true` (not `SESSION_CLOSE_STARTED`). These are consistent with each other but inconsistent with the bead's milestone name specification. Not a runtime failure — the detection logic works — but the name doesn't match the bead description.
- **Suggested fix**: Minor — update the bead description or a comment in parse-progress-log.sh to note that `step6` replaces `SESSION_CLOSE_STARTED` as the final milestone key.

### Finding 5: checkpoints.md SSV section FAIL example has no worked PASS example — asymmetric documentation

- **File(s)**: `orchestration/templates/checkpoints.md:674-686`
- **Severity**: P3
- **Category**: correctness
- **Description**: The SSV checkpoint in checkpoints.md provides a detailed FAIL example (lines 674-686) but no PASS example. ant-farm-wiq's acceptance criteria required a FAIL example for the CCO section — which was delivered. However, for SSV, which is a new checkpoint, neither a PASS nor a comprehensive FAIL example was specified in the acceptance criteria. This is minor and stylistic but noted for completeness. Unlike Finding 1, this does not violate any acceptance criterion.
- **Suggested fix**: Not required by acceptance criteria. Can be added as enhancement.

### Finding 7: parse-progress-log.sh uses bash 4+ associative arrays — broken on macOS bash 3.2 (primary target platform)

- **File(s)**: `scripts/parse-progress-log.sh:113-115`, `scripts/parse-progress-log.sh:25`
- **Severity**: P1
- **Category**: correctness
- **Description**: The script uses `declare -A` (bash 4+ associative arrays) at lines 113-115, but the shebang is `#!/usr/bin/env bash`. On macOS (Darwin), `/usr/bin/env bash` resolves to the system bash at `/bin/bash`, which is version 3.2.57 (confirmed on this machine). Under `set -euo pipefail` (line 25), `declare -A` on bash 3.2 exits with a non-zero code — specifically, bash exits with code 2 on this failure.

  Verified behavior:
  ```
  $ /bin/bash --version
  GNU bash, version 3.2.57(1)-release (arm64-apple-darwin25)
  $ /bin/bash -c 'set -euo pipefail; declare -A test_map' 2>&1; echo "exit: $?"
  /bin/bash: line 0: declare: -A: invalid option
  exit: 2
  ```

  RULES.md Step 0 defines exit code 2 from `parse-progress-log.sh` as "the prior session completed — proceed normally with a new SESSION_ID." This means every crash recovery attempt on a stock macOS machine silently treats the prior session as completed and starts fresh. The resume-plan.md is never written. The user is never offered the chance to resume.

  This makes ant-farm-b219 criteria 1 and 2 fail in production on the primary target platform (MacBook Air, as specified in the meta-orchestration plan's Resource Constraints section). No Homebrew bash 5 is installed at `/opt/homebrew/bin/bash` or `/usr/local/bin/bash` on this machine — bash 3.2 is the only bash on PATH.
- **Suggested fix**: Replace the three `declare -A` associative arrays with bash 3.2-compatible alternatives. Simple approach: use two parallel indexed arrays (keys and values) or a flat key=value approach parsed with `grep`. Since the step keys are a fixed known set, a simpler `grep`-based approach would work:
  ```bash
  # Instead of: STEP_COMPLETED["$step_key"]="yes"
  # Use: echo "$step_key" >> /tmp/completed_steps
  # And check: grep -q "^$step_key$" /tmp/completed_steps
  ```
  Alternatively, change the shebang to `#!/usr/bin/env bash5` or `#!/opt/homebrew/bin/bash` with a fallback check, or document that bash 5 via Homebrew is required.
- **Cross-reference**: Flagged by edge-cases reviewer. Confirmed via direct test on this machine. Blocks ant-farm-b219 criteria 1 and 2 in production.

### Finding 6: reviews.md DMVDC transition gate now specifies "most recent by timestamp" but doesn't define timestamp ordering

- **File(s)**: `orchestration/templates/reviews.md:10`
- **Severity**: P3
- **Category**: correctness
- **Description**: ant-farm-pid required documenting the most-recent-by-timestamp rule for wildcard artifact selection. The new text reads: "if multiple files match (e.g., after retries), check the most recent by timestamp — it must contain an explicit PASS verdict, not merely exist." The instruction says "most recent by timestamp" but the artifact filenames contain the timestamp embedded in the name (e.g., `pc-74g1-dmvdc-20260215-003422.md`). To determine most recent by filename-embedded timestamp, one must parse filenames — `ls -t` sorts by file modification time, which may differ from the embedded timestamp if files were copied or modified. This ambiguity could cause a recovery session to select the wrong artifact if files were touched out of order.
- **Suggested fix**: Specify the ordering method: "Use `ls -t` to find the most recently modified file, or sort by embedded timestamp in filename using `ls | sort`." Either works, but the instruction should clarify which is authoritative.

---

## Preliminary Groupings

### Group A: Progress Log Design Diverges from Bead Specification (Findings 2, 3, 4)

Root cause: The progress log implementation chose a simpler step-numbered design rather than the event-named milestone design specified in ant-farm-0b4k. This is a consistent design divergence — not random bugs. Finding 2 (wrong filename in report= field) is a concrete error within this design. Findings 3 and 4 are the broader naming/granularity mismatch.

### Group B: SSV PASS Human Approval Gate (Finding 1)

Root cause: Tension between ant-farm-s0ak's acceptance criterion ("no human approval") and the deliberate fix commit that restored user approval to align with RULES.md. These two sources of truth disagree on the intended design.

### Group C: Minor Documentation Gaps (Findings 5, 6)

Root cause: New checkpoint sections added without parity in examples or timestamp ordering clarity. Low-stakes documentation polish.

### Group D: parse-progress-log.sh Platform Incompatibility (Finding 7)

Root cause: Script written using bash 4+ syntax (`declare -A`) on a platform where the default shell is bash 3.2. Combined with `set -euo pipefail`, this causes the script to exit with code 2 on every invocation — the same exit code that RULES.md defines as "session already completed." The crash recovery feature is silently non-functional on stock macOS.

---

## Summary Statistics

- Total findings: 7
- By severity: P1: 1, P2: 3, P3: 3
- Preliminary groups: 4

---

## Cross-Review Messages

### Sent
- None sent.

### Received
- From edge-cases-reviewer: "parse-progress-log.sh uses declare -A (bash 4+) but macOS has bash 3.2; under set -euo pipefail this exits code 2, which RULES.md interprets as 'session complete' — crash recovery silently broken." — Action taken: verified on this machine (bash 3.2.57, no homebrew bash 5), confirmed exit code 2, filed as Finding 7 (P1).

### Deferred Items
- None deferred.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `docs/plans/2026-02-19-meta-orchestration-plan.md` | Reviewed — no issues | 277 lines, 7 sections reviewed. iTerm2/tmux research findings documented accurately. Open questions section updated with confirmed findings (tmux send-keys + sleep 5 pattern, iTerm2 compatibility). No logic errors or acceptance criteria violations found. ant-farm-lajv criteria 1-4 verified: commands documented, iTerm2 compatibility addressed, meta-orchestration plan updated. |
| `orchestration/RULES.md` | Findings: #1, #2, #3 | 396 lines, 9 workflow steps reviewed. Progress log entries added at each step. Step 1b SSV gate added. Stuck-agent diagnostic procedure and wave failure threshold added per ant-farm-5q3. Counter interaction clarification added per ant-farm-98c. Crash recovery detection block added per ant-farm-b219. |
| `orchestration/templates/checkpoints.md` | Findings: #1 | 711 lines reviewed. SSV section added with full checkpoint template and FAIL example (ant-farm-s0ak). {checkpoint} placeholder defined in term definitions (ant-farm-r8m). Agent type labels updated to "spawned by Pest Control" throughout (ant-farm-957). DMVDC sampling formula expanded with plain English and worked examples (ant-farm-3n2). CCO FAIL example added (ant-farm-wiq). CCB Check 0 simplified to reference "Individual reports above" (ant-farm-3fm). WWD known-limitation note added for ant-farm-c05. |
| `orchestration/templates/pantry.md` | Reviewed — no issues | 557 lines, 3 sections reviewed. Section 2 Step 3.5 added for dummy reviewer data file composition. Correctly excludes dummy report from Big Head consolidation brief. ant-farm-hz4t criteria 2 (identical input to correctness reviewer), 3 (not wired into Big Head), verified correct. |
| `orchestration/templates/reviews.md` | Findings: #6 | 890 lines reviewed. Transition gate check 2 updated for most-recent artifact selection (ant-farm-pid criteria met). Minor timestamp ordering ambiguity noted in Finding 6. |
| `scripts/parse-progress-log.sh` | Findings: #4, #7 | 230 lines reviewed. New file implementing ant-farm-b219 automated recovery. Exit codes 0/1/2 correctly specified. Step keys match RULES.md log entries. Resume plan format is correct. However, `declare -A` on lines 113-115 is bash 4+ syntax that fails on macOS system bash 3.2, causing exit code 2 on every invocation — silently reporting "session complete" when it should offer recovery. |

---

## Acceptance Criteria Verification

### ant-farm-3fm (CCB duplicate paths)
- Criterion: "Report paths appear only once in the CCB template, with Check 0 referencing the earlier listing." **MET** — checkpoints.md Check 0 now reads "Verify that every report file listed in **Individual reports** above exists at its path" (referencing the listing above rather than re-listing).

### ant-farm-3n2 (DMVDC sampling formula)
- Criterion 1: "checkpoints.md DMVDC section includes plain English explanation of the sampling formula." **MET** — "Take one-third of all findings (rounded up), but never fewer than 3 and never more than 5."
- Criterion 2: "At least 3 worked examples show input finding counts and resulting sample sizes." **MET** — 6-row worked example table present.
- Criterion 3: "The formula and English description produce the same results for all examples." **MET** — verified against table values.

### ant-farm-957 (Agent type vs code-reviewer role)
- Criterion 1: "checkpoints.md explicitly states Pest Control orchestrates and code-reviewer executes." **MET** — Role distinction paragraph added at top of Pest Control Overview.
- Criterion 2: "The Agent type field is annotated with spawned agent type to prevent misinterpretation." **MET** — All Agent type fields now read "Agent type (spawned by Pest Control)."
- Criterion 3: "The Pest Control vs code-reviewer distinction is stated once at the top and referenced throughout." **MET** — stated once at top; labels on each section reinforce it.

### ant-farm-c05 (WWD known limitation)
- Criterion: "Either A.5 has an independent scope reference, or the limitation is explicitly documented." **MET** — Known limitation note added after CCO check 1: "The commit range is Queen-provided. If the Queen passes incorrect commit hashes...there is no independent way for Pest Control to derive the 'correct' commit range."

### ant-farm-r8m ({checkpoint} placeholder definition)
- Criterion: "{checkpoint} is defined in the term definitions block or has an explanatory note." **MET** — Line 11: `{checkpoint}` defined in the term definitions block with examples.

### ant-farm-wiq (CCO FAIL example)
- Criterion: implied — a FAIL example with check number, name, and evidence. **MET** — FAIL example added to CCO section showing Failed checks with evidence and passing checks.

### ant-farm-0b4k (progress log)
- Criterion 1: "Queen appends exactly one log entry after each workflow milestone listed above." **PARTIALLY MET** — Step-numbered entries cover the workflow steps but do not produce per-dirt-pusher entries (DIRT_PUSHER_COMPLETE per agent). See Finding 3.
- Criterion 2: "Log is append-only — Queen never reads or overwrites the file during normal operation." **MET** — All entries use `>>` append. The file is read only by parse-progress-log.sh.
- Criterion 3: "Each entry includes enough context (paths, counts, status) to determine resume point." **MET** — Each entry includes relevant path/count/status fields.
- Criterion 4: "Progress log is written to {session-dir}/progress.log." **MET** — All echo commands target `${SESSION_DIR}/progress.log`.
- Criterion 5: "Format is human-readable with pipe-delimited fields." **MET** — `TIMESTAMP|step_key|field=value...` format.

### ant-farm-98c (retry counter interaction)
- Criterion: "Retry table explicitly states how per-checkpoint retries interact with the session total." **MET** — Counter interaction paragraph added: "each CCB re-run counts as 1 toward both the per-checkpoint limit (1) and the session total (5)."

### ant-farm-pid (DMVDC wildcard artifact selection)
- Criterion 1: "reviews.md transition gate specifies which artifact to check when multiple match the wildcard." **MET** — "if multiple files match...check the most recent by timestamp."
- Criterion 2: "The most-recent-by-timestamp rule is documented for retry scenarios." **MET** — explicitly mentioned.
- Criterion 3: "The PASS verdict requirement is explicit (not just file existence)." **MET** — "it must contain an explicit PASS verdict, not merely exist."

### ant-farm-lajv (tmux + iTerm2 research)
- Criterion 1: "Document the exact commands needed to: start a tmux control mode session, create a new window, send a prompt to that window, and check window status." **MOSTLY MET** — commands for new-window, send-keys, display-message, list-windows, kill-window documented. Starting a tmux control mode session itself is not explicitly documented (the plan focuses on attaching to existing sessions).
- Criterion 2: "Verify whether tmux send-keys works as expected in control mode or if an alternative is needed." **MET** — documented that standard tmux commands work identically regardless of -CC client.
- Criterion 3: "Update the dummy reviewer bead's description." **CANNOT VERIFY** — bead update would be in bd, not in reviewed files.
- Criterion 4: "Update the meta-orchestration plan with correct iTerm2 control mode commands." **MET** — docs/plans/2026-02-19-meta-orchestration-plan.md updated with iTerm2 compatibility section and status-checking commands.

### ant-farm-s0ak (SSV checkpoint)
- Criterion 1: "Haiku PC agent runs after Scout returns and before Pantry is spawned." **MET** — RULES.md Step 1b runs before Step 2 (Pantry).
- Criterion 2: "All three checks (file overlap, file list match, dependency ordering) are performed." **MET** — all three checks documented in checkpoints.md SSV section.
- Criterion 3: "PASS allows workflow to continue without human approval." **NOT MET** — See Finding 1. Both files retain user approval gate on SSV PASS.
- Criterion 4: "FAIL halts workflow and reports specific violations." **MET** — FAIL response documented in RULES.md and checkpoints.md.
- Criterion 5: "Checkpoint report written to {session-dir}/pc/pc-session-ssv-{timestamp}.md." **MET** — verified in checkpoints.md SSV section.

### ant-farm-5q3 (error recovery procedures)
- Criterion 1: "RULES.md retry limits table includes entries for Pantry and Scout with retry counts." **MET** — Pantry CCO fails (1 retry) and Scout fails (1 retry) rows added.
- Criterion 2: "A step-by-step stuck-agent diagnostic procedure is documented." **MET** — 5-step Stuck-Agent Diagnostic Procedure added.
- Criterion 3: "A wave-level failure threshold (e.g., >50%) triggers pause and user notification." **MET** — Wave Failure Threshold section added with >50% trigger.

### ant-farm-hz4t (dummy reviewer via tmux)
- Criterion 1: "Dummy reviewer spawns as a tmux window during the review phase." **MET** — RULES.md Step 3b-v documents the tmux window launch.
- Criterion 2: "Dummy reviewer receives identical input to the correctness reviewer." **MET** — cp command copies review-correctness.md as review-dummy.md.
- Criterion 3: "Big Head does not read or consolidate the dummy reviewer's report." **MET** — explicitly documented in RULES.md notes and pantry.md.
- Criterion 4: "User can observe context usage in the dummy reviewer's tmux pane." **MET** — documented in notes.
- Criterion 5: "Dummy reviewer can be removed without affecting the rest of the workflow." **MET** — sunset clause documented.

### ant-farm-b219 (automated crash recovery)
- Criterion 1: "Incomplete progress logs are detected on session startup." **NOT MET IN PRODUCTION** — RULES.md Step 0 detection logic is correct, but parse-progress-log.sh fails immediately with exit 2 on macOS bash 3.2 due to `declare -A` incompatibility. RULES.md interprets exit 2 as "session already completed," so the detection silently fails and no resume plan is offered. See Finding 7.
- Criterion 2: "A structured resume plan is presented showing completed/in-progress/pending steps." **NOT MET IN PRODUCTION** — resume-plan.md is never written because the script exits before reaching the plan-writing section. See Finding 7.
- Criterion 3: "User can approve resume or choose fresh start." **MET** — the protocol is correctly documented in RULES.md; blocked only by the script failure.
- Criterion 4: "No action is taken automatically — user must approve the resume plan." **MET** — script only writes the plan; RULES.md says "Wait for the user to reply."

---

## Overall Assessment

**Score**: 5/10

**Verdict**: NEEDS WORK

The implementation delivers all major features (progress log, SSV checkpoint, dummy reviewer instrumentation, error recovery procedures, iTerm2 research) correctly. However, the crash recovery script — the primary deliverable of ant-farm-b219 — is broken on the target platform (macOS bash 3.2) due to use of bash 4+ `declare -A` associative arrays. Every crash recovery attempt silently resolves to "session complete, start fresh," defeating the feature's purpose.

P1 finding (Finding 7) blocks shipping:
- `scripts/parse-progress-log.sh:113-115` — `declare -A` on bash 3.2 exits code 2 under `set -euo pipefail`, which RULES.md misinterprets as "session already completed."

P2 findings:
1. RULES.md:186 — step3b progress log entry embeds a non-existent `big-head-summary.md` path (actual: `review-consolidated-{timestamp}.md`).
2. RULES.md:94 + checkpoints.md:698 — ant-farm-s0ak criterion 3 (no human approval on SSV PASS) unmet by design choice; needs bead or RULES.md update to resolve the contradiction.
3. RULES.md progress log milestone naming deviates from ant-farm-0b4k per-dirt-pusher granularity spec.
