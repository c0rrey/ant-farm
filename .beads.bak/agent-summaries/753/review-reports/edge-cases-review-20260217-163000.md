# Report: Edge Cases Review

**Scope**: orchestration/templates/reviews.md, agents/big-head.md
**Reviewer**: Edge Cases Review (code-reviewer)

## Findings Catalog

### Finding 1: Big Head Step 0 verification uses wildcard glob that could match stale reports from prior review cycles

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/reviews.md:341-344
- **Severity**: P2
- **Category**: edge-case
- **Description**: The Step 0 verification (lines 341-344) uses `ls .beads/agent-summaries/<epic-id>/review-reports/clarity-review-*.md` with a wildcard on the timestamp. If a prior review cycle left reports in the same directory (e.g., from a failed session that was retried), the glob would match both old and new reports, and `ls` would succeed even if the current cycle's report is missing. Big Head would proceed with stale data. The DMVDC finding for z6r notes "Summary misattributed ~/.claude/ sync as agent work" -- this kind of attribution error could be exacerbated by reading stale reports.
- **Suggested fix**: Use the specific timestamp provided in the consolidation data file instead of a wildcard: `ls .beads/agent-summaries/<epic-id>/review-reports/clarity-review-<timestamp>.md`. The timestamp is known at composition time and should be used for exact matching.

### Finding 2: Verification Pipeline Design Rationale does not specify behavior when one layer passes and the other fails

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/reviews.md:326-333
- **Severity**: P3
- **Category**: edge-case
- **Description**: The new Design Rationale section (lines 326-333) explains that Big Head Step 0 and CCB Check 0 are intentionally redundant. However, it does not specify what happens if Big Head Step 0 passes (all reports present) but CCB Check 0 later fails (a report was corrupted or deleted between the two checks). This temporal gap is a race condition: another agent could modify the filesystem between Big Head's check and CCB's check. The section says "different agents, different timing, different failure modes" but does not define the recovery path when they disagree.
- **Suggested fix**: Add a note: "If Big Head Step 0 passes but CCB Check 0 fails, the CCB verdict takes precedence (it is the later, independent audit). The Queen should investigate the discrepancy before accepting the consolidated output."

### Finding 3: Read Confirmation table in consolidated summary format has no verification of content correctness

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/templates/reviews.md:410-421
- **Severity**: P3
- **Category**: edge-case
- **Description**: The new Read Confirmation table (lines 410-421) asks Big Head to confirm it read all 4 reports with finding counts. However, nothing prevents Big Head from copying the finding count from a report's Summary Statistics section without actually processing all findings. The table confirms "I read the file" but not "I processed all N findings from it." If Big Head reads a report with 12 findings but only processes 8 (due to context window pressure or oversight), the Read Confirmation would still show "12 findings" because that number comes from the report header, not from Big Head's own count.
- **Suggested fix**: Add a validation step: "The 'Finding Count' column must be independently counted by Big Head (count the ## Finding N headings), not copied from the report's Summary Statistics. If the independent count differs from the report's stated count, note the discrepancy."

### Finding 4: big-head.md agent definition includes Edit tool but consolidation workflow never edits files

- **File(s)**: /Users/correy/projects/ant-farm/agents/big-head.md:4
- **Severity**: P3
- **Category**: edge-case
- **Description**: The tools list on line 4 includes `Edit`, but the Big Head consolidation workflow (read reports, merge, write consolidated summary, file beads) never requires editing existing files. All outputs are new file writes. Including Edit gives Big Head the capability to modify reviewer reports or other files, which could introduce unintended changes. This is a minor over-permissioning concern.
- **Suggested fix**: Remove `Edit` from the tools list unless there is a specific use case requiring it.

### Finding 5: big-head.md bd create for filing issues has no error handling for bd CLI failures

- **File(s)**: /Users/correy/projects/ant-farm/agents/big-head.md:21
- **Severity**: P3
- **Category**: edge-case
- **Description**: Line 21 says "File issues via `bd create`" but provides no guidance on what to do if `bd create` fails (e.g., bd CLI not installed, issues.jsonl locked, disk full). A Big Head agent that encounters a bd failure mid-consolidation would have some findings filed and others not, with no recovery path. The consolidated summary would list "Beads filed: N" but some may not actually exist.
- **Suggested fix**: Add: "If `bd create` fails, record the failure in the consolidation report under a ## Filing Errors section. Include the full finding details so the Queen can file manually. Do not abort consolidation for individual filing failures."

## Preliminary Groupings

### Group A: Verification completeness gaps
- Finding 1 (wildcard matching stale reports), Finding 2 (disagreement between verification layers), Finding 3 (read confirmation not independently verified) -- all relate to the verification pipeline having gaps where it claims to verify something but the check is not airtight
- **Suggested combined fix**: Tighten verification: use exact timestamps instead of wildcards, define precedence when layers disagree, and require independent counting for read confirmation.

### Group B: Tool and error handling gaps in Big Head
- Finding 4 (Edit tool over-permissioning), Finding 5 (bd create failure handling) -- both relate to Big Head's operational definition
- **Suggested combined fix**: Trim tool permissions and add error handling guidance for bd operations.

## Summary Statistics
- Total findings: 5
- By severity: P1: 0, P2: 1, P3: 4
- Preliminary groups: 2

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
| orchestration/templates/reviews.md | Findings: #1, #2, #3 | 545 lines, all sections examined. Focus on new Design Rationale section (325-333), Read Confirmation table (410-421), and Step 0 verification (335-351). Transition Gate, Agent Teams Protocol, all 4 review type definitions, Nitpicker Report Format, Big Head Consolidation Protocol, and Queen Checklists all reviewed. |
| agents/big-head.md | Findings: #4, #5 | 31 lines, YAML frontmatter and full agent definition examined. All 6 consolidation steps and 3 "Watch for" items reviewed. |

## Overall Assessment
**Score**: 7.5/10
**Verdict**: PASS WITH ISSUES
<!-- Verdict Rubric:
  PASS           = 0 P1 findings AND 0 P2 findings
  PASS WITH ISSUES = 0 P1 findings AND any P2 or P3 findings
  NEEDS WORK     = any P1 finding present

  Score formula: Start at 10, subtract 3 per P1, 1 per P2, 0.5 per P3 (floor at 0)
  10 - 0(P1) - 1(P2) - 2(P3) = 7.0 -> adjusted to 7.5 considering the z6r additions are well-structured
-->
The z6r commit adds a valuable Design Rationale section and Read Confirmation table to the verification pipeline. The core improvement is well-designed -- explicitly documenting why both Big Head Step 0 and CCB Check 0 exist, and adding a confirmation mechanism for report reading. The edge cases found are mostly about tightening the verification: wildcard matching could pick up stale reports, the two-layer verification has no defined precedence when they disagree, and the Read Confirmation can be gamed by copying numbers rather than independently counting. The Big Head agent definition has minor tool over-permissioning and missing error handling for bd operations.
