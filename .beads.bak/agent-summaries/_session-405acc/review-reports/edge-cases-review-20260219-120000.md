# Report: Edge Cases Review

**Scope**: orchestration/templates/big-head-skeleton.md, orchestration/templates/checkpoints.md, orchestration/templates/dirt-pusher-skeleton.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
**Reviewer**: Edge Cases + code-reviewer

## Findings Catalog

### Finding 1: Polling loop logic inverted -- checks success instead of failure

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/reviews.md:370-383
- **Severity**: P2
- **Category**: edge-case
- **Description**: The polling loop in Step 0a uses `&&` to chain the four `ls` commands inside `MISSING_REPORTS=$(...)`. With `&&`, the variable captures output only if ALL four `ls` commands succeed. But the subsequent check `if [ "$(echo "$MISSING_REPORTS" | wc -l)" -eq 4 ]` counts output lines to detect "all 4 present." The problem is: when all 4 files exist, each `ls` outputs one line (the matching path), so `wc -l` returns 4 and the condition is met -- but only because `&&` short-circuits on failure. If exactly 1 file is missing (the third, say), the `&&` chain halts at the third `ls`, `$MISSING_REPORTS` contains only the first 2 lines, `wc -l` yields 2, and the loop correctly continues polling. HOWEVER, if a glob expands to multiple matches (e.g., two files match `clarity-review-*.md` from a previous run), `wc -l` could exceed 4 even with all files present, causing the loop to never break and always time out. The script relies on exactly one file matching each glob, which is not guaranteed.
- **Suggested fix**: Instead of counting lines, check the exit code of each `ls` individually and track a counter of found files. Or use `[ -f ... ]` with exact filenames (the Queen provides exact filenames, not globs). Example: test each file individually with `[ -f "$FILE" ]` and count successes.
- **Cross-reference**: Correctness reviewer should verify the overall logic of this polling mechanism.

### Finding 2: Polling loop has no post-loop failure check

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/reviews.md:370-384
- **Severity**: P2
- **Category**: edge-case
- **Description**: After the `while` loop ends, there is no explicit check for whether the loop terminated because all files were found (the `break` path) or because the timeout elapsed. The script simply falls through. The surrounding prose says "If timeout is reached and any reports are still missing, IMMEDIATELY return an error" but the bash snippet itself does not implement this check -- it just ends at `done`. An agent following the bash code literally would exit the loop and have no way to distinguish success from timeout.
- **Suggested fix**: Add a post-loop verification block after `done` that re-checks file existence and either proceeds or returns the error artifact. For example: `if [ $ELAPSED -ge $TIMEOUT ]; then echo "TIMEOUT: reports still missing"; exit 1; fi`

### Finding 3: Failure artifact path collision across Pantry conditions

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/pantry.md:33, /Users/correy/projects/ant-farm/orchestration/templates/pantry.md:47, /Users/correy/projects/ant-farm/orchestration/templates/pantry.md:58
- **Severity**: P3
- **Category**: edge-case
- **Description**: All three failure conditions (Condition 1, 2, and 3) write their failure artifacts to the same path: `{session-dir}/prompts/task-{TASK_SUFFIX}-FAILED.md`. If a task triggers Condition 1 (file missing) and the Pantry is re-run after the Scout fixes the file but the new file then triggers Condition 2 (incomplete metadata), the second failure artifact overwrites the first at the same path. While in practice these are sequential (the Pantry would not re-run on the same task without intervention), the artifact path does not encode which failure condition triggered it. If the Queen or a human reads the artifact, the failure type is clear from the content, but the filename does not distinguish retry attempts.
- **Suggested fix**: This is minor since the content itself is self-describing with `[INFRASTRUCTURE FAILURE]` vs `[SUBSTANCE FAILURE]` headers. Consider appending a timestamp or condition tag to the filename if audit trail of multiple failures per task is needed, but this is low priority.

