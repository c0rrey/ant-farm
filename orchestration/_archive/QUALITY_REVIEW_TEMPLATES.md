# Quality Review Templates

Standard protocol for running quality reviews using agent teams after implementation work completes.

**Scope constraint**: Agent teams are for reviews ONLY. Implementation tasks use parallel subagents via the Task tool (no change to implementation workflow).

## Agent Teams Review Protocol

After all Dirt Pushers complete, the Queen launches **the Nitpickers** — four specialized reviewers running in parallel with bidirectional messaging. Reviewers produce **reports only** and do NOT file beads. Big Head consolidates all findings, deduplicates by root cause, and files beads.

### Model Assignments

- **Big Head (consolidation)**: `opus` — needs judgment for cross-report deduplication, root-cause grouping, and priority calibration
- **Nitpickers (all 4)**: `sonnet` — sufficient for code review and finding cataloging

### Why Agent Teams (Not Sequential)

- **Wall-clock time**: 4 parallel reviews vs 4 sequential = ~4x faster
- **Cross-pollination**: Reviewers can message each other about overlapping findings, reducing duplicate work
- **Unified dedup**: Big Head sees ALL findings before filing, so root-cause grouping is authoritative — no duplicate beads

### Team Setup

**Pre-spawn requirement**: Before creating the Nitpickers, run **Checkpoint A (Pre-Spawn Prompt Audit)** on all 4 review prompts. See "Verification Checkpoints" section below.

The Queen creates the Nitpickers with 4 tasks:

```markdown
Create a team with these 4 review tasks. All reviewers work in parallel.

Nitpickers produce REPORTS ONLY — do NOT file beads (`bd create`).
Big Head consolidates all reports, groups findings by root cause, and files beads.

Review scope: commits <first-commit> through <last-commit> (<N> commits total)
Files to review: <list of files changed in session>

1. Clarity Review (P3) — see prompt below
2. Edge Cases Review (P2) — see prompt below
3. Correctness Redux Review (P1-P2) — see prompt below
4. Excellence Review (P3) — see prompt below
```

### Messaging Guidelines

**Nitpickers SHOULD message when:**
- They find something that crosses into another reviewer's domain (e.g., clarity reviewer spots a potential edge case)
- They want to flag "I'm covering X, skip it" to avoid duplicate analysis
- They discover context that would help another reviewer (e.g., "this function is only called from one place")

**Nitpickers should NOT message:**
- Status updates ("I'm 50% done")
- General observations that don't help other reviewers
- Questions that should go to Big Head

## Review 1: Clarity Review (P3)

**Agent Type:** `code-reviewer`
**Model:** `sonnet`
**Priority:** P3 (polish, not blocking)

```markdown
Perform a CLARITY review of the completed work in this session.

Review scope: commits <first-commit> through <last-commit> (<N> commits total)

Focus areas:
1. **Code readability** - Are variable names clear? Is logic easy to follow?
2. **Documentation** - Are docstrings complete? Are comments helpful?
3. **Consistency** - Do changes follow project patterns and style?
4. **Naming** - Are functions, variables, and fields well-named?
5. **Structure** - Is code organized logically?

## Catalog Phase
Read all files in scope. For each issue, note the file, line, and what's wrong.
Group findings into preliminary root causes where possible.

## Report (MANDATORY)
Write your report to `.beads/agent-summaries/<epic-id>/review-reports/clarity-review-<timestamp>.md` using the format below. (The Queen provides the exact filename in your prompt.)
Do NOT file beads — Big Head handles all bead filing.

If you find something that looks like an edge case or correctness bug, message the
relevant Nitpicker so they can investigate in depth.

Review these files:
<list of files changed in session>
```

## Review 2: Edge Cases Review (P2)

**Agent Type:** `code-reviewer`
**Model:** `sonnet`
**Priority:** P2 (important, should fix soon)

