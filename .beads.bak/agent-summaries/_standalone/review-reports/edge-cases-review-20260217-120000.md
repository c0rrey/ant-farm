# Report: Edge Cases Review

**Scope**: ~/.claude/orchestration/RULES.md, ~/.claude/orchestration/templates/pantry.md, ~/.claude/orchestration/templates/checkpoints.md, ~/.claude/orchestration/templates/big-head-skeleton.md, ~/.claude/orchestration/templates/dirt-pusher-skeleton.md
**Reviewer**: Edge Cases Review (code-reviewer)

> **IMPORTANT: File Version Discrepancy** -- The review brief listed `~/.claude/` paths, but the
> repo versions at `/Users/correy/projects/ant-farm/orchestration/templates/` differ significantly
> from the `~/.claude/` copies. All five files have diverged. Findings 1-11 were based on the
> `~/.claude/` versions. Finding 12 was added after re-reading the repo version of
> big-head-skeleton.md (71 lines vs 37 in `~/.claude/`). The `~/.claude/` versions appear to be
> stale pre-session copies that were not synced after this session's commits. Big Head will need
> to assess whether findings based on stale files should be re-verified against the repo versions.

## Findings Catalog

### Finding 1: Session ID collision risk from truncated shasum

- **File(s)**: ~/.claude/orchestration/RULES.md:85
- **Severity**: P3
- **Category**: edge-case
- **Description**: The session ID generation `date +%s | shasum | head -c 6` produces a 6-character hex string (24 bits of entropy, ~16 million possible values). While collisions are unlikely in normal usage, the command uses epoch seconds as input to shasum, meaning two Queens started within the same second on different repos (or the same repo in different terminals) would produce identical session IDs. The `_session-` prefix prevents collision with epic directories, but two concurrent sessions in the same repo would write to the same `_session-XXXXXX/` directory, causing artifact overwrites.
- **Suggested fix**: Add a source of per-invocation randomness, e.g., `(date +%s%N; echo $$) | shasum | head -c 6` or simply use `head -c 3 /dev/urandom | xxd -p` for 6 hex chars with true randomness. Alternatively, document that concurrent Queens in the same repo are unsupported (the concurrency rules already imply single-Queen operation).

### Finding 2: No validation that task-metadata files exist before Pantry reads them

