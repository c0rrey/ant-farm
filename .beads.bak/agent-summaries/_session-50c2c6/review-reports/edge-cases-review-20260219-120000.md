# Report: Edge Cases Review

**Scope**: orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/checkpoints.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/queen-state.md, orchestration/templates/reviews.md
**Reviewer**: edge-cases / code-reviewer

## Findings Catalog

### Finding 1: Polling loop exits without action if TIMED_OUT but continues
- **File(s)**: orchestration/templates/reviews.md:483-485
- **Severity**: P2
- **Category**: edge-case
- **Description**: The polling loop in the Big Head Step 0a protocol checks `TIMED_OUT` and echoes a message, but the surrounding prose instructs Big Head to "IMMEDIATELY return an error" only after the loop. However, the shell block itself only prints a message (`echo "TIMEOUT: ..."`); there is no shell-level action that actually halts Big Head. An LLM following the script may not reliably connect the echo output to the mandate to stop and return the structured error block. If the LLM continues past the shell block without reading the `TIMED_OUT` flag, consolidation proceeds on partial data with no gate.
- **Suggested fix**: After the `echo "TIMEOUT: ..."` line, add `exit 1` (or equivalent) to make the shell block itself signal failure. Then update the prose: "If TIMED_OUT=1 after the loop exits, return the error block below and do NOT proceed." The structural signal (non-zero exit) makes it unambiguous.
- **Cross-reference**: Also relevant to correctness-reviewer — this is a control-flow correctness issue in addition to an edge case.

### Finding 2: Polling loop uses glob matching that can silently match stale files from a prior round
- **File(s)**: orchestration/templates/reviews.md:464-472, orchestration/templates/reviews.md:411-424
- **Severity**: P2
- **Category**: edge-case
- **Description**: The polling loop uses `ls <session-dir>/review-reports/correctness-review-*.md 2>/dev/null | head -1` to check for report existence. In a multi-round session, a report from round 1 (e.g., `correctness-review-20260219-090000.md`) still exists on disk when round 2 runs. The glob will match the old file, making `ALL_FOUND=1` immediately — even though the round-2 reviewer has not yet produced output. Big Head would consolidate the old round-1 reports as if they were the current round's reports, producing incorrect results.
  The Step 0 ls-based check (line 411-424) has the same problem: it uses `ls ...-review-*.md`, which matches any file with that prefix, regardless of timestamp.
- **Suggested fix**: Use the exact expected timestamp in the path check (e.g., `ls <session-dir>/review-reports/correctness-review-20260219-120000.md`), not a glob. The Queen generates the timestamp once per review cycle and passes it to Big Head, so the exact path is known. If the Pantry embeds the exact paths, the glob is unnecessary.
- **Cross-reference**: This is also a correctness issue (wrong data in consolidation). Will message correctness-reviewer.

### Finding 3: No hard cap on review rounds creates unbounded retry loop risk
- **File(s)**: orchestration/templates/reviews.md:143-144, orchestration/RULES.md:117-121
- **Severity**: P2
- **Category**: edge-case
- **Description**: The termination rule states "There is no hard cap on rounds." The retry limits table in RULES.md (line 230-235) defines a max of 5 total retries per session, but that table covers Dirt Pusher DMVDC and CCB failures — not review round cycles. If an agent repeatedly introduces the same P1/P2 issue (e.g., every fix causes a new regression), the review loop never terminates, consuming resources indefinitely.
  The queen-state.md template (line 37) tracks `Current round` and `Termination` but does not record a cap or trigger for manual escalation.
- **Suggested fix**: Add a recommended cap (e.g., "after round 4 with no convergence, escalate to user with full round history and ask whether to continue or abort") in reviews.md Termination Rule section and in RULES.md Step 3c. Document it in queen-state.md's Review Rounds section.
- **Cross-reference**: None; this is purely an edge-case / operational boundary issue.

