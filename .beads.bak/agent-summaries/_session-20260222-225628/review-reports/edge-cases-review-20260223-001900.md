# Report: Edge Cases Review (Round 2)

**Scope**: Fix commits 9fcfc87..HEAD (5 commits)
**Files in scope**:
- `orchestration/RULES.md`
- `orchestration/templates/big-head-skeleton.md`
- `orchestration/templates/checkpoints.md`
- `orchestration/templates/reviews.md`

**Reviewer**: Edge Cases / nitpicker (sonnet)
**Review round**: 2 — mandate is: did fixes land correctly and not break anything? Out-of-scope findings only reportable if they cause runtime failure or silently wrong results.

---

## Findings Catalog

### Finding 1: `SendMessage(Queen)` is pseudocode in shell error-handler, not a real tool call
- **File(s)**: `orchestration/templates/reviews.md:742`, `orchestration/templates/big-head-skeleton.md:125`
- **Severity**: P2
- **Category**: edge-case
- **Description**: Both files contain the following construct inside a shell `if !` error block:
  ```bash
  SendMessage(Queen): "Big Head FAILED: ..."
  exit 1
  ```
  `SendMessage(Queen)` is Claude's tool call syntax — it is not a valid shell command. When this block is executed in a Bash tool call, the `SendMessage(...)` line will be treated as a shell command, fail silently or error, and the agent will `exit 1` without ever actually notifying the Queen. The Queen will not learn that `bd list` failed; it will only observe that Big Head terminated early. This is the exact failure mode the fix was intended to prevent ("she can act immediately rather than waiting for stuck-agent timeout").
- **Suggested fix**: Remove the `SendMessage(Queen)` line from inside the bash heredoc/script block entirely. The comment "# Notify the Queen..." is documentation intent, not executable code. The failure artifact written to `{CONSOLIDATED_OUTPUT_PATH}` is the correct recovery path — the Queen reads that path on timeout. Alternatively, clearly mark it as a prose instruction outside the code block: "After `exit 1`, Big Head must (outside of shell) SendMessage to the Queen." But placing it inside an `if ! ... ; then ... exit 1; fi` block as a shell line is incorrect.
- **Cross-reference**: None — this is edge-cases territory (unhandled error path delivers no notification).

### Finding 2: `exit 1` inside Big Head's bash block terminates shell but Big Head agent continues
- **File(s)**: `orchestration/templates/reviews.md:742-744`, `orchestration/templates/big-head-skeleton.md:125-127`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The `exit 1` in the `bd list` failure handler terminates the Bash subshell for the tool call. It does NOT stop the Big Head agent process. Big Head continues running and may attempt downstream steps (consolidation, bead filing) despite the failed `bd list`. The failure artifact is written before `exit 1`, which is correct, but there is no instruction to Big Head to stop proceeding after the Bash tool call returns non-zero. A model following the script mechanically may ignore the non-zero exit and continue.
- **Suggested fix**: After the bash block, add prose instruction: "If the bash block above exits with code 1, stop immediately. Do NOT proceed to consolidation. Use SendMessage to notify the Queen (as the comment instructs) and end your turn."
- **Cross-reference**: Related to Finding 1 (same error path).

### Finding 3: Crash recovery dir-check fix does not guard against path injection in the echo output
- **File(s)**: `orchestration/RULES.md:70-73`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The new dir-check step is:
  ```bash
  [ -d "<prior_SESSION_DIR>" ] || echo "Session directory not found: <prior_SESSION_DIR>"
  ```
  `<prior_SESSION_DIR>` is a template placeholder — at runtime the Queen fills in an actual path from the user's message. If the user's message contains shell metacharacters (backticks, `$()`, semicolons) in the path string, the echo could behave unexpectedly. In practice, session directory names follow the `_session-YYYYMMDD-HHmmss` format and pose negligible risk. This is informational — the Queen composing this as a bash string should quote `"${prior_SESSION_DIR}"` for correctness.