```markdown
Perform an EDGE CASES review of the completed work in this session.

Review scope: commits <first-commit> through <last-commit> (<N> commits total)

Focus areas:
1. **Input validation** - What happens with malformed input? Missing fields? Invalid values?
2. **Error handling** - Are exceptions caught? Are error messages helpful?
3. **Boundary conditions** - Empty strings? None values? Zero-length lists? Max values?
4. **File operations** - What if files don't exist? Can't be read? Can't be written?
5. **Concurrency** - Race conditions? Thread safety? Lock contention?
6. **Platform differences** - Windows vs Unix? Path separators? Line endings?

## Catalog Phase
Read all files in scope. For each issue, note the file, line, trigger condition, and impact.
Group findings into preliminary root causes where possible.

## Report (MANDATORY)
Write your report to `.beads/agent-summaries/<epic-id>/review-reports/edge-cases-review-<timestamp>.md` using the format below. (The Queen provides the exact filename in your prompt.)
Do NOT file beads — Big Head handles all bead filing.

Pay special attention to:
- Functions that read/write files
- Functions that parse user input
- Functions with external dependencies
- Loops and iterations
- Error handling blocks

Review these files:
<list of files changed in session>
```

## Review 3: Correctness Redux Review (P1-P2)

**Agent Type:** `code-reviewer`
**Model:** `sonnet`
**Priority:** P1-P2 (critical, must fix before deploy)

```markdown
Perform a CORRECTNESS REDUX review of the completed work in this session.

Review scope: commits <first-commit> through <last-commit> (<N> commits total)

This is a second-pass correctness review focusing on logic and requirements.

Focus areas:
1. **Acceptance criteria verification** - Did each fix actually solve what was requested?
2. **Logic correctness** - Are there logical errors? Off-by-one errors? Incorrect assumptions?
3. **Data integrity** - Are all data transformations correct? No data loss?
4. **Regression risks** - Could these changes break existing functionality?
5. **Cross-file consistency** - Do changes in one file align with related files?
6. **Algorithm correctness** - Are calculations, sorts, filters correct?

## Catalog Phase
Read all files in scope. For each issue, note the file, line, expected vs actual behavior.
Group findings into preliminary root causes where possible.

## Report (MANDATORY)
Write your report to `.beads/agent-summaries/<epic-id>/review-reports/correctness-review-<timestamp>.md` using the format below. (The Queen provides the exact filename in your prompt.)
Do NOT file beads — Big Head handles all bead filing.

Review these files and their acceptance criteria:
<list of files and their original task requirements>

**IMPORTANT**: Run `bd show <task-id>` for each task in the commit range to retrieve
the original acceptance criteria. Do not rely solely on the orchestrator's prompt —
verify against the source of truth. For each finding, cite the specific acceptance
criterion that is violated or unmet.

For each completed task, verify:
- All acceptance criteria met
- Acceptance criteria source documented (which `bd show` output, which requirement)
- No unintended side effects
- Related files updated consistently
- Tests would pass (if tests exist)
```

## Review 4: Excellence Review (P3)

**Agent Type:** `code-reviewer`
**Model:** `sonnet`
**Priority:** P3 (nice-to-have, future work)

```markdown
Perform an EXCELLENCE review of the completed work in this session.

Review scope: commits <first-commit> through <last-commit> (<N> commits total)

This is the final quality gate focusing on best practices and opportunities.

Focus areas:
1. **Best practices** - Does code follow language/framework best practices?
2. **Performance** - Are there inefficiencies? Unnecessary operations? N+1 queries?
3. **Security** - Any vulnerabilities? Path traversal? XSS? Code injection?
4. **Maintainability** - Will future developers understand this easily?
5. **Architecture** - Does this fit the project's design principles?
6. **Scalability** - Will this perform well at 10x scale?
7. **Modern features** - Could we use newer language features for clarity?

## Catalog Phase
Read all files in scope. For each issue, note the file, line, improvement details.
Group findings into preliminary root causes where possible.

## Report (MANDATORY)
Write your report to `.beads/agent-summaries/<epic-id>/review-reports/excellence-review-<timestamp>.md` using the format below. (The Queen provides the exact filename in your prompt.)
Do NOT file beads — Big Head handles all bead filing.

Look for opportunities to:
- Reduce complexity (cyclomatic complexity, nesting depth)
- Add caching where appropriate
- Improve type safety
- Use modern language patterns
- Enhance security posture
- Add missing tests
- Improve error messages

Review these files:
<list of files changed in session>
```