### Finding 4: P3 auto-filing in big-head-skeleton.md step 10 runs after all beads are filed, but "Future Work" epic lookup has no error handling
- **File(s)**: orchestration/templates/big-head-skeleton.md:93-98, orchestration/templates/reviews.md:681-692
- **Severity**: P3
- **Category**: edge-case
- **Description**: The P3 auto-filing flow (both big-head-skeleton step 10 and reviews.md P3 Auto-Filing section) instructs Big Head to run `bd list --status=open | grep -i "future work"` and if not found, create the epic. If `bd list` fails (bd command error, lock contention, network issue) or if `grep -i "future work"` matches zero results but then `bd epic create` also fails, there is no recovery path. The Big Head session would end without auto-filing P3s, and since the round 2+ flow skips the Queen-level P3 handling (lines 752-756 in reviews.md), those P3 findings would be silently lost — not in the consolidated summary's P3 section and not filed.
  Note: this finding covers the command-failure scenario only. The excellence-reviewer's Finding 6 covers two additional sub-cases of the same grep pattern: (a) grep returns 0 results due to an epic title typo, silently creating a duplicate epic; (b) grep returns 2+ results, causing the wrong epic to be selected. Big Head should merge all three sub-cases into one root cause.
- **Suggested fix**: Add explicit failure handling: "If `bd epic create` fails, record the error in the consolidated summary under '## Auto-Filed P3s (Future Work)' as 'FAILED: <error>'. Do NOT treat this as a session-level failure — escalate only if P1/P2 beads also failed to file." Additionally, replace the grep-based lookup with an exact epic ID stored in the session state file, eliminating ambiguity from grep matches entirely.
- **Cross-reference**: excellence-reviewer Finding 6 — covers the duplicate-epic and wrong-epic-selected sub-cases of the same pattern.

### Finding 5: CCB Check 1 reconciliation formula only accounts for round-specific counts but not the consolidated doc's "merged as duplicates" count edge case
- **File(s)**: orchestration/templates/checkpoints.md:501-505
- **Severity**: P3
- **Category**: edge-case
- **Description**: The CCB Check 1 instructs Pest Control to verify: "Every finding must be accounted for — either standalone, merged into a group, or explicitly marked as duplicate in the deduplication log." The formula in the report template says "RECONCILED / NOT RECONCILED — {list orphaned findings}". However, there is no instruction on what to do if a finding appears in the dedup log as "merged" but the target root-cause group was subsequently dropped (e.g., because Pest Control flagged it as a false positive). The finding would be in the dedup log as merged into a group that no longer exists, causing a reconciliation gap that CCB's mechanical count would miss.
- **Suggested fix**: Add a clause: "Verify that every root cause listed in the dedup log as the merge target actually appears in the Root Causes Filed table. If a target root cause is absent, flag as NOT RECONCILED."
- **Cross-reference**: None.

### Finding 6: Pantry empty file list guard only checks the Queen-provided list, not the actual git diff result
- **File(s)**: orchestration/templates/pantry.md:216-228
- **Severity**: P3
- **Category**: edge-case
- **Description**: The GUARD in Section 2 Step 3 checks "if the file list is empty or contains only whitespace" as provided by the Queen. However, it does not instruct the Pantry to run `git diff --name-only <range>` to cross-check. If the Queen provides a non-empty list that does not match the actual git diff (e.g., a stale list from a prior run), the Pantry proceeds with the wrong file list without noticing. The correctness reviewer's CCO check (checkpoints.md line 201) is supposed to catch this, but the Pantry's own guard is a weaker line of defence.
- **Suggested fix**: Add a secondary check after the empty-list guard: "Run `git diff --name-only <commit-range>` to confirm the Queen's file list is non-empty and matches the actual diff. If the Queen's list and the git diff disagree, log the discrepancy and use the git diff result as the authoritative source." This prevents propagating stale file lists into review briefs.
- **Cross-reference**: Overlaps with CCO correctness. Flagged to correctness-reviewer.

