# Report: Correctness Redux Review

**Scope**: orchestration/templates/big-head-skeleton.md, orchestration/templates/checkpoints.md, orchestration/templates/dirt-pusher-skeleton.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
**Reviewer**: Correctness Redux + code-reviewer

## Findings Catalog

### Finding 1: Polling loop logic is inverted -- MISSING_REPORTS variable counts FOUND files, not missing ones

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md`:370-383
- **Severity**: P2
- **Category**: correctness
- **Description**: The polling loop in Step 0a uses `&&` to chain `ls` commands, meaning `MISSING_REPORTS` will contain output only when ALL four files are found (since `&&` short-circuits on failure). The variable name says "MISSING_REPORTS" but actually holds found-report paths. More critically, the completion check `if [ "$(echo "$MISSING_REPORTS" | wc -l)" -eq 4 ]` tests whether the output has exactly 4 lines. However, `ls` may output multiple lines per glob match (e.g., if multiple files match `clarity-review-*.md`), or the `|| true` fallback could produce a single empty line when all `ls` commands fail, causing `wc -l` to report 1 rather than 0.

  The logic works in the happy path (all 4 files exist, each `ls` prints one line, total = 4 lines, loop breaks). But if some files exist and some don't, the `&&` chain short-circuits on the first missing file, the `|| true` produces an empty-string result, and `wc -l` on that counts 1 line (the empty line), which is not 4, so polling continues -- this is accidentally correct but for the wrong reason.

  The real failure case: if a reviewer writes two files matching the same glob (e.g., `clarity-review-20260219-120000.md` and `clarity-review-20260219-120001.md`), `wc -l` would count >4, and the loop would never break even though all 4 review types are present. The loop silently times out and falls through to the error return path.

- **Suggested fix**: Rewrite to check file existence independently rather than chaining with `&&`. Use separate checks per file type that increment a counter, or use `test -f` with specific paths rather than globs. The variable should also be renamed from `MISSING_REPORTS` to something accurate like `FOUND_REPORTS`.
- **Cross-reference**: This is guidance text for an LLM agent (Big Head), not executable production code. The polling loop is a reference script. The LLM may interpret the intent correctly despite the naming inconsistency, but could also follow the script literally if given shell access. Severity is P2 because this template is a direct instruction to Big Head, and a literal interpretation of the script would produce incorrect behavior in edge cases.

### Finding 2: Big Head skeleton and reviews.md have divergent failure handling for missing reports

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md`:57-66, `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md`:354-424
- **Severity**: P2
- **Category**: correctness
- **Description**: The big-head-skeleton.md (the agent-facing template spawned via TeamCreate) instructs Big Head at Step 1 to "Verify all 4 report files exist (FAIL immediately if any missing)" and specifies: write a failure artifact, return FAIL error, and do NOT proceed. This is an immediate fail-fast with no waiting.

  However, reviews.md Step 0a (the protocol document read by the Pantry to compose the consolidation brief) specifies a 30-second polling loop with timeout before failing. These two documents give Big Head contradictory instructions about the same scenario:
  - Skeleton says: FAIL immediately
  - reviews.md says: poll for 30 seconds, then fail

  Since Big Head reads the consolidation brief (composed by Pantry from reviews.md), and its spawn prompt comes from the skeleton, it receives both sets of instructions. The skeleton's "FAIL immediately" and the brief's "poll for 30 seconds" create an ambiguity that the agent must resolve at runtime.

  Additionally, the failure artifact paths differ: skeleton writes to `{SESSION_DIR}/review-reports/review-consolidated-{TIMESTAMP}-FAILED.md` while reviews.md Step 0a has no explicit failure artifact path (it returns a structured markdown error message inline).

- **Suggested fix**: Harmonize the two templates. Either (a) update the skeleton to say "See consolidation brief for the full remediation protocol including timeout" and remove the inline failure instructions, or (b) add the 30-second timeout to the skeleton and remove the detailed Step 0a from reviews.md. The failure artifact convention should be consistent -- pick one output path format and use it in both places.
- **Cross-reference**: Relates to acceptance criteria for ant-farm-e9k (remediation path for missing reports) and ant-farm-zeu (missing-input guards). Both tasks added content to different templates without cross-referencing each other.

