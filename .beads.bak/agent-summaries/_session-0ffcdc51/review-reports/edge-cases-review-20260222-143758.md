# Report: Edge Cases Review

**Scope**: agents/big-head.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
**Reviewer**: edge-cases / code-reviewer

---

## Findings Catalog

### Finding 1: Polling loop timeout is off-by-one — can run up to 32 seconds instead of 30

- **File(s)**: `orchestration/templates/reviews.md:L565-584`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The polling loop initializes `ELAPSED=0` and enters `while [ $ELAPSED -lt $POLL_TIMEOUT_SECS ]`. On each iteration it checks files, sleeps `$POLL_INTERVAL_SECS` (2s), then adds 2 to ELAPSED. This means the loop's final possible iteration starts at ELAPSED=28 (still `< 30`), then sleeps 2 more seconds before incrementing to 30, giving a maximum actual wait of 30 seconds elapsed + the 2-second sleep = 32 seconds of wall-clock time before the timeout is reported. The comment at L490 says "Wait a maximum of 30 seconds" but the script can wait up to 32. Minor breach of the documented contract; in practice harmless but the comment is misleading.
- **Suggested fix**: Either change `POLL_TIMEOUT_SECS=30` to `28`, or change the `while` condition to `while [ $ELAPSED -le $((POLL_TIMEOUT_SECS - POLL_INTERVAL_SECS)) ]`, or document the distinction between "30 seconds of polling" and "30 seconds of wall-clock wait".
- **Cross-reference**: Clarity domain (misleading comment) — mentioned here only because the off-by-one also affects the actual timing behavior.

---

### Finding 2: Polling script exit does not write failure artifact — leaves downstream consumers with no written record

- **File(s)**: `orchestration/templates/reviews.md:L586-589`, `orchestration/templates/big-head-skeleton.md:L91-99`
- **Severity**: P2
- **Category**: edge-case
- **Description**: When the polling loop times out, the script emits `echo "TIMEOUT: Not all expected reports arrived within ${POLL_TIMEOUT_SECS}s"` and `exit 1`. The instruction to write a failure artifact to `{CONSOLIDATED_OUTPUT_PATH}` is expressed only in the surrounding narrative prose (`big-head-skeleton.md:L91-99`), not inside the script block itself. If Big Head executes the bash block as a single invocation (as directed by the comment at `reviews.md:L497`), the exit happens before Big Head can read and act on the narrative prose. Result: downstream consumers (Queen, Pest Control) find no file at the expected `{CONSOLIDATED_OUTPUT_PATH}` — a worse failure mode than finding a FAILED artifact because the absence of the file may be misinterpreted as Big Head not having run at all.
- **Suggested fix**: Move the failure artifact write command into the bash script block itself, just before `exit 1`:
  ```bash
  if [ $REPORTS_FOUND -eq 0 ]; then
    echo "TIMEOUT: Not all expected reports arrived within ${POLL_TIMEOUT_SECS}s"
    cat > "$CONSOLIDATED_OUTPUT_PATH" << 'EOF'
  # Big Head Consolidation — BLOCKED: Missing Nitpicker Reports
  **Status**: FAILED — prerequisite gate timeout
  ...
  EOF
    exit 1
  fi
  ```
  This requires `$CONSOLIDATED_OUTPUT_PATH` to be set as a shell variable before the loop, which the Pantry already provides as a filled placeholder.
- **Cross-reference**: None.

---

### Finding 3: Temp file `/tmp/bead-desc.md` has no session uniqueness — concurrent Queen sessions will collide

- **File(s)**: `agents/big-head.md:L23`, `orchestration/templates/reviews.md:L794`, `orchestration/templates/reviews.md:L836`
- **Severity**: P2
- **Category**: edge-case
- **Description**: All three bead-filing code blocks write to the same temp file path `/tmp/bead-desc.md` and then `rm -f` it afterward. In a multi-Queen environment (documented in MEMORY.md as a real production scenario with brief lock contention), two concurrent Big Head consolidation agents writing to the same path will silently corrupt each other's bead descriptions. The first `bd create` may succeed with correct content; the second may succeed with content from a different root cause (or an empty/partial file if the first agent's `rm -f` races with the second agent's write). There is no error from `bd create` — it will file a bead with wrong or empty description.
- **Suggested fix**: Use a session-specific or process-specific temp file name, e.g. `/tmp/bead-desc-$SESSION_SUFFIX-$$.md` (where `$$` is the shell PID). The session suffix is available in Big Head's context as it is embedded in all artifact paths.
- **Cross-reference**: None.