- **File(s)**: ~/.claude/orchestration/templates/pantry.md:26
- **Severity**: P3
- **Category**: edge-case
- **Description**: In Implementation Mode Step 2, the Pantry reads `{session-dir}/task-metadata/{TASK_SUFFIX}.md` for each task. The template states these files are "Pre-extracted by the Scout" but does not specify behavior if a metadata file is missing (e.g., the Scout failed partway through, or a task ID was misspelled in the Queen's input). The error handling section (Section 3, line 165) covers unrecoverable errors generically but does not address this specific failure mode.
- **Suggested fix**: Add an explicit guard in Step 2: "If `{session-dir}/task-metadata/{TASK_SUFFIX}.md` does not exist, skip this task and include it in the partial failure table (Section 3) with error 'metadata file not found'."

### Finding 3: No handling for empty or malformed task-metadata files

- **File(s)**: ~/.claude/orchestration/templates/pantry.md:26-32
- **Severity**: P3
- **Category**: edge-case
- **Description**: The Pantry extracts Title, Affected files, Root cause, Expected behavior, and Acceptance criteria from task-metadata files. If the Scout wrote a metadata file that is missing one of these fields (e.g., a task has no "Root cause" because it is a feature, not a bug), the Pantry has no fallback behavior. The data file template at line 46 would contain an unfilled `{from bead description}` placeholder, which Step 3's validation (line 65) should catch, but the Pantry has no instruction on what to do when a field is genuinely absent from the source metadata.
- **Suggested fix**: Add guidance: "If a field is absent from the task metadata (e.g., feature tasks may not have 'Root cause'), use 'N/A -- feature task' or similar contextual default. Do NOT leave placeholder text."

### Finding 4: Checkpoint A.5 relies on Queen providing expected file list, with no fallback

- **File(s)**: ~/.claude/orchestration/templates/checkpoints.md:189
- **Severity**: P3
- **Category**: edge-case
- **Description**: Checkpoint A.5's prompt template includes `{list files from task description}` as the expected file list. If the Queen passes an incomplete or incorrect file list (e.g., because the task description was vague or the Pantry derived scope boundaries imprecisely), Checkpoint A.5 will produce false positives (flagging legitimate files as scope creep) or false negatives (missing actual scope violations). The checkpoint has no independent way to derive expected scope.
- **Suggested fix**: Consider having Pest Control cross-reference the expected file list against the original data file (which should be accessible at a known path) rather than relying solely on the Queen's passed-in list. Alternatively, document this as a known limitation: "A.5 accuracy depends on the Queen's file list -- review WARN verdicts carefully."

### Finding 5: Retry counter location undefined for Checkpoint C

- **File(s)**: ~/.claude/orchestration/RULES.md:150-151
- **Severity**: P3
- **Category**: edge-case
- **Description**: The retry limits table says "Checkpoint C fails" allows 1 retry, and retry count should be tracked in the Queen's state file. However, there is no explicit instruction for what constitutes a "retry" for Checkpoint C specifically. Checkpoint B retries are well-defined (resume agent, re-verify), but for Checkpoint C, the Queen's response section (checkpoints.md:466-469) says "Fix consolidation gaps... re-run Checkpoint C." If the fix itself spawns a new Big Head instance, does this count against the "Total retries per session" cap of 5? The interaction between per-checkpoint and global retry limits is unspecified.
- **Suggested fix**: Clarify in RULES.md retry table: "Each Checkpoint C re-run counts as 1 toward both the per-checkpoint limit (1) and the session total (5)."

### Finding 6: `bd close` in dirt-pusher-skeleton occurs after commit, before summary doc

- **File(s)**: ~/.claude/orchestration/templates/dirt-pusher-skeleton.md:42
- **Severity**: P2
- **Category**: edge-case
- **Description**: The Dirt Pusher skeleton instructs agents to run `bd close {TASK_ID}` after committing (Step 5) but the instruction appears after Step 6 (summary doc). However, reading carefully, the `bd close` line is placed as a standalone line after all 6 steps. If an agent closes the bead and then crashes before writing the summary doc, the task is marked as closed with no summary artifact. Checkpoint B (checkpoints.md:246) requires reading the summary doc -- it would find no file, but the task is already closed. The Queen's remediation path (resume agent) would need to also re-open the bead.
- **Suggested fix**: Move `bd close {TASK_ID}` to a position explicitly after Step 6 with a note: "Close the bead ONLY after the summary doc is successfully written." Alternatively, have Checkpoint B check for the summary doc's existence before checking substance, with a clear FAIL path if missing.

### Finding 7: Big Head skeleton has no guard for missing report files

- **File(s)**: ~/.claude/orchestration/templates/big-head-skeleton.md:23
- **Severity**: P3
- **Category**: edge-case
- **Description**: The Big Head skeleton instructs step 1 as "Verify all 4 report files exist (FAIL immediately if any missing)." This is good. However, the skeleton itself does not specify WHERE to write the failure report if this verification fails. Checkpoint C (checkpoints.md:392-397) also checks for report existence, meaning there are two layers of verification for the same condition. If Big Head fails at step 1, it presumably returns a failure message to the Queen, but the skeleton does not instruct Big Head to write a failure artifact to disk (unlike successful consolidation, which goes to `{CONSOLIDATED_OUTPUT_PATH}`).
- **Suggested fix**: Add to the skeleton: "If any report file is missing, write a brief failure report to {CONSOLIDATED_OUTPUT_PATH} explaining which files are missing, then return FAIL to the Queen." This ensures an artifact always exists for the Queen's reference.

### Finding 8: Pantry review mode has no handling for empty changed-file list

- **File(s)**: ~/.claude/orchestration/templates/pantry.md:94
- **Severity**: P3
- **Category**: edge-case
- **Description**: Review Mode input includes "list of changed files" from the Queen. If the commit range contains only documentation changes that were excluded from review scope, or if `git diff --name-only` returns an empty set (e.g., all commits were reverts), the Pantry would compose 4 review data files with empty file lists. These would pass to Pest Control's Checkpoint A check 0 (file list matches git diff) and technically pass, but the Nitpickers would have nothing to review, wasting 4 agent spawns.
- **Suggested fix**: Add a guard in Review Mode Step 3: "If the changed file list is empty, return immediately with a note: 'No reviewable files in commit range -- review cycle skipped.' Do NOT compose review data files."

### Finding 9: No specification for handling `bd show` failures in Checkpoint B

- **File(s)**: ~/.claude/orchestration/templates/checkpoints.md:259
- **Severity**: P3
- **Category**: edge-case
- **Description**: Checkpoint B Check 2 instructs Pest Control to `bd show {TASK_ID}` to get acceptance criteria. If the bead system is unavailable or the task ID is invalid (e.g., typo propagated from the Pantry), the checkpoint would fail in an unexpected way. The verdict options (PASS/PARTIAL/FAIL) don't account for infrastructure failures vs. genuine substance issues.
- **Suggested fix**: Add a note: "If `bd show` fails (command error or empty output), report this as a FAIL with category 'infrastructure' rather than 'substance', so the Queen can distinguish between tool failures and agent quality issues."

### Finding 10: Sampling formula contradicts minimum-3 prose in Checkpoint B

- **File(s)**: ~/.claude/orchestration/templates/checkpoints.md:311
- **Severity**: P2
- **Category**: edge-case
- **Description**: The formula `min(5, ceil(N/3))` for selecting findings to spot-check can produce values below 3. For example, when N=6, `ceil(6/3) = 2`, then `min(5, 2) = 2`. But the same line states "minimum 3, or all findings if fewer than 3." The formula does not enforce the stated floor of 3. If Pest Control follows the formula literally, it would under-sample findings (2 instead of 3), reducing verification coverage. If it follows the English text, the formula is misleading. Either way, the contradiction creates ambiguity for Pest Control during Checkpoint B verification of Nitpicker reports.
- **Suggested fix**: Replace the formula with `max(3, min(5, ceil(N/3)))` to enforce the minimum of 3 as stated in the prose. For N < 3, the "all findings if fewer than 3" clause already applies.
- **Cross-reference**: Flagged by clarity reviewer; confirmed as edge-case issue here.

### Finding 11: `prompts/` directory creation inconsistency between RULES.md and pantry.md

- **File(s)**: ~/.claude/orchestration/RULES.md:86, ~/.claude/orchestration/templates/pantry.md:107
- **Severity**: P3
- **Category**: edge-case
- **Description**: RULES.md Step 0 (line 86) creates `_session-${SESSION_ID}/{task-metadata,previews}` using brace expansion. The commit f72f69e added `prompts/` to this brace expansion. However, pantry.md Review Mode Step 3 (line 107) says "Create the prompts directory if needed: `{session-dir}/prompts/`" -- suggesting the Pantry is prepared for the directory not to exist. This is defensive and fine, but it means there are two places that handle `prompts/` creation, which could lead to confusion about responsibility. If RULES.md already creates it, the Pantry instruction is redundant; if the Pantry creates it, the RULES.md change was unnecessary.
- **Suggested fix**: This is minor. Keep both (belt-and-suspenders) but add a comment in pantry.md: "The Queen pre-creates this directory at Step 0, but create if needed as a safety net." This documents the intentional redundancy.

### Finding 12: Queen-to-Big-Head SendMessage may not work in team model

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md:32-43
- **Severity**: P2
- **Category**: edge-case
- **Description**: The repo version of big-head-skeleton.md (which differs from the `~/.claude/` copy) includes Step 3 (lines 32-39) instructing the Queen to use `SendMessage(to="big-head", ...)` to notify Big Head that all 4 Nitpicker reports are ready. However, the Queen is the team lead who spawned the team via TeamCreate -- she is NOT a team member. In Claude Code's team model, the team lead may not be able to use SendMessage to reach team members directly; SendMessage is designed for peer-to-peer communication between team members. If this call silently fails or errors, Big Head would never receive the trigger to begin consolidation. Lines 42-43 provide a partial fallback: "Big Head can also discover them from the brief if SendMessage is delayed." However, this fallback has its own edge case: Big Head would need a separate trigger to know WHEN to start reading. Without a notification, Big Head might start consolidation before all 4 reports are written (race condition), or never start at all (deadlock).
- **Suggested fix**: Three options: (1) Have one of the 4 Nitpickers (e.g., the last to finish) send the SendMessage to Big Head instead of the Queen, since Nitpickers ARE team members. (2) Have Big Head poll for report file existence on a loop until all 4 exist, removing the need for a trigger message. (3) Verify whether the Queen (team lead) can indeed use SendMessage to team members in Claude Code's implementation -- if so, document this as confirmed behavior.
- **Cross-reference**: Flagged by excellence reviewer; confirmed and expanded with race condition / deadlock analysis here.

## Preliminary Groupings

### Group A: Missing-file guards and existence checks
- Finding 2, Finding 3, Finding 7, Finding 8 -- These all involve scenarios where an expected input file or data is missing/empty, and the template does not specify explicit error behavior for that case.
- **Suggested combined fix**: Establish a convention across all templates: "If an expected input artifact is missing or empty, write a brief failure artifact to the expected output path explaining the issue, then return FAIL with a partial results table." Apply this pattern to the Pantry (missing metadata), Big Head (missing reports), and Review Mode (empty file list).

### Group B: Ordering and lifecycle of task closure
- Finding 6 -- standalone issue about `bd close` timing relative to summary doc writing.
- **Suggested combined fix**: Explicitly sequence `bd close` after summary doc in the skeleton template.

### Group C: Retry and error classification ambiguity
- Finding 5, Finding 9 -- Both involve unclear boundaries: retry counting interaction for Checkpoint C, and infrastructure vs. substance failure classification in Checkpoint B.
- **Suggested combined fix**: Add an "Error Classification" section to checkpoints.md distinguishing infrastructure failures (tool unavailability, missing artifacts) from substance failures (agent quality issues), with different escalation paths.

### Group D: Input derivation and validation
- Finding 4 -- standalone issue about Checkpoint A.5 relying on potentially imprecise Queen-provided file lists.

### Group E: Session isolation
- Finding 1 -- standalone issue about session ID collision risk.

### Group F: Redundant directory creation
- Finding 11 -- standalone issue about `prompts/` created in both RULES.md and pantry.md.

### Group G: Formula-prose mismatch in verification sampling
- Finding 10 -- standalone issue about `min(5, ceil(N/3))` not enforcing the stated minimum of 3.

### Group H: Team communication model assumptions
- Finding 12 -- Queen uses SendMessage to reach Big Head (a team member), but the Queen is the team lead, not a team member. Potential silent failure, race condition, or deadlock.

## Summary Statistics
- Total findings: 12
- By severity: P1: 0, P2: 3, P3: 9
- Preliminary groups: 8

## Cross-Review Messages

### Sent
- To correctness: "Finding 6 (bd close ordering in dirt-pusher-skeleton.md:42) may be relevant to your correctness review -- the task closure happens before summary doc write, creating a window where the bead is closed but no summary exists. Checkpoint B would then find no summary doc for a closed task." -- Action: flagged for potential cross-domain overlap.

### Received
- From clarity: "checkpoints.md:311 -- sampling formula `min(5, ceil(N/3))` contradicts 'minimum 3' prose; checkpoints.md:140-154 -- 0-based vs 1-based numbering inconsistency between Checkpoint A sections." -- Action taken: Confirmed the formula issue as a genuine edge case (Finding 10, P2). The 0-based numbering issue is primarily a clarity concern; deferred back to clarity reviewer as it does not create a boundary-condition failure.
- From excellence: "big-head-skeleton.md lines 32-43 describe SendMessage wiring where Queen notifies Big Head, but Queen is team lead, not team member -- may not work in Claude Code's team model." -- Action taken: Initially could not reproduce (was reading stale ~/.claude/ copy). After excellence reviewer identified the file version discrepancy, re-read the repo version at /Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md and confirmed the issue. Added as Finding 12 (P2) with expanded race condition / deadlock analysis.

### Deferred Items
- (none)

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| ~/.claude/orchestration/RULES.md | Findings: #1, #5, #11 | 172 lines examined. Reviewed session ID generation (line 85-86), retry limits table (lines 146-154), concurrency rules (lines 73-79), hard gates (lines 54-59), anti-patterns (lines 113-127), template lookup (lines 129-143), context preservation targets (lines 168-172). |
| ~/.claude/orchestration/templates/pantry.md | Findings: #2, #3, #8, #11 | 167 lines examined. Reviewed Implementation Mode Steps 1-4 (lines 17-88), Review Mode Steps 1-6 (lines 92-159), Error Handling Section 3 (lines 163-167). |
| ~/.claude/orchestration/templates/checkpoints.md | Findings: #4, #5, #9, #10 | 469 lines examined. Reviewed all checkpoint types: A (lines 54-169), A.5 (lines 173-226), B (lines 229-364), C (lines 367-469). Reviewed artifact naming conventions (lines 19-50), epic ID resolution table (lines 40-44). |
| ~/.claude/orchestration/templates/big-head-skeleton.md | Findings: #7, #12 | Initially reviewed ~/.claude/ version (37 lines). After excellence reviewer flagged file version discrepancy, re-reviewed repo version at /Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md (71 lines). Reviewed instruction block (lines 1-45), TeamCreate wiring (lines 16-30), SendMessage Step 3 (lines 32-43), template body (lines 49-71). |
| ~/.claude/orchestration/templates/dirt-pusher-skeleton.md | Findings: #6 | 43 lines examined. Reviewed instruction block (lines 1-19), template body (lines 21-43), 6-step sequence, scope constraints, `bd close` placement. |

## Overall Assessment
**Score**: 5.5/10
**Verdict**: PASS WITH ISSUES

The orchestration templates are well-structured with clear separation of concerns and good defensive patterns (e.g., Big Head's step-1 existence check, the Pantry's error handling section). Three P2 findings were identified: (1) bd close ordering (Finding 6) creating a failure window where a task is closed without a summary artifact; (2) the sampling formula contradiction (Finding 10) that could cause Pest Control to under-sample findings; and (3) the Queen-to-Big-Head SendMessage wiring (Finding 12) that may silently fail because the Queen is the team lead, not a team member, with a fallback that introduces race condition and deadlock risks. The P3 findings are mostly about adding explicit guards for missing/empty inputs.

**Note on file version discrepancy**: This review initially read `~/.claude/` versions of all 5 files, which turned out to be stale copies that predate this session's commits. The repo versions at `/Users/correy/projects/ant-farm/orchestration/templates/` contain significant additional content (e.g., big-head-skeleton.md: 71 lines vs 37, RULES.md: agent type table, SESSION_DIR variable, renamed checkpoints). Findings 1-11 were based on the stale versions. While the core logic reviewed (data file composition, checkpoint verification flow, skeleton steps) appears substantively similar between versions, Big Head should assess whether any findings need re-verification against the repo versions.
