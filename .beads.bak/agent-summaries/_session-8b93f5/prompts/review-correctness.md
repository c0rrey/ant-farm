# Review Brief: Correctness Redux

**Review Type**: correctness
**Priority**: P1-P2 (critical, must fix before deploy)
**Report Output Path**: .beads/agent-summaries/_session-8b93f5/review-reports/correctness-review-20260220-120000.md

## Commit Range

`89c2ec0~1..HEAD`

## Files to Review

- README.md
- orchestration/GLOSSARY.md
- orchestration/PLACEHOLDER_CONVENTIONS.md
- orchestration/RULES.md
- orchestration/templates/SESSION_PLAN_TEMPLATE.md
- orchestration/templates/big-head-skeleton.md
- orchestration/templates/checkpoints.md
- orchestration/templates/dirt-pusher-skeleton.md
- orchestration/templates/implementation.md
- orchestration/templates/nitpicker-skeleton.md
- orchestration/templates/pantry.md
- orchestration/templates/reviews.md
- orchestration/templates/scout.md

## Focus Areas

1. **Acceptance criteria verification** - Did each fix actually solve what was requested?
2. **Logic correctness** - Are there logical errors? Off-by-one errors? Incorrect assumptions?
3. **Data integrity** - Are all data transformations correct? No data loss?
4. **Regression risks** - Could these changes break existing functionality?
5. **Cross-file consistency** - Do changes in one file align with related files?
6. **Algorithm correctness** - Are calculations, sorts, filters correct?

## Catalog Phase

Read all files in scope. For each issue, note the file, line, expected vs actual behavior.
Group findings into preliminary root causes where possible.

## Report Instructions

Write your report to `.beads/agent-summaries/_session-8b93f5/review-reports/correctness-review-20260220-120000.md` using the Nitpicker Report Format below.

Do NOT file beads -- Big Head handles all bead filing.

## Task IDs for Acceptance Criteria Verification

Run `bd show <task-id>` for each of these task IDs to retrieve the original acceptance criteria. Do not rely solely on this prompt -- verify against the source of truth.

- ant-farm-wi0
- ant-farm-jxf
- ant-farm-4vg
- ant-farm-s57
- ant-farm-k32
- ant-farm-8jg
- ant-farm-81y
- ant-farm-x0m
- ant-farm-cn0

For each completed task, verify:
- All acceptance criteria met
- Acceptance criteria source documented (which `bd show` output, which requirement)
- No unintended side effects
- Related files updated consistently
- Tests would pass (if tests exist)

For each finding, cite the specific acceptance criterion that is violated or unmet.

## Messaging Guidelines

**DO message teammates when:**
- You find something that crosses into another reviewer's domain (e.g., you spot a clarity issue or edge case)
- You want to flag "I'm covering X, skip it" to avoid duplicate analysis
- You discover context that would help another reviewer (e.g., "this function is only called from one place")

**Do NOT message teammates for:**
- Status updates ("I'm 50% done")
- General observations that don't help other reviewers
- Questions that should go to Big Head

## Nitpicker Report Format

```markdown
# Report: Correctness Redux Review

**Scope**: <list of files reviewed>
**Reviewer**: Correctness Redux Review / code-reviewer

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
| <file3> | Reviewed -- no issues | <N> functions, <M> lines examined |

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
