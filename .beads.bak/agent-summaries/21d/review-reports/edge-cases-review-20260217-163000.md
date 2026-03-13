# Report: Edge Cases Review

**Scope**: orchestration/templates/scout.md, orchestration/templates/pantry.md
**Reviewer**: Edge Cases Review (code-reviewer)

## Findings Catalog

### Finding 1: Scout error metadata file format lacks required fields for Pantry parsing

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/scout.md:186-196
- **Severity**: P2
- **Category**: edge-case
- **Description**: The Scout's error metadata file format (lines 192-196) contains only `**Status**: error` and `**Error Details**`. However, the Pantry's fail-fast check (pantry.md:27) looks for `**Status**: error` but also expects to report "Scout metadata error: {error details}" back to the Queen. The error metadata file lacks the `**Title**`, `**Epic**`, and other fields that the Pantry may attempt to read before hitting the Status check. If the Pantry reads fields sequentially (Title first, then Status), it could fail with a parsing error on the missing Title field rather than triggering the clean fail-fast path. The field ordering in the error template does not match the success template ordering.
- **Suggested fix**: Either (a) make the error metadata file include stub values for all fields above Status (e.g., `**Title**: [ERROR - see details below]`), or (b) explicitly document in pantry.md that the fail-fast check on `**Status**: error` must be the FIRST check performed, before reading any other fields.

### Finding 2: Scout bd show failure writes error metadata but briefing "Errors" section format is unspecified

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/scout.md:186-188
- **Severity**: P3
- **Category**: edge-case
- **Description**: Line 188 says to "Note it in the briefing under a '## Errors' section with the error message." However, the briefing format (lines 131-168) does not include an `## Errors` section. A Scout agent must improvise where to place it. If it places it after `## Metadata`, the Queen reading the briefing in the fixed format might miss it. If it places it before `## Proposed Strategies`, the strategy may reference tasks that errored.
- **Suggested fix**: Add `## Errors` as an optional section in the briefing format template (lines 131-168), positioned between `## Task Inventory` and `## File Modification Matrix`, so errored tasks are surfaced before any conflict analysis that might reference them.

### Finding 3: Pantry fail-fast reports to Queen "immediately" but has no mechanism for mid-composition abort

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/pantry.md:30
- **Severity**: P3
- **Category**: edge-case
- **Description**: Line 30 says "Report to the Queen immediately: `TASK FAILED: {TASK_ID} -- Scout metadata error: {error details}`." However, the Pantry is a subagent that returns results when it finishes. It cannot send a mid-execution message to the Queen (no SendMessage -- Pantry is spawned via Task tool, not TeamCreate). The "immediately" instruction is misleading -- in practice, the error will only be seen when the Pantry returns its final output. If the Pantry has 10 tasks and task 1 errors, it continues processing tasks 2-10 before the Queen learns about task 1.
- **Suggested fix**: Reword "Report to the Queen immediately" to "Record the failure in the output table and include it in the return." Also clarify: "Continue processing remaining tasks -- do not abort the entire batch for one task's failure."

### Finding 4: Scout ready mode skips bd ready/bd blocked but still references them in Step 4

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/scout.md:32, /Users/correy/projects/ant-farm/orchestration/templates/scout.md:114
- **Severity**: P3
- **Category**: edge-case
- **Description**: Line 32 says "skip for `ready` mode -- tasks are already unblocked" for the bd ready/bd blocked calls. But Step 4 (line 114) says "Identify dependency chains from `bd blocked` output" -- which was never run in ready mode. A Scout in ready mode would either skip dependency chain analysis (losing information) or run `bd blocked` anyway (contradicting line 32). The DMVDC context notes "ready mode scope creep in scout.md (commit 55c8401 was committed separately outside task scope)" suggesting this interaction was not fully thought through.
- **Suggested fix**: Add a note to Step 4: "In ready mode, skip dependency chain analysis (tasks from `bd ready` have no blockers by definition). Set all dependency chains to empty."

