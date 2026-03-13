# Report: Edge Cases Review

**Scope**: orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/checkpoints.md, orchestration/templates/reviews.md
**Reviewer**: Edge Cases / nitpicker

---

## Findings Catalog

### Finding 1: Polling loop in big-head-skeleton.md uses shell sleep but shell state does not persist across Bash tool calls
- **File(s)**: `orchestration/templates/big-head-skeleton.md:L519` (block comment), `L616` (`sleep $POLL_INTERVAL_SECS`)
- **Severity**: P1
- **Category**: edge-case
- **Description**: The polling loop (`while [ $ELAPSED -lt $POLL_TIMEOUT_SECS ]`) uses `sleep $POLL_INTERVAL_SECS` and expects all variables (`ELAPSED`, `REPORTS_FOUND`, `ALL_FOUND`) to survive across loop iterations. The comment at L519 already warns "This entire block must execute in a single Bash invocation" because shell state does not persist. However, if Big Head calls the Bash tool once per iteration (the common LLM pattern), the loop variables are reset to zero each call, producing an infinite polling cycle that never terminates — or in practice never increments `ELAPSED`, so `REPORTS_FOUND` is never set and the block always exits via timeout. The guard comment exists but there is no mechanism enforcing a single invocation. If Big Head forgets the comment or the runtime does not support long-running shells, the loop silently fails.
- **Suggested fix**: Add an explicit hard break on the first invocation that does NOT rely on shell persistence: either (a) rewrite the loop as a one-shot check (no sleep/poll — just check once, return missing list, let the Queen retry), or (b) replace the sleep loop with a hard-exit on first missing-file detection, letting the Queen decide whether to retry. A one-shot check removes the fragile dependency on shell state.
- **Cross-reference**: Correctness domain overlap — if the loop logic itself is wrong (ELAPSED never advances), the stated 30-second timeout is illusory.

