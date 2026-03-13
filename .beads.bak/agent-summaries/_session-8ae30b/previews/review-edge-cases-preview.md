Perform a edge-cases review of the completed work.

Step 0: Read your full review brief from .beads/agent-summaries/_session-8ae30b/prompts/review-edge-cases.md
(Contains: commit range, files to review, focus areas, detailed instructions.)

Your workflow:
1. Read ALL files listed in the brief
2. Catalog findings with file:line references and severity (P1/P2/P3)
3. Group findings into preliminary root causes
4. Write your report to .beads/agent-summaries/_session-8ae30b/review-reports/edge-cases-review-20260220-150515.md
5. Message relevant Nitpickers if you find cross-domain issues

Your report MUST include these sections (see brief for full format):
- **Findings Catalog**: each finding with file:line, severity, category, description, suggested fix
- **Preliminary Groupings**: findings grouped by root cause
- **Summary Statistics**: total findings, breakdown by severity
- **Cross-Review Messages**: log of messages sent/received with other reviewers
- **Coverage Log**: every scoped file listed, even those with no issues found
- **Overall Assessment**: score out of 10 + verdict (PASS / PASS WITH ISSUES / NEEDS WORK)

Do NOT file beads (`bd create`) -- Big Head handles all bead filing.

---

# Review Brief: Edge Cases Review

**Review Type**: edge-cases
**Priority**: P2 (important, should fix soon)
**Review Round**: 1

## Scope

**Commit range**: 541aac2~1..HEAD (3 commits)
**Epic(s)**: ant-farm-7hh

**Files to review** (all files changed in this session):
- AGENTS.md
- agents/pantry-review.md
- orchestration/RULES.md
- orchestration/templates/pantry.md
- orchestration/templates/reviews.md

## Report Output

**Write your report to**: .beads/agent-summaries/_session-8ae30b/review-reports/edge-cases-review-20260220-150515.md

## Focus Areas

1. **Input validation** - What happens with malformed input? Missing fields? Invalid values?
2. **Error handling** - Are exceptions caught? Are error messages helpful?
3. **Boundary conditions** - Empty strings? None values? Zero-length lists? Max values?
4. **File operations** - What if files don't exist? Can't be read? Can't be written?
5. **Concurrency** - Race conditions? Thread safety? Lock contention?
6. **Platform differences** - Windows vs Unix? Path separators? Line endings?

## Catalog Phase

Read all files in scope. For each issue, note the file, line, trigger condition, and impact.
Group findings into preliminary root causes where possible.

## Instructions

Do NOT file beads -- Big Head handles all bead filing.

Pay special attention to:
- Functions that read/write files
- Functions that parse user input
- Functions with external dependencies
- Loops and iterations
- Error handling blocks

### Messaging Guidelines

**You SHOULD message other Nitpickers when:**
- You find something that crosses into another reviewer's domain (e.g., you spot a clarity issue or correctness bug)
- You want to flag "I'm covering X, skip it" to avoid duplicate analysis
- You discover context that would help another reviewer (e.g., "this function is only called from one place")

**You should NOT message:**
- Status updates ("I'm 50% done")
- General observations that don't help other reviewers
- Questions that should go to Big Head

## Report Format

Write your report using the following format:

```markdown
# Report: Edge Cases Review

**Scope**: AGENTS.md, agents/pantry-review.md, orchestration/RULES.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
**Reviewer**: Edge Cases Review (code-reviewer)

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
| AGENTS.md | ... | ... |
| agents/pantry-review.md | ... | ... |
| orchestration/RULES.md | ... | ... |
| orchestration/templates/pantry.md | ... | ... |
| orchestration/templates/reviews.md | ... | ... |

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
