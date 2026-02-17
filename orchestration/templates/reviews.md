<!-- Reader: the Pantry (review mode). The Queen does NOT read this file. -->
# Quality Review Protocol

## Transition Gate Checklist

**When**: After all Dirt Pushers from Step 3 complete, BEFORE launching the Nitpickers.

Verify all 4 criteria before proceeding to team launch:

1. **All Dirt Pushers completed** — none stuck or errored (check the Queen's state file)
2. **Checkpoint B PASS for every agent** — verify artifact exists at `.beads/agent-summaries/<epic>/verification/pest-control/pest-control-<task-id>-checkpoint-b-*.md` with PASS verdict
3. **The Queen's state file updated** — all completions tracked, checkpoint results recorded
4. **Git log shows expected commits** — run `git log --oneline -N` (where N = number of agents) to confirm commits exist

**If any check fails**: Do NOT launch reviews. Investigate stuck agents, re-run failed checkpoints, or escalate to user.

**If all checks pass**: Proceed to Agent Teams Protocol below.

### Pre-Spawn Directory Setup

Before composing review prompts or running Checkpoint A, create the review-reports directory:

```bash
mkdir -p .beads/agent-summaries/<epic-id>/review-reports/
```

This ensures all 4 reviewers can write reports immediately without each needing to create the directory independently.

---

## Agent Teams Protocol

After the transition gate passes, the Queen launches **the Nitpickers** using **TeamCreate** (NOT the Task tool) — four specialized reviewers plus **Big Head** (the consolidator), all as members of the same team. Reviewers produce **reports only** and do NOT file beads. Big Head consolidates all findings, deduplicates by root cause, and files beads.

**CRITICAL**: Reviews MUST use Agent Teams (TeamCreate + SendMessage), NOT plain Task tool subagents. The team structure enables cross-pollination between reviewers. **Big Head MUST be spawned as a team member** (not a separate Task agent) so it can receive messages from reviewers and coordinate within the team.

### Why Agent Teams (Not Sequential)

- **Wall-clock time**: 4 parallel reviews vs 4 sequential = ~4x faster
- **Cross-pollination**: Reviewers can message each other about overlapping findings, reducing duplicate work
- **Unified dedup**: Lead sees ALL findings before filing, so root-cause grouping is authoritative — no duplicate beads

### Model Assignments

- **Big Head (consolidation)**: `opus` — needs judgment for cross-report deduplication, root-cause grouping, and priority calibration
- **Nitpickers (all 4)**: `sonnet` — sufficient for code review and finding cataloging

### Team Setup

**Pre-spawn requirement**: Before creating the Nitpickers, run **Checkpoint A (Pre-Spawn Prompt Audit)** on all 4 review prompts. See `templates/checkpoints.md`.

The Queen creates the Nitpicker team with **5 members** (4 reviewers + Big Head):

```markdown
Create a team with these 5 members. The 4 reviewers work in parallel.
Big Head waits for all 4 reports, then consolidates.

Nitpickers produce REPORTS ONLY — do NOT file beads (`bd create`).
Big Head consolidates all reports, groups findings by root cause, and files beads.

Review scope: commits <first-commit> through <last-commit> (<N> commits total)
Files to review: <list of files changed in session>

1. Clarity Review (P3) — see prompt below
2. Edge Cases Review (P2) — see prompt below
3. Correctness Redux Review (P1-P2) — see prompt below
4. Excellence Review (P3) — see prompt below
5. Big Head (consolidation, opus) — see prompt from big-head-skeleton.md
```

**Big Head is spawned as a team member using the big-head-skeleton.md template**, not as a separate Task agent. The Queen fills in the skeleton placeholders and uses the result as the teammate's prompt.

### Messaging Guidelines

**Nitpickers SHOULD message when:**
- They find something that crosses into another reviewer's domain (e.g., clarity reviewer spots a potential edge case)
- They want to flag "I'm covering X, skip it" to avoid duplicate analysis
- They discover context that would help another reviewer (e.g., "this function is only called from one place")

**Nitpickers should NOT message:**
- Status updates ("I'm 50% done")
- General observations that don't help other reviewers
- Questions that should go to Big Head

## Review 1: Clarity (P3)

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

## Review 2: Edge Cases (P2)

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

## Review 3: Correctness Redux (P1-P2)

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

## Review 4: Excellence (P3)

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

## Big Head Consolidation Protocol

**Model:** `opus`

After all 4 Nitpicker reports are complete, Big Head (a member of the same team) consolidates:

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
## Root-Cause Grouping (Big Head Consolidation)

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

## The Queen's Checklists

### Nitpicker Checklist (verify before launching team)

Before launching the review agent team, confirm:
- [ ] All 4 Nitpicker prompts include review scope (list of all files to review)
- [ ] Each Nitpicker has focus areas specific to their review type
- [ ] Catalog phase instructions included (find all, group preliminarily)
- [ ] Report format instructions included (use standard Nitpicker report format)
- [ ] Each prompt says "Do NOT file beads — Big Head handles all bead filing"
- [ ] Messaging guidelines included (what to share, what not to share)
- [ ] Reports write to `.beads/agent-summaries/<epic-id>/review-reports/<review-type>-review-<timestamp>.md`

### Big Head Consolidation Checklist (after all Nitpickers finish)

Before filing beads, confirm Big Head has:
- [ ] Read all 4 Nitpicker reports
- [ ] Merged duplicate findings across reviews
- [ ] Grouped all findings by root cause (not per-occurrence)
- [ ] Filed ONE bead per root cause with all affected surfaces listed
- [ ] Written consolidated summary to `.beads/agent-summaries/<epic-id>/review-reports/review-consolidated-<timestamp>.md`

## After Consolidation Complete

**Prerequisite**: Checkpoint C (Consolidation Audit) must PASS before proceeding.

### Step 1: Present Findings to User

Show the consolidated summary with:
- Total issues by priority (P1: X, P2: Y, P3: Z)
- Root causes identified
- Deduplication stats (N raw findings → M root causes)

### Step 2: Triage P1/P2 Issues

**If P1 or P2 issues found:**

1. **Ask user**: "Reviews found X P1 and Y P2 issues. Should we fix them now, or push and address later?"

2. **If user chooses "fix now"**:

   a. **Test-first workflow** (TDD approach):
      - For each P1/P2 bead, create a test-writing task FIRST
      - Group test tasks by file (same conflict analysis as original implementation)
      - Spawn Dirt Pushers (via Task tool, NOT agent teams) to write failing tests
      - Test requirements: Must cover edge cases and failure scenarios, not just happy path
      - Verify tests fail with expected error messages
      - Run `bd close` on test-writing tasks after verification

   b. **Implementation workflow**:
      - For each P1/P2 bead, create a fix implementation task
      - Group fix tasks by file (use reference/dependency-analysis.md for conflict analysis)
      - Spawn Dirt Pushers to implement fixes (same 6-step process as original work)
      - Agents must run tests and verify they now PASS
      - Run Checkpoint B on each fix agent
      - Run `bd close` on fix tasks after Checkpoint B passes

   c. **Re-run reviews** (optional):
      - If fixes touched >3 files or made significant changes, consider re-running Step 3b (the Nitpickers)
      - Otherwise, rely on test verification + Checkpoint B

3. **If user chooses "push and address later"**:
   - P1/P2 beads already filed during consolidation — they stay open
   - Document in CHANGELOG: "Known issues filed for future work: <list bead IDs>"
   - Proceed to Step 3 (Handle P3 Issues)

### Step 3: Handle P3 Issues

**Create "Future Work" epic if needed**:
```bash
# Check if future-work epic exists
bd list --status=open | grep -i "future work" || \
bd epic create --title="Future Work" --description="Low-priority polish and improvements from review sessions"
```

**File P3 beads under the epic**:
- All P3 beads from consolidation should be children of the future-work epic
- Use `bd epic add-child <future-work-epic-id> <p3-bead-id>` for each P3 issue
- These can be addressed in future sessions
- No immediate action required — they're queued for later

### Step 4: Continue to Documentation (RULES.md Step 4)

Proceed with CHANGELOG, README, CLAUDE.md updates.

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