### Finding 2: Placeholder guard in big-head-skeleton.md checks only two paths but round 1 requires four
- **File(s)**: `orchestration/templates/big-head-skeleton.md:L554–L572` (outer for loop), `L573–L593` (round-1-only loop)
- **Severity**: P2
- **Category**: edge-case
- **Description**: The placeholder substitution guard checks whether `<session-dir>` and `<timestamp>` tokens were replaced by `fill-review-slots.sh`. The outer loop (L554–L572) only iterates over the two paths always expected (correctness, edge-cases). The round-1-only paths (clarity, drift) are in a second loop inside `if [ "$REVIEW_ROUND" -eq 1 ]`. Both loops set `PLACEHOLDER_ERROR=1` and reach the same `if [ $PLACEHOLDER_ERROR -eq 1 ]; then exit 1; fi` guard (L594–L596). However, if `REVIEW_ROUND` itself contains unresolved placeholders (e.g., `{{REVIEW_ROUND}}`), the outer case statement (L525–L533) exits 1 — but the clarity/drift placeholder check inside the `if [ "$REVIEW_ROUND" -eq 1 ]` block would never execute. This is actually fine for round-2+ (clarity/drift don't need checking), but in round 1 with a bad `REVIEW_ROUND`, the clarity/drift paths are never validated. The check at the top of the block (L524–L533) fires before the round-1 paths are checked, so a bad REVIEW_ROUND prevents discovering bad clarity/drift paths. This is a narrow but real gap: an upstream substitution failure that corrupts REVIEW_ROUND will not reveal whether the round-1 paths are also bad.
- **Suggested fix**: Run the placeholder guard for all four paths unconditionally (outside any `if [ "$REVIEW_ROUND" ...]` block), then separately gate the polling loop on round number. Substitution validity and round gating are independent concerns.
- **Cross-reference**: None — pure edge case on placeholder validation ordering.

### Finding 3: bd list failure in Big Head cross-session dedup aborts bead filing entirely but does not propagate the error clearly
- **File(s)**: `orchestration/templates/big-head-skeleton.md:L113–L117` (reviews.md equivalent: `L720–L724`), also `orchestration/templates/reviews.md:L720–L724`
- **Severity**: P2
- **Category**: edge-case
- **Description**: Both big-head-skeleton.md and reviews.md contain:
  ```bash
  if ! bd list --status=open -n 0 --short > /tmp/open-beads-$$.txt 2>&1; then
    echo "ERROR: bd list failed ..."
    exit 1
  fi
  ```
  `exit 1` in this context terminates the Big Head agent entirely — no beads are filed, no failure artifact is written to `{CONSOLIDATED_OUTPUT_PATH}`, and the Queen receives no structured error. The consolidated summary was already written in Step 3 (before this block in the skeleton), but the Queen is told to wait for Big Head's SendMessage handoff (step 12 / Step 4 in reviews.md). If `bd list` fails, that message is never sent. The Queen's only signal is Big Head going idle — which the stuck-agent diagnostic treats as a 0-retry escalation. This is a silent failure mode that stalls the entire workflow with no actionable error.
- **Suggested fix**: Before calling `exit 1`, write a failure artifact to `{CONSOLIDATED_OUTPUT_PATH}` (using the same pattern as the polling timeout failure) and send a structured error message to the Queen via SendMessage. The Queen can then decide to retry or escalate without waiting for the stuck-agent timer.

### Finding 4: DMVDC Nitpicker artifact naming uses review type as TASK_SUFFIX — docs and code examples are inconsistent
- **File(s)**: `orchestration/templates/checkpoints.md:L489–L493`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The Nitpicker DMVDC output path uses `{TASK_SUFFIX}` redefined as the review type (e.g., `review-correctness`), documented in the inline note at L491: "Nitpicker review type (e.g., `review-correctness`)". However, the Dirt Pusher section defines `{TASK_SUFFIX}` as the suffix of a bead ID (e.g., `74g1`). Reusing the same placeholder name with two different meanings in the same file can cause an agent parsing the Nitpicker section to apply the Dirt Pusher extraction algorithm instead, producing a corrupt filename. The different meaning is documented but only in a trailing `Where:` block that could be missed.
- **Suggested fix**: Rename the Nitpicker-specific concept to `{REVIEW_SUFFIX}` or `{REVIEW_TYPE}` in the output path to make the distinction unambiguous. Update the surrounding text accordingly.

### Finding 5: `parse-progress-log.sh` crash recovery does not handle missing progress.log before calling the script
- **File(s)**: `orchestration/RULES.md:L64–L75` (crash recovery detection block)
- **Severity**: P2
- **Category**: edge-case
- **Description**: The crash recovery block instructs the Queen to call `bash scripts/parse-progress-log.sh <prior_SESSION_DIR>` and respond to exit codes 0, 1, and 2. Exit 1 is documented as "error (missing log, unreadable)". However, the Queen is told to check for a prior session directory in the user's message ("Check whether the user's message contains a session directory path") — it does NOT verify whether `<prior_SESSION_DIR>` actually exists on disk before running the script. If the user pastes a path that no longer exists (e.g., after a disk wipe or session directory pruning), the script will exit 1 with a generic file-not-found error. The Queen is instructed to "surface the error to the user and await instruction" on exit 1, which is correct behavior — but the error message will be opaque ("cannot read log") rather than diagnostic ("session directory does not exist"). This is a minor usability issue but the error handling is technically present.
- **Suggested fix**: Add a pre-check before running the script: `[ -d "${prior_SESSION_DIR}" ] || echo "Session directory not found: ${prior_SESSION_DIR}"`. Document this in RULES.md so the Queen can give a clear diagnosis instead of waiting for the script to fail.

### Finding 6: Wave failure threshold section does not define what "fail" means for agents mid-WWD/DMVDC
- **File(s)**: `orchestration/RULES.md:L674–L682`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The wave failure threshold (>50% of agents in a single wave fail) triggers a stop-and-escalate procedure. The threshold definition says "DMVDC failure, stuck, or unrecoverable error" but does not address the boundary case: an agent that has committed (WWD PASS) but subsequently fails DMVDC with a first retry still pending. Is that agent "failed" for threshold counting purposes? If partial failures are counted prematurely (before retries exhaust), the 50% threshold could be incorrectly triggered, stopping the wave before all retries are used. Conversely, if failures are only counted after all retries exhaust, the threshold detection is delayed.
- **Suggested fix**: Clarify the counting rule: "An agent counts toward the failure threshold after all retries are exhausted (2 retries for DMVDC, 0 for stuck)." Add this sentence to the threshold definition.

### Finding 7: ESV Check 2 git log range uses `^` prefix but no guard for missing commit
- **File(s)**: `orchestration/templates/checkpoints.md:L791–L795`
- **Severity**: P2
- **Category**: edge-case
- **Description**: Check 2 instructs Pest Control to run `git log --oneline {SESSION_START_COMMIT}^..{SESSION_END_COMMIT}`. The `^` suffix on `{SESSION_START_COMMIT}` requires that commit's parent to exist. If `{SESSION_START_COMMIT}` is the very first commit in the repo (no parent), `git log <root>^..` produces a git error: "unknown revision or path not in the working tree". There is no guard for this edge case. In practice, an ant-farm session is unlikely to start at the repo root commit, but the template contains no acknowledgment of the boundary.
- **Suggested fix**: Add a guard: if `git rev-parse {SESSION_START_COMMIT}^ 2>/dev/null` fails, use `git log {SESSION_START_COMMIT}..{SESSION_END_COMMIT}` with a note that the session start commit is included in scope manually. Document this in the check.

### Finding 8: CCB Check 7 uses `bd list --status=open --after=SESSION_START_DATE` but the date scope may miss same-day beads from a prior session
- **File(s)**: `orchestration/templates/checkpoints.md:L615–L618`
- **Severity**: P3
- **Category**: edge-case
- **Description**: Check 7 scopes `bd list` to `--after={SESSION_START_DATE}` to find beads filed during this session. If two sessions run on the same calendar date (a common scenario for iterative work), beads from the earlier session on the same day will appear in this list. Pest Control would then flag them as "beads filed during the review phase but not in the consolidated summary" — a false positive. The comment at L616 says "This scopes results to beads filed during this session only" but the granularity is calendar date, not session timestamp, so it does NOT actually scope to a single session.
- **Suggested fix**: Use `--after={SESSION_START_DATETIME}` with ISO 8601 datetime precision (or pass the session's first commit timestamp) rather than a calendar date. Alternatively, add a note acknowledging same-day false positives and instructing Pest Control to cross-reference against the session's progress.log before flagging.

### Finding 9: Big Head step 10 retry protocol says "2 subsequent turns" but does not define what counts as a turn
- **File(s)**: `orchestration/templates/reviews.md:L799–L810` (Big Head Consolidation Protocol — Step 4)
- **Severity**: P3
- **Category**: edge-case
- **Description**: Big Head is told to retry Pest Control "if no reply after 2 subsequent turns". A "turn" is ambiguous in a team context: it could mean 2 messages Big Head sends to any teammate, 2 incoming messages Big Head receives from any source, or 2 full conversation exchanges between Big Head and Pest Control specifically. If Big Head receives 2 messages from Nitpickers (not Pest Control), it may incorrectly trigger the retry before Pest Control has had a chance to respond. The ambiguity is particularly risky because Big Head has a tendency to interpret "turns" as "any activity in my context window."
- **Suggested fix**: Define "turn" precisely: "2 incoming messages from any teammate that are not the expected Pest Control reply." This disambiguates the retry trigger from unrelated team activity.

---

## Preliminary Groupings

### Group A: Silent failure on infrastructure errors (no structured error return to Queen)
- Finding 3 — `bd list` failure kills Big Head silently
- Finding 1 — Polling loop failure produces no actionable error output to Queen if shell state is fragile

Root cause: Multiple places in the workflow assume that when an infrastructure command fails, an `exit 1` is sufficient to signal the Queen. In an asynchronous team context, `exit 1` just makes the agent go idle — the Queen only learns about it via the stuck-agent diagnostic, which has a long (15-turn) timeout and zero retries.

### Group B: Placeholder validation is incomplete or inconsistent
- Finding 2 — `REVIEW_ROUND` corruption masks whether round-1 paths are valid
- Finding 4 — `{TASK_SUFFIX}` reused with two different semantics in checkpoints.md

Root cause: Placeholder names and validation logic were added incrementally without a consistent naming policy or validation-first design. Each placeholder guard was written to solve a known failure mode, not to provide comprehensive coverage.

### Group C: Date/time granularity issues in scoped queries
- Finding 8 — CCB Check 7 uses calendar date, not session timestamp, for bead scoping
- Finding 7 — ESV Check 2 `^` prefix has no guard for repo root commit

Root cause: Commands that scope by time assume a single session per day or a well-formed git history. Neither assumption is guaranteed.

### Group D: Imprecise protocol language causing agent misinterpretation
- Finding 6 — Wave failure threshold ambiguity around retry counting
- Finding 9 — "Subsequent turns" is ambiguous in team context

Root cause: Retry and turn-counting language is defined in terms of the sequential Queen context but applied in asynchronous multi-agent team contexts without adjustment.

### Group E: Crash recovery usability (standalone)
- Finding 5 — Missing session directory gives opaque error

---

## Summary Statistics
- Total findings: 9
- By severity: P1: 1, P2: 4, P3: 4
- Preliminary groups: 5

---

## Cross-Review Messages

### Sent
- To correctness-reviewer: "Finding 1 (big-head-skeleton.md:L519/L616) involves a polling loop whose logic is also potentially incorrect (ELAPSED never increments if shell state resets per call, meaning the while condition `$ELAPSED -lt $POLL_TIMEOUT_SECS` is always true but the loop exits only via REPORTS_FOUND). This has both an edge-case dimension (shell state fragility) and a correctness dimension (the loop invariant is wrong under a single-call-per-iteration model). The edge-case aspect is mine; you may want to verify the loop logic also correctly terminates under valid execution."

### Received
- From correctness-reviewer: "Reviewed polling loop (reviews.md:L519–L630). Under single-invocation constraint, the timeout logic is logically correct — ELAPSED advances within one bash process and the while condition exits after exactly 30 seconds. The constraint-violation scenario (ELAPSED resets if Big Head calls Bash per iteration, causing infinite loop when reports are missing) is confirmed as edge-cases domain only. No separate correctness finding to add." — Action taken: Updated Finding 1 cross-reference note; finding retained as P1 edge-case (constraint-violation failure mode confirmed, not a correctness bug under valid execution).

### Deferred Items
- Finding 4 (`{TASK_SUFFIX}` dual semantics) — has a clarity dimension (naming confusion); messaging clarity-reviewer for awareness, but the edge-case risk (wrong filename construction) is the primary concern here and is reported above.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/RULES.md` | Findings: #5, #6 | 700 lines examined; all steps, gates, and session directory logic reviewed; crash recovery (Step 0), wave failure threshold, retry limits, and session directory sections specifically checked for boundary conditions |
| `orchestration/templates/big-head-skeleton.md` | Findings: #1, #2, #3 | 220 lines examined; polling loop (L519–L631), placeholder guard (L549–L596), bd list failure block (L113–L117), and all step-numbered workflow blocks reviewed |
| `orchestration/templates/checkpoints.md` | Findings: #4, #7, #8 | 919 lines examined; all 6 checkpoint types (SSV, CCO, WWD, DMVDC for Dirt Pushers and Nitpickers, CCB, ESV) reviewed; artifact naming, verdict thresholds, and all guard blocks checked |
| `orchestration/templates/reviews.md` | Findings: #3 (duplicate block), #9 | 1132 lines examined; all 4 review types, Big Head Consolidation Protocol (all steps), and the full workflow section reviewed; cross-session dedup, bd list block, and turn-based retry protocol examined |

---

## Overall Assessment
**Score**: 6.5/10
**Verdict**: PASS WITH ISSUES

The reviewed files contain one P1 edge case (Finding 1: polling loop fragility under single-Bash-invocation model) and four P2 issues (Findings 3, 2, 5, 7). The P1 is serious because it affects Big Head's ability to detect missing reviewer reports — if the loop never increments ELAPSED, the 30-second timeout is never enforced and the block either hangs or exits incorrectly on every call. The P2 issues cluster around silent failure modes and ambiguous scoping that could silently produce wrong results. P3 issues are polish and low-risk. No data loss or persistent state corruption was found.