## Nitpicker Report Format (All 4 Reviewers)

Every reviewer MUST write their report to `.beads/agent-summaries/<epic-id>/review-reports/<review-type>-review-<timestamp>.md` using this format. The Queen generates the timestamp once per review cycle and provides the exact output path in each reviewer's prompt.

```markdown
# Report: <review-type> Review

**Scope**: <list of files reviewed>
**Reviewer**: <review type + agent type>

## Findings Catalog

### Finding 1: <short title>
- **File(s)**: <file:line references>
- **Severity**: P1 / P2 / P3
- **Category**: <clarity|edge-case|correctness|excellence>
- **Description**: <what's wrong>
- **Suggested fix**: <how to fix>
- **Cross-reference**: <if related to another reviewer's domain, note it>

### Finding 2: <short title>
...

## Preliminary Groupings

Group findings that share a root cause:

### Group A: <root cause title>
- Finding 1, Finding 3 — same underlying issue
- **Suggested combined fix**: <one fix covering all>

### Group B: <root cause title>
- Finding 2 — standalone

## Summary Statistics
- Total findings: <N>
- By severity: P1: <N>, P2: <N>, P3: <N>
- Preliminary groups: <N>

## Cross-Review Messages

Log all messages sent to and received from other reviewers:

### Sent
- To <reviewer>: "<summary of message>" — Action: <what you asked them to do or look at>

### Received
- From <reviewer>: "<summary of message>" — Action taken: <what you did in response>

### Deferred Items
- "<finding title>" — Deferred to <reviewer> because <reason>

## Coverage Log

List every in-scope file with its review status. Files with no findings MUST still appear here — omission is not acceptable.

| File | Status | Evidence |
|------|--------|----------|
| <file1> | Findings: #1, #3 | N/A |
| <file2> | Reviewed — no issues | <N> functions, <M> lines examined |
| <file3> | Reviewed — no issues | <N> functions, <M> lines examined |

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

## Big Head Consolidation Step

**Model:** `opus`

After all 4 Nitpicker reports are complete, Big Head (orchestrator) consolidates:

### Step 0: Verify All Reports Exist (MANDATORY GATE)

Before reading any reports, verify all 4 expected files exist:

```bash
# Verify all 4 review types + consolidated exist for this epic
ls .beads/agent-summaries/<epic-id>/review-reports/clarity-review-*.md \
   .beads/agent-summaries/<epic-id>/review-reports/edge-cases-review-*.md \
   .beads/agent-summaries/<epic-id>/review-reports/correctness-review-*.md \
   .beads/agent-summaries/<epic-id>/review-reports/excellence-review-*.md
```

**All 4 files MUST exist.** If any file is missing:
1. Identify which reviewer failed to produce output
2. Check if the reviewer is still running, errored, or wrote to the wrong path
3. Do NOT proceed with consolidation until all 4 reports are present

### Step 1: Read All Reports

Read all 4 reports from `.beads/agent-summaries/<epic-id>/review-reports/` (the Queen provides exact filenames in the consolidation prompt):
- `clarity-review-<timestamp>.md`
- `edge-cases-review-<timestamp>.md`
- `correctness-review-<timestamp>.md`
- `excellence-review-<timestamp>.md`

### Step 2: Merge and Deduplicate

1. **Collect all findings** across all 4 reports into a single list
2. **Identify duplicates** — findings reported by multiple reviewers about the same issue
3. **Merge cross-referenced items** — where one reviewer flagged something for another's domain
4. **Group by root cause** — apply the root-cause grouping principle across ALL review types:
5. **Document merge rationale** — for EVERY merge (two or more findings combined into one root cause), state:
   - WHY these findings share a root cause (not just that they do)
   - What the common code path, pattern, or design flaw is
   - If merged findings span unrelated files or functions, provide extra justification

```markdown
## Root-Cause Grouping (Lead Consolidation)