### Finding 7: queen-state.md "Fix commit range" field has no guidance for when it is set to a non-empty value before a fix cycle runs
- **File(s)**: orchestration/templates/queen-state.md:36
- **Severity**: P3
- **Category**: edge-case
- **Description**: The queen-state template shows `**Fix commit range**: <first-fix-commit>..<HEAD> (set after fix cycle in Step 3c)`. If a session crashes mid-review and is resumed, the Queen would re-read this state file. If the fix cycle started but crashed before updating the state file, the "Fix commit range" remains blank, so a resumed Queen cannot construct the correct round 2+ commit range. There is no fallback instruction for how to reconstruct it (e.g., from git log).
- **Suggested fix**: Add a note to the queen-state.md template: "If resuming a crashed session, reconstruct fix commit range via `git log --oneline <first-session-commit>..HEAD` and identify commits with '[fix]' or 'ant-farm-ha7a.N' suffixes." Alternatively, add a recovery field: `**Recovery hint**: <git log --oneline instructions>`
- **Cross-reference**: None.

### Finding 8: RULES.md Step 3b instructs the Queen to read `git diff --name-only <commit-range>` but no error handling if the range is invalid
- **File(s)**: orchestration/RULES.md:95
- **Severity**: P3
- **Category**: edge-case
- **Description**: Step 3b states "File list: `git diff --name-only <commit-range>` (deduplicated)". If the Queen mistypes or produces an invalid commit range (e.g., first-commit hash not yet reachable, or reversed order), `git diff --name-only` returns an empty result or an error message. The file list passed to the Pantry would then be empty or contain error text, which would only be caught by the Pantry's empty-file-list guard — and even then only if it's completely empty. An error message like "fatal: bad object" would not trigger the empty-list guard.
- **Suggested fix**: Add a note in Step 3b: "Verify the commit range is valid by first running `git log --oneline <commit-range>` and confirming it lists at least one commit. If zero commits appear, stop and investigate before running the file diff."
- **Cross-reference**: None.

---

## Preliminary Groupings

### Group A: Glob-based file existence checks can match stale files from prior rounds
- Finding 1, Finding 2 — share a root cause: file existence checks in the Big Head polling loop and Step 0 `ls` checks use glob patterns that can match old-round reports. Neither check enforces that the file was produced in the current round.
- **Suggested combined fix**: Replace all `ls *-review-*.md` patterns in Big Head's Step 0 and the polling loop with exact-timestamp path checks. Since the Queen generates and passes a single timestamp, Big Head should receive exact file paths and check `[ -f "$EXACT_PATH" ]` rather than globbing. This eliminates both the stale-file false-positive and the shell exit ambiguity around glob failures.

### Group B: Missing error handling for external command failures in auto-filing and state recovery
- Finding 4, Finding 7 — both represent cases where an external operation (bd command, git reconstruction) can fail silently with no recovery path defined.
- **Suggested combined fix**: Add explicit fallback sections to both: Big Head's P3 auto-filing should record failures in the consolidated summary rather than silently dropping them; queen-state.md should provide a git-log-based reconstruction hint for the fix commit range.

### Group C: Commit range and file list boundary conditions
- Finding 6, Finding 8 — both relate to boundary conditions on the commit range or file list input: either the Queen's list is stale/wrong (Finding 6) or the range itself is invalid (Finding 8).
- **Suggested combined fix**: Add validation steps in both RULES.md Step 3b and pantry.md Section 2 Step 3 that verify the commit range produces a non-empty, sensible result before proceeding.

### Group D: Standalone findings
- Finding 3 — unbounded review loop. No related finding.
- Finding 5 — CCB dedup log orphan. No related finding.

---

## Summary Statistics
- Total findings: 8
- By severity: P1: 0, P2: 3, P3: 5
- Preliminary groups: 4