### Finding 3: Pantry Condition 1 failure artifact says "Halt and report" but logic says "skip to next task"

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md`:30-43
- **Severity**: P3
- **Category**: correctness
- **Description**: Line 30 says `**FAIL-FAST CHECK**: Halt and report for any of these conditions`. "Halt" implies stopping all processing. But the actual behavior described in Condition 1's bullet points is "Record the task ID... Do NOT write a task brief for this task... Do not proceed with task brief composition for this task" -- which is per-task skipping, not halting all work. Conditions 2 and 3 explicitly say "skip to the next task." The "Halt and report" preamble is misleading relative to the actual skip-and-continue behavior.

  This predates the current changes -- the new commit (ant-farm-zeu) added failure artifact writing but did not change the "Halt and report" wording. The inconsistency is now more prominent because the detailed per-condition behavior (write artifact, skip to next) conflicts more visibly with the blanket "halt" instruction.

- **Suggested fix**: Change "Halt and report" to "Check and skip on failure" or "Validate before proceeding" to match the actual skip-to-next-task behavior described in the conditions.

### Finding 4: Pantry "On any failure above" partial verdict table placement is ambiguous after Condition 3

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md`:68-74
- **Severity**: P3
- **Category**: correctness
- **Description**: The "On any failure above" block with the partial verdict table appears after Condition 3 at the same indentation level. It says "Return a partial verdict table to the Queen showing completed and failed tasks." But is this triggered once after processing ALL tasks (some succeeded, some failed), or after EACH individual failure? The placement suggests it runs after Condition 3 specifically, but the "any failure above" wording spans all three conditions.

  Given that Conditions 1-3 say "skip to the next task," the intended behavior is likely: process all tasks, then return one partial verdict table at the end with all successes and failures. But the current structure could be read as: return a partial table after each failure (mid-loop), which would mean the Pantry returns multiple times.

- **Suggested fix**: Move the partial verdict table instruction to after the per-task loop ends (after Step 2 item 5, the brief validation), and clarify it runs once at the end: "After processing all tasks, if any failures occurred, return a partial verdict table..."

## Preliminary Groupings

### Group A: Big Head missing-report handling is inconsistent across templates

- Finding 1, Finding 2 -- both relate to how Big Head handles missing Nitpicker reports
- **Suggested combined fix**: Designate reviews.md as the authoritative source for the full remediation protocol (including polling, timeout, and failure artifact). Update big-head-skeleton.md Step 1 to reference the consolidation brief for remediation details rather than specifying its own inline failure behavior. Fix the polling script logic while consolidating.

### Group B: Pantry failure-flow control language is ambiguous

- Finding 3, Finding 4 -- both relate to confusion in the Pantry's failure handling flow
- **Suggested combined fix**: Rewrite the Pantry Step 2 opening to say "Validate and skip on failure" instead of "Halt," and restructure the partial verdict table instruction to appear clearly outside the per-task loop with explicit "run once after all tasks processed" wording.

## Summary Statistics
- Total findings: 4
- By severity: P1: 0, P2: 2, P3: 2
- Preliminary groups: 2

## Cross-Review Messages

### Sent
- (None sent -- findings are within correctness domain)

### Received
- From excellence-reviewer: "Polling loop logic bug in reviews.md:377 -- MISSING_REPORTS variable name inverted, wc -l fragile with multi-match globs" -- Action taken: Confirmed overlap with my Finding 1 (same issue, same severity P2, independently identified). No changes needed to my report; this cross-validation strengthens the finding.
- From edge-cases-reviewer: "Polling loop glob logic fragility in reviews.md:370-383 -- wc -l check assumes 1 line per review type, breaks on multi-match globs from previous runs" -- Action taken: Same overlap with Finding 1. Third independent confirmation across correctness, excellence, and edge-cases reviewers. No report changes needed.