For each group of related findings across all 4 reviews:
- **Root cause**: <what's systematically wrong>
- **Affected surfaces**:
  - file1.html:L10 — <specific instance> (from clarity review)
  - file2.html:L25 — <specific instance> (from edge-cases review)
  - file3.py:L100 — <specific instance> (from correctness review)
- **Combined priority**: <highest priority from any contributing finding>
- **Fix**: <one fix that covers all surfaces>
- **Merge rationale**: <why these specific findings share this root cause — must reference shared code path, pattern, or design flaw>
- **Acceptance criteria**: <how to verify across all surfaces>
```

### Step 3: File Beads

File ONE bead per root cause (not per finding, not per review):

```bash
bd create --type=bug --priority=<combined-priority> --title="<root cause title>"
# Then update with full description including all affected surfaces
bd label add <id> <primary-review-type>
```

### Step 4: Write Consolidated Summary

Write the consolidated summary to `.beads/agent-summaries/<epic-id>/review-reports/review-consolidated-<timestamp>.md`:

```markdown
# Consolidated Review Summary

**Scope**: <list of all files reviewed>
**Reviews completed**: Clarity, Edge Cases, Correctness, Excellence
**Reports verified**: clarity-review.md ✓, edge-cases-review.md ✓, correctness-review.md ✓, excellence-review.md ✓
**Total raw findings**: <N across all reviews>
**Root causes identified**: <N after dedup>
**Beads filed**: <N>

## Root Causes Filed

| Bead ID | Priority | Title | Contributing Reviews | Surfaces |
|---------|----------|-------|---------------------|----------|
| <id> | P<N> | <title> | clarity, edge-cases | <N> files |
| ... | ... | ... | ... | ... |

## Deduplication Log

Findings merged:
- <Finding X from clarity> + <Finding Y from edge-cases> → Root Cause A
- ...

## Priority Breakdown
- P1 (blocking): <N> beads
- P2 (important): <N> beads
- P3 (polish): <N> beads

## Verdict
<PASS / PASS WITH ISSUES / NEEDS WORK>
<overall quality assessment>
```

## Verification Checkpoints

All checkpoint verifications are executed by **Pest Control**, a dedicated verification subagent that cross-checks review work against ground truth. Pest Control produces verification reports with PASS/PARTIAL/FAIL verdicts and stores artifacts in `.beads/agent-summaries/<epic-id>/verification/pest-control/` using timestamped filenames to prevent overwriting. This ensures complete audit history for all checkpoints across all review sessions.

Three checkpoints cross-check agent claims against ground truth. See `ORCHESTRATOR_DISCIPLINE.md` "Verification Checkpoint System" for Checkpoint A (implementation) and Checkpoint B (implementation) templates.

### Checkpoint A: Pre-Spawn Prompt Audit (The Nitpickers)

**When**: After composing all 4 review prompts, BEFORE creating the team
**Model**: `haiku`
**Agent type**: `code-reviewer`

```markdown
**Pest Control verification - Checkpoint A (Pre-Spawn Nitpickers Audit)**

You are **Pest Control**, the verification subagent. Your role is to audit the Nitpickers prompts before spawn.

Audit the following 4 Nitpicker prompts for completeness and consistency.
Do NOT execute the prompts — only verify their contents.

<prompt_clarity>
{paste clarity review prompt}
</prompt_clarity>