- **Suggested fix**: Template could show `[ -d "${PRIOR_SESSION_DIR}" ] || echo "Session directory not found: ${PRIOR_SESSION_DIR}"` with the path as a properly-quoted shell variable, consistent with how `SESSION_DIR` is used elsewhere in the file.

### Finding 4: ESV Check 2 root-commit guard missing note about first-commit exclusion in fallback path
- **File(s)**: `orchestration/templates/checkpoints.md:795`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The root-commit fallback uses `git log --oneline {SESSION_START_COMMIT}..{SESSION_END_COMMIT}` (without `^`). The note correctly warns: "SESSION_START_COMMIT itself is not included in the git log output." However, there is no guidance on how Pest Control should handle the scenario where the session-start commit is also the root commit AND it is unaccounted for in the exec summary. Is this an expected Check 2 FAIL or a known gap to accept? A reviewer encountering this for the first time may either (a) incorrectly FAIL Check 2 when the root commit is legitimately unrepresentable, or (b) silently accept a missing commit.
- **Suggested fix**: Add a clarification: "In the root-commit case, SESSION_START_COMMIT is excluded from the git log range. If the exec summary omits SESSION_START_COMMIT, this is an expected gap — do NOT FAIL Check 2 on this account. Document it as 'known omission: root commit' in the report."

---

## Preliminary Groupings

### Group A: Pseudocode in shell context — error notification unreachable
- **Finding 1** — `SendMessage(Queen)` placed inside a Bash `if` block is not executable shell and will silently fail to notify the Queen when `bd list` fails.
- **Root cause**: The fix added a Queen notification as shell syntax rather than as prose instructions outside the code block. The intent is correct; the implementation is in the wrong layer.

### Group B: Agent continuation after bash failure — no stop instruction
- **Finding 2** — Big Head has no prose-level instruction to halt after the bash block exits 1; the model may continue past the error.
- **Root cause**: The fix writes a failure artifact and calls `exit 1` in shell, but doesn't tell Big Head (as an agent) to stop. Complements Group A: even if Finding 1 were fixed, Finding 2 would leave Big Head proceeding.

### Group C: Minor edge cases in new guard logic (low risk)
- **Finding 3**, **Finding 4** — Small gaps in newly-added guard code that are unlikely to cause runtime failures but leave subtle unhandled paths.

---

## Summary Statistics
- Total findings: 4
- By severity: P1: 0, P2: 1, P3: 3
- Preliminary groups: 3

---

## Cross-Review Messages

### Sent
- None

### Received
- None

### Deferred Items
- None

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/RULES.md` | Findings: #3 | Reviewed crash recovery block (L65-82), shutdown prohibition addition (L19), Step 3c shutdown text (L297-302), Edge Cases re-task message (L398-403). 710 lines total. |
| `orchestration/templates/big-head-skeleton.md` | Findings: #1, #2 | Reviewed bd list failure handler (L112-128), single-invocation constraint additions (L91-95), timeout note (L93-95), error message timeout value (L99). 232 lines total. |
| `orchestration/templates/checkpoints.md` | Findings: #4 | Reviewed ESV Check 2 root-commit guard additions (L789-796). 922 lines total. |
| `orchestration/templates/reviews.md` | Findings: #1, #2 | Reviewed round 2+ team persistence fix (L81-97), POLL_TIMEOUT_SECS change (L553-560), placeholder validation comments (L557-580), bd list failure handler (L730-744), checklist update (L954), team_name fix (L1005). 1157 lines total. |

---

## Overall Assessment
**Score**: 8/10
**Verdict**: PASS WITH ISSUES

The five fix commits address their stated problems correctly. The crash recovery directory check lands cleanly; the shutdown prohibition is properly placed; the ESV root-commit guard handles the happy path. The one P2 issue (Finding 1) is a structural problem in the bd-list error handler: `SendMessage(Queen)` written as a shell line inside an `if` block cannot execute — the Queen notification that was the entire point of the fix will silently not fire. Finding 2 (P3) compounds this: even with Finding 1 fixed, Big Head needs a prose-level halt instruction. Both findings share the same root cause and are addressable with a single targeted change.