### Deferred Items
- (None)

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md` | Findings: #2 | 80 lines, 3 sections (Instructions, Wiring, Template) examined |
| `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md` | Reviewed -- no issues | 551 lines, 6 major sections (CCO Dirt Pushers, CCO Nitpickers, WWD, DMVDC Dirt Pushers, DMVDC Nitpickers, CCB) examined. The bd show guard at line 332-337 is well-placed, correctly distinguishes infrastructure vs substance failure, uses fallback criteria from summary doc, and marks the fallback clearly. |
| `/Users/correy/projects/ant-farm/orchestration/templates/dirt-pusher-skeleton.md` | Reviewed -- no issues | 46 lines, 2 sections (Instructions, Template) examined. Format specification at line 30 correctly lists sections matching the Pantry's task brief format (Context, Scope Boundaries, Focus). Explicit "markdown" declaration satisfies ant-farm-x4m acceptance criteria. |
| `/Users/correy/projects/ant-farm/orchestration/templates/nitpicker-skeleton.md` | Reviewed -- no issues | 38 lines, 2 sections (Instructions, Template) examined. Format specification at line 20 correctly lists sections (Scope, Files, Focus, Detailed Instructions) matching the Pantry's review brief format. Explicit "markdown" declaration satisfies ant-farm-x4m acceptance criteria. |
| `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md` | Findings: #3, #4 | 288 lines, 3 major sections (Implementation Mode, Review Mode, Error Handling) examined. Fail-fast checks at lines 30-74 now include failure artifact writing and infrastructure/substance distinction (ant-farm-zeu). Empty file list guard at lines 216-228 correctly handles review mode edge case. |
| `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md` | Findings: #1, #2 | 620 lines, 8 major sections (Transition Gate, Agent Teams Protocol, Reviews 1-4, Report Format, Big Head Consolidation, Queen's Checklists) examined. Step 0a remediation path (lines 354-424) added for ant-farm-e9k. |

## Acceptance Criteria Verification

### ant-farm-x4m: Add data file format specification to skeleton templates
Source: `bd show ant-farm-x4m`

| Criterion | Status | Evidence |
|-----------|--------|---------|
| dirt-pusher-skeleton.md specifies the data file format and expected sections | MET | Line 30: "(Format: markdown. Sections: Context, Scope Boundaries, Focus.)" |
| nitpicker-skeleton.md specifies the data file format and expected sections | MET | Line 20: "(Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions.)" |
| Both skeletons explicitly state the file is markdown (not JSON/YAML) | MET | Both use "Format: markdown" as the opening of the parenthetical |

### ant-farm-e9k: Add remediation path for missing Nitpicker reports
Source: `bd show ant-farm-e9k`

| Criterion | Status | Evidence |
|-----------|--------|---------|
| reviews.md Big Head section includes a remediation step for missing reports | MET | Step 0a added at lines 354-424 with full remediation protocol |
| The step specifies: return error to Queen, list missing reports, request re-spawn | MET | Error return template at lines 390-420 includes all three elements |
| A timeout or maximum wait is specified before triggering the remediation path | MET | 30-second timeout specified at line 358, with 2-second polling interval |

**Note**: All criteria technically met, but Finding #1 (polling logic) and Finding #2 (skeleton divergence) identify correctness issues in the implementation quality.

### ant-farm-zeu: Templates lack explicit guards for missing or empty input artifacts
Source: `bd show ant-farm-zeu`

| Criterion | Status | Evidence |
|-----------|--------|---------|
| Each template has explicit instructions for handling missing/empty inputs | MET | Pantry: 3 conditions with failure artifacts (lines 32-66). Big Head skeleton: missing-report guard (lines 57-66). Checkpoints: bd show failure guard (lines 332-337). Reviews: empty file list guard (lines 216-228). |
| Failure artifacts are written to expected output paths so downstream consumers are not left guessing | MET | Pantry writes to `{session-dir}/prompts/task-{TASK_SUFFIX}-FAILED.md`. Big Head writes to `{SESSION_DIR}/review-reports/review-consolidated-{TIMESTAMP}-FAILED.md`. Reviews writes to `{session-dir}/prompts/review-FAILED.md`. |
| Infrastructure failures are distinguished from substance failures | MET | Pantry: Condition 1 labeled "INFRASTRUCTURE FAILURE", Conditions 2-3 labeled "SUBSTANCE FAILURE". Big Head: labeled "INFRASTRUCTURE FAILURE". Checkpoints: labeled "INFRASTRUCTURE FAILURE". Reviews: labeled "SUBSTANCE FAILURE". |

## Overall Assessment
**Score**: 8/10
**Verdict**: PASS WITH ISSUES
<!-- Score: 10 - 1(P2) - 1(P2) - 0.5(P3) - 0.5(P3) = 8 -->

All three tasks' acceptance criteria are met. The two P2 findings (polling loop logic inversion and skeleton/reviews.md divergence on Big Head failure handling) are real issues that should be addressed but do not block shipping -- they affect edge-case error handling in agent templates, not the primary workflow. The P3 findings are language clarity issues in the Pantry's failure flow documentation.
