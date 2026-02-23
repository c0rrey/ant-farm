<!-- Reader: fill-review-slots.sh (replaces pantry-review). The Queen does NOT read this file directly. -->
# Quality Review Protocol

## Transition Gate Checklist

**When**: After all Dirt Pushers from Step 3 complete across ALL epics, BEFORE launching the Nitpickers.

Verify all 4 criteria before proceeding to team launch. These checks span ALL epics worked in this session:

1. **All Dirt Pushers completed across ALL epics** — none stuck or errored (check the Queen's state file for every epic)
2. **Dirt Moved vs Dirt Claimed (DMVDC) PASS for every agent** — verify at least one artifact exists at `<session-dir>/pc/pc-<task-id>-dmvdc-*.md`; if multiple files match (e.g., after retries), check the most recent by timestamp — it must contain an explicit `PASS` verdict, not merely exist
3. **The Queen's state file updated** — all completions tracked, checkpoint results recorded for all epics
4. **Git log shows expected commits** — run `git log --oneline -N` (where N = total number of agents across all epics) to confirm commits exist

**If any check fails**: Do NOT launch reviews. Investigate stuck agents, re-run failed checkpoints, or escalate to user.

**If all checks pass**: Proceed to Agent Teams Protocol below.

### Pre-Spawn Directory Setup

Directory creation is handled by the Queen in RULES.md Step 3b-iii. All active reviewers write to `${SESSION_DIR}/review-reports/`. Verification artifacts (`pc/`) are already created at Step 0.

---

## Agent Teams Protocol

After the transition gate passes, the Queen launches **the Nitpickers** using **TeamCreate** (NOT the Task tool) — four specialized reviewers plus **Big Head** (the consolidator) plus **Pest Control** (checkpoint validator), all as members of the same team. Reviewers produce **reports only** and do NOT file beads. Big Head consolidates all findings, deduplicates by root cause, and files beads.

**CRITICAL**: Reviews MUST use Agent Teams (TeamCreate + SendMessage), NOT plain Task tool subagents. The team structure enables cross-pollination between reviewers. **Big Head MUST be spawned as a team member** (not a separate Task agent) so it can receive messages from reviewers and coordinate within the team.

### Why Agent Teams (Not Sequential)

- **Wall-clock time**: 4 parallel reviews vs 4 sequential = ~4x faster
- **Cross-pollination**: Reviewers can message each other about overlapping findings, reducing duplicate work
- **Unified dedup**: Lead sees ALL findings before filing, so root-cause grouping is authoritative — no duplicate beads

### Model Assignments

- **Nitpickers (all active reviewers)**: `sonnet` — sufficient for code review and finding cataloging
- **Big Head**: `opus` — consolidation requires high-judgment dedup and root-cause grouping
- **Pest Control (team member)**: `sonnet` — runs DMVDC (judgment-heavy) inside the team; sonnet needed for substance verification

### Review Type Canonical Names

Each review type has one canonical short name used in template placeholders, file output paths, and report labels. The display title is the expanded form used in team setup listings and section headers.

| Short Name | Display Title | Priority | File Output Pattern |
|------------|---------------|----------|---------------------|
| `clarity` | Clarity Review | P3 | `clarity-review-<timestamp>.md` |
| `edge-cases` | Edge Cases Review | P2 | `edge-cases-review-<timestamp>.md` |
| `correctness` | Correctness Review | P1-P2 | `correctness-review-<timestamp>.md` |
| `drift` | Drift Review | P3 | `drift-review-<timestamp>.md` |

The short name is the authoritative identifier. Any template using a review type name that differs from the short name in this table without explanation is incorrect.

### Team Setup

**Pre-spawn requirement**: Before creating the Nitpickers, run **CCO** on all review prompts. See `templates/checkpoints.md`.

**Round 1**: the Queen creates the Nitpicker team with **6 members** (4 reviewers + Big Head + Pest Control):

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
3. Correctness Review (P1-P2) — see prompt below
4. Drift Review (P3) — see prompt below
5. Big Head (consolidation) — see prompt from big-head-skeleton.md; model specified in Big Head Consolidation Protocol section
6. Pest Control (checkpoint validator) — receives consolidated report path from Big Head via SendMessage; runs DMVDC and CCB checkpoints and replies with verdict
~~~

**Round 2+**: the Queen creates the Nitpicker team with **4 members** (2 reviewers + Big Head + Pest Control):

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

1. Correctness Review (P1-P2) — see prompt below
2. Edge Cases Review (P2) — see prompt below
3. Big Head (consolidation) — see prompt from big-head-skeleton.md
4. Pest Control (checkpoint validator) — same role as round 1
~~~

**Big Head is spawned as a team member using the big-head-skeleton.md template**, not as a separate Task agent. The Queen fills in the skeleton placeholders and uses the result as the teammate's prompt.

### Fallback: Sequential Reviews with File-Based Coordination (When TeamCreate Unavailable)

**When to use this fallback**: If the runtime environment does not support TeamCreate (e.g., the team slot is already in use for another epic, or messaging is unavailable), use this alternative workflow.

**Key difference from Team Protocol**: Reviewers are spawned as individual Task agents (not team members). Coordination happens via shared files instead of SendMessage.

**Output**: Both paths produce the same 4 review reports (clarity, edge-cases, correctness, drift) and Big Head consolidated summary.

#### Fallback Workflow

1. **Spawn reviewers sequentially or in batches** (no team):
   ```
   For each review type (clarity, edge-cases, correctness, drift):
   - Spawn as Task agent (model: sonnet)
   - Provide review prompt from review-clarity.md, review-edge-cases.md, etc.
   - Report output: {session-dir}/review-reports/{review-type}-review-{timestamp}.md
   ```

2. **File-based messaging (instead of SendMessage)**:
   - No cross-reviewer messages via SendMessage
   - Reviewers work independently
   - Skip "Cross-Review Messages" section in report (messaging not available in fallback mode)

3. **Spawn Big Head (after all 4 reviews complete)**:
   - Spawn as Task agent (model: opus)
   - Input: paths to all 4 review reports (copy from the reports directory)
   - Use big-head-skeleton.md template (same as team mode)
   - Output: consolidated summary to {session-dir}/review-reports/review-consolidated-{timestamp}.md

4. **Quality assurance**:
   - CCO still runs on all 4 review prompts (before spawning reviewers)
   - DMVDC and CCB still run on review artifacts (after Big Head completes)
   - Final output format identical to Team Protocol

#### Trade-offs of Fallback Mode

- **No parallel review execution**: Sequential or batched spawning is slower than team parallelism
- **No cross-reviewer messaging**: Reviewers cannot flag overlaps or share context (Big Head deduplication handles this)
- **Same consolidation logic**: Big Head still performs full deduplication, root-cause grouping, and bead filing
- **Same output quality**: Final reports and consolidated summary are identical to Team Protocol

#### When to Prefer Team Protocol Over Fallback

- Team Protocol preferred when: TeamCreate is available, you want ~4x faster wall-clock time, you want cross-reviewer coordination during review phase
- Fallback required when: TeamCreate unavailable (team slot exhausted by another epic, environment limitation, messaging unavailable)

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

- **Reviewers**: 4 (Clarity, Edge Cases, Correctness, Drift)
- **Scope**: All session commits (`<first-session-commit>..<HEAD>`)
- **Findings**: All severities reported and presented to user
- **Team size**: 6 (4 reviewers + Big Head + Pest Control)

This is the existing protocol — no changes to round 1 behavior.

### Round 2+ (Fix Verification)

- **Reviewers**: 2 (Correctness, Edge Cases only — Clarity and Drift are dropped)
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
2. In round 1, P3s are filed via the existing "Handle P3 Issues" flow in the Queen's Step 3c below
3. Queen proceeds directly to RULES.md Step 4 (documentation — README and CLAUDE.md only)
   - Note: CHANGELOG is authored by the Scribe at Step 5b, not here
4. No user prompt needed — the loop simply ends

**Escalation cap**: After round 4 with no convergence (P1 or P2 findings still present), do NOT start round 5. Instead, escalate to the user with the full round history (round numbers, finding counts per round, bead IDs) and ask whether to continue or abort. The reduced scope + reduced reviewers + P3 auto-filing make convergence fast; if it has not converged by round 4, human judgment is required.

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
Write your report to `<session-dir>/review-reports/clarity-review-<timestamp>.md` using the format below. (the Queen provides the exact filename in your prompt.)
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
Write your report to `<session-dir>/review-reports/edge-cases-review-<timestamp>.md` using the format below. (the Queen provides the exact filename in your prompt.)
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

## Review 3: Correctness (P1-P2)

**Agent Type:** `code-reviewer`
**Model:** `sonnet`
**Priority:** P1-P2 (critical, must fix before deploy)

```markdown
Perform a CORRECTNESS review of the completed work in this session.

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
Write your report to `<session-dir>/review-reports/correctness-review-<timestamp>.md` using the format below. (the Queen provides the exact filename in your prompt.)
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

## Review 4: Drift (P3)

**Agent Type:** `code-reviewer`
**Model:** `sonnet`
**Priority:** P3 (stale assumptions, incomplete propagation)

```markdown
Perform a DRIFT review of the completed work in this session.

Review scope: commits <first-commit> through <last-commit> (<N> commits total)

This review checks whether all changes propagated consistently across the codebase.

Focus areas:
1. **Value propagation** - Did changed values, names, counts, or paths get updated everywhere?
2. **Caller/consumer updates** - When a function signature or type changed, do all call sites match?
3. **Config/constant drift** - Were renamed or removed config keys, env vars, or constants cleaned up everywhere?
4. **Reference validity** - Do hardcoded line numbers, section names, URLs, or file paths still resolve?
5. **Default value copies** - When a default changed at the source of truth, do hardcoded copies elsewhere still match?
6. **Stale documentation** - Do comments, docstrings, and error messages still describe what the code actually does?

## Catalog Phase
Read all files in scope. For each meaningful change in the diff, ask: "what else assumes the old behavior?"
Grep for old values. Trace callers. Check documentation references.
Group findings into preliminary root causes where possible.

## Report (MANDATORY)
Write your report to `<session-dir>/review-reports/drift-review-<timestamp>.md` using the format below. (the Queen provides the exact filename in your prompt.)
Do NOT file beads — Big Head handles all bead filing.

For each change in scope, check:
- Old value still present elsewhere in scoped files
- Callers/consumers still match the new contract
- Hardcoded references still resolve
- Documentation still describes current behavior
- Default copies still match the source of truth

Review these files:
<list of files changed in session>
```

## Nitpicker Report Format (All Reviewers)

Every reviewer MUST write their report to `<session-dir>/review-reports/<review-type>-review-<timestamp>.md` using this format. The Queen generates the timestamp once per review cycle and provides the exact output path in each reviewer's prompt.

```markdown
# Report: <review-type> Review

**Scope**: <list of files reviewed>
**Reviewer**: <review type + agent type>

## Findings Catalog

### Finding 1: <short title>
- **File(s)**: <file:line references>
- **Severity**: P1 / P2 / P3
- **Category**: <clarity|edge-case|correctness|drift>
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

After all Nitpicker reports are complete (4 in round 1; 2 in round 2+), Big Head (a member of the same team) consolidates:

### Verification Pipeline Design Rationale

The Big Head consolidation process includes two distinct verification layers that work together:

1. **Big Head Step 0 (Prerequisite Gate)**: A mandatory check performed by Big Head BEFORE reading any reports. This gate ensures all expected reports exist (4 in round 1; 2 in round 2+) before consolidation logic begins. This prevents wasted effort on reading partial report sets or proceeding with missing data.

2. **Pest Control CCB Check 0 (Independent Audit)**: A separate, independent check performed AFTER Big Head consolidation is complete (see checkpoints.md). This audit verifies the same round-appropriate reports but runs in a different context — it confirms that consolidation did not proceed in a degraded state (e.g., no reviewer failures during the review phase).

**Why both?** The prerequisite gate (Big Head Step 0) is a blocker for Big Head's own work. The audit check (CCB Check 0) is an independent verification that consolidation ran on complete input — a safety check from a different agent with fresh eyes. The redundancy is intentional: different agents, different timing, different failure modes.

### Step 0: Verify All Reports Exist (MANDATORY GATE)

Before reading any reports, verify the expected files exist. The number of expected reports depends on the review round:

**Round 1**: Verify all 4 report files exist using the exact paths provided in your prompt:

```bash
[ -f "<session-dir>/review-reports/clarity-review-<timestamp>.md" ] || echo "MISSING: clarity"
[ -f "<session-dir>/review-reports/edge-cases-review-<timestamp>.md" ] || echo "MISSING: edge-cases"
[ -f "<session-dir>/review-reports/correctness-review-<timestamp>.md" ] || echo "MISSING: correctness"
[ -f "<session-dir>/review-reports/drift-review-<timestamp>.md" ] || echo "MISSING: drift"
```

**Round 2+**: Verify 2 report files exist using exact paths:

```bash
[ -f "<session-dir>/review-reports/correctness-review-<timestamp>.md" ] || echo "MISSING: correctness"
[ -f "<session-dir>/review-reports/edge-cases-review-<timestamp>.md" ] || echo "MISSING: edge-cases"
```

**All expected files MUST exist.** If any file is missing:
1. Identify which reviewer failed to produce output
2. Check if the reviewer is still running, errored, or wrote to the wrong path
3. Do NOT proceed with consolidation until all expected reports are present

### Step 0a: Remediation Path for Missing Reports (TIMEOUT + ERROR RETURN)

> **Authoritative source**: This section is the authoritative protocol for missing-report handling. The big-head-skeleton.md step 1 defers to this brief. If any apparent conflict exists between the skeleton and this brief, follow this brief.

If any report file is missing after the initial check, do NOT wait indefinitely. Instead:

**Timeout specification:** Wait a maximum of 30 seconds for all expected reports to appear (4 in round 1; 2 in round 2+).
- Check once at T=0
- If all expected reports exist, proceed to Step 1
- If any reports are missing, enter the polling loop below

**Polling loop (if files missing):**
```bash
# IMPORTANT: This entire block must execute in a single Bash invocation.
# Shell state (variables) does not persist across separate Bash tool calls.

# REVIEW_ROUND is filled in by fill-review-slots.sh before this brief is delivered.
# It is a shell integer (1, 2, 3, ...) used to gate round-1-only checks below.
REVIEW_ROUND={{REVIEW_ROUND}}
case "$REVIEW_ROUND" in
  *'{'*|*'}'*)
    echo "PLACEHOLDER ERROR: REVIEW_ROUND was not substituted by fill-review-slots.sh (got: $REVIEW_ROUND)"
    echo "This brief was delivered with an unresolved {{REVIEW_ROUND}} placeholder."
    echo "Root cause: fill-review-slots.sh was bypassed or failed during prompt composition."
    echo "Do NOT proceed. Return this error to the Queen immediately."
    exit 1
    ;;
esac

# --- Timing constants (document rationale, not just values) ---
# 30 seconds: enough for a slow reviewer to write its report; short enough to
# return a clear error rather than block the Queen indefinitely.
POLL_TIMEOUT_SECS=30
# 2 seconds: balances responsiveness against unnecessary busy-polling.
POLL_INTERVAL_SECS=2
ELAPSED=0

# --- Report count constraint (which reports to expect per round) ---
# Round 1:  correctness, edge-cases, clarity, drift (4 reports)
# Round 2+: correctness, edge-cases only (2 reports)
# The Pantry writes the exact file paths (with timestamp) into this brief.
# Use [ -f "$EXACT_PATH" ] — no globs. Globs match stale reports from prior rounds.

# Placeholder substitution guard: verify the Pantry replaced all template placeholders
# before entering the polling loop. Unsubstituted placeholders (angle brackets or curly
# braces) in file paths cause every [ -f ] test to fail silently, producing a misleading
# timeout error instead of a clear diagnosis.
PLACEHOLDER_ERROR=0
for _path in \
  "<session-dir>/review-reports/correctness-review-<timestamp>.md" \
  "<session-dir>/review-reports/edge-cases-review-<timestamp>.md"; do
  if [ -z "$_path" ]; then
    echo "PLACEHOLDER ERROR: path resolved to empty string (SESSION_DIR or timestamp unset)"
    echo "Root cause: unset or empty shell variable in Pantry prompt composition."
    echo "Do NOT proceed. Return this error to the Queen immediately."
    PLACEHOLDER_ERROR=1
  fi
  case "$_path" in
    *'<'*|*'>'*|*'{'*|*'}'*)
      echo "PLACEHOLDER ERROR: path was not substituted by Pantry: $_path"
      echo "This brief was delivered with unresolved template placeholders."
      echo "Root cause: upstream substitution failure in Pantry prompt composition."
      echo "Do NOT proceed. Return this error to the Queen immediately."
      PLACEHOLDER_ERROR=1
      ;;
  esac
done
if [ "$REVIEW_ROUND" -eq 1 ]; then
for _path in \
  "<session-dir>/review-reports/clarity-review-<timestamp>.md" \
  "<session-dir>/review-reports/drift-review-<timestamp>.md"; do
  if [ -z "$_path" ]; then
    echo "PLACEHOLDER ERROR: path resolved to empty string (SESSION_DIR or timestamp unset)"
    echo "Root cause: unset or empty shell variable in Pantry prompt composition."
    echo "Do NOT proceed. Return this error to the Queen immediately."
    PLACEHOLDER_ERROR=1
  fi
  case "$_path" in
    *'<'*|*'>'*|*'{'*|*'}'*)
      echo "PLACEHOLDER ERROR: path was not substituted by Pantry: $_path"
      echo "This brief was delivered with unresolved template placeholders."
      echo "Root cause: upstream substitution failure in Pantry prompt composition."
      echo "Do NOT proceed. Return this error to the Queen immediately."
      PLACEHOLDER_ERROR=1
      ;;
  esac
done
fi
if [ $PLACEHOLDER_ERROR -eq 1 ]; then
  exit 1
fi

REPORTS_FOUND=0  # set to 1 when all expected reports are present
while [ $ELAPSED -lt $POLL_TIMEOUT_SECS ]; do
  ALL_FOUND=1

  # Always expected (both rounds):
  [ -f "<session-dir>/review-reports/correctness-review-<timestamp>.md" ] || ALL_FOUND=0
  [ -f "<session-dir>/review-reports/edge-cases-review-<timestamp>.md" ] || ALL_FOUND=0

  # Round 1 only: clarity and drift reports are also expected.
  if [ "$REVIEW_ROUND" -eq 1 ]; then
  [ -f "<session-dir>/review-reports/clarity-review-<timestamp>.md" ] || ALL_FOUND=0
  [ -f "<session-dir>/review-reports/drift-review-<timestamp>.md" ] || ALL_FOUND=0
  fi

  if [ $ALL_FOUND -eq 1 ]; then
    REPORTS_FOUND=1
    break
  fi
  sleep $POLL_INTERVAL_SECS
  ELAPSED=$((ELAPSED + POLL_INTERVAL_SECS))
done

if [ $REPORTS_FOUND -eq 0 ]; then
  echo "TIMEOUT: Not all expected reports arrived within ${POLL_TIMEOUT_SECS}s"
  cat > "{CONSOLIDATED_OUTPUT_PATH}" << 'EOF'
# Big Head Consolidation — BLOCKED: Missing Nitpicker Reports
**Status**: FAILED — prerequisite gate timeout
**Timestamp**: <current ISO 8601 timestamp>
**Reason**: Not all expected Nitpicker reports arrived within the polling timeout. Check the list of missing reports above.
**Recovery**: Check reviewer logs. Once all expected reports are present, re-spawn Big Head consolidation.
EOF
  exit 1
fi
```

**Script responsibility**: `fill-review-slots.sh` substitutes `{{REVIEW_ROUND}}` with the actual round integer before delivering this brief to Big Head. The `if [ "$REVIEW_ROUND" -eq 1 ]; then ... fi` blocks execute in shell — they do not depend on LLM interpretation. Round 2+ behavior is reliable regardless of whether an LLM reads the template.

**Error return (if timeout exceeded):**

If timeout is reached and any reports are still missing, IMMEDIATELY return an error to the Queen:

```markdown
# Big Head Consolidation - BLOCKED: Missing Nitpicker Reports

**Status**: FAILED (timeout after 30 seconds)
**Timestamp**: <current ISO 8601 timestamp>

## Missing Reports

The following expected Nitpicker report files were not found:
- Clarity review report (clarity-review-<timestamp>.md) — MISSING
- Edge cases review report (edge-cases-review-<timestamp>.md) — MISSING [or: FOUND at <path>]
- Correctness review report (correctness-review-<timestamp>.md) — MISSING [or: FOUND at <path>]
- Drift review report (drift-review-<timestamp>.md) — MISSING [or: FOUND at <path>]

## Remediation

Big Head cannot proceed with consolidation without all expected reports present. The prerequisite gate (Step 0) FAILED.

**Action required from Queen:**
1. Check review agent logs for errors or crashes
2. Verify all Nitpicker team members completed their reviews
3. Confirm reports were written to: `<session-dir>/review-reports/`
4. Once all expected reports are confirmed present, re-spawn Big Head consolidation

**Re-spawn instruction:**
~~~
Spawn Big Head again with all expected report paths provided in the consolidation prompt.
~~~

**Do not proceed** with partial or missing review data.
```

Once the error is returned:
- Return the error message and STOP (do not continue to Steps 1-4)
- The Queen receives this error and must decide: retry with fresh Nitpicker spawn, or abort session

### Step 1: Read All Reports

Read all expected reports from `<session-dir>/review-reports/` (the Queen provides exact filenames in the consolidation prompt):

Round 1 (4 reports):
- `clarity-review-<timestamp>.md`
- `edge-cases-review-<timestamp>.md`
- `correctness-review-<timestamp>.md`
- `drift-review-<timestamp>.md`

Round 2+ (2 reports):
- `correctness-review-<timestamp>.md`
- `edge-cases-review-<timestamp>.md`

### Step 2: Merge and Deduplicate

1. **Collect all findings** across all reports into a single list
2. **Identify duplicates** — findings reported by multiple reviewers about the same issue
3. **Merge cross-referenced items** — where one reviewer flagged something for another's domain
4. **Group by root cause** — apply the root-cause grouping principle across ALL review types:
5. **Document merge rationale** — for EVERY merge (two or more findings combined into one root cause), state:
   - WHY these findings share a root cause (not just that they do)
   - What the common code path, pattern, or design flaw is
   - If merged findings span unrelated files or functions, provide extra justification

```markdown
## Root-Cause Grouping (Big Head Consolidation)

For each group of related findings across all reviews:
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

### Step 2.5: Deduplicate Against Existing Beads

Before writing the consolidated summary or filing any beads, check for open beads that already cover your root causes. This prevents duplicate tracking of issues found in previous sessions.

```bash
if ! bd list --status=open -n 0 --short > /tmp/open-beads-$$.txt 2>&1; then
  echo "ERROR: bd list failed (lock contention or bd error). Aborting bead filing to prevent duplicates."
  exit 1
fi
```

For each root cause group, compare against existing bead titles (from `/tmp/open-beads-$$.txt`):

- **Exact title match** (case-insensitive): Do NOT file. Log in the summary: "Dedup: RC-N matches existing bead ant-farm-XXXX — skipped."
- **Similar title** (same root cause, different wording): Run `bd search "<key phrases>" --status open` to confirm. If the existing bead covers the same root cause, do NOT file. Log the match and the existing bead ID.
- **No match found**: Mark the root cause for filing.

When uncertain whether a match is truly the same root cause, err on the side of filing — a human can merge later; a missed filing is harder to recover.

Include a **Cross-Session Dedup** section in the consolidated summary listing, for each root cause, whether it was filed (new bead ID), skipped (matched existing bead ID and why), or merged with an existing bead.

### Step 3: Write Consolidated Summary

Write the consolidated summary to `<session-dir>/review-reports/review-consolidated-<timestamp>.md`:

```markdown
# Consolidated Review Summary

**Scope**: <list of all files reviewed>
**Reviews completed**: <Round 1: Clarity, Edge Cases, Correctness, Drift | Round 2+: Correctness, Edge Cases>
**Total raw findings**: <N across all reviews>
**Root causes identified**: <N after dedup>
**Beads filed**: <N>

## Read Confirmation

**Reports read and processed by Big Head consolidation:**

Round 1: 4 reports (clarity, edge-cases, correctness, drift)
Round 2+: 2 reports (correctness, edge-cases)

| Report Type | File | Status | Finding Count |
|-------------|------|--------|----------------|
| <for each report in this round> | <filename> | ✓ Read | <N> findings |

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
  ```bash
  cat > "{CONSOLIDATED_OUTPUT_PATH%.md}-pc-timeout.md" << 'EOF'
  # Big Head Consolidation — BLOCKED: Pest Control Timeout
  **Status**: FAILED — Pest Control checkpoint unavailable
  **Timestamp**: <current ISO 8601 timestamp>
  **Reason**: Pest Control did not respond after 2 attempts (120s total). Consolidated report was written but checkpoints could not be validated.
  **Recovery**: Re-spawn Pest Control manually and provide the consolidated report path, or accept consolidated findings without checkpoint validation.
  EOF
  ```
  Then send to Queen:
  ```
  Big Head checkpoint escalation to Queen:
  - Pest Control verdict: UNAVAILABLE (no response after 2 attempts, 120s total)
  - Consolidated report path: {CONSOLIDATED_OUTPUT_PATH}
  - Timeout failure artifact: {CONSOLIDATED_OUTPUT_PATH%.md}-pc-timeout.md
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
cat > /tmp/bead-desc-$$.md << 'BEAD_DESC'
## Root Cause
<What is specifically wrong — cite the code path, pattern, or design flaw.
Reference file:line locations where the issue originates. This must be
substantive analysis, NOT a restatement of the title.>

## Affected Surfaces
- `file1.py:L42` — <specific instance> (from clarity review)
- `file2.sh:L15` — <specific instance> (from edge-cases review)

## Fix
<Specific corrective action — what to change, where, and why.>

## Changes Needed
- `path/to/file1.py`: <what to change>
- `path/to/file2.sh`: <what to change>

## Acceptance Criteria
- [ ] <First independently testable criterion>
- [ ] <Second independently testable criterion>
- [ ] <Third independently testable criterion>
BEAD_DESC

bd create --type=bug --priority=<combined-priority> --title="<root cause title>" --body-file /tmp/bead-desc-$$.md
bd label add <new-bead-id> <primary-review-type>
rm -f /tmp/bead-desc-$$.md
```

### P3 Auto-Filing (Round 2+ Only)

In round 2+, Big Head auto-files P3 findings to the "Future Work" epic without user involvement:

1. Find or create the "Future Work" epic:
   ```bash
   # Check if future-work epic exists
   bd list --status=open | grep -i "future work"
   # If not found:
   bd epic create --title="Future Work" --description="Low-priority polish and improvements from review sessions"
   ```

2. For each P3 root cause:
   ```bash
   cat > /tmp/bead-desc-$$.md << 'BEAD_DESC'
   ## Root Cause
   <What is wrong — file:line refs to the primary location.>

   ## Affected Surfaces
   - `file:line` — <instance> (from <reviewer>)

   ## Acceptance Criteria
   - [ ] <testable criterion>
   BEAD_DESC

   bd create --type=bug --priority=3 --title="<root cause title>" --body-file /tmp/bead-desc-$$.md
   bd dep add <new-bead-id> <future-work-epic-id> --type parent-child
   rm -f /tmp/bead-desc-$$.md
   ```

3. In the consolidated summary, list P3 beads in a separate section:
   ~~~markdown
   ## Auto-Filed P3s (Future Work)
   | Bead ID | Title | Epic |
   |---------|-------|------|
   | <id> | <title> | Future Work |
   ~~~

4. Do NOT include P3 findings in the fix-or-defer prompt to the Queen. They appear only in the consolidated summary for the record.

**Round 1**: P3s are NOT auto-filed by Big Head. They follow the existing "Handle P3 Issues" flow in the Queen's Step 3c below.

## The Queen's Checklists

### Nitpicker Checklist (verify before launching team)

Before launching the review agent team, confirm:
- [ ] Review round number passed to Pantry (`Review round: <N>`)
- [ ] Round 1: All 4 Nitpicker prompts include review scope; Round 2+: 2 prompts (Correctness, Edge Cases)
- [ ] Each Nitpicker has focus areas specific to their review type
- [ ] Round 2+ reviewers include out-of-scope finding bar instructions from the Round 2+ Reviewer Instructions section
- [ ] Catalog phase instructions included (find all, group preliminarily)
- [ ] Report format instructions included (use standard Nitpicker report format)
- [ ] Each prompt says "Do NOT file beads — Big Head handles all bead filing"
- [ ] Messaging guidelines included (what to share, what not to share)
- [ ] Reports write to `<session-dir>/review-reports/<review-type>-review-<timestamp>.md`
- [ ] Round 1: Team has 6 members (4 Nitpickers + Big Head + Pest Control); Round 2+: 4 members (2 Nitpickers + Big Head + Pest Control)
- [ ] Round 2+: Big Head prompt includes review round number and P3 auto-filing instructions

### Big Head Consolidation Checklist (after all Nitpickers finish)

Before filing beads, confirm Big Head has:
- [ ] Round 1: Read all 4 Nitpicker reports; Round 2+: Read 2 reports (Correctness, Edge Cases)
- [ ] Merged duplicate findings across reviews
- [ ] Grouped all findings by root cause (not per-occurrence)
- [ ] Written consolidated summary to `<session-dir>/review-reports/review-consolidated-<timestamp>.md`
- [ ] Sent consolidated report path to Pest Control via SendMessage
- [ ] Received Pest Control verdict (PASS or FAIL + specifics)
- [ ] On PASS: filed ONE bead per root cause with all affected surfaces listed
- [ ] Round 2+ on PASS: P3 beads auto-filed to "Future Work" epic (not presented to user)
- [ ] On FAIL: escalated failed findings to Queen; filed beads only for validated findings

## After Consolidation Complete

**Prerequisite**: Colony Census Bureau (CCB) must PASS before proceeding.

Big Head writes the consolidated summary to `{session-dir}/review-reports/review-consolidated-<timestamp>.md`.

This section documents the Queen's Step 3c (User Triage) workflow. **The Queen owns this step**, not the review agents.
The Queen reads Big Head's consolidated summary and follows the procedures below.

## Queen's Step 3c: User Triage on P1/P2 Issues

**Prerequisite**: CCB PASS + consolidated summary written by Big Head

### Termination Check (zero P1/P2 findings)

If the consolidated summary shows zero P1 and zero P2 findings, the review loop has converged:

1. **Round 2+**: Big Head has already auto-filed any P3 findings to "Future Work" epic — no action needed
2. **Round 1**: P3 findings follow the existing "Handle P3 Issues" flow below — the Queen files them to Future Work
3. Queen updates session state: `Termination: terminated (round N: 0 P1/P2)`
4. Proceed to RULES.md Step 4 (Documentation — update README and CLAUDE.md only)
   - Scribe authors the session CHANGELOG entry at Step 5b

No user prompt needed — the loop simply ends.

### If P1 or P2 issues found:

The Queen determines the fix action based on RULES.md Step 3c decision tree:
- **Auto-fix** (round 1, ≤5 root causes): proceed directly to Fix Workflow below
- **Escalation** (round 1, >5 root causes): present to user, await decision
- **User prompt** (round 2+): present to user, "Fix now or defer?"
- **Defer**: P1/P2 beads stay open; document deferred items for the Scribe (Step 5b CHANGELOG); proceed to Step 4

### Fix Workflow

Triggered by auto-fix (round 1) or user choosing "fix now" (round 2+). The workflow splits by severity:

#### P1 Root Causes — TDD Workflow (test-first)

For each P1 root cause bead:

1. **Create test-writing task** — Queen creates a bead for the test-writing task
2. **Compose test specification** — Queen extracts from the consolidated summary and includes in the task brief:

   ~~~markdown
   ## Test Specification (from review finding)

   **Root cause**: <root cause description from consolidated summary>
   **Affected surfaces**: <file:line references>

   ### Required test cases:
   1. **Failing case**: <specific scenario from review finding>
      - Input: <concrete input that triggers the bug>
      - Expected: <what should happen>
      - Actual: <what currently happens>
   2. **Boundary condition**: <derived from affected surfaces>
      - Input: <edge case input>
      - Expected: <correct behavior at boundary>
   3. **Regression guard**: <happy path that must still pass>
      - Input: <normal input>
      - Expected: <existing correct behavior preserved>
   ~~~

3. **Spawn Dirt Pushers** (via Task tool, NOT agent teams) to write tests matching the spec
4. **Verify tests fail** with expected error messages
5. **Create fix implementation task** — Queen creates a bead for the fix task
6. **Spawn Dirt Pushers** to implement fixes, run tests, verify they now PASS
7. **DMVDC** on each fix agent
8. **Close tasks** — `bd close` on both test and fix tasks after DMVDC passes

Group test tasks by file (use orchestration/reference/dependency-analysis.md for conflict analysis).

#### P2 Root Causes — Fix-Only Workflow (direct)

For each P2 root cause bead:

1. **Create fix implementation task** — Queen creates a bead (skip test phase)
2. **Compose fix brief** — include root cause, affected surfaces, and suggested fix from consolidated summary
3. **Spawn Dirt Pushers** to implement fixes
4. **DMVDC** on each fix agent
5. **Close tasks** — `bd close` on fix tasks after DMVDC passes

Group fix tasks by file (use orchestration/reference/dependency-analysis.md for conflict analysis).

#### Wave Composition

P1 test tasks and P2 fix tasks target different root causes (different files), so they can be waved together:

```
Wave 1: [P1 test tasks] + [P2 fix tasks]    (concurrent)
Wave 2: [P1 fix tasks]                       (after P1 tests verified failing)
```

Existing wave rules apply: max 7 Dirt Pushers per wave, no file overlap within a wave.

#### Re-Run Reviews (MANDATORY)

After all fix agents complete and pass DMVDC:
- Re-run Step 3b with `Review round: <N+1>`
- Round 2+ uses only Correctness + Edge Cases reviewers, scoped to fix commits
- The loop continues until a round produces zero P1/P2 findings

### Handle P3 Issues (Queen's Step 3c)

> **Round 1 only.** In round 2+, P3s are auto-filed by Big Head during consolidation (see "P3 Auto-Filing" above). This section applies only when round 1 terminates with P3 findings.

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

After handling P3 issues, proceed to RULES.md Step 4 (Documentation — update README and CLAUDE.md only).
The Scribe authors the session CHANGELOG entry at Step 5b.

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