---

## Cross-Review Messages

### Sent
- To correctness-reviewer: "Finding 1 (polling loop exit without action) and Finding 2 (stale glob matching in Big Head step 0) both affect correctness of the consolidation pipeline. The stale glob match would cause Big Head to consolidate the wrong round's reports. Recommend filing these as correctness issues as well." -- Action: asked correctness-reviewer to verify control flow in Big Head Step 0.
- To correctness-reviewer: "Finding 6 (Pantry empty file list guard doesn't cross-check git diff) may result in the wrong file list being passed to reviewers. CCO is supposed to catch this downstream, but if the Queen's list is non-empty but stale, CCO's file-match check runs against the wrong baseline." -- Action: asked correctness-reviewer to assess whether CCO's Check 1 is sufficient or if the Pantry guard needs strengthening.

### Received
- From excellence-reviewer: "Finding 6 covers the `bd list | grep 'future work'` pattern — specifically grep returning 0 results (typo → duplicate epic created) and grep returning 2+ results (wrong epic selected)." -- Action taken: updated Finding 4 to reference these sub-cases and recommend exact epic ID storage as the fix. Left deduplication to Big Head.
- From correctness-reviewer: Assessed all 3 cross-domain findings. Stale glob (my Finding 2) confirmed P2. Polling loop exit (my Finding 1) confirmed P2. Pantry empty-file-list guard (my Finding 6) assessed as P3 — CCO Check 1 runs `git diff --name-only` independently and is a hard gate that blocks spawn on mismatch, providing genuine defense-in-depth. -- Action taken: no change to my report; my Finding 6 is already P3 and that severity aligns. Added note below for Big Head: the CCO hard gate is a meaningful mitigating factor that should inform the root-cause group's priority calibration for Group C (Finding 6, Finding 8).

### Deferred Items
- None.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| orchestration/RULES.md | Findings: #3, #8 | Reviewed all 254 lines; Step 0-6 workflow, hard gates table, session directory section, retry limits table, concurrency rules all examined for boundary conditions |
| orchestration/templates/big-head-skeleton.md | Findings: #1, #4 | Reviewed all 104 lines; Steps 1-10 of the agent-facing template examined for error handling, timeout handling, and P3 auto-filing edge cases |
| orchestration/templates/checkpoints.md | Findings: #5 | Reviewed all 571 lines; all 4 checkpoint types (CCO, WWD, DMVDC, CCB) examined; Check 0-7 in CCB section scrutinized for reconciliation edge cases |
| orchestration/templates/nitpicker-skeleton.md | Reviewed -- no issues | 42 lines; 1 template section, instructions block examined; round-aware scope instructions (added in this session at line 20-21) are clear and correctly constrain round 2+ reviewers |
| orchestration/templates/pantry.md | Findings: #6 | Reviewed all 316 lines; Section 1 (implementation) and Section 2 (review mode) both examined; fail-fast checks, empty file list guard, and Big Head brief composition scrutinized |
| orchestration/templates/queen-state.md | Findings: #7 | Reviewed all 47 lines; all tracked fields examined for resume/recovery edge cases |
| orchestration/templates/reviews.md | Findings: #1, #2, #3, #4, #6 | Reviewed all 830 lines; polling loop (Step 0a), termination rule, P3 auto-filing, round-aware protocol, and Big Head consolidation protocol all examined in depth |

---

## Overall Assessment
**Score**: 6.5/10
**Verdict**: PASS WITH ISSUES

Three P2 findings reduce the score: the stale-glob issue (Finding 2) is the most operationally dangerous — in any multi-round session it would cause Big Head to silently consolidate the wrong round's reports, producing incorrect bead filings. The other two P2s (exit signal ambiguity and unbounded retry loop) are also real risks in production use. No P1 findings; the system would not break on first run, but multi-round sessions are clearly the new critical path and have several unguarded edge cases.