---

### Finding 4: `bd list --status=open` for cross-session dedup has no error handling — silent skip on lock failure

- **File(s)**: `agents/big-head.md:L22`, `orchestration/templates/reviews.md:L679`
- **Severity**: P2
- **Category**: edge-case
- **Description**: Before filing beads, Big Head runs `bd list --status=open -n 0 --short` to check for existing duplicates. If the beads database is locked by another process (dolt access lock contention, documented in MEMORY.md as a real production scenario), this command fails with a non-zero exit code and outputs a lock error. There is no instruction to check the exit code, retry, or abort filing. Big Head's instructions say only to "check for matching titles" — if the command fails, there are no titles to check, and Big Head proceeds to file beads that may already exist as open issues. The result is silent duplicate filing.
- **Suggested fix**: Wrap the `bd list` call with exit-code checking:
  ```bash
  if ! bd list --status=open -n 0 --short > /tmp/open-beads.txt 2>&1; then
    # lock contention or other error — abort to avoid duplicate filing
    echo "ERROR: bd list failed (lock contention?). Aborting bead filing to prevent duplicates."
    exit 1
  fi
  ```
  Alternatively, add a retry loop consistent with the retry guidance in MEMORY.md.
- **Cross-reference**: None.

---

### Finding 5: `{CONSOLIDATED_OUTPUT_PATH}` placeholder in big-head-skeleton.md failure artifact block — unfilled placeholder silently misfires

- **File(s)**: `orchestration/templates/big-head-skeleton.md:L91-99`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The failure artifact write instruction in `big-head-skeleton.md:L91-99` references `{CONSOLIDATED_OUTPUT_PATH}` as the destination file path. This is a placeholder that must be substituted by the Pantry (or Queen) before delivery to Big Head. If the Pantry fails to substitute it (e.g., partial failure in prompt composition), Big Head would attempt to write the failure artifact to a directory literally named `{CONSOLIDATED_OUTPUT_PATH}` which does not exist, and the write silently fails or errors. Since this failure artifact is the only written record of the timeout, downstream consumers again find nothing at the expected path.

  Note: this is distinct from Finding 2 — Finding 2 is about the *bash script* not writing the artifact; this finding is about the *LLM narrative instruction* using an unfilled placeholder even if the agent were to follow it.
- **Suggested fix**: The Pantry's fill step for `{CONSOLIDATED_OUTPUT_PATH}` should include verification that this specific path is substituted in the failure artifact prose block. Alternatively, the narrative could use a relative placeholder that the agent can resolve from context: "write to the consolidated output path specified in your prompt."
- **Cross-reference**: None.

---

### Finding 6: Pest Control verdict timeout escalation specifies no failure artifact — Queen receives only a message, no written record

- **File(s)**: `orchestration/templates/reviews.md:L765-773`, `agents/big-head.md` (implied by step 10)
- **Severity**: P3
- **Category**: edge-case
- **Description**: When Pest Control does not respond after 120 seconds (2 attempts × 60s), Big Head is instructed to "escalate to the Queen immediately" with a formatted message. Unlike the missing-report timeout case (which specifies a failure artifact be written to `{CONSOLIDATED_OUTPUT_PATH}`), the Pest Control timeout escalation has no corresponding instruction to write a failure artifact at the consolidated output path. If the Queen is not watching the session in real time, there is no written record of what happened — only the in-memory message. If the session is interrupted after escalation but before the Queen acts, the state is lost.
- **Suggested fix**: Add an instruction to write a failure artifact to `{CONSOLIDATED_OUTPUT_PATH}` before or alongside the escalation message, using the same standard format as the missing-report failure artifact.
- **Cross-reference**: None.

---

### Finding 7: Pantry Section 1 Step 3 reads `dirt-pusher-skeleton.md` without existence check

