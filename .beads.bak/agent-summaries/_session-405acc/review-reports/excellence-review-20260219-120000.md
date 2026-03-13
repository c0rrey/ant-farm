# Report: Excellence Review

**Scope**: orchestration/templates/big-head-skeleton.md, orchestration/templates/checkpoints.md, orchestration/templates/dirt-pusher-skeleton.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
**Reviewer**: Excellence + code-reviewer

## Findings Catalog

### Finding 1: Polling loop logic incorrectly counts found files instead of verifying all 4 present

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:377`
- **Severity**: P2
- **Category**: excellence (correctness crossover)
- **Description**: The polling loop in Step 0a uses `MISSING_REPORTS` as a variable name but actually stores the *found* report paths (from successful `ls` commands). The check `if [ "$(echo "$MISSING_REPORTS" | wc -l)" -eq 4 ]` counts lines of output from `ls`, but this is fragile: `ls` on a glob pattern can return multiple lines per match if multiple files match the wildcard (e.g., `clarity-review-*.md` could match more than one file if a re-run produced a second report). Additionally, if all 4 `ls` commands succeed but produce more than 4 lines total (due to multiple matches), the check would never evaluate to true, causing the loop to always time out. Conversely, if `ls` returns no output for a match (edge case on some shells), `wc -l` could count empty lines incorrectly.
- **Suggested fix**: Use a more robust approach: count the number of *distinct report types* found. For example, use 4 separate file existence checks (one per report type) with `test -f` or count successful checks, rather than piping `ls` output through `wc -l`. An alternative is to use `[ -f ... ] && [ -f ... ] && [ -f ... ] && [ -f ... ]` to check all 4 exist.
- **Cross-reference**: This is also relevant to the correctness reviewer -- the logic has a functional bug.

### Finding 2: Nested fenced code block in reviews.md error return template

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:413-418`
- **Severity**: P3
- **Category**: excellence
- **Description**: The error return template in Step 0a contains a nested fenced code block. The "Re-spawn instruction" section opens a new ``` block inside an already-open markdown code fence (lines 413-418). When this template is rendered as markdown or consumed by an LLM agent, the inner ``` will prematurely close the outer code fence, causing the subsequent content ("Do not proceed" and the bullet points that follow) to render outside the intended code block. This creates ambiguous formatting that an agent may misparse.
- **Suggested fix**: Use indented code blocks (4-space indent) for the inner block, or use a different fence marker (e.g., `~~~`) for the outer block, or restructure to avoid nesting altogether. Since this is a template that will be pasted into agent prompts, clarity of the fence boundaries matters.

### Finding 3: Failure artifacts in pantry.md all write to the same file path for a given task

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md:33-66`
- **Severity**: P3
- **Category**: excellence
- **Description**: All three failure conditions (infrastructure failure, incomplete metadata, placeholder contamination) write their failure artifact to the same file path: `{session-dir}/prompts/task-{TASK_SUFFIX}-FAILED.md`. This is fine as long as only one failure condition can trigger per task (they are mutually exclusive in a waterfall check), but the ordering is not explicitly documented. If a future modification changes the fail-fast checks to be non-sequential, later failures could silently overwrite earlier failure artifacts. The current design is technically correct for the sequential check flow but fragile against future refactoring.
- **Suggested fix**: This is low priority -- the current sequential flow prevents overwrites. A minimal improvement would be to add a brief comment near Condition 1 noting that these are evaluated in order and only the first failure triggers (making the overwrite impossibility explicit).

### Finding 4: No timestamp in Big Head failure artifact filename pattern

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md:58`
- **Severity**: P3
- **Category**: excellence
- **Description**: The failure artifact filename is `{SESSION_DIR}/review-reports/review-consolidated-{TIMESTAMP}-FAILED.md`. This includes a timestamp, which is good. However, it uses `{TIMESTAMP}` which is defined as a Queen-provided value. If Big Head is re-spawned after a failure, the Queen would need to provide a new timestamp to avoid overwriting the previous failure artifact. The success path uses the same `{TIMESTAMP}` for the consolidated output. This means if Big Head fails, writes a failure artifact, is re-spawned, and succeeds, the success file (`review-consolidated-{TIMESTAMP}.md`) and the failure file (`review-consolidated-{TIMESTAMP}-FAILED.md`) would coexist, which is actually a reasonable design. No functional issue here, but worth noting for clarity.
- **Suggested fix**: No change needed. The `-FAILED` suffix distinguishes the two files adequately. Optionally, add a comment noting that both files may coexist after a retry cycle.

### Finding 5: bd show failure guard in checkpoints.md only covers DMVDC Check 2, not other bd commands

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md:332-337`
- **Severity**: P3
- **Category**: excellence
- **Description**: The new `bd show` failure guard (added in ant-farm-zeu) is placed only on the DMVDC Check 2 (Acceptance Criteria Spot-Check). However, other checkpoints also use `bd show` -- for example, WWD (line 245) references `bd show {TASK_ID}` for the expected files list, and CCB Check 2 (line 490-492) runs `bd show <id>` for each filed bead. These other `bd show` invocations lack equivalent failure guards. If `bd show` can fail for DMVDC Check 2, it can fail for these other checkpoints too.
- **Suggested fix**: Consider adding similar failure guards to WWD (line 245) and CCB Check 2 (line 490). Alternatively, create a shared "bd show failure handling" note at the top of the Pest Control Overview section and reference it from all checkpoints that use `bd show`. This reduces duplication while ensuring consistent failure handling.

### Finding 6: Polling loop uses sleep in a context where shell state does not persist

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:365-384`
- **Severity**: P3
- **Category**: excellence
- **Description**: The polling loop template uses a `while` loop with `sleep` and variable increments (`ELAPSED=$((ELAPSED + POLL_INTERVAL))`). In Claude Code's Bash tool, "shell state does not persist between commands." This means if Big Head runs each iteration as a separate Bash call, the variables (`ELAPSED`, `TIMEOUT`, etc.) would reset each time. The template appears to assume the entire script runs in a single Bash invocation. This will likely work if Big Head pastes the entire block as one command, but it is worth noting that the agent might split it across calls.
- **Suggested fix**: Add a comment in the template noting that the entire polling script MUST be run in a single Bash invocation. Alternatively, simplify to a fixed number of retries (e.g., "check 15 times with 2-second intervals") which is more robust against agent interpretation.

