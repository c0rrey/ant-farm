# Report: Edge Cases Review

**Scope**: orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
**Reviewer**: Edge Cases / nitpicker (sonnet)

---

## Findings Catalog

### Finding 1: REVIEW_ROUND validation allows "0" through review-prompts path

- **File(s)**: `scripts/build-review-prompts.sh:95-98`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The REVIEW_ROUND validation in `build-review-prompts.sh` uses `grep -qE '^[0-9]+$'`, which matches `0`. Review round 0 is not a valid state (rounds are 1-indexed), yet it would pass the guard and proceed into review-type selection — where `[ "$REVIEW_ROUND" -eq 1 ]` would be false, causing the script to silently produce round-2+ output (2 reviewers only) for what is actually an invalid input. RULES.md Step 3b-i.5 uses the stricter regex `^[1-9][0-9]*$` which correctly rejects 0, but that guard runs in the Queen's shell, not in the script itself. If the script is called directly or the Queen's guard is bypassed, REVIEW_ROUND=0 produces the wrong review composition without surfacing an error.
- **Suggested fix**: Change `grep -qE '^[0-9]+$'` to `grep -qE '^[1-9][0-9]*$'` at line 95 of `build-review-prompts.sh`, matching the stricter pattern already specified in RULES.md.
- **Cross-reference**: None — this is solely an input-validation edge case for the script.

---

### Finding 2: Polling loop in reviews.md uses literal `<angle-bracket>` placeholder paths in file-existence tests

- **File(s)**: `orchestration/templates/reviews.md:531-587` (Big Head Step 0a polling loop)
- **Severity**: P2
- **Category**: edge-case
- **Description**: The polling loop code block uses literal `<session-dir>/review-reports/correctness-review-<timestamp>.md` (and sibling paths) inside `[ -f ... ]` tests. These angle-bracket strings are template-source examples, not filled values. The template includes a placeholder guard that detects `*'<'*|*'>'*` patterns and aborts. However, the guard logic only runs **after** `PLACEHOLDER_ERROR` is evaluated, and the guard itself checks a subset of paths — it checks correctness and edge-cases unconditionally and adds clarity/drift for round 1. If `fill-review-slots.sh` (now `build-review-prompts.sh`) partially fills placeholders (e.g., substitutes session-dir but not timestamp), the guard can silently pass while the `[ -f ]` tests still fail with misleading "not found" results. The guard is helpful but not exhaustive — it only checks for angle/curly brackets in path strings, not for empty strings resulting from partial substitution.
- **Suggested fix**: After the placeholder guard, add a check that none of the path variables resolve to empty string. The existing `if [ -z "$_path" ]` check covers the empty-string case but runs inside a for-loop that iterates over literal strings (not variables), so the `-z` test is applied to the unevaluated literal, not to any substituted variable value. The fix is to store the paths in named variables before the guard and check the variables.
- **Cross-reference**: This is primarily an edge-case issue. If the guard produces misleading errors, I flagged it here; if the false error message content is the concern, that belongs to Clarity.

---

### Finding 3: `fill_slot` in `build-review-prompts.sh` leaves temp file on awk failure

- **File(s)**: `scripts/build-review-prompts.sh:141-175`
- **Severity**: P3
- **Category**: edge-case
- **Description**: `fill_slot` creates a temp file via `mktemp`, then runs `awk ... "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"`. On awk failure (disk full, permission error, etc.), `"${file}.tmp"` may be left on disk. The `rm -f "$tmpval"` at the end of the function also runs unconditionally but only after the awk pipeline — if `awk` fails and `set -e` triggers an exit, `rm` never runs. The temp value file (`$tmpval`) leaks. Under normal conditions this is harmless, but on a disk-full failure it could accumulate stale temp files.
- **Suggested fix**: Use a `trap "rm -f '$tmpval' '${file}.tmp'" EXIT` inside the function, or use a subshell with cleanup, to ensure both temp files are removed on any exit path.
- **Cross-reference**: None.