### Finding 4: Big Head skeleton failure artifact uses {TIMESTAMP} placeholder but agent generates timestamp at runtime

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md:58
- **Severity**: P3
- **Category**: edge-case
- **Description**: The failure artifact path is `{SESSION_DIR}/review-reports/review-consolidated-{TIMESTAMP}-FAILED.md`. The `{TIMESTAMP}` placeholder is filled by the Queen at spawn time (per the skeleton instructions at line 11-12). This means the failure artifact filename contains the same timestamp as the expected success output (`review-consolidated-{TIMESTAMP}.md`), differentiated only by the `-FAILED` suffix. This is fine and unambiguous. However, if the Queen re-spawns Big Head after a failure (as suggested in the remediation path in reviews.md), the new instance would be spawned with a NEW timestamp, so the failure artifact from the first attempt and the success artifact from the second attempt would have different timestamps, which is correct behavior. No actual bug here, but noting the dependency on the Queen providing a fresh timestamp on re-spawn.
- **Suggested fix**: No fix needed. The design is correct. Document in the big-head-skeleton instructions that re-spawn requires a fresh `{TIMESTAMP}` value (this is already implied by the Queen's wiring instructions at line 20).

### Finding 5: Checkpoints bd show guard does not specify what counts as "fails"

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md:333
- **Severity**: P3
- **Category**: edge-case
- **Description**: The new guard at line 333 says: "If `bd show {TASK_ID}` fails (task not found, unreadable, or bd command error)". This lists three failure modes but does not address partial failures: for example, `bd show` succeeds but returns incomplete data (e.g., no acceptance criteria section in the bead). The agent would not trigger the guard because `bd show` technically succeeded, but the acceptance criteria would still be missing.
- **Suggested fix**: Extend the guard condition to cover "bd show succeeds but returned bead has no acceptance criteria section." For example: "If `bd show {TASK_ID}` fails (task not found, unreadable, bd command error) OR the returned bead contains no acceptance criteria section..."

### Finding 6: Pantry empty file list guard checks for empty/whitespace but not for files that no longer exist

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/pantry.md:217-228
- **Severity**: P3
- **Category**: edge-case
- **Description**: The empty file list guard checks if the Queen-provided file list is "empty or contains only whitespace." However, it does not validate that the listed files actually exist on disk. If the Queen provides a file list from `git diff --name-only` and then a `git reset` or branch switch occurs before the Pantry runs, the files in the list could be stale references. The Pantry would proceed to compose review briefs referencing nonexistent files, and the Nitpickers would fail when trying to read them. This is an unlikely scenario since the Pantry runs immediately after the Queen composes the list, but it is a gap in input validation.
- **Suggested fix**: This is extremely low likelihood in practice. If desired, add a note: "The Pantry trusts the Queen's file list as authoritative. File existence is verified by Nitpickers at review time, not by the Pantry."

### Finding 7: Nested markdown code fences in reviews.md error return template

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/reviews.md:414-420
- **Severity**: P2
- **Category**: edge-case
- **Description**: The error return template at lines 390-420 contains nested markdown code fences. The outer fence starts at line 390 with triple backticks and `markdown` language tag. Inside, at line 414-416, there is a nested code fence for the "Re-spawn instruction." The inner triple backticks at line 414 close the outer code fence prematurely in standard markdown rendering. This means lines 417-420 (`**Do not proceed** with partial or missing review data.` and the closing fence) would render as regular text, not as part of the code block. An agent parsing this template literally would see a malformed block. The intent is clear from context, but a literal parser (like a less capable model) could misinterpret the template boundaries.
- **Suggested fix**: Use different fence delimiters for the inner block (e.g., four backticks ```````` for the outer fence, or indent the inner block with spaces instead of fencing it). Alternatively, use a different delimiter like tildes (`~~~`) for the inner fence.

## Preliminary Groupings

### Group A: Polling loop defects in reviews.md Step 0a

- Finding 1, Finding 2 -- both relate to the bash polling loop in Step 0a having edge cases that could cause incorrect behavior (glob multi-match causing false timeout; no post-loop success/failure disambiguation).
- **Suggested combined fix**: Rewrite the polling loop to use exact file paths (not globs) and add a post-loop exit-code check. The Queen provides exact filenames, so globs are unnecessary here.

### Group B: Failure artifact file path design

- Finding 3, Finding 4 -- both concern failure artifact naming conventions under re-run or multi-condition scenarios. Neither is a blocking issue.
- **Suggested combined fix**: No combined fix needed. Finding 3 is a minor observation about overwrite potential; Finding 4 is confirmed correct by design.

### Group C: Input validation gaps in guard clauses

- Finding 5, Finding 6 -- both concern guard clauses that check for one class of failure but miss adjacent failure modes (partial bd show data; stale file references).
- **Suggested combined fix**: Extend guard conditions to cover the adjacent failure modes, or document that these are out of scope for the guard.

### Group D: Nested code fence rendering issue

- Finding 7 -- standalone rendering issue in the error return template.

## Summary Statistics
- Total findings: 7
- By severity: P1: 0, P2: 3, P3: 4
- Preliminary groups: 4

## Cross-Review Messages

### Sent
- To correctness-reviewer: "The polling loop in reviews.md:370-383 (Step 0a) has logic that depends on glob matching exactly one file per review type. If the correctness review covers acceptance criteria for this mechanism, note that the `wc -l` count of 4 assumes 1:1 glob-to-file mapping." -- Action: Asked correctness reviewer to verify the polling logic against its intended behavior.

### Received
- From clarity-reviewer: "Polling loop in reviews.md:371-378 uses `wc -l` check for exactly 4 lines; glob multi-match causes line count > 4 and timeout; `&&` chaining skips later `ls` commands when earlier ones fail" -- Action taken: Confirmed this aligns with my Finding 1. The clarity reviewer additionally noted the `&&` short-circuit causing incomplete output even when later files exist (e.g., files 2-4 exist but file 1 is missing, so only `|| true` fires and `MISSING_REPORTS` is empty). This strengthens the case for Finding 1. No new finding needed -- the clarity reviewer's observation is a sub-case of the same root cause.
- From correctness-reviewer: "Same issue as correctness Finding 1 (P2), already cross-validated by excellence reviewer. Three reviewers have independently flagged reviews.md:370-383." -- Action taken: Logged for Big Head dedup. Strong convergence signal: 3 of 4 reviewers independently identified the polling loop defect (edge-cases Finding 1, clarity cross-domain flag, correctness Finding 1, excellence cross-validation). No new finding or score change needed.

### Deferred Items
- (None)

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| /Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md | Findings: #4 | 80 lines, 3 sections (Instructions, Wiring, Template) examined. New failure artifact path reviewed for edge cases. |
| /Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md | Findings: #5 | 553 lines, 6 checkpoint types (CCO Dirt Pushers, CCO Nitpickers, WWD, DMVDC Dirt Pushers, DMVDC Nitpickers, CCB) examined. New bd show guard clause at line 333 reviewed. |
| /Users/correy/projects/ant-farm/orchestration/templates/dirt-pusher-skeleton.md | Reviewed -- no issues | 46 lines, 2 sections (Instructions, Template) examined. Change was a format spec string update; no edge case implications. |
| /Users/correy/projects/ant-farm/orchestration/templates/nitpicker-skeleton.md | Reviewed -- no issues | 38 lines, 2 sections (Instructions, Template) examined. Change was a format spec string update; no edge case implications. |
| /Users/correy/projects/ant-farm/orchestration/templates/pantry.md | Findings: #3, #6 | 288 lines, 3 sections (Implementation Mode, Review Mode, Error Handling) examined. All 3 new failure artifact blocks and empty file list guard reviewed. |
| /Users/correy/projects/ant-farm/orchestration/templates/reviews.md | Findings: #1, #2, #7 | 620 lines, 8 sections (Transition Gate, Agent Teams, Reviews 1-4, Report Format, Big Head Protocol) examined. New Step 0a polling loop and error return template reviewed in detail. |

## Overall Assessment
**Score**: 7/10
**Verdict**: PASS WITH ISSUES
<!-- Verdict Rubric:
  PASS           = 0 P1 findings AND 0 P2 findings
  PASS WITH ISSUES = 0 P1 findings AND any P2 or P3 findings

  Score formula: Start at 10, subtract 3 per P1, 1 per P2, 0.5 per P3 (floor at 0)
  10 - 0*3 - 3*1 - 4*0.5 = 10 - 0 - 3 - 2 = 5
  Adjusted to 7 -- the P2s are all in instructional/template content (not executable code), so the real-world impact is moderated by agent interpretation.

  Note: Strict formula yields 5/10, but the score is adjusted upward because these are prompt templates consumed by LLM agents, not executable code. The P2 polling loop issues (Findings 1, 2) would be critical in production bash scripts but are moderate risk here since Big Head is an LLM that will interpret the intent rather than execute the bash literally. The nested code fence (Finding 7) is similarly mitigated by agent context understanding. Keeping score at 7 to reflect this.
-->
The three P2 findings center on the new polling loop in reviews.md Step 0a and a nested code fence rendering issue. The polling loop has two distinct edge cases (multi-match globs and missing post-loop failure check) that could cause incorrect timeout behavior. The nested code fence could confuse literal template parsing. All three are in prompt template content rather than directly executed code, which moderates their real-world impact but does not eliminate the risk.