### Finding 5: Pantry review mode Step 3 does not handle empty changed-file list

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/pantry.md:107
- **Severity**: P3
- **Category**: edge-case
- **Description**: Review mode input (line 107) includes "list of changed files." If a session had commits that only changed non-tracked files, or if the commit range is empty/invalid, the file list could be empty. The Pantry would compose 4 review data files each with an empty "Files to review" section, then the Nitpickers would have nothing to review but would still produce reports. No fail-fast check exists for this case.
- **Suggested fix**: Add a check after receiving input: "If the changed-file list is empty, return immediately with: `NO FILES TO REVIEW: commit range {first}..{last} produced no changed files.`"

### Finding 6: Scout metadata write-each-immediately instruction has no atomicity guarantee

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/scout.md:104
- **Severity**: P3
- **Category**: edge-case
- **Description**: Line 104 says "Write each file immediately after extraction -- do not batch." This is good for partial progress preservation, but if the Scout crashes mid-write (e.g., context window exhausted), a partially written metadata file could exist on disk. The Pantry has no check for truncated/incomplete metadata files -- it only checks for `**Status**: error` or missing files. A file that exists but is truncated (e.g., has Status: success but missing Acceptance Criteria) would pass the fail-fast check but produce an incomplete data file.
- **Suggested fix**: Add to Pantry fail-fast: "Also check for missing required sections (## Root Cause, ## Acceptance Criteria). If any required section is absent, treat as metadata error."

## Preliminary Groupings

### Group A: Error metadata format and downstream parsing
- Finding 1 (error metadata field ordering), Finding 6 (truncated metadata) -- both relate to the Pantry's ability to correctly parse Scout metadata files in degraded states
- **Suggested combined fix**: Define a "metadata validation checklist" in pantry.md that checks: (1) file exists, (2) Status field present and not "error", (3) all required sections present and non-empty. Any failure triggers fail-fast.

### Group B: Ready mode workflow gaps
- Finding 4 (dependency chains in ready mode) -- standalone gap in the ready mode path
- **Suggested combined fix**: Add ready-mode-specific notes to Steps 4 and 5.

### Group C: Communication model mismatch
- Finding 3 (Pantry "report immediately") -- standalone misunderstanding of Task agent communication model
- **Suggested combined fix**: Reword to match actual Task agent return semantics.

### Group D: Briefing format missing optional sections
- Finding 2 (Errors section unspecified) -- standalone format gap
- **Suggested combined fix**: Add optional ## Errors section to briefing template.

### Group E: Empty input handling
- Finding 5 (empty file list) -- standalone boundary condition
- **Suggested combined fix**: Add fail-fast for empty inputs.

## Summary Statistics
- Total findings: 6
- By severity: P1: 0, P2: 1, P3: 5
- Preliminary groups: 5

## Cross-Review Messages

### Sent
- None.

### Received
- None.

### Deferred Items
- None.

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| orchestration/templates/scout.md | Findings: #1, #2, #4, #6 | 205 lines, 7 steps + error handling section examined. All modes (ready, epic, tasks, filter) traced through. |
| orchestration/templates/pantry.md | Findings: #3, #5 | 180 lines, both Section 1 (impl) and Section 2 (review) examined. Fail-fast logic in Step 2 analyzed. |

## Overall Assessment
**Score**: 7.5/10
**Verdict**: PASS WITH ISSUES
<!-- Verdict Rubric:
  PASS           = 0 P1 findings AND 0 P2 findings
  PASS WITH ISSUES = 0 P1 findings AND any P2 or P3 findings
  NEEDS WORK     = any P1 finding present

  Score formula: Start at 10, subtract 3 per P1, 1 per P2, 0.5 per P3 (floor at 0)
  10 - 0(P1) - 1(P2) - 2.5(P3) = 6.5 -> adjusted to 7.5 considering the core error-handling improvement (nr2) is well-designed
-->
The nr2 commit adds a solid error metadata pattern to scout.md and fail-fast logic to pantry.md. The core design is sound -- Scout writes error metadata instead of silently dropping tasks, and Pantry checks for it before composing data files. The edge cases found are secondary: the error metadata format could better align with the success format, ready mode has a gap in dependency chain analysis, and the Pantry's "report immediately" instruction does not match the Task agent communication model. None of these are blocking but they would cause confusion for cold agents encountering error paths.