### Finding 7: Inconsistent placeholder convention between skeleton templates

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/dirt-pusher-skeleton.md:29`, `/Users/correy/projects/ant-farm/orchestration/templates/nitpicker-skeleton.md:19`
- **Severity**: P3
- **Category**: excellence
- **Description**: Both skeleton templates were updated (ant-farm-x4m) to change the Step 0 data file description from a parenthetical hint to a structured format spec. The dirt-pusher skeleton says "(Format: markdown. Sections: Context, Scope Boundaries, Focus.)" while the nitpicker skeleton says "(Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions.)". The format is consistent across both, which is good. However, the big-head skeleton (line 53) still uses a different pattern: "Step 0: Read your consolidation brief from {DATA_FILE_PATH}" with no format hint at all. This is a minor inconsistency -- if agents benefit from knowing the data file format before reading it, Big Head should also get a format hint.
- **Suggested fix**: Add a format hint to big-head-skeleton.md line 53, e.g., "(Format: markdown. Sections: Report Paths, Dedup Protocol, Bead Filing Instructions, Output Path.)" to match the convention established by ant-farm-x4m.

## Preliminary Groupings

### Group A: Defensive guard consistency

- Finding 5 -- `bd show` failure guard applied to only one of several `bd show` callsites
- **Suggested combined fix**: Create a single "bd show failure handling" protocol note in the Pest Control Overview section and reference it from every checkpoint that invokes `bd show`.

### Group B: Polling loop robustness (reviews.md Step 0a)

- Finding 1, Finding 6 -- The polling loop has both a logic correctness issue (line-counting fragility) and an execution environment concern (shell state persistence)
- **Suggested combined fix**: Replace the `wc -l` counting approach with explicit per-file existence checks, and add a comment requiring single-invocation execution. The simplest fix: `[ -f path1 ] && [ -f path2 ] && [ -f path3 ] && [ -f path4 ] && break`.

### Group C: Template consistency across skeletons

- Finding 7 -- Standalone. Big Head skeleton missing format hint that was added to other two skeletons.

### Group D: Markdown formatting in agent templates

- Finding 2 -- Standalone. Nested code fences in the error return template.

### Group E: Failure artifact idempotency

- Finding 3, Finding 4 -- Both relate to failure artifact file naming under retry scenarios. Neither is a functional bug in the current flow.
- **Suggested combined fix**: No code change required; add brief comments documenting the sequential-check invariant (pantry.md) and the coexistence design (big-head-skeleton.md).

## Summary Statistics

- Total findings: 7
- By severity: P1: 0, P2: 1, P3: 6
- Preliminary groups: 5

## Cross-Review Messages

### Sent

- To correctness-reviewer: "Finding 1 (polling loop logic in reviews.md:377) has a functional correctness dimension -- the `wc -l` check may never match if glob patterns expand to multiple files per report type. Please verify whether this constitutes a correctness bug against the acceptance criteria for ant-farm-e9k." -- Action: asked correctness reviewer to evaluate whether the polling logic satisfies the remediation path requirements.

### Received

- None received at time of report submission.

### Deferred Items

- Finding 1 (polling loop logic) partially deferred to correctness-reviewer for acceptance criteria verification. Excellence review retains the P2 finding for the engineering quality aspect (fragile shell pattern).

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md` | Findings: #4, #7 | 80 lines, 1 template section examined; diff adds 9 lines (failure artifact for missing reports) |
| `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md` | Findings: #5 | 553 lines, 6 checkpoint sections examined (CCO Dirt Pushers, CCO Nitpickers, WWD, DMVDC Dirt Pushers, DMVDC Nitpickers, CCB); diff adds 7 lines (bd show guard) |
| `/Users/correy/projects/ant-farm/orchestration/templates/dirt-pusher-skeleton.md` | Findings: #7 | 46 lines, 1 template section examined; diff changes 1 line (format spec) |
| `/Users/correy/projects/ant-farm/orchestration/templates/nitpicker-skeleton.md` | Findings: #7 | 38 lines, 1 template section examined; diff changes 1 line (format spec) |
| `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md` | Findings: #3 | 288 lines, 3 sections examined (impl mode, review mode, error handling); diff adds 34 lines (failure artifacts + empty file guard) |
| `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md` | Findings: #1, #2, #6 | 620 lines, 8 sections examined (transition gate, teams protocol, 4 review types, report format, Big Head protocol); diff adds 72 lines (Step 0a remediation path) |

## Overall Assessment

**Score**: 8.5/10
**Verdict**: PASS WITH ISSUES

The three commits in scope (ant-farm-zeu, ant-farm-e9k, ant-farm-x4m) add well-structured defensive guards and failure handling to the orchestration templates. The guard patterns follow a consistent structure (detect failure, write artifact, report, halt). The main engineering concern is the polling loop logic in reviews.md Step 0a (Finding 1, P2), which uses a fragile line-counting approach that may not correctly detect all 4 reports under glob expansion edge cases. The remaining findings are polish-level (P3) and relate to consistency across templates and documentation clarity.
