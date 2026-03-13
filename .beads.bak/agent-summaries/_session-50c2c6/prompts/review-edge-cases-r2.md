# Review Brief: Edge Cases (Round 2)

**Review Type**: edge-cases
**Round**: 2 (fix verification only)
**Commit Range**: 002ee87..d9201c9 (3 fix commits only)
**Report Output Path**: .beads/agent-summaries/_session-50c2c6/review-reports/edge-cases-review-20260220-120000.md

## Scope

**Round 2 mandate**: These 3 commits are fixes for issues found in Round 1 review. Your job is to verify the fixes did not introduce new edge-case vulnerabilities and that the changed code handles boundary conditions correctly. You may read full files for context, but your review scope is limited to changes in the commit range. Out-of-scope findings are only reportable if they would cause a runtime failure or silently wrong results.

## Files to Review

- orchestration/RULES.md
- orchestration/templates/checkpoints.md
- orchestration/templates/queen-state.md
- orchestration/templates/reviews.md

## Task IDs (Fixes)

- ant-farm-60mh
- ant-farm-4l0t
- ant-farm-rcdd

**Epic**: ant-farm-ha7a

## Focus Areas

1. **Input validation** - What happens with malformed input? Missing fields? Invalid values in the changed sections?
2. **Error handling** - Are exceptions caught in the fix code? Are error messages helpful? Did fixes remove or weaken existing error handling?
3. **Boundary conditions** - Empty strings? None values? Zero-length lists? Max values in the changed code?
4. **File operations** - What if files referenced in the changed code don't exist? Can't be read? Can't be written?
5. **Concurrency** - Race conditions? Thread safety? Lock contention introduced or exposed by fixes?
6. **Platform differences** - Windows vs Unix? Path separators? Line endings in the changed code?

## Catalog Phase

Read all files in scope. For each issue, note the file, line, trigger condition, and impact.
Group findings into preliminary root causes where possible.

## Report Format

Write your report to the Report Output Path above using this format:

```markdown
# Report: Edge Cases Review (Round 2)

**Scope**: orchestration/RULES.md, orchestration/templates/checkpoints.md, orchestration/templates/queen-state.md, orchestration/templates/reviews.md
**Reviewer**: edge-cases / code-reviewer
**Round**: 2 (fix verification)

## Findings Catalog

### Finding 1: <short title>
- **File(s)**: <file:line references>
- **Severity**: P1 / P2 / P3
- **Category**: edge-case
- **Description**: <what's wrong>
- **Suggested fix**: <how to fix>
- **Cross-reference**: <if related to another reviewer's domain, note it>

### Finding 2: <short title>
...

## Preliminary Groupings

Group findings that share a root cause:

### Group A: <root cause title>
- Finding 1, Finding 3 -- same underlying issue
- **Suggested combined fix**: <one fix covering all>

### Group B: <root cause title>
- Finding 2 -- standalone

## Summary Statistics
- Total findings: <N>
- By severity: P1: <N>, P2: <N>, P3: <N>
- Preliminary groups: <N>

## Cross-Review Messages

Log all messages sent to and received from other reviewers:

### Sent
- To <reviewer>: "<summary of message>" -- Action: <what you asked them to do or look at>

### Received
- From <reviewer>: "<summary of message>" -- Action taken: <what you did in response>

### Deferred Items
- "<finding title>" -- Deferred to <reviewer> because <reason>

## Coverage Log

List every in-scope file with its review status. Files with no findings MUST still appear here -- omission is not acceptable.

| File | Status | Evidence |
|------|--------|----------|
| <file1> | Findings: #1, #3 | N/A |
| <file2> | Reviewed -- no issues | <N> functions, <M> lines examined |

## Overall Assessment
**Score**: <X/10>
**Verdict**: <PASS / PASS WITH ISSUES / NEEDS WORK>
<1-2 sentence summary>
```

## Instructions

Pay special attention to:
- Functions that read/write files in the changed code
- Functions that parse user input or template placeholders
- Functions with external dependencies
- Loops and iterations in the changed sections
- Error handling blocks that were added or modified by the fixes

Do NOT file beads -- Big Head handles all bead filing.

## Messaging Guidelines

**Message teammates when:**
- You find something that crosses into the correctness reviewer's domain (e.g., an edge case that reveals a logic error)
- You want to flag "I'm covering X, skip it" to avoid duplicate analysis
- You discover context that would help the other reviewer (e.g., "this template is only used in one workflow")

**Do NOT message for:**
- Status updates ("I'm 50% done")
- General observations that don't help the other reviewer
- Questions that should go to Big Head
