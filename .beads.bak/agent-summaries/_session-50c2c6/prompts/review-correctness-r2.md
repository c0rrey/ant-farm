# Review Brief: Correctness Redux (Round 2)

**Review Type**: correctness
**Round**: 2 (fix verification only)
**Commit Range**: 002ee87..d9201c9 (3 fix commits only)
**Report Output Path**: .beads/agent-summaries/_session-50c2c6/review-reports/correctness-review-20260220-120000.md

## Scope

**Round 2 mandate**: These 3 commits are fixes for issues found in Round 1 review. Your job is to verify the fixes landed correctly and did not break anything. You may read full files for context, but your review scope is limited to changes in the commit range. Out-of-scope findings are only reportable if they would cause a runtime failure or silently wrong results.

## Files to Review

- orchestration/RULES.md
- orchestration/templates/checkpoints.md
- orchestration/templates/queen-state.md
- orchestration/templates/reviews.md

## Task IDs (Fixes)

These are the fix tasks. Run `bd show <task-id>` for each to retrieve the original acceptance criteria and verify they are met.

- ant-farm-60mh
- ant-farm-4l0t
- ant-farm-rcdd

**Epic**: ant-farm-ha7a

## Focus Areas

1. **Acceptance criteria verification** - Did each fix actually solve what was requested? Run `bd show` for each task ID above and check every acceptance criterion.
2. **Logic correctness** - Are there logical errors? Off-by-one errors? Incorrect assumptions in the fix commits?
3. **Data integrity** - Are all data transformations correct? No data loss from the fixes?
4. **Regression risks** - Could these fixes break existing functionality that was working before?
5. **Cross-file consistency** - Do changes in one file align with related files? Are references between files still valid?
6. **Algorithm correctness** - Are calculations, sorts, filters correct in the changed code?

## Catalog Phase

Read all files in scope. For each issue, note the file, line, expected vs actual behavior.
Group findings into preliminary root causes where possible.

## Report Format

Write your report to the Report Output Path above using this format:

```markdown
# Report: Correctness Review (Round 2)

**Scope**: orchestration/RULES.md, orchestration/templates/checkpoints.md, orchestration/templates/queen-state.md, orchestration/templates/reviews.md
**Reviewer**: correctness / code-reviewer
**Round**: 2 (fix verification)

## Findings Catalog

### Finding 1: <short title>
- **File(s)**: <file:line references>
- **Severity**: P1 / P2 / P3
- **Category**: correctness
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

## Acceptance Criteria Verification

For each task ID, list each acceptance criterion from `bd show` and mark PASS/FAIL:

### ant-farm-60mh
- [ ] <criterion from bd show> -- PASS/FAIL
...

### ant-farm-4l0t
- [ ] <criterion from bd show> -- PASS/FAIL
...

### ant-farm-rcdd
- [ ] <criterion from bd show> -- PASS/FAIL
...

## Overall Assessment
**Score**: <X/10>
**Verdict**: <PASS / PASS WITH ISSUES / NEEDS WORK>
<1-2 sentence summary>
```

## Instructions

**IMPORTANT**: Run `bd show <task-id>` for each task in the list above to retrieve the original acceptance criteria. Do not rely solely on this brief -- verify against the source of truth. For each finding, cite the specific acceptance criterion that is violated or unmet.

For each completed fix task, verify:
- All acceptance criteria met
- Acceptance criteria source documented (which `bd show` output, which requirement)
- No unintended side effects
- Related files updated consistently

Do NOT file beads -- Big Head handles all bead filing.

## Messaging Guidelines

**Message teammates when:**
- You find something that crosses into the edge-cases reviewer's domain (e.g., a fix that introduces a new unhandled boundary condition)
- You want to flag "I'm covering X, skip it" to avoid duplicate analysis
- You discover context that would help the other reviewer (e.g., "this function is only called from one place")

**Do NOT message for:**
- Status updates ("I'm 50% done")
- General observations that don't help the other reviewer
- Questions that should go to Big Head