<prompt_edge_cases>
{paste edge cases review prompt}
</prompt_edge_cases>

<prompt_correctness>
{paste correctness review prompt}
</prompt_correctness>

<prompt_excellence>
{paste excellence review prompt}
</prompt_excellence>

## Verify each item (PASS or FAIL with evidence):

0. **File list matches git diff**: Run `git diff --name-only <first-commit>..<last-commit>` and verify the prompt file list matches exactly. Every file in the diff must appear in the prompt, and every file in the prompt must appear in the diff. If there is a mismatch, FAIL with the list of missing/extra files.
1. **Same file list**: All 4 prompts contain the same set of files to review (not different subsets)
2. **Same commit range**: All 4 prompts reference the same commit range
3. **Correct focus areas**: Each prompt has focus areas specific to its review type:
   - Clarity: readability, naming, documentation, consistency, structure
   - Edge Cases: input validation, error handling, boundaries, file ops, concurrency
   - Correctness: acceptance criteria, logic errors, data integrity, regressions, cross-file
   - Excellence: best practices, performance, security, maintainability, architecture
   (Flag if focus areas are copy-pasted identically across prompts)
4. **No bead filing instruction**: Each prompt contains "Do NOT file beads" or equivalent
5. **Report format reference**: Each prompt specifies the output path `.beads/agent-summaries/<epic-id>/review-reports/<type>-review-<timestamp>.md`
6. **Messaging guidelines**: Each prompt includes guidance on when to message teammates

## Verdict
- **PASS** — All 7 checks pass for all 4 prompts
- **FAIL: <list each failing check, specifying which prompt(s)>**

Write your verification report to:
`.beads/agent-summaries/<epic-id>/verification/pest-control/pest-control-{epic-id}-checkpoint-a-review-{timestamp}.md`

Where:
- epic-id: 3-char epic suffix (e.g., `74g` from `hs_website-74g`), or `multi` for multi-epic reviews
- timestamp: YYYYMMDD-HHMMSS format
```

**On FAIL**: Fix the specific gaps in the prompts, then re-run. Do NOT create the team until PASS.

### Checkpoint B: Substance Verification (Nitpickers)

**When**: After each Nitpicker completes its report
**Model**: `sonnet`
**Agent type**: `code-reviewer`

```markdown
**Pest Control verification - Checkpoint B (Nitpicker Substance Verification)**

You are **Pest Control**, the verification subagent. Your role is to cross-check Nitpicker findings against actual code.

Verify the substance of a Nitpicker's report by cross-checking findings against actual code.

**Report path**: `.beads/agent-summaries/<epic-id>/review-reports/{review-type}-review-<timestamp>.md`
**Review type**: {clarity|edge-cases|correctness|excellence}

Read the report first, then perform these 4 checks:

## Check 1: Code Pointer Verification
Pick `min(5, ceil(N/3))` random findings from the report (where N = total findings; minimum 3, or all findings if fewer than 3). Always include the highest-severity finding and at least one finding from each severity tier present in the report.
For each finding:
- Read the actual code at the referenced file:line
- Verify the finding description matches what's actually there
- Report: "Finding N claims {file}:L{line} has {description}. Actual code at L{line}: `{actual code}`. CONFIRMED / REFUTED — {explanation}"

## Check 2: Scope Coverage
Compare files listed in the report's "Scope" against both the Findings Catalog AND the Coverage Log.
- Every scoped file MUST appear in either the Findings Catalog (with specific findings) or the Coverage Log (with "Reviewed — no issues" and evidence of review depth)
- If any scoped file appears in NEITHER section, FAIL this check — the file was silently skipped
- For files marked "Reviewed — no issues," verify the evidence is specific (function count, line count) not generic ("looks fine")
- List any files that were skipped without acknowledgment

