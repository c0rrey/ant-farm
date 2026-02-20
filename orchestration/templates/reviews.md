<!-- Reader: the Pantry (review mode). The Queen does NOT read this file. -->
# Quality Review Protocol

## Transition Gate Checklist

**When**: After all Dirt Pushers from Step 3 complete across ALL epics, BEFORE launching the Nitpickers.

Verify all 4 criteria before proceeding to team launch. These checks span ALL epics worked in this session:

1. **All Dirt Pushers completed across ALL epics** — none stuck or errored (check the Queen's state file for every epic)
2. **Dirt Moved vs Dirt Claimed (DMVDC) PASS for every agent** — verify artifact exists at `<session-dir>/pc/pc-<task-id>-dmvdc-*.md` with PASS verdict
3. **The Queen's state file updated** — all completions tracked, checkpoint results recorded for all epics
4. **Git log shows expected commits** — run `git log --oneline -N` (where N = total number of agents across all epics) to confirm commits exist

**If any check fails**: Do NOT launch reviews. Investigate stuck agents, re-run failed checkpoints, or escalate to user.

**If all checks pass**: Proceed to Agent Teams Protocol below.

### Pre-Spawn Directory Setup

The Queen handles directory creation in RULES.md Step 3b:

```bash
mkdir -p ${SESSION_DIR}/review-reports
```

This creates the session-scoped directory for review reports. All 4 reviewers write to `${SESSION_DIR}/review-reports/`. Verification artifacts (`pc/`) are already created at Step 0.

---

## Agent Teams Protocol

After the transition gate passes, the Queen launches **the Nitpickers** using **TeamCreate** (NOT the Task tool) — four specialized reviewers plus **Big Head** (the consolidator) plus **Pest Control** (checkpoint validator), all as members of the same team. Reviewers produce **reports only** and do NOT file beads. Big Head consolidates all findings, deduplicates by root cause, and files beads.

**CRITICAL**: Reviews MUST use Agent Teams (TeamCreate + SendMessage), NOT plain Task tool subagents. The team structure enables cross-pollination between reviewers. **Big Head MUST be spawned as a team member** (not a separate Task agent) so it can receive messages from reviewers and coordinate within the team.

### Why Agent Teams (Not Sequential)

- **Wall-clock time**: 4 parallel reviews vs 4 sequential = ~4x faster
- **Cross-pollination**: Reviewers can message each other about overlapping findings, reducing duplicate work
- **Unified dedup**: Lead sees ALL findings before filing, so root-cause grouping is authoritative — no duplicate beads

### Model Assignments

- **Nitpickers (all 4)**: `sonnet` — sufficient for code review and finding cataloging

(Big Head model is specified in the Big Head Consolidation Protocol section below.)

### Team Setup

**Pre-spawn requirement**: Before creating the Nitpickers, run **CCO** on all review prompts. See `templates/checkpoints.md`.

**Round 1**: The Queen creates the Nitpicker team with **6 members** (4 reviewers + Big Head + Pest Control):

~~~markdown
Create a team with these 6 members. The 4 reviewers work in parallel.
Big Head waits for all 4 reports, then consolidates.
Pest Control is a team member so Big Head can SendMessage to it directly for checkpoint validation.

Nitpickers produce REPORTS ONLY — do NOT file beads (`bd create`).
Big Head consolidates all reports, groups findings by root cause, and files beads.

Review scope: commits <first-commit> through <last-commit> (<N> commits total, across epics: <epic-list>)
Files to review: <deduplicated list of ALL files changed across all epics>
Task IDs for acceptance criteria: <list of all task IDs worked this session>

1. Clarity Review (P3) — see prompt below
2. Edge Cases Review (P2) — see prompt below
3. Correctness Redux Review (P1-P2) — see prompt below
4. Excellence Review (P3) — see prompt below
5. Big Head (consolidation) — see prompt from big-head-skeleton.md; model specified in Big Head Consolidation Protocol section
6. Pest Control (checkpoint validator) — receives consolidated report path from Big Head via SendMessage; runs DMVDC and CCB checkpoints and replies with verdict
~~~

**Round 2+**: The Queen creates the Nitpicker team with **4 members** (2 reviewers + Big Head + Pest Control):

~~~markdown
Create a team with these 4 members. The 2 reviewers work in parallel.
Big Head waits for both reports, then consolidates.
Pest Control is a team member so Big Head can SendMessage to it directly for checkpoint validation.

Nitpickers produce REPORTS ONLY — do NOT file beads (`bd create`).
Big Head consolidates all reports, groups findings by root cause, and files beads.
Big Head auto-files P3 findings to "Future Work" epic (no user prompt needed).

Review scope: fix commits only — <first-fix-commit> through <HEAD>
Files to review: <files changed in fix commits only>
Task IDs for acceptance criteria: <list of fix task IDs>

1. Correctness Redux Review (P1-P2) — see prompt below
2. Edge Cases Review (P2) — see prompt below
3. Big Head (consolidation) — see prompt from big-head-skeleton.md
4. Pest Control (checkpoint validator) — same role as round 1
~~~

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

## Round-Aware Review Protocol

The review pipeline supports multiple rounds. The Queen passes `Review round: <N>` to the Pantry. Round number determines reviewer composition, scope, and P3 handling.

### Round 1 (Full Review)

- **Reviewers**: 4 (Clarity, Edge Cases, Correctness, Excellence)
- **Scope**: All session commits (`<first-session-commit>..<HEAD>`)
- **Findings**: All severities reported and presented to user
- **Team size**: 6 (4 reviewers + Big Head + Pest Control)

This is the existing protocol — no changes to round 1 behavior.

### Round 2+ (Fix Verification)

- **Reviewers**: 2 (Correctness, Edge Cases only — Clarity and Excellence are dropped)
- **Scope**: Fix commits only (`<first-fix-commit>..<HEAD>`)
- **Team size**: 4 (2 reviewers + Big Head + Pest Control)
- **In-scope findings**: All severities reported
- **Out-of-scope findings**: Only reportable if they would cause:
  - **Runtime failure**: an agent, tool call, or workflow step would crash or error
  - **Silently wrong results**: an agent would succeed but produce incorrect output (e.g., stale cross-references pointing the Queen to the wrong section)
- **Not reportable out-of-scope**: naming conventions, style preferences, documentation gaps, improvement opportunities, hypothetical edge cases requiring unusual conditions
- **P3 handling**: Big Head auto-files P3s to "Future Work" epic (no user prompt)

### Termination Rule

The review loop terminates when a round produces **zero P1 or P2 findings**. At termination:

1. Big Head auto-files any P3 findings to "Future Work" epic (round 2+ only)
2. In round 1, P3s are filed via the existing "Handle P3 Issues" flow in the Queen's Step 3c/Step 4 below
3. Queen proceeds directly to RULES.md Step 4 (documentation)
4. No user prompt needed — the loop simply ends

There is no hard cap on rounds. The reduced scope + reduced reviewers + P3 auto-filing make convergence fast.

### Round 2+ Reviewer Instructions

Correctness and Edge Cases reviewers receive this additional scope constraint in round 2+. The Pantry includes this text in each reviewer's brief:

> **Fix verification scope**: Review commits `<fix-start>..<HEAD>` only. You may read full files for context, but your mandate is: did these fixes land correctly and not break anything?
>
> **Out-of-scope findings**: If you notice something outside the fix commits that would cause a runtime failure, incorrect agent behavior, or silently wrong results (e.g., stale cross-references pointing to wrong sections), report it. Do NOT report naming conventions, style preferences, documentation gaps, or improvement opportunities outside the fix scope.

The `[OUT-OF-SCOPE]` tag is for labeling only — it helps Big Head and human readers distinguish fix-scope findings from incidental discoveries. Big Head treats all findings identically for dedup and root-cause grouping regardless of tag.

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
Write your report to `<session-dir>/review-reports/clarity-review-<timestamp>.md` using the format below. (The Queen provides the exact filename in your prompt.)
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
Write your report to `<session-dir>/review-reports/edge-cases-review-<timestamp>.md` using the format below. (The Queen provides the exact filename in your prompt.)
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
Write your report to `<session-dir>/review-reports/correctness-review-<timestamp>.md` using the format below. (The Queen provides the exact filename in your prompt.)
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
Write your report to `<session-dir>/review-reports/excellence-review-<timestamp>.md` using the format below. (The Queen provides the exact filename in your prompt.)
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

Every reviewer MUST write their report to `<session-dir>/review-reports/<review-type>-review-<timestamp>.md` using this format. The Queen generates the timestamp once per review cycle and provides the exact output path in each reviewer's prompt.

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

### Verification Pipeline Design Rationale

The Big Head consolidation process includes two distinct verification layers that work together:

1. **Big Head Step 0 (Prerequisite Gate)**: A mandatory check performed by Big Head BEFORE reading any reports. This gate ensures all 4 expected reports exist before consolidation logic begins. This prevents wasted effort on reading partial report sets or proceeding with missing data.

2. **Pest Control CCB Check 0 (Independent Audit)**: A separate, independent check performed AFTER Big Head consolidation is complete (see checkpoints.md). This audit verifies the same 4 reports but runs in a different context — it confirms that consolidation did not proceed in a degraded state (e.g., no reviewer failures during the review phase).

**Why both?** The prerequisite gate (Big Head Step 0) is a blocker for Big Head's own work. The audit check (CCB Check 0) is an independent verification that consolidation ran on complete input — a safety check from a different agent with fresh eyes. The redundancy is intentional: different agents, different timing, different failure modes.

### Step 0: Verify All Reports Exist (MANDATORY GATE)

Before reading any reports, verify all 4 expected files exist:

```bash
# Verify all 4 review types exist in the session review-reports directory
ls <session-dir>/review-reports/clarity-review-*.md \
   <session-dir>/review-reports/edge-cases-review-*.md \
   <session-dir>/review-reports/correctness-review-*.md \
   <session-dir>/review-reports/excellence-review-*.md
```

**All 4 files MUST exist.** If any file is missing:
1. Identify which reviewer failed to produce output
2. Check if the reviewer is still running, errored, or wrote to the wrong path
3. Do NOT proceed with consolidation until all 4 reports are present

### Step 0a: Remediation Path for Missing Reports (TIMEOUT + ERROR RETURN)

> **Authoritative source**: This section is the authoritative protocol for missing-report handling. The big-head-skeleton.md step 1 defers to this brief. If any apparent conflict exists between the skeleton and this brief, follow this brief.

If any report file is missing after the initial check, do NOT wait indefinitely. Instead:

**Timeout specification:** Wait a maximum of 30 seconds for all 4 reports to appear.
- Check once at T=0
- If all 4 reports exist, proceed to Step 1
- If any reports are missing, enter the polling loop below

**Polling loop (if files missing):**
```bash
# IMPORTANT: This entire block must execute in a single Bash invocation.
# Shell state (variables) does not persist across separate Bash tool calls.

# Poll up to 30 seconds total for missing reports
TIMEOUT=30
ELAPSED=0
POLL_INTERVAL=2
TIMED_OUT=1

while [ $ELAPSED -lt $TIMEOUT ]; do
  # Check each report type individually with [ -f ] to avoid wc -l count fragility.
  # head -1 ensures re-runs with multiple matching files don't break the check.
  FOUND_CLARITY=$(ls <session-dir>/review-reports/clarity-review-*.md 2>/dev/null | head -1)
  FOUND_EDGE=$(ls <session-dir>/review-reports/edge-cases-review-*.md 2>/dev/null | head -1)
  FOUND_CORRECTNESS=$(ls <session-dir>/review-reports/correctness-review-*.md 2>/dev/null | head -1)
  FOUND_EXCELLENCE=$(ls <session-dir>/review-reports/excellence-review-*.md 2>/dev/null | head -1)

  if [ -f "$FOUND_CLARITY" ] && [ -f "$FOUND_EDGE" ] && [ -f "$FOUND_CORRECTNESS" ] && [ -f "$FOUND_EXCELLENCE" ]; then
    # All 4 reports now present, proceed
    TIMED_OUT=0
    break
  fi
  sleep $POLL_INTERVAL
  ELAPSED=$((ELAPSED + POLL_INTERVAL))
done

if [ $TIMED_OUT -eq 1 ]; then
  # Timeout reached — fall through to the error return below
  echo "TIMEOUT: Not all 4 reports arrived within ${TIMEOUT}s"
fi
```

**Error return (if timeout exceeded):**

If timeout is reached and any reports are still missing, IMMEDIATELY return an error to the Queen:

```markdown
# Big Head Consolidation - BLOCKED: Missing Nitpicker Reports

**Status**: FAILED (timeout after 30 seconds)
**Timestamp**: <current ISO 8601 timestamp>

## Missing Reports

The following expected Nitpicker report files were not found:
- Clarity review report (clarity-review-*.md) — MISSING
- Edge cases review report (edge-cases-review-*.md) — MISSING [or: FOUND at <path>]
- Correctness review report (correctness-review-*.md) — MISSING [or: FOUND at <path>]
- Excellence review report (excellence-review-*.md) — MISSING [or: FOUND at <path>]

## Remediation

Big Head cannot proceed with consolidation without all 4 reports present. The prerequisite gate (Step 0) FAILED.

**Action required from Queen:**
1. Check review agent logs for errors or crashes
2. Verify all 4 Nitpicker team members completed their reviews
3. Confirm reports were written to: `<session-dir>/review-reports/`
4. Once all 4 reports are confirmed present, re-spawn Big Head consolidation

**Re-spawn instruction:**
~~~
Spawn Big Head again with all 4 report paths provided in the consolidation prompt.
~~~

**Do not proceed** with partial or missing review data.
```

Once the error is returned:
- Return the error message and STOP (do not continue to Steps 1-4)
- The Queen receives this error and must decide: retry with fresh Nitpicker spawn, or abort session

### Step 1: Read All Reports

Read all 4 reports from `<session-dir>/review-reports/` (the Queen provides exact filenames in the consolidation prompt):
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

### Step 3: Write Consolidated Summary

Write the consolidated summary to `<session-dir>/review-reports/review-consolidated-<timestamp>.md`:

```markdown
# Consolidated Review Summary

**Scope**: <list of all files reviewed>
**Reviews completed**: Clarity, Edge Cases, Correctness, Excellence
**Reports verified**: clarity-review.md ✓, edge-cases-review.md ✓, correctness-review.md ✓, excellence-review.md ✓
**Total raw findings**: <N across all reviews>
**Root causes identified**: <N after dedup>
**Beads filed**: <N>

## Read Confirmation

**All 4 reports read and processed by Big Head consolidation:**

| Report Type | File | Status | Finding Count |
|-------------|------|--------|----------------|
| Clarity | clarity-review-<timestamp>.md | ✓ Read | <N> findings |
| Edge Cases | edge-cases-review-<timestamp>.md | ✓ Read | <N> findings |
| Correctness | correctness-review-<timestamp>.md | ✓ Read | <N> findings |
| Excellence | excellence-review-<timestamp>.md | ✓ Read | <N> findings |

**Total findings from all reports**: <N>

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

### Step 4: Checkpoint Gate — Await Pest Control Validation Before Filing Beads

**Do NOT file any beads yet.** After writing the consolidated summary (Step 3), notify Pest Control and wait for its verdict before calling `bd create`.

**Notification to Pest Control (SendMessage):**
```
SendMessage(
  to="pest-control",
  message="Consolidated report ready. Path: <session-dir>/review-reports/review-consolidated-<timestamp>.md. Please run DMVDC and CCB checkpoints and reply with PASS or FAIL + specifics."
)
```

**Wait for Pest Control reply (timeout: 60 seconds). Then act on verdict:**

**Timeout and retry protocol:**
- After sending the SendMessage, wait up to 60 seconds for Pest Control's reply.
- If no response arrives within 60 seconds, send one retry message to Pest Control:
  ```
  SendMessage(
    to="pest-control",
    message="Retry request: Consolidated report ready at {CONSOLIDATED_OUTPUT_PATH}. Please run DMVDC and CCB checkpoints and reply with PASS or FAIL + specifics. (First message sent 60s ago — no reply received.)"
  )
  ```
- Wait an additional 60 seconds after the retry.
- If still no response after the retry window, **escalate to the Queen immediately**:
  ```
  Big Head checkpoint escalation to Queen:
  - Pest Control verdict: UNAVAILABLE (no response after 2 attempts, 120s total)
  - Consolidated report path: {CONSOLIDATED_OUTPUT_PATH}
  - Action required: PC checkpoint could not be completed. User must decide: re-spawn Pest Control
    manually, or accept consolidated findings without checkpoint validation.
  ```
  Do NOT file any beads when escalating due to Pest Control timeout.

- **PASS**: File ONE bead per root cause. See bead filing instructions below.
- **FAIL**: Big Head MUST escalate to the Queen with specifics. File beads ONLY for findings that passed. Do NOT file beads for flagged findings. Use this escalation format:

```
Big Head checkpoint escalation to Queen:
- Pest Control verdict: FAIL
- Findings that failed validation: <list with reasons per finding>
- Findings that passed: <list>
- Beads filed for validated findings: <ids or "none">
- Action required: User decides whether to drop, adjust, or re-review failed findings.
```

**Bead filing (validated findings only):**

File ONE bead per root cause (not per finding, not per review).

**Important**: Beads filed during session review are standalone. Do NOT assign them to a specific epic via `bd dep add --type parent-child`. They represent session-wide findings, not epic-specific work.

```bash
bd create --type=bug --priority=<combined-priority> --title="<root cause title>"
# Then update with full description including all affected surfaces
bd label add <id> <primary-review-type>
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
- [ ] Reports write to `<session-dir>/review-reports/<review-type>-review-<timestamp>.md`
- [ ] Team has 6 members: 4 Nitpickers + Big Head + Pest Control (Pest Control must be a team member so Big Head can SendMessage to it for checkpoint validation)

### Big Head Consolidation Checklist (after all Nitpickers finish)

Before filing beads, confirm Big Head has:
- [ ] Read all 4 Nitpicker reports
- [ ] Merged duplicate findings across reviews
- [ ] Grouped all findings by root cause (not per-occurrence)
- [ ] Written consolidated summary to `<session-dir>/review-reports/review-consolidated-<timestamp>.md`
- [ ] Sent consolidated report path to Pest Control via SendMessage
- [ ] Received Pest Control verdict (PASS or FAIL + specifics)
- [ ] On PASS: filed ONE bead per root cause with all affected surfaces listed
- [ ] On FAIL: escalated failed findings to Queen; filed beads only for validated findings

## After Consolidation Complete

**Prerequisite**: Colony Census Bureau (CCB) must PASS before proceeding.

Big Head writes the consolidated summary to `{session-dir}/review-reports/review-consolidated-<timestamp>.md`.

This section documents the Queen's Step 3c (User Triage) workflow. **The Queen owns this step**, not the review agents.
The Queen reads Big Head's consolidated summary and follows the procedures below.

## Queen's Step 3c: User Triage on P1/P2 Issues

**Prerequisite**: CCB PASS + consolidated summary written by Big Head

### If P1 or P2 issues found:

1. **Present findings to user** with consolidated summary showing:
   - Total issues by priority (P1: X, P2: Y, P3: Z)
   - Root causes identified
   - Deduplication stats (N raw findings → M root causes)

2. **Ask user**: "Reviews found X P1 and Y P2 issues. Should we fix them now, or push and address later?"

3. **If user chooses "fix now"** — Queen spawns fix tasks:

   a. **Test-first workflow** (TDD approach):
      - For each P1/P2 bead, Queen creates a test-writing task FIRST
      - Group test tasks by file (use orchestration/reference/dependency-analysis.md for conflict analysis)
      - Queen spawns Dirt Pushers (via Task tool, NOT agent teams) to write failing tests
      - Test requirements: Must cover edge cases and failure scenarios, not just happy path
      - Verify tests fail with expected error messages
      - Run `bd close` on test-writing tasks after verification

   b. **Implementation workflow**:
      - For each P1/P2 bead, Queen creates a fix implementation task
      - Group fix tasks by file (use orchestration/reference/dependency-analysis.md for conflict analysis)
      - Queen spawns Dirt Pushers to implement fixes (same 6-step process as original work)
      - Agents must run tests and verify they now PASS
      - Run DMVDC on each fix agent
      - Run `bd close` on fix tasks after DMVDC passes

   c. **Re-run reviews** (optional):
      - If fixes touched >3 files or made significant changes, consider re-running Step 3b (the Nitpickers)
      - Otherwise, rely on test verification + DMVDC

4. **If user chooses "push and address later"**:
   - P1/P2 beads already filed during consolidation — they stay open
   - Document in CHANGELOG: "Known issues filed for future work: <list bead IDs>"
   - Proceed to Step 4 (Handle P3 Issues and Documentation)

### Handle P3 Issues (Queen's Step 4)

**Create "Future Work" epic if needed**:
```bash
# Check if future-work epic exists
bd list --status=open | grep -i "future work" || \
bd epic create --title="Future Work" --description="Low-priority polish and improvements from review sessions"
```

**File P3 beads under the epic**:
- All P3 beads from consolidation should be children of the future-work epic
- Use `bd dep add <p3-bead-id> <future-work-epic-id> --type parent-child` for each P3 issue
- These can be addressed in future sessions
- No immediate action required — they're queued for later

After handling P3 issues, proceed to RULES.md Step 4 (Documentation — update CHANGELOG, README, CLAUDE.md).

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
