# Report: Edge Cases Review (Round 3)

**Scope**: Fix commits 365a0d9..HEAD (1 commit: `50844a7`)
**Reviewer**: edge-cases | Nitpicker (Round 3 — fix verification only)
**Files reviewed**: `orchestration/templates/big-head-skeleton.md`, `orchestration/templates/reviews.md`

---

## Fix Summary

The fix commit (`50844a7`) addresses pseudocode-in-shell and criteria drift findings from round 2. The change:

1. Removed `SendMessage(Queen):` pseudocode lines from inside bash code blocks in both files.
2. Added equivalent prose instructions outside the bash blocks: "If the bash block above exits with code 1, stop immediately. Do NOT proceed to consolidation or bead filing. Use the SendMessage tool to notify the Queen: ..."

---

## Findings Catalog

### Finding 1: Unsubstituted `{CONSOLIDATED_OUTPUT_PATH}` in prose instruction may silently produce wrong SendMessage content

- **File(s)**: `orchestration/templates/big-head-skeleton.md:127`, `orchestration/templates/reviews.md:744`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The newly-added prose instruction (the fix) contains `{CONSOLIDATED_OUTPUT_PATH}` in its text:

  `big-head-skeleton.md:127`:
  ```
  If the bash block above exits with code 1, stop immediately. Do NOT proceed to consolidation or bead filing. Use the SendMessage tool to notify the Queen: "Big Head FAILED: bd list infrastructure error during cross-session dedup. Bead filing aborted to prevent duplicates. Consolidated output written to {CONSOLIDATED_OUTPUT_PATH}. Please check bd status and re-spawn Big Head when ready." Then end your turn.
  ```

  `reviews.md:744`:
  ```
  If the bash block above exits with code 1, stop immediately. Do NOT proceed to consolidation or bead filing. Use the SendMessage tool to notify the Queen: "Big Head FAILED: bd list infrastructure error during cross-session dedup. Bead filing aborted to prevent duplicates. Consolidated output written to {CONSOLIDATED_OUTPUT_PATH}. Please check bd status and re-spawn Big Head when ready." Then end your turn.
  ```

  This is consistent with other prose uses of `{CONSOLIDATED_OUTPUT_PATH}` throughout both files (e.g., `big-head-skeleton.md:133`, `big-head-skeleton.md:134`, `big-head-skeleton.md:212`; `reviews.md:844`, `reviews.md:845`). The placeholder convention in this codebase uses `{CURLY_BRACES}` for template-time placeholders that `build-review-prompts.sh` fills via `fill_slot`, and `<angle-brackets>` for illustrative examples the Queen fills manually. If `build-review-prompts.sh` does NOT substitute `{CONSOLIDATED_OUTPUT_PATH}` in prose (only inside bash blocks), then when Big Head encounters the prose instruction the literal string `{CONSOLIDATED_OUTPUT_PATH}` would appear in its SendMessage to the Queen — a confusing but non-fatal result. The existing bash blocks already have an explicit comment at `big-head-skeleton.md:95-97` clarifying that `{CONSOLIDATED_OUTPUT_PATH}` in code blocks IS substituted at runtime. There is no equivalent clarification for prose uses.

  This is an extremely low-impact condition: the Queen would still receive the alert and would still understand the failure. No data is lost, no process crashes. Severity calibrated to P3.

- **Suggested fix**: Either (a) add a brief inline note as is done in the bash-block comment at line 95-97, confirming that `{CONSOLIDATED_OUTPUT_PATH}` in prose is also substituted by `fill-review-slots.sh`, or (b) confirm via `build-review-prompts.sh` that prose substitution happens (no code change needed if it does). This is a documentation/clarity concern more than a runtime concern, so it may be better handed to the Clarity reviewer — deferring accordingly.
- **Cross-reference**: Deferred to Clarity reviewer (see Cross-Review Messages). Not reporting here.

---

### No additional edge-case findings

The two changed sections (removal of `SendMessage(Queen):` pseudocode from inside bash blocks; addition of prose instruction outside the blocks) do not introduce new input validation gaps, error-handling gaps, boundary condition failures, file operation risks, or concurrency issues. Specifically:

- The bash blocks themselves (`bd list`, `cat > {CONSOLIDATED_OUTPUT_PATH}`, `exit 1`) are unchanged and already handle the error path correctly.
- The `exit 1` still terminates the bash block on failure, which is the correct behavior.
- The prose instruction now outside the block correctly instructs the LLM agent (Big Head) to use `SendMessage` tool — which is the right mechanism for inter-agent communication, not a bash command.
- The fix did not change the polling loop, the placeholder-guard logic, or any file-existence checks.
- No new file I/O operations were introduced.
- No new external inputs were introduced.

---

## Preliminary Groupings

### Group A: Prose `{CONSOLIDATED_OUTPUT_PATH}` substitution ambiguity (Finding 1)
- Finding 1 — standalone
- **Suggested combined fix**: Confirm substitution behavior in `build-review-prompts.sh`; add note if prose is also substituted, or adjust if not.

---

## Summary Statistics
- Total findings: 1
- By severity: P1: 0, P2: 0, P3: 1
- Preliminary groups: 1

---

## Cross-Review Messages

### Sent
- To Clarity reviewer: "Finding 1 (`big-head-skeleton.md:127`, `reviews.md:744`) — the newly-added prose instruction from the fix contains `{CONSOLIDATED_OUTPUT_PATH}` with no comment clarifying whether it is substituted at runtime (unlike the bash-block comment at line 95-97 which explicitly notes this). This is a documentation/clarity concern more than a runtime concern. May want to review."

### Received
- None received.

### Deferred Items
- "Prose `{CONSOLIDATED_OUTPUT_PATH}` substitution ambiguity" — Deferred to Clarity because the concern is primarily about a missing explanatory comment, not a functional failure. The edge-case impact (confusing literal placeholder in Queen's message) is P3/cosmetic.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/templates/big-head-skeleton.md` | Reviewed — 1 P3 finding (deferred to Clarity) | Full file read; 231 lines. Examined bash blocks at lines 93-107, 113-127; prose instructions at lines 127-132; all `{CONSOLIDATED_OUTPUT_PATH}` references; polling loop at lines 89-92; timeout handling; bead-filing instructions. Fix landed correctly. |
| `orchestration/templates/reviews.md` | Reviewed — 1 P3 finding (deferred to Clarity) | Full file read; 1157 lines. Examined Step 2.5 bash block at lines 730-742; prose instruction at line 744; all `{CONSOLIDATED_OUTPUT_PATH}` references; polling bash block at lines 514-641; placeholder guards; Round 2+ reviewer instructions. Fix landed correctly. |

---

## Overall Assessment

**Score**: 9.5/10
**Verdict**: PASS

The fix landed cleanly and correctly. The pseudocode `SendMessage(Queen):` call was removed from both bash blocks in both files, and replaced with a valid prose instruction directing Big Head to use the `SendMessage` tool — which is the appropriate mechanism. No new edge-case risks were introduced. The single P3 finding (deferred to Clarity) is a cosmetic ambiguity about whether a prose placeholder is substituted at runtime, with no functional failure mode. Zero P1 or P2 findings.