## Check 3: Finding Specificity
For each finding, check that it is actionable:
- Flag findings that use weasel language: "could be improved", "might cause issues", "may not be ideal", "consider refactoring"
- Every finding needs: what's wrong, where (file:line), and how to fix it
- List any findings that fail the specificity bar

## Check 4: Process Compliance
Search the report for `bd create`, `bd update`, `bd close`, or bead ID patterns (e.g., `hs_website-xxx`).
- Nitpickers must NOT file beads
- If any bead-filing commands or IDs are found, FAIL this check
- If unauthorized bead filing is detected, this is a FAIL (not just a flag). The remediation step is: delete the unauthorized bead (`bd close <id> --reason="unauthorized filing during review"`) and document the violation in the verification report.

## Verdict
- **PASS** — All 4 checks confirm substance and compliance
- **PARTIAL: <list checks that failed with evidence>**
- **FAIL: <list all failures with evidence>**

Write your verification report to:
`.beads/agent-summaries/<epic-id>/verification/pest-control/pest-control-{task-id}-checkpoint-b-review-{timestamp}.md`

Where:
- task-id: Nitpicker task ID (e.g., `review-clarity`, `review-edge`)
- timestamp: YYYYMMDD-HHMMSS format
```

**On PARTIAL or FAIL**: Resume the original Nitpicker with specific gaps. Re-verify after fix. Second failure → flag to user.

### Checkpoint C: Consolidation Audit

**When**: After Big Head consolidation (after all 4 reports merged and beads filed)
**Model**: `haiku` (mechanical counting + record-checking)
**Agent type**: `code-reviewer`

**Checkpoint C must PASS before presenting results to the user.**

```markdown
**Pest Control verification - Checkpoint C (Consolidation Audit)**

You are **Pest Control**, the verification subagent. Your role is to audit Big Head's consolidated report for integrity.

Audit the review consolidation for completeness, accuracy, and traceability.

**Consolidated summary**: `.beads/agent-summaries/<epic-id>/review-reports/review-consolidated-<timestamp>.md`
**Individual reports**: (The Queen provides exact filenames in the consolidation prompt.)
- `.beads/agent-summaries/<epic-id>/review-reports/clarity-review-<timestamp>.md`
- `.beads/agent-summaries/<epic-id>/review-reports/edge-cases-review-<timestamp>.md`
- `.beads/agent-summaries/<epic-id>/review-reports/correctness-review-<timestamp>.md`
- `.beads/agent-summaries/<epic-id>/review-reports/excellence-review-<timestamp>.md`

Read all 5 documents, then perform these 8 checks:

## Check 0: Report Existence Verification
Verify exactly 4 report files exist at their expected paths (the Queen provides exact filenames):
- `.beads/agent-summaries/<epic-id>/review-reports/clarity-review-<timestamp>.md`
- `.beads/agent-summaries/<epic-id>/review-reports/edge-cases-review-<timestamp>.md`
- `.beads/agent-summaries/<epic-id>/review-reports/correctness-review-<timestamp>.md`
- `.beads/agent-summaries/<epic-id>/review-reports/excellence-review-<timestamp>.md`
If any file is missing, FAIL immediately — consolidation should not have proceeded.

## Check 1: Finding Count Reconciliation
Count total findings across all 4 individual reports.
Count total findings referenced in the consolidated summary.
Every finding must be accounted for — either standalone, merged into a group, or explicitly marked as duplicate in the deduplication log.
Report the math: "Clarity: N, Edge Cases: N, Correctness: N, Excellence: N = TOTAL total. Consolidated references TOTAL findings across N root causes. N findings merged as duplicates. RECONCILED / NOT RECONCILED — {list orphaned findings}"

## Check 2: Bead Existence Check
For each bead ID in the consolidated summary, run `bd show <id>`.
Verify it exists and has status=open.
Report any IDs that don't resolve or have unexpected status.

## Check 3: Bead Quality Check
For each filed bead, verify its description contains:
- Root cause explanation (not just symptom)
- At least one file:line reference
- Acceptance criteria or verification steps
- Suggested fix
Flag any beads missing these elements. List which elements are missing.

