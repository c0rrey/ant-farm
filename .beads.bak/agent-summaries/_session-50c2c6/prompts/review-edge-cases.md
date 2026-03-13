# Review Brief: Edge Cases

**Review Type**: edge-cases
**Priority**: P2 (important, should fix soon)
**Review Round**: 1
**Report Output Path**: .beads/agent-summaries/_session-50c2c6/review-reports/edge-cases-review-20260219-120000.md

## Scope

**Commit range**: ea25412..c1a7157 (11 commits)
**Epic**: ant-farm-ha7a

**Files to review**:
- orchestration/RULES.md
- orchestration/templates/big-head-skeleton.md
- orchestration/templates/checkpoints.md
- orchestration/templates/nitpicker-skeleton.md
- orchestration/templates/pantry.md
- orchestration/templates/queen-state.md
- orchestration/templates/reviews.md

## Focus Areas

1. **Input validation** - What happens with malformed input? Missing fields? Invalid values?
2. **Error handling** - Are exceptions caught? Are error messages helpful?
3. **Boundary conditions** - Empty strings? None values? Zero-length lists? Max values?
4. **File operations** - What if files don't exist? Can't be read? Can't be written?
5. **Concurrency** - Race conditions? Thread safety? Lock contention?
6. **Platform differences** - Windows vs Unix? Path separators? Line endings?

## Instructions

Perform an EDGE CASES review of the completed work in this session.

### Catalog Phase
Read all files in scope. For each issue, note the file, line, trigger condition, and impact.
Group findings into preliminary root causes where possible.

### Report Phase (MANDATORY)
Write your report to `.beads/agent-summaries/_session-50c2c6/review-reports/edge-cases-review-20260219-120000.md` using the format specified below.

Do NOT file beads -- Big Head handles all bead filing.

Pay special attention to:
- Functions that read/write files
- Functions that parse user input
- Functions with external dependencies
- Loops and iterations
- Error handling blocks

### Messaging Guidelines

**DO message teammates when:**
- You find something that crosses into another reviewer's domain (e.g., you spot a clarity issue or correctness bug)
- You want to flag "I'm covering X, skip it" to avoid duplicate analysis
- You discover context that would help another reviewer (e.g., "this function is only called from one place")

**Do NOT message teammates for:**
- Status updates ("I'm 50% done")
- General observations that don't help other reviewers
- Questions that should go to Big Head

## Report Format

Your report MUST use this exact structure:

```markdown
# Report: Edge Cases Review

**Scope**: <list of files reviewed>
**Reviewer**: edge-cases / code-reviewer

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
<!-- Verdict Rubric:
  PASS           = 0 P1 findings AND 0 P2 findings
  PASS WITH ISSUES = 0 P1 findings AND any P2 or P3 findings
  NEEDS WORK     = any P1 finding present

  Score formula: Start at 10, subtract 3 per P1, 1 per P2, 0.5 per P3 (floor at 0)
-->
<1-2 sentence summary>
```