- **File(s)**: `orchestration/templates/pantry.md:L143`
- **Severity**: P3
- **Category**: edge-case
- **Description**: Step 3 instructs the Pantry to "Read `~/.claude/orchestration/templates/dirt-pusher-skeleton.md`" with no fallback behavior specified if the file is missing. The Pantry's Section 3 error handling (L414-417) only covers per-task-brief failures; it does not describe what to do if a template file is missing. In practice the file exists today (verified), but the absence of a guard means any future rename, move, or deletion of this file would cause the Pantry to fail with no diagnostic written to disk. There is no corresponding failure artifact instruction for this case.
- **Suggested fix**: Add a fail-fast check before reading the skeleton: verify the file exists and write a FAILED artifact to `{session-dir}/prompts/task-previews-FAILED.md` if not. Consistency with the existing Condition 1/2/3 fail-fast pattern in Section 1 Step 2.
- **Cross-reference**: None.

---

### Finding 8: Round 2+ reviewer instructions instruct agent to check `[OUT-OF-SCOPE]` tag semantics only after dedup — tag has no enforcement

- **File(s)**: `orchestration/templates/reviews.md:L199-207`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The Round 2+ Reviewer Instructions at L199-207 define what is and is not reportable in fix-verification scope. Reviewers are told to use the `[OUT-OF-SCOPE]` tag for labeling. But L208 says "Big Head treats all findings identically for dedup and root-cause grouping regardless of tag." There is no mechanism to suppress out-of-scope P3 findings from being filed as beads if Big Head consolidates them under a root cause that also includes in-scope findings. A P3 finding tagged `[OUT-OF-SCOPE]` could inadvertently elevate the priority of a root-cause group if merged with an in-scope P2. The tag is informational only with no enforcement path.
- **Suggested fix**: Add an explicit instruction to Big Head (in the consolidation brief or reviews.md Big Head protocol): "If an [OUT-OF-SCOPE] finding is merged with an in-scope finding, do NOT use the out-of-scope finding's severity contribution — use only in-scope severities when computing combined priority."
- **Cross-reference**: Correctness reviewer — the severity merging logic may violate intended behavior. Messaging correctness reviewer.

---

### Finding 9: P3 auto-filing in big-head-skeleton.md provides no guidance for capturing epic ID or new bead ID from command output

- **File(s)**: `orchestration/templates/big-head-skeleton.md:L151-169`
- **Severity**: P3
- **Category**: edge-case
- **Description**: Step 11's bash block at L167 uses `bd dep add <new-bead-id> <epic-id> --type parent-child` as a literal example. Neither `<new-bead-id>` nor `<epic-id>` is set as a shell variable anywhere in the block. An agent executing this literally would either pass the placeholder strings verbatim to `bd dep add` (causing a command error) or must infer how to capture the values from command output without guidance. The `bd create` command at L166 presumably prints the new bead ID, but there is no `NEW_BEAD_ID=$(bd create ...)` assignment shown. Similarly, the find-or-create line at L152 — `bd list --status=open | grep -i "future work"` or `bd epic create ...` — has no capture pattern for the epic ID. A round 2+ Big Head following these instructions has no reliable path to a correct `bd dep add` call.
- **Suggested fix**: Make the ID capture explicit in the code block:
  ```bash
  EPIC_ID=$(bd list --status=open | grep -i "future work" | awk '{print $1}')
  if [ -z "$EPIC_ID" ]; then
    EPIC_ID=$(bd epic create --title="Future Work" --description="..." | awk '{print $NF}')
  fi
  # ... for each P3:
  NEW_BEAD_ID=$(bd create --type=bug --priority=3 --title="<title>" --body-file /tmp/bead-desc.md | awk '{print $NF}')
  bd dep add "$NEW_BEAD_ID" "$EPIC_ID" --type parent-child
  ```
  The exact parsing pattern depends on `bd` output format, but the structural gap (no capture shown) should be closed.
- **Cross-reference**: Flagged by correctness-reviewer as pre-existing (predates current commit range asdl.*). Confirmed within edge-cases domain — missing input capture is a boundary/robustness concern.

---

## Preliminary Groupings

### Group A: Failure artifact not written to disk on failure paths (Findings 2, 5, 6)

All three findings share the same root cause: instructions to produce a written failure artifact either live only in narrative prose (not in the code that runs at failure time), use an unfilled placeholder for the output path, or are omitted entirely for one of the failure paths (Pest Control timeout). The underlying design flaw is that failure artifact writes are described as LLM-level instructions rather than being embedded in the executable bash code blocks that trigger on failure.