## Check 4: Priority Calibration
Read P1 bead descriptions. Do they describe genuinely blocking issues (crashes, data loss, security vulnerabilities, broken functionality)?
Or are they style preferences or minor improvements mislabeled as P1?
Flag any suspicious priority assignments with reasoning.

## Check 5: Traceability Matrix
Build a matrix: Finding → Root Cause Group → Bead ID.
For every finding from every report, trace it to either:
- A bead ID (via root cause group), OR
- An explicit entry in the dedup log marking it as merged/duplicate
Report any orphaned findings (not traceable to a bead or dedup entry).

## Check 6: Deduplication Correctness
For each merged group of 3+ findings:
- Verify the merged findings share at least one common file or function
- If findings span unrelated code areas with no shared pattern, flag for review
- Read the merge rationale in the dedup log — is it coherent? Does it reference a real shared code path or design pattern?

Spot-check 2 merged groups by reading the actual code at each finding's location:
- Do the findings genuinely share a root cause, or were unrelated issues incorrectly merged?
- Report: "Group '<title>' merges N findings across files {list}. Common pattern: {yes/no — explanation}. CONFIRMED / SUSPECT"

## Check 7: Bead Provenance Audit
Run `bd list --status=open` and cross-reference against the consolidated summary's "Beads filed" list.
- Every open bead should trace back to the consolidation step
- Flag any beads that were filed during the review phase (not consolidation) — these are unauthorized
- Verify bead count matches the consolidated summary's count

## Verdict
- **PASS** — All 8 checks confirm consolidation integrity
- **PARTIAL: <list checks that failed with evidence>**
- **FAIL: <list all failures with evidence>**

Write your verification report to:
`.beads/agent-summaries/<epic-id>/verification/pest-control/pest-control-{epic-id}-consolidation-checkpoint-c-{timestamp}.md`

Where:
- epic-id: 3-char epic suffix (e.g., `74g` from `hs_website-74g`), or `multi` for multi-epic consolidations
- timestamp: YYYYMMDD-HHMMSS format

**CRITICAL FIX**: The timestamp ensures each Checkpoint C audit is preserved. Previous versions used static filename `consolidation-audit.md` which caused overwrites on repeated consolidations. Now each audit has a unique timestamped filename, preserving complete audit history.
```

**On PASS**: Proceed to present results to user.

**On PARTIAL or FAIL**:
1. Fix consolidation gaps (re-read reports, file missing beads, update dedup log)
2. Re-run Checkpoint C
3. If it fails a second time, present to user with the verification report attached so they can see what was flagged

---

## After Consolidation Complete

**Prerequisite**: Checkpoint C (Consolidation Audit) must PASS before proceeding.

1. **Present summary to user:**
   - Total issues by root cause
   - Priority breakdown (P1: X, P2: Y, P3: Z)
   - Deduplication stats (X raw findings → Y root causes)
   - Recommendation: Continue with fixes? Or push and address later?

2. **If continuing with fixes:**
   - Group new beads by file (same pattern as original work)
   - Spawn Dirt Pushers to address issues (via Task tool, NOT agent teams)
   - May need to run reviews again on fixes

3. **If pushing without fixes:**
   - Document in CHANGELOG that X issues were filed for future work
   - Ensure no P1 blockers remain
   - Proceed with documentation update and push

## Review Quality Metrics

Good reviews should:
- Find 3-10 root-cause issues per review type (NOT 30+ per-occurrence issues)
- Categorize issues correctly (clarity vs correctness)
- Provide specific line numbers and examples
- Suggest concrete fixes, not just identify problems
- Avoid false positives (issues that aren't really issues)
- Consider project context and constraints

If a review finds 0 issues:
- May indicate review was too superficial
- Or work quality was genuinely excellent
- Have user spot-check to calibrate