---

### Finding 4: `build_big_head_prompt` self-references `$out_file` as `DATA_FILE_PATH` before the file is fully written

- **File(s)**: `scripts/build-review-prompts.sh:254-298`
- **Severity**: P2
- **Category**: edge-case
- **Description**: At line 296, `fill_slot "{{DATA_FILE_PATH}}" "$out_file" "$out_file"` replaces `{{DATA_FILE_PATH}}` in `$out_file` with the value of `$out_file` (the file's own path). The slot is being filled while the file is being written by the `fill_slot` awk pipeline, which reads the file, creates `.tmp`, then `mv`s it back. This works correctly if `$out_file` is already fully written (it is — it was written by the heredoc-style `{ ... } > "$out_file"` block at lines 273-291). However, the same `fill_slot` is also called for `{{DATA_FILE_PATH}}` with the same value that was already literally injected into the file at line 282 (`echo "**Data file**: ${out_file}"`). So the slot fill is redundant for the literal-value section, but is needed for any `{{DATA_FILE_PATH}}` occurrences that came from the template body (extracted skeleton). If the skeleton body uses `{{DATA_FILE_PATH}}` and the file hasn't been fully flushed before the awk read (edge case on some filesystems), the in-place substitution could read stale data. On standard POSIX filesystems with buffered I/O and `set -euo pipefail`, this is benign, but the dual-write pattern is fragile.
- **Suggested fix**: This is more a clarity/design issue than an immediate safety risk. Document the ordering dependency: "skeleton body slots are filled AFTER the literal section is written." No code change required for correctness, but a comment would help.
- **Cross-reference**: Sent to clarity-reviewer — the dual-write pattern needs a comment explaining the ordering dependency.

---

### Finding 5: `resolve_arg` in `build-review-prompts.sh` does not validate that the resolved file is non-empty

- **File(s)**: `scripts/build-review-prompts.sh:74-86`
- **Severity**: P3
- **Category**: edge-case
- **Description**: `resolve_arg` reads a `@filepath` file using `cat "$fpath"`, but does not check whether the file is empty. If `@/tmp/changed-files.txt` exists but is empty (e.g., from a failed `git diff`), `CHANGED_FILES` is set to empty string. The script later proceeds to write prompt files with empty `CHANGED_FILES` slots — reviewers would receive a prompt with no files listed. RULES.md Step 3b-i.5 has a `CHANGED_FILES` guard, but that runs in the Queen's shell before calling the script, not inside the script. If the Queen's guard is bypassed, the script will silently produce prompts with empty file lists.
- **Suggested fix**: After resolving `@file` arguments, check that `CHANGED_FILES` and `TASK_IDS` are non-empty and emit a clear error if they are. This mirrors the validation already described in RULES.md Step 3b-i.5 but makes the script self-validating regardless of caller.
- **Cross-reference**: None.

---

### Finding 6: Big Head polling loop — `ELAPSED` accounting skips one interval at the boundary

- **File(s)**: `orchestration/templates/reviews.md:576-595` (polling while loop)
- **Severity**: P3
- **Category**: edge-case
- **Description**: The polling loop increments `ELAPSED` **after** `sleep`, so the final check at `ELAPSED=$POLL_TIMEOUT_SECS` is never reached — the `while` condition `[ $ELAPSED -lt $POLL_TIMEOUT_SECS ]` exits when `ELAPSED` equals `POLL_TIMEOUT_SECS`, meaning the last possible check runs one sleep interval before the nominal timeout. With `POLL_TIMEOUT_SECS=30` and `POLL_INTERVAL_SECS=2`, the loop makes at most 14 iterations (checks at T=0, then waits and rechecks at T=2, T=4, …, T=28), giving at most 28 seconds of effective wait time instead of the documented 30. The discrepancy is minor (2 seconds) and unlikely to matter in practice, but the comment says "30 seconds" while the implementation stops at 28.
- **Suggested fix**: Change the while condition to `[ $ELAPSED -le $POLL_TIMEOUT_SECS ]` or restructure to check after sleeping (do-while pattern). A comment noting the off-by-one is also acceptable for low-severity documentation purposes.
- **Cross-reference**: None.

---

### Finding 7: `big-head-skeleton.md` failure artifact uses heredoc with unresolved `{CONSOLIDATED_OUTPUT_PATH}` placeholder

- **File(s)**: `orchestration/templates/big-head-skeleton.md:92-101`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The failure-artifact bash block in the skeleton uses `cat > "{CONSOLIDATED_OUTPUT_PATH}" << 'EOF'`. The `{CONSOLIDATED_OUTPUT_PATH}` is a `{UPPERCASE}` placeholder that the Queen is expected to fill before passing the template to Big Head. However, the placeholder is embedded inside a heredoc that is wrapped in backticks (it appears in a code block in the markdown). If `build-review-prompts.sh`'s `fill_slot` function misses this occurrence (because it is inside a markdown code block which uses a different quoting pattern), Big Head would receive the literal string `{CONSOLIDATED_OUTPUT_PATH}` and `cat > "{CONSOLIDATED_OUTPUT_PATH}"` would create a file named literally `{CONSOLIDATED_OUTPUT_PATH}` in the working directory rather than at the correct session path. The downstream consumer (Queen, Pest Control) would find no failure artifact at the expected path — a silent failure.

  Investigation: `build-review-prompts.sh` calls `fill_slot "{{CONSOLIDATED_OUTPUT_PATH}}" ...` (double-brace form) after converting `{UPPERCASE}` → `{{UPPERCASE}}` via the sed pass. So the substitution should reach this code block. The risk is if the sed substitution at line 270 (`sed 's/{\([A-Z][A-Z_]*\)}/{{\1}}/g'`) fails to match the occurrence inside the code block (markdown code blocks are not special to sed, so this should work). But the failure artifact block in reviews.md at line 599–607 (`cat > "{CONSOLIDATED_OUTPUT_PATH}" << 'EOF'`) is in `reviews.md`, which is NOT processed by `build-review-prompts.sh` — it is only read by the Pantry in Section 2 (deprecated) or used as reference. The actual delivery is through `big-head-skeleton.md` which IS processed by the script. Confirmed: the `big-head-skeleton.md` instance at line 92 is in a Bash code block inside the agent-facing section, and `build-review-prompts.sh` applies `fill_slot` to the whole prompt file after extraction. This should be filled correctly. However, if the sed conversion at line 270 runs before `fill_slot` and the Bash code block uses `{CONSOLIDATED_OUTPUT_PATH}` (single-brace), sed will convert it to `{{CONSOLIDATED_OUTPUT_PATH}}`, and then `fill_slot` will replace it. This chain is correct. The risk is low but exists if any sed-special characters appear in the path.
- **Suggested fix**: Add an integration test or post-write verification that confirms no `{{UPPERCASE}}` slots remain unfilled in any output prompt file. (Currently the script verifies files are non-empty but not that all slots are filled.)
- **Cross-reference**: If this is also a drift issue (stale placeholder convention), message drift-reviewer.

---

### Finding 8: `pantry.md` Section 2 (deprecated) contains active validation code with unfilled placeholder `{{REVIEW_ROUND}}`

- **File(s)**: `orchestration/templates/pantry.md:501` (Section 2, now marked DEPRECATED)
- **Severity**: P3
- **Category**: edge-case
- **Description**: Section 2 of `pantry.md` is marked `[DEPRECATED — replaced by build-review-prompts.sh]` at line 227, yet it still contains the full polling-loop code block including `REVIEW_ROUND={{REVIEW_ROUND}}` at line 501. If an agent accidentally reads Section 2 and tries to execute the bash block, the `{{REVIEW_ROUND}}` placeholder will be unresolved and the `case "$REVIEW_ROUND"` guard will trigger a "PLACEHOLDER ERROR" — a correct safety response, but it means a deprecated code path is still capable of generating confusing error messages. More critically, the deprecation warning (lines 228-234) is at the top of Section 2, but the content that follows is identical to the active polling loop, making the section misleading about what is safe to reference.
- **Suggested fix**: Strip the executable bash blocks from Section 2 and replace them with a forward-reference note: "See `build-review-prompts.sh` and `reviews.md` for current logic." Alternatively, collapse Section 2 to a one-paragraph deprecation notice. If retaining for historical reference is intentional, add a comment to each code block: "# DEPRECATED — do not execute".
- **Cross-reference**: Sent to clarity-reviewer regarding the misleading structure of the deprecated section.

---

### Finding 9: `RULES.md` Step 3b-v dummy-reviewer tmux loop — `grep -q '>'` could false-positive match prompt text

- **File(s)**: `orchestration/RULES.md:253`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The readiness check for the tmux pane uses:
  ```bash
  tmux capture-pane -t "${TMUX_SESSION}:${DUMMY_WINDOW}" -p 2>/dev/null | grep -q '>'
  ```
  The `>` character matches the shell prompt (e.g., `>` in `zsh` or `bash`), but it would also match any output that happens to contain `>` — such as the Claude Code welcome banner, error messages with redirects, or partial output from a previous command. A false positive here means the Queen sends the dummy reviewer prompt before Claude is actually ready to receive input, which silently drops the entire prompt. The resulting "dummy reviewer" either never runs or runs with garbage input. Since the dummy reviewer is measurement-only and its absence is explicitly documented as acceptable (line 267), this is low-severity.
- **Suggested fix**: Use a more specific pattern, such as `grep -qE '^[>$%#] *$'` (anchored prompt detection) or wait for a Claude-specific string like `Human:` or `>` at start-of-line. Alternatively, increase the sleep to 15 seconds (the current max is already 15 total, but the check loops every 1s — acceptable).
- **Cross-reference**: None.

---

### Finding 10: `RULES.md` crash recovery — exit-code handling for `parse-progress-log.sh` does not cover exit codes > 2

- **File(s)**: `orchestration/RULES.md:67-75`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The crash recovery block documents three exit codes: 0 (resume), 1 (error), 2 (completed). Any other exit code from `parse-progress-log.sh` (e.g., 3, 126, 127 from command-not-found, 130 from SIGINT) falls through without any handler. The text "4. On exit 1: surface the error" only mentions exit 1 as the error case. If the script exits with a signal code or unexpected status, the Queen receives no documented behavior — the workflow silently continues on an ambiguous state.
- **Suggested fix**: Add a catch-all case: "On any other exit code: treat as exit 1 — surface the error to the user and await instruction."
- **Cross-reference**: None.

---

## Preliminary Groupings

### Group A: Script-level input validation gaps (Findings 1, 5)

- Finding 1 (`REVIEW_ROUND` allows 0) and Finding 5 (`CHANGED_FILES` empty after `@file` resolution) share the same root cause: `build-review-prompts.sh` does not fully replicate the input guards that RULES.md Step 3b-i.5 mandates in the Queen's shell. The script assumes the caller has already validated inputs, but the guard is not duplicated inside the script.
- **Combined priority**: P2
- **Suggested combined fix**: Add a validation block after argument parsing (after resolving `@file` args) that checks REVIEW_ROUND >= 1 and CHANGED_FILES is non-empty. This makes the script self-validating regardless of whether the Queen ran her pre-call guards.

### Group B: Placeholder substitution completeness (Findings 2, 7)

- Finding 2 (polling loop `<angle-bracket>` paths in `reviews.md`) and Finding 7 (`{CONSOLIDATED_OUTPUT_PATH}` in failure artifact) both stem from the same root cause: the template system (both in `reviews.md` and `big-head-skeleton.md`) contains bash code blocks with placeholder text that must be filled before execution. There is no end-to-end test that validates all placeholders are resolved after `build-review-prompts.sh` runs.
- **Combined priority**: P2
- **Suggested combined fix**: After `build-review-prompts.sh` writes all output files, scan for unfilled `{{UPPERCASE}}` and `<angle-bracket>` patterns and emit a warning or error if any remain.

### Group C: Minor boundary/timing issues (Findings 3, 6, 9, 10)

- Findings 3 (temp file leak on awk failure), 6 (off-by-one in polling timeout), 9 (tmux readiness false positive), and 10 (unhandled exit codes) are individually P3 and unlikely to cause observable failures in normal operation. They share the root cause of missing defensive handling at the edges of well-defined paths.
- **Combined priority**: P3

### Group D: Deprecated content with active executable code (Finding 8)

- Finding 8 stands alone — it is about a deprecated section that retains executable bash blocks with unfilled placeholders. This is a distinct concern from the placeholder-substitution group because the code is in a section that is not supposed to be executed at all.
- **Combined priority**: P3

---

## Summary Statistics

- Total findings: 10
- By severity: P1: 0, P2: 4, P3: 6
- Preliminary groups: 4

---

## Cross-Review Messages

### Sent

- To clarity-reviewer: "Found dual-write pattern in `build-review-prompts.sh:296` (DATA_FILE_PATH self-reference) that lacks an ordering-dependency comment — may want to review for clarity (Finding 4)."
- To clarity-reviewer: "Found deprecated Section 2 in `pantry.md:227` that retains full executable bash blocks with unfilled placeholders — the structure is misleading about what is safe to reference. May want to review (Finding 8)."

### Received

- None received at time of writing.

### Deferred Items

- Finding 4 (`build_big_head_prompt` self-reference) — Deferred to clarity-reviewer for the comment/documentation aspect; retained here as P3 edge-case for the ordering-dependency fragility.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/RULES.md` | Findings: #9, #10 | 586 lines, all workflow steps reviewed; Findings at L253 (tmux readiness) and L67-75 (crash recovery exit codes) |
| `orchestration/templates/big-head-skeleton.md` | Findings: #7 | 185 lines; placeholder substitution path reviewed; Finding at L92 (failure artifact heredoc) |
| `orchestration/templates/pantry.md` | Findings: #8 | 431 lines; Section 1 reviewed (no issues), Section 2 deprecated block reviewed; Finding at deprecated polling loop |
| `orchestration/templates/reviews.md` | Findings: #2, #6 | 1063 lines; entire file reviewed; Findings at L531-587 (placeholder guard) and L576-595 (polling off-by-one) |
| `scripts/build-review-prompts.sh` | Findings: #1, #3, #4, #5 | 367 lines; full script reviewed; Findings at L95 (round validation), L141-175 (temp file leak), L254-298 (self-reference), L74-86 (empty file validation) |

Note: `scripts/build-review-prompts.sh` is not in the brief's stated file list, but it is the primary implementation artifact for RULES.md Step 3b and is referenced directly by all four scoped files. It was read to validate edge-case claims about template files. Findings filed against it are based on direct evidence in the script.

---

## Overall Assessment

**Score**: 7.5/10
**Verdict**: PASS WITH ISSUES

The orchestration templates and scripts have solid structure with multiple layers of input validation (RULES.md Step 3b-i.5, script-level guards, placeholder detection in the polling loop). The main gaps are: (1) the `build-review-prompts.sh` script does not fully replicate the input guards described in RULES.md, leaving the script caller-dependent for safety; (2) the placeholder-substitution path has no end-to-end completeness check, so a partially-filled prompt would produce misleading errors rather than a clear "substitution failed" message. No P1 issues found — no data loss or crash paths in common usage. Four P2 issues represent gaps that would produce incorrect behavior (wrong reviewer composition, missing failure artifacts at expected paths) in edge cases that are plausible in production (e.g., REVIEW_ROUND=0 from a state-file corruption, empty `@file` from a failed `git diff`).