- **Suggested combined fix**: For every failure path (polling timeout, Pest Control timeout), write the failure artifact inside the bash script block before `exit 1`, using a shell variable for the output path that is set early in the script.

### Group B: No error handling for external command failures (Findings 3, 4)

Findings 3 and 4 share the root cause that external command invocations (`bd list`, `bd create`) have no exit-code checking and no retry logic at the points where concurrent access or lock contention can occur. The pattern is: assume command succeeds, act on result, no fallback.

- **Suggested combined fix**: Add exit-code checks with explicit error messages and abort-or-retry logic to all `bd` command invocations in Big Head's bead-filing workflow.

### Group C: Standalone findings (Findings 1, 7, 8, 9)

These four findings do not share a root cause with each other or with Groups A/B. Each is a distinct gap. Finding 9 (missing ID capture in auto-filing) is pre-existing per correctness-reviewer — not introduced in the current commit range.

---

## Summary Statistics

- Total findings: 9
- By severity: P1: 0, P2: 4 (Findings 2, 3, 4, 5), P3: 5 (Findings 1, 6, 7, 8, 9)
- Preliminary groups: 3 (A: Findings 2+5+6, B: Findings 3+4, C: Findings 1+7+8+9)
- Pre-existing (not introduced in current commit range): Findings 8 and 9

---

## Cross-Review Messages

### Sent

- To correctness-reviewer: "Severity merging logic for [OUT-OF-SCOPE] findings in round 2+ (reviews.md:L199-208) may violate intended behavior — out-of-scope P3 findings could inflate combined priority when merged with in-scope findings by Big Head. Check whether acceptance criteria address this scenario."

### Received

- From correctness-reviewer: "Pre-existing gap at big-head-skeleton.md step 11 — `bd dep add <new-bead-id> <epic-id>` uses literal placeholder strings with no shell variable capture guidance." — Action taken: evaluated and added as Finding 9 (P3, pre-existing, within edge-cases domain).
- From correctness-reviewer: "reviews.md:L199-208 [OUT-OF-SCOPE] priority merging is pre-existing and outside asdl.* commit scope — none of the 5 task acceptance criteria address it. Confirmed ownership is mine, not reporting it themselves." — Action taken: Finding 8 confirmed as pre-existing, retained in this report. No duplicate filing.

### Deferred Items

- Finding 1 (off-by-one polling comment) — partially deferred to Clarity for the misleading comment angle; I retain it here because the actual timing behavior is also affected.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `agents/big-head.md` | Findings: #3 (temp file collision), #4 (bd list no error handling) | 37 lines, ~10 instructions, all reviewed |
| `orchestration/templates/big-head-skeleton.md` | Findings: #2 (artifact not in script), #5 (unfilled placeholder in failure prose) | 180 lines, polling script, failure artifact instructions, bead filing workflow reviewed |
| `orchestration/templates/pantry.md` | Finding: #7 (missing file existence check for skeleton) | 418 lines; Section 1 (implementation mode) reviewed in full; Section 2 (deprecated) reviewed for residual risk; Section 3 reviewed |
| `orchestration/templates/reviews.md` | Findings: #1 (off-by-one), #2 (script exit without artifact), #6 (Pest Control timeout no artifact), #8 ([OUT-OF-SCOPE] tag no enforcement) | 988 lines reviewed in full including polling script, consolidation protocol, round-aware instructions |

---

## Overall Assessment

**Score**: 3.5/10 (formula: 10 - 0×3 P1 - 4×1 P2 - 5×0.5 P3 = 3.5)
**Verdict**: PASS WITH ISSUES

Nine findings (0 P1, 4 P2, 5 P3). The score is formula-driven and reflects finding volume; the actual severity profile is bounded — no P1s, and the P3s are mostly pre-existing or low-likelihood gaps. The four P2s are real, reproducible failure modes: the polling script exits without writing its failure artifact (Finding 2), concurrent Big Head sessions collide on `/tmp/bead-desc.md` (Finding 3), `bd list` lock failures silently allow duplicate bead filing (Finding 4), and the failure artifact narrative block uses an unfilled placeholder (Finding 5). Finding 9 (missing ID capture in auto-filing) is pre-existing and P3. The framework's guard structure for placeholder substitution and round-number validation is solid; the gaps are concentrated in failure paths and concurrent-access scenarios.
