<!-- Reader: build-review-prompts.sh (extracts inline prompts and protocol). The Queen does NOT read this file directly. -->
# Quality Review Protocol

## Transition Gate Checklist

**When**: After all Crumb Gatherers from Step 3 complete across ALL trails, BEFORE launching the Reviewers.

Verify all 4 criteria before proceeding to team launch. These checks span ALL trails worked in this session:

1. **All Crumb Gatherers completed across ALL trails** — none stuck or errored (check the Queen's state file for every trail)
2. **claims-vs-code PASS for every agent** — verify at least one artifact exists at `{session-dir}/pc/pc-{TASK_ID}-claims-vs-code-*.md`. If multiple files match (e.g., after retries), select the most recent by embedded filename timestamp (YYYYMMDD-HHmmss, sorted descending). That file must contain an explicit `PASS` verdict, not merely exist
3. **The Queen's state file updated** — all completions tracked, checkpoint results recorded for all trails
4. **Git log shows expected commits** — run `git log --oneline -N` (where N = total number of agents across all trails) to confirm commits exist

**If any check fails**: Do NOT launch reviews. Investigate stuck agents, re-run failed checkpoints, or escalate to user.

**If all checks pass**: Proceed to Agent Teams Protocol below.

### Pre-Spawn Directory Setup

Directory creation is handled by the Queen in RULES.md Step 3b-iii. All active reviewers write to `${SESSION_DIR}/review-reports/`. Verification artifacts (`pc/`) are already created at Step 0.

---

## Agent Teams Protocol

After the transition gate passes, the Queen launches **the Reviewers** using **TeamCreate** (NOT the Task tool) — reviewers plus **Review Consolidator** (the consolidator) plus **Checkpoint Auditor** (checkpoint validator), all as members of the same team. Reviewers produce **reports only** and do NOT file crumbs. Review Consolidator consolidates all findings, deduplicates by root cause, and files crumbs.

**CRITICAL**: Reviews MUST use Agent Teams (TeamCreate + SendMessage), NOT plain Task tool subagents. The team structure enables cross-pollination between reviewers. **Review Consolidator MUST be spawned as a team member** (not a separate Task agent) so it can receive messages from reviewers and coordinate within the team.

### Why Agent Teams (Not Sequential)

- **Wall-clock time**: parallel reviews vs sequential = proportional speedup (scales with reviewer count)
- **Cross-pollination**: Reviewers can message each other about overlapping findings, reducing duplicate work
- **Unified dedup**: Lead sees ALL findings before filing, so root-cause grouping is authoritative — no duplicate crumbs

### Model Assignments

- **Reviewers — Correctness, Edge Cases**: `opus` — higher-judgment reviews requiring deeper reasoning
- **Reviewers — Clarity, Drift**: `sonnet` — lower-judgment reviews sufficient for code review and finding cataloging
- **Review Consolidator**: `opus` — consolidation requires high-judgment dedup and root-cause grouping
- **Checkpoint Auditor (team member)**: `sonnet` — runs claims-vs-code (pattern-matching) inside the team; sonnet sufficient for substance verification

### Review Type Canonical Names

Each review type has one canonical short name used in template placeholders, file output paths, and report labels. The display title is the expanded form used in team setup listings and section headers.

| Short Name | Display Title | Priority | File Output Pattern |
|------------|---------------|----------|---------------------|
| `clarity` | Clarity Review | P3 | `clarity-review-{timestamp}.md` |
| `edge-cases` | Edge Cases Review | P2 | `edge-cases-review-{timestamp}.md` |
| `correctness` | Correctness Review | P1-P2 | `correctness-review-{timestamp}.md` |
| `drift` | Drift Review | P3 | `drift-review-{timestamp}.md` |

The short name is the authoritative identifier. Any template using a review type name that differs from the short name in this table without explanation is incorrect.

### Team Setup

**Pre-spawn requirement**: Before creating the reviewers, run **pre-spawn-check** on all review prompts. See `templates/checkpoints/pre-spawn-check.md`.

**Round 1**: the Queen creates the Reviewer team with a **variable member count** determined by `build-review-prompts.sh`'s return table. Base case is 6 members (4 reviewers + Review Consolidator + Checkpoint Auditor); when split reviewer instances occur the count increases (e.g., 8 members when 2 Clarity + 2 Drift splits are produced). Do NOT hardcode 6 members — build the list from the return table.

**Split instance naming**: When `build-review-prompts.sh` splits a reviewer type across multiple instances, each instance is named `{review-type}-{N}` (e.g., `clarity-1`, `clarity-2`, `drift-1`, `drift-2`). The base-case single-instance names (`clarity-reviewer`, `drift-reviewer`) apply only when no split occurred. SendMessage to these members must use these exact names — never broadcast.

Base case (no splits) — 6 members:

~~~markdown
Create a team with these members. Reviewers work in parallel.
Review Consolidator waits for all expected reports (count from consolidation brief's expected_paths), then consolidates.
Checkpoint Auditor is a team member so Review Consolidator can SendMessage to it directly for checkpoint validation.

Reviewers produce REPORTS ONLY — do NOT file crumbs (`crumb create`).
Review Consolidator consolidates all reports, groups findings by root cause, and files crumbs.

Review scope: commits {first-commit} through {last-commit} ({N} commits total, across trails: {trail-list})
Files to review: {deduplicated list of ALL files changed across all trails}
Task IDs for acceptance criteria: {list of all task IDs with commits in the review range — see Task ID Scoping section}

1. Clarity Review (P3) — see prompt below; model: sonnet
2. Edge Cases Review (P2) — see prompt below; model: opus
3. Correctness Review (P1-P2) — see prompt below; model: opus
4. Drift Review (P3) — see prompt below; model: sonnet
5. Review Consolidator (consolidation) — see prompt from review-consolidator-skeleton.md; model specified in Review Consolidator Protocol section
6. Checkpoint Auditor (checkpoint validator) — receives consolidated report path from Review Consolidator via SendMessage; runs claims-vs-code and review-integrity checkpoints and replies with verdict
~~~

Split instance example (2 Clarity + 2 Drift splits) — 8 members:

~~~markdown
Create a team with these members. Reviewers work in parallel.
Review Consolidator waits for all expected reports (count from consolidation brief's expected_paths), then consolidates.
Checkpoint Auditor is a team member so Review Consolidator can SendMessage to it directly for checkpoint validation.

Reviewers produce REPORTS ONLY — do NOT file crumbs (`crumb create`).
Review Consolidator consolidates all reports, groups findings by root cause, and files crumbs.

Review scope: commits {first-commit} through {last-commit} ({N} commits total, across trails: {trail-list})
Files to review: {deduplicated list of ALL files changed across all trails}
Task IDs for acceptance criteria: {list of all task IDs with commits in the review range — see Task ID Scoping section}

1. Clarity Review part 1 (P3) — clarity-1; file subset A from return table; model: sonnet
2. Clarity Review part 2 (P3) — clarity-2; file subset B from return table; model: sonnet
3. Edge Cases Review (P2) — see prompt below; model: opus
4. Correctness Review (P1-P2) — see prompt below; model: opus
5. Drift Review part 1 (P3) — drift-1; file subset A from return table; model: sonnet
6. Drift Review part 2 (P3) — drift-2; file subset B from return table; model: sonnet
7. Review Consolidator (consolidation) — see prompt from review-consolidator-skeleton.md; model specified in Review Consolidator Protocol section
8. Checkpoint Auditor (checkpoint validator) — receives consolidated report path from Review Consolidator via SendMessage; runs claims-vs-code and review-integrity checkpoints and replies with verdict
~~~

**Round 2+**: the Reviewer team is **persistent** — do NOT create a new team. Re-task the existing Correctness and Edge Cases reviewers via named-member SendMessage (see Round Transition via SendMessage section). Review Consolidator and Checkpoint Auditor remain in the team and are re-tasked the same way. The team has at minimum 4 active members (Correctness + Edge Cases + Review Consolidator + Checkpoint Auditor); Clarity and Drift reviewers — including all split instances (e.g., `clarity-1`, `clarity-2`, `drift-1`, `drift-2`) — remain idle and are NOT re-tasked.

Re-tasking message fields for each reviewer (named-member SendMessage — no broadcast):

~~~markdown
Review scope: fix commits only — {first-fix-commit} through HEAD
Files to review: {files changed in fix commits only}
Task IDs for acceptance criteria: {list of fix task IDs with commits in the fix range — see Task ID Scoping section}
Review round: {N+1}
Report output path: {reviewer-specific path from Round Transition section}

1. Correctness Review (P1-P2) — SendMessage to `correctness-reviewer`; model: opus (unchanged from round 1)
2. Edge Cases Review (P2) — SendMessage to `edge-cases-reviewer`; model: opus (unchanged from round 1)
3. Review Consolidator (consolidation) — SendMessage to `ant-farm-review-consolidator` with round N+1 and 2 expected report paths
4. Checkpoint Auditor (checkpoint validator) — remains available; Review Consolidator SendMessages `ant-farm-checkpoint-auditor` as in round 1

Clarity and Drift reviewers (including split instances clarity-1, clarity-2, drift-1, drift-2, etc.) are NOT
re-tasked — they remain idle. Do NOT send them messages in round 2+.
~~~

### Task ID Scoping (Commit-Range Filtering)

When compiling the "Task IDs for acceptance criteria" list for any review round, **exclude tasks whose fix commits fall outside the review commit range**. A task whose fix commit predates `{first-commit}` (Round 1) or `{first-fix-commit}` (Round 2+) cannot be verified by the reviewer because the relevant changes are not in the diff.

**Filtering rule**: For each candidate task ID, verify that at least one commit attributed to that task appears in `git log --oneline {first-commit}..{last-commit}`. If none of the task's commits fall within the range, exclude it from the task ID list.

This prevents reviewers from being asked to verify acceptance criteria for changes they cannot see in the review scope.

**The Review Consolidator is spawned as a team member using the review-consolidator-skeleton.md template**, not as a separate Task agent. The Queen fills in the skeleton placeholders and uses the result as the teammate's prompt.

### Fallback: Sequential Reviews with File-Based Coordination (When TeamCreate Unavailable)

**When to use this fallback**: If the runtime environment does not support TeamCreate (e.g., the team slot is already in use for another trail, or messaging is unavailable), use this alternative workflow.

**Key difference from Team Protocol**: Reviewers are spawned as individual Task agents (not team members). Coordination happens via shared files instead of SendMessage.

**Output**: Both paths produce the same 4 review reports (clarity, edge-cases, correctness, drift) and Review Consolidator consolidated summary.

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

3. **Spawn Review Consolidator (after all 4 reviews complete)**:
   - Spawn as Task agent (model: opus)
   - Input: paths to all 4 review reports (copy from the reports directory)
   - Use review-consolidator-skeleton.md template for the Review Consolidator (same as team mode)
   - Output: consolidated summary to {session-dir}/review-reports/review-consolidated-{timestamp}.md

4. **Quality assurance**:
   - pre-spawn-check still runs on all 4 review prompts (before spawning reviewers)
   - claims-vs-code and review-integrity still run on review artifacts (after Review Consolidator completes)
   - Final output format identical to Team Protocol

#### Trade-offs of Fallback Mode

- **No parallel review execution**: Sequential or batched spawning is slower than team parallelism
- **No cross-reviewer messaging**: Reviewers cannot flag overlaps or share context (Review Consolidator deduplication handles this)
- **Same consolidation logic**: Review Consolidator still performs full deduplication, root-cause grouping, and crumb filing
- **Same output quality**: Final reports and consolidated summary are identical to Team Protocol

#### When to Prefer Team Protocol Over Fallback

- Team Protocol preferred when: TeamCreate is available, you want ~4x faster wall-clock time, you want cross-reviewer coordination during review phase
- Fallback required when: TeamCreate unavailable (team slot exhausted by another trail, environment limitation, messaging unavailable)

### Messaging Guidelines

**Reviewers SHOULD message when:**
- They find something that crosses into another reviewer's domain (e.g., clarity reviewer spots a potential edge case)
- They want to flag "I'm covering X, skip it" to avoid duplicate analysis
- They discover context that would help another reviewer (e.g., "this function is only called from one place")

**Reviewers should NOT message:**
- Status updates ("I'm 50% done")
- General observations that don't help other reviewers
- Questions that should go to Review Consolidator

## Round-Aware Review Protocol

The review pipeline supports multiple rounds. The Queen passes `Review round: {N}` to the Pantry. Round number determines reviewer composition, scope, and P3 handling.

### Round 1 (Full Review)

- **Reviewers**: 4 (Clarity, Edge Cases, Correctness, Drift)
- **Scope**: All session commits (`{first-session-commit}..HEAD`)
- **Findings**: All severities reported and presented to user
- **Team size**: 6 base case (4 reviewers + Review Consolidator + Checkpoint Auditor); more when split reviewer instances are present (count from `build-review-prompts.sh` return table)

This is the existing protocol — no changes to round 1 behavior.

### Round 2+ (Fix Verification)

- **Reviewers**: 2 (Correctness, Edge Cases only — Clarity and Drift are dropped)
- **Scope**: Fix commits only (`{first-fix-commit}..HEAD`)
- **Team size**: 4 (2 reviewers + Review Consolidator + Checkpoint Auditor)
- **In-scope findings**: All severities reported
- **Out-of-scope findings**: Only reportable if they would cause:
  - **Runtime failure**: an agent, tool call, or workflow step would crash or error
  - **Silently wrong results**: an agent would succeed but produce incorrect output (e.g., stale cross-references pointing the Queen to the wrong section)
- **Not reportable out-of-scope**: naming conventions, style preferences, documentation gaps, improvement opportunities, hypothetical edge cases requiring unusual conditions
- **P3 handling**: Review Consolidator auto-files P3s to "Future Work" trail (no user prompt)

### Termination Rule

The review loop terminates when a round produces **zero P1 or P2 findings**. At termination:

1. Review Consolidator auto-files any P3 findings to "Future Work" trail (round 2+ only)
2. In round 1, P3s are filed via the existing "Handle P3 Issues" flow in the Queen's Step 3c below
3. Queen then proceeds to RULES.md Step 4 (documentation — README and CLAUDE.md only)
   - Note: CHANGELOG is authored by the Scribe at Step 5, not here
4. No user prompt needed — the loop simply ends

**Escalation cap**: After round 4 with no convergence (P1 or P2 findings still present), do NOT start round 5. Instead, escalate to the user with the full round history (round numbers, finding counts per round, crumb IDs) and ask whether to continue or abort. The reduced scope + reduced reviewers + P3 auto-filing make convergence fast; if it has not converged by round 4, human judgment is required.

### Round 2+ Reviewer Instructions

Correctness and Edge Cases reviewers receive this additional scope constraint in round 2+. The Pantry includes this text in each reviewer's brief:

> **Fix verification scope**: Review commits `{fix-start}..HEAD` only. You may read full files for context, but your mandate is: did these fixes land correctly and not break anything?
>
> **Out-of-scope findings**: If you notice something outside the fix commits that would cause a runtime failure, incorrect agent behavior, or silently wrong results (e.g., stale cross-references pointing to wrong sections), report it. Do NOT report naming conventions, style preferences, documentation gaps, or improvement opportunities outside the fix scope.

The `[OUT-OF-SCOPE]` tag is for labeling and severity isolation. It helps Review Consolidator and human readers distinguish fix-scope findings from incidental discoveries. **Severity enforcement rule**: when merging findings into a root-cause group, `[OUT-OF-SCOPE]` findings do NOT contribute to the group's combined priority. Use only in-scope severity levels to compute the group priority. `[OUT-OF-SCOPE]` findings contribute their affected surfaces and context to the group but are excluded from severity calculation. Example: a root-cause group with an in-scope P2 finding and an `[OUT-OF-SCOPE]` P3 finding uses P2 as the group priority — the P3 does not increase it.

## Review 1: Clarity (P3)

**Agent Type:** `code-reviewer`
**Model:** `sonnet`
**Priority:** P3 (polish, not blocking)

```markdown
Perform a CLARITY review of the completed work in this session.

Review scope: commits {first-commit} through {last-commit} ({N} commits total)

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
Write your report to `{session-dir}/review-reports/clarity-review-{timestamp}.md` using the format below. (the Queen provides the exact filename in your prompt.)
Do NOT file crumbs — Review Consolidator handles all crumb filing.

If you find something that looks like an edge case or correctness bug, message the
relevant Reviewer so they can investigate in depth.

Review these files:
{list of files changed in session}
```

## Review 2: Edge Cases (P2)

**Agent Type:** `code-reviewer`
**Model:** `opus`
**Priority:** P2 (important, should fix soon)

```markdown
Perform an EDGE CASES review of the completed work in this session.

Review scope: commits {first-commit} through {last-commit} ({N} commits total)

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
Write your report to `{session-dir}/review-reports/edge-cases-review-{timestamp}.md` using the format below. (the Queen provides the exact filename in your prompt.)
Do NOT file crumbs — Review Consolidator handles all crumb filing.

Pay special attention to:
- Functions that read/write files
- Functions that parse user input
- Functions with external dependencies
- Loops and iterations
- Error handling blocks

Review these files:
{list of files changed in session}
```

## Review 3: Correctness (P1-P2)

**Agent Type:** `code-reviewer`
**Model:** `opus`
**Priority:** P1-P2 (critical, must fix before deploy)

```markdown
Perform a CORRECTNESS review of the completed work in this session.

Review scope: commits {first-commit} through {last-commit} ({N} commits total)

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
Write your report to `{session-dir}/review-reports/correctness-review-{timestamp}.md` using the format below. (the Queen provides the exact filename in your prompt.)
Do NOT file crumbs — Review Consolidator handles all crumb filing.

Review these files and their acceptance criteria:
{list of files and their original task requirements}

**IMPORTANT**: Run `crumb show <task-id>` for each task in the commit range to retrieve
the original acceptance criteria. Do not rely solely on the orchestrator's prompt —
verify against the source of truth. For each finding, cite the specific acceptance
criterion that is violated or unmet.

For each completed task, verify:
- All acceptance criteria met
- Acceptance criteria source documented (which `crumb show` output, which requirement)
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

Review scope: commits {first-commit} through {last-commit} ({N} commits total)

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
Write your report to `{session-dir}/review-reports/drift-review-{timestamp}.md` using the format below. (the Queen provides the exact filename in your prompt.)
Do NOT file crumbs — Review Consolidator handles all crumb filing.

For each change in scope, check:
- Old value still present elsewhere in scoped files
- Callers/consumers still match the new contract
- Hardcoded references still resolve
- Documentation still describes current behavior
- Default copies still match the source of truth

Review these files:
{list of files changed in session}
```

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

## Reviewer Report Format (All Reviewers)

Every reviewer MUST write their report to `{session-dir}/review-reports/{review-type}-review-{timestamp}.md` using this format. The Queen generates the timestamp once per review cycle and provides the exact output path in each reviewer's prompt.

```markdown
# Report: {review-type} Review

**Scope**: {list of files reviewed}
**Reviewer**: {review type + agent type}

## Findings Catalog

### Finding 1: {short title}
- **File(s)**: {file:line references}
- **Severity**: P1 / P2 / P3
- **Category**: {clarity|edge-case|correctness|drift}
- **Description**: {what's wrong}
- **Suggested fix**: {how to fix}
- **Cross-reference**: {if related to another reviewer's domain, note it}

### Finding 2: {short title}
...

## Preliminary Groupings

Group findings that share a root cause:

### Group A: {root cause title}
- Finding 1, Finding 3 — same underlying issue
- **Suggested combined fix**: {one fix covering all}

### Group B: {root cause title}
- Finding 2 — standalone

## Summary Statistics
- Total findings: {N}
- By severity: P1: {N}, P2: {N}, P3: {N}
- Preliminary groups: {N}

## Cross-Review Messages

Log all messages sent to and received from other reviewers:

### Sent
- To {reviewer}: "{summary of message}" — Action: {what you asked them to do or look at}

### Received
- From {reviewer}: "{summary of message}" — Action taken: {what you did in response}

### Deferred Items
- "{finding title}" — Deferred to {reviewer} because {reason}

## Coverage Log

List every in-scope file with its review status. Files with no findings MUST still appear here — omission is not acceptable.

| File | Status | Evidence |
|------|--------|----------|
| {file1} | Findings: #1, #3 | N/A |
| {file2} | Reviewed — no issues | {N} functions, {M} lines examined |
| {file3} | Reviewed — no issues | {N} functions, {M} lines examined |

## Overall Assessment
**Score**: {X/10}
**Verdict**: {PASS / PASS WITH ISSUES / NEEDS WORK}
<!-- Verdict Rubric:
  PASS           = 0 P1 findings AND 0 P2 findings
  PASS WITH ISSUES = 0 P1 findings AND any P2 or P3 findings
  NEEDS WORK     = any P1 finding present

  Score formula: Start at 10, subtract 3 per P1, 1 per P2, 0.5 per P3 (floor at 0)
-->
{1-2 sentence summary}
```

## Review Consolidator Consolidation Protocol

**Model:** `opus`

After all Reviewer reports are complete (count determined by the consolidation brief's `expected_paths` list; typically 4 in round 1, 2 in round 2+, but may vary if split reviewer instances are used), Review Consolidator (a member of the same team) consolidates:

### Step Numbering Cross-Reference

reviews.md and review-consolidator-skeleton.md (Review Consolidator template) use different step numbering schemes. Use this table to cross-reference them without consulting both files simultaneously:

| reviews.md step | review-consolidator-skeleton.md (Review Consolidator) step | Description |
|----------------|--------------------------|-------------|
| Step 0 | Step 1 | Verify all expected report files exist (prerequisite gate) |
| Step 0a | Step 1 (continued) | Polling loop and timeout handling for missing reports |
| Step 1 | Step 2 | Read all expected Reviewer reports |
| Step 2 | Steps 3–6 | Merge findings, deduplicate, group by root cause, document merge rationale |
| Step 2.5 | Step 7 | Cross-session dedup against existing open crumbs |
| Step 3 | Step 8 | Write consolidated summary to output path |
| Step 4 | Steps 9–10 | SendMessage to Checkpoint Auditor, await verdict, file crumbs on PASS |
| (round 2+ only) | Step 11 | P3 auto-filing to Future Work trail |
| (all rounds) | Step 12 | Send crumb list handoff message to Queen |

### Verification Pipeline Design Rationale

The Review Consolidator consolidation process includes two distinct verification layers that work together:

1. **Review Consolidator Step 0 (Prerequisite Gate)**: A mandatory check performed by Review Consolidator BEFORE reading any reports. This gate ensures all expected reports exist (count from the consolidation brief's `expected_paths` list) before consolidation logic begins. This prevents wasted effort on reading partial report sets or proceeding with missing data.

2. **Checkpoint Auditor review-integrity Check 0 (Independent Audit)**: A separate, independent check performed AFTER Review Consolidator consolidation is complete (see checkpoints/review-integrity.md). This audit verifies the same round-appropriate reports but runs in a different context — it confirms that consolidation did not proceed in a degraded state (e.g., no reviewer failures during the review phase).

**Why both?** The prerequisite gate (Review Consolidator Step 0) is a blocker for the Review Consolidator's own work. The audit check (review-integrity Check 0) is an independent verification that consolidation ran on complete input — a safety check from a different agent with fresh eyes. The redundancy is intentional: different agents, different timing, different failure modes.

### Step 0: Verify All Reports Exist (MANDATORY GATE)

Before reading any reports, verify the expected files exist. The authoritative list of expected paths is in the consolidation brief's `expected_paths` section — use that list, not a hardcoded count. The bash examples below show typical paths for the default reviewer set; adapt for split instances if present.

**Round 1** (typical paths — verify all paths in `expected_paths`):

```bash
[ -f "{session-dir}/review-reports/clarity-review-{timestamp}.md" ] || echo "MISSING: clarity"
[ -f "{session-dir}/review-reports/edge-cases-review-{timestamp}.md" ] || echo "MISSING: edge-cases"
[ -f "{session-dir}/review-reports/correctness-review-{timestamp}.md" ] || echo "MISSING: correctness"
[ -f "{session-dir}/review-reports/drift-review-{timestamp}.md" ] || echo "MISSING: drift"
# If split instances exist (e.g., clarity-2), add additional [ -f ] checks here
```

**Round 2+** (typical paths — verify all paths in `expected_paths`):

```bash
[ -f "{session-dir}/review-reports/correctness-review-{timestamp}.md" ] || echo "MISSING: correctness"
[ -f "{session-dir}/review-reports/edge-cases-review-{timestamp}.md" ] || echo "MISSING: edge-cases"
# If split instances exist, add additional [ -f ] checks here
```

**All expected files MUST exist.** If any file is missing:
1. Identify which reviewer failed to produce output
2. Check if the reviewer is still running, errored, or wrote to the wrong path
3. Do NOT proceed with consolidation until all expected reports are present

### Step 0a: Remediation Path for Missing Reports (TIMEOUT + ERROR RETURN)

> **Authoritative source**: This section is the authoritative protocol for missing-report handling. The review-consolidator-skeleton.md step 1 defers to this brief. If any apparent conflict exists between the skeleton and this brief, follow this brief.

If any report file is missing after the initial check, do NOT wait indefinitely. Instead:

**Timeout specification:** Wait a maximum of 30 seconds for all expected reports to appear (count determined by the consolidation brief's `expected_paths` list).
- Check once at T=0
- If all expected reports exist, proceed to Step 1
- If any reports are missing, enter the polling loop below

**Polling loop (if files missing):**

> **Template source note**: The curly-brace values (`{session-dir}`, `{timestamp}`) in
> the code block below are **template placeholders**. `build-review-prompts.sh` substitutes
> them with real paths before this brief is delivered to Review Consolidator. When Review Consolidator runs this
> block, every `{session-dir}` and `{timestamp}` token will already be replaced with the
> actual session directory and timestamp strings. The angle-bracket guard below (`case "$_path" in *'<'*|*'>'*`)
> is checking the **substituted** paths — a failure there means substitution was incomplete upstream.

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

# --- Single-invocation constraint ---
# This entire bash block (the while loop and all path checks below) MUST be
# submitted as a single Bash tool call. Shell state (variables, sleep) does not
# persist across turns. Do NOT attempt to poll by calling Bash repeatedly across
# multiple conversation turns.

# --- Timing constants (document rationale, not just values) ---
# 60 seconds (30 iterations × 2s): enough for a slow reviewer to write its
# report under typical load; short enough to return a clear error rather than
# block the Queen indefinitely. If reviewers consistently time out, the Queen
# should re-spawn Review Consolidator rather than increasing this timeout.
POLL_TIMEOUT_SECS=60
# 2 seconds: balances responsiveness against unnecessary busy-polling.
POLL_INTERVAL_SECS=2
ELAPSED=0

# --- Report paths to expect ---
# The consolidation brief's expected_paths list is authoritative. Typical counts:
# Round 1:  correctness, edge-cases, clarity, drift (4 paths, or more if split instances)
# Round 2+: correctness, edge-cases only (2 paths, or more if split instances)
# The Pantry writes the exact file paths (with timestamp) into this brief.
# Use [ -f "$EXACT_PATH" ] — no globs. Globs match stale reports from prior rounds.

# Placeholder substitution guard: verify the Pantry replaced all template placeholders
# before entering the polling loop. Unsubstituted placeholders (angle brackets or curly
# braces) in file paths cause every [ -f ] test to fail silently, producing a misleading
# timeout error instead of a clear diagnosis.
PLACEHOLDER_ERROR=0
# Validate paths for reports expected in ALL rounds (correctness + edge-cases).
# Note: REVIEW_ROUND corruption is caught above in the case statement before we
# reach this block, so REVIEW_ROUND is guaranteed to be a valid integer here.
for _path in \
  "{session-dir}/review-reports/correctness-review-{timestamp}.md" \
  "{session-dir}/review-reports/edge-cases-review-{timestamp}.md"; do
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
# Validate round-1-only paths (clarity + drift). Pantry only substitutes these
# paths in round-1 briefs; round-2+ briefs leave these as literal angle-bracket
# placeholders (they are not in ACTIVE_REVIEW_TYPES for round 2+). Checking them
# unconditionally in round 2+ would always trigger a false PLACEHOLDER_ERROR.
if [ "$REVIEW_ROUND" -eq 1 ]; then
for _path in \
  "{session-dir}/review-reports/clarity-review-{timestamp}.md" \
  "{session-dir}/review-reports/drift-review-{timestamp}.md"; do
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
while [ $ELAPSED -le $POLL_TIMEOUT_SECS ]; do
  ALL_FOUND=1

  # Always expected (both rounds):
  [ -f "{session-dir}/review-reports/correctness-review-{timestamp}.md" ] || ALL_FOUND=0
  [ -f "{session-dir}/review-reports/edge-cases-review-{timestamp}.md" ] || ALL_FOUND=0

  # Round 1 only: clarity and drift reports are also expected.
  if [ "$REVIEW_ROUND" -eq 1 ]; then
  [ -f "{session-dir}/review-reports/clarity-review-{timestamp}.md" ] || ALL_FOUND=0
  [ -f "{session-dir}/review-reports/drift-review-{timestamp}.md" ] || ALL_FOUND=0
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
# Review Consolidator Consolidation — BLOCKED: Missing Reviewer Reports
**Status**: FAILED — prerequisite gate timeout
**Timestamp**: {current ISO 8601 timestamp}
**Reason**: Not all expected Reviewer reports arrived within the polling timeout. Check the list of missing reports above.
**Recovery**: Check reviewer logs. Once all expected reports are present, re-spawn Review Consolidator consolidation.
EOF
  exit 1
fi
```

**Script responsibility**: `fill-review-slots.sh` substitutes `{{REVIEW_ROUND}}` with the actual round integer before delivering this brief to Review Consolidator. The `if [ "$REVIEW_ROUND" -eq 1 ]; then ... fi` blocks execute in shell — they do not depend on LLM interpretation. Round 2+ behavior is reliable regardless of whether an LLM reads the template.

**Error return (if timeout exceeded):**

If timeout is reached and any reports are still missing, IMMEDIATELY return an error to the Queen:

```markdown
# Review Consolidator Consolidation - BLOCKED: Missing Reviewer Reports

**Status**: FAILED (timeout after 60 seconds)
**Timestamp**: {current ISO 8601 timestamp}

## Missing Reports

The following expected Reviewer report files were not found:
- Clarity review report (clarity-review-{timestamp}.md) — MISSING
- Edge cases review report (edge-cases-review-{timestamp}.md) — MISSING [or: FOUND at {path}]
- Correctness review report (correctness-review-{timestamp}.md) — MISSING [or: FOUND at {path}]
- Drift review report (drift-review-{timestamp}.md) — MISSING [or: FOUND at {path}]

## Remediation

Review Consolidator cannot proceed with consolidation without all expected reports present. The prerequisite gate (Step 0) FAILED.

**Action required from Queen:**
1. Check review agent logs for errors or crashes
2. Verify all Reviewer team members completed their reviews
3. Confirm reports were written to: `{session-dir}/review-reports/`
4. Once all expected reports are confirmed present, re-spawn Review Consolidator consolidation

**Re-spawn instruction:**
~~~
Spawn Review Consolidator again with all expected report paths provided in the consolidation prompt.
~~~

**Do not proceed** with partial or missing review data.
```

Once the error is returned:
- Return the error message and STOP (do not continue to Steps 1-4)
- The Queen receives this error and must decide: retry with fresh Reviewer spawn, or abort session

### Step 1: Read All Reports

Read all expected reports from `{session-dir}/review-reports/` using the exact paths provided in the consolidation brief's `expected_paths` list. The count varies based on how many reviewers were spawned.

Round 1 typical paths (may include additional paths for split reviewer instances):
- `clarity-review-{timestamp}.md`
- `edge-cases-review-{timestamp}.md`
- `correctness-review-{timestamp}.md`
- `drift-review-{timestamp}.md`

Round 2+ typical paths (may include additional paths for split reviewer instances):
- `correctness-review-{timestamp}.md`
- `edge-cases-review-{timestamp}.md`

### Step 2: Merge and Deduplicate

1. **Collect all findings** across all reports into a single list
2. **Identify duplicates** — findings reported by multiple reviewers about the same issue
3. **Merge cross-referenced items** — where one reviewer flagged something for another's domain
4. **Group by root cause** — apply the root-cause grouping principle across ALL review types:
5. **Split-instance dedup**: If the same reviewer type produced multiple reports (e.g., `clarity-1` and `clarity-2`), treat them as a **single logical review type** for root-cause grouping. A finding from `clarity-1` and a finding from `clarity-2` about the same root cause are merged into one root cause entry — they are NOT treated as cross-type duplicates. Dedup across split instances by **file path + line range**, not solely by prose similarity. If two findings reference the same `file:line` location, treat them as the same instance regardless of how the finding is worded.
6. **Document merge rationale** — for EVERY merge (two or more findings combined into one root cause), state:
   - WHY these findings share a root cause (not just that they do)
   - What the common code path, pattern, or design flaw is
   - If merged findings span unrelated files or functions, provide extra justification
   - For split-instance merges, note which split instance each finding came from (e.g., "from clarity-1" vs "from clarity-2")

```markdown
## Root-Cause Grouping (Review Consolidator Consolidation)

For each group of related findings across all reviews:
- **Root cause**: {what's systematically wrong}
- **Affected surfaces**:
  - file1.html:L10 — {specific instance} (from clarity review)
  - file2.html:L25 — {specific instance} (from edge-cases review)
  - file3.py:L100 — {specific instance} (from correctness review)
- **Combined priority**: {highest priority from any contributing finding}
- **Fix**: {one fix that covers all surfaces}
- **Merge rationale**: {why these specific findings share this root cause — must reference shared code path, pattern, or design flaw}
- **Acceptance criteria**: {how to verify across all surfaces}
```

### Step 2.5: Deduplicate Against Existing Crumbs

Before writing the consolidated summary or filing any crumbs, check for open crumbs that already cover your root causes. This prevents duplicate tracking of issues found in previous sessions.

```bash
_OPEN_CRUMBS_TMP="$(mktemp /tmp/open-crumbs-XXXXXX.txt)"
if ! crumb list --open --short > "$_OPEN_CRUMBS_TMP" 2>/dev/null; then
  echo "ERROR: crumb list failed (file error or crumb error). Aborting crumb filing to prevent duplicates."
  cat > "{CONSOLIDATED_OUTPUT_PATH}" << 'EOF'
  # Review Consolidator Consolidation — BLOCKED: Cross-Session Dedup Infrastructure Error
  **Status**: FAILED — crumb list infrastructure error
  **Timestamp**: {current ISO 8601 timestamp}
  **Reason**: `crumb list --open` failed. Crumb filing aborted to prevent duplicate filing. This is likely a file access or crumb CLI issue.
  **Recovery**: Retry after the issue clears. If the issue persists, run `crumb doctor` and re-spawn Review Consolidator.
  EOF
  exit 1
fi
```

If the bash block above exits with code 1, stop immediately. Do NOT proceed to consolidation or crumb filing. Use the SendMessage tool to notify the Queen: "Review Consolidator FAILED: crumb list infrastructure error during cross-session dedup. Crumb filing aborted to prevent duplicates. Consolidated output written to {CONSOLIDATED_OUTPUT_PATH}. Please check crumb status and re-spawn Review Consolidator when ready." Then end your turn.
<!-- NOTE: {CONSOLIDATED_OUTPUT_PATH} in the SendMessage text above is a template placeholder substituted by build-review-prompts.sh at build time — a real filesystem path appears in its place when Review Consolidator receives this prompt. Consistent with the bash-block comment in review-consolidator-skeleton.md. -->

For each root cause group, compare against existing crumb titles (from `$_OPEN_CRUMBS_TMP`):

- **Exact title match** (case-insensitive): Do NOT file. Log in the summary: "Dedup: RC-N matches existing crumb {ID} — skipped."
- **Similar title** (same root cause, different wording): Run `crumb search "<key phrases>"` to confirm. If the existing crumb covers the same root cause, do NOT file. Log the match and the existing crumb ID.
- **No match found**: Mark the root cause for filing.

When uncertain whether a match is truly the same root cause, err on the side of filing — a human can merge later; a missed filing is harder to recover.

Include a **Cross-Session Dedup** section in the consolidated summary listing, for each root cause, whether it was filed (new crumb ID), skipped (matched existing crumb ID and why), or merged with an existing crumb.

### Step 3: Write Consolidated Summary

Write the consolidated summary to `{session-dir}/review-reports/review-consolidated-{timestamp}.md`:

```markdown
# Consolidated Review Summary

**Scope**: {list of all files reviewed}
**Reviews completed**: {Round 1: Clarity, Edge Cases, Correctness, Drift | Round 2+: Correctness, Edge Cases}
**Total raw findings**: {N across all reviews}
**Root causes identified**: {N after dedup}
**Crumbs filed**: {N}

## Read Confirmation

**Reports Received** (all paths from consolidation brief's `expected_paths` list):

| Path | Status | Finding Count |
|------|--------|---------------|
| {full path from expected_paths} | PRESENT / MISSING | {N} findings |
| ... | ... | ... |

Every path in `expected_paths` MUST appear in this table. A MISSING entry indicates a reviewer did not produce output.

**Total findings from all reports**: {N}

## Root Causes Filed

| Crumb ID | Priority | Title | Contributing Reviews | Surfaces |
|---------|----------|-------|---------------------|----------|
| {id} | P{N} | {title} | clarity, edge-cases | {N} files |
| ... | ... | ... | ... | ... |

## Deduplication Log

Findings merged:
- {Finding X from clarity} + {Finding Y from edge-cases} → Root Cause A
- ...

## Priority Breakdown
- P1 (blocking): {N} crumbs
- P2 (important): {N} crumbs
- P3 (polish): {N} crumbs

## Verdict
{PASS / PASS WITH ISSUES / NEEDS WORK}
{overall quality assessment}
```

### Step 4: Checkpoint Gate — Await Checkpoint Auditor Validation Before Filing Crumbs

**Do NOT file any crumbs yet.** After writing the consolidated summary (Step 3), notify Checkpoint Auditor and wait for its verdict before calling `crumb create`.

**Notification to Checkpoint Auditor (SendMessage):**
```
SendMessage(
  to="ant-farm-checkpoint-auditor",
  message="Consolidated report ready. Path: {session-dir}/review-reports/review-consolidated-{timestamp}.md. Please run claims-vs-code and review-integrity checkpoints and reply with PASS or FAIL + specifics.",
  summary="Consolidated report ready for checkpoint"
)
```

**End your turn immediately after sending to Checkpoint Auditor. Checkpoint Auditor's reply will arrive as a new teammate message on your next turn. Do NOT use sleep or poll — waiting blocks incoming messages.**

**Turn-based retry protocol:**
- After sending the SendMessage, **end your turn**. Do not sleep or poll.
- The Checkpoint Auditor's reply arrives as a new conversation turn. Process it when it arrives.
- If the Checkpoint Auditor has not replied after receiving 2 incoming messages from any teammate that are not the expected Checkpoint Auditor reply (i.e., 2 non-Checkpoint-Auditor messages arrive before you receive a verdict), send one retry message:
  ```
  SendMessage(
    to="ant-farm-checkpoint-auditor",
    message="Retry request: Consolidated report ready at {CONSOLIDATED_OUTPUT_PATH}. Please run claims-vs-code and review-integrity checkpoints and reply with PASS or FAIL + specifics. (First message sent — no reply received after 2 turns.)",
    summary="Retry: consolidated report ready for checkpoint"
  )
  ```
  Then end your turn again and await the reply.
- If still no response after 2 more non-Checkpoint-Auditor incoming messages following the retry, **escalate to the Queen immediately**:
  ```bash
  cat > "{CONSOLIDATED_OUTPUT_PATH%.md}-pc-timeout.md" << 'EOF'
  # Review Consolidator Consolidation — BLOCKED: Checkpoint Auditor Timeout
  **Status**: FAILED — Checkpoint Auditor checkpoint unavailable
  **Timestamp**: {current ISO 8601 timestamp}
  **Reason**: Checkpoint Auditor did not respond after 2 attempts (4 turns total). Consolidated report was written but checkpoints could not be validated.
  **Recovery**: Re-spawn Checkpoint Auditor manually and provide the consolidated report path, or accept consolidated findings without checkpoint validation.
  EOF
  ```
  Then send to Queen:
  ```
  Review Consolidator checkpoint escalation to Queen:
  - Checkpoint Auditor verdict: UNAVAILABLE (no response after 2 attempts, 4 turns total)
  - Consolidated report path: {CONSOLIDATED_OUTPUT_PATH}
  - Timeout failure artifact: {CONSOLIDATED_OUTPUT_PATH%.md}-pc-timeout.md
  - Action required: PC checkpoint could not be completed. User must decide: re-spawn Checkpoint Auditor
    manually, or accept consolidated findings without checkpoint validation.
  ```
  Do NOT file any crumbs when escalating due to Checkpoint Auditor timeout.

- **PASS**: File ONE crumb per root cause. See crumb filing instructions below.
- **FAIL**: Review Consolidator MUST escalate to the Queen with specifics. File crumbs ONLY for findings that passed. Do NOT file crumbs for flagged findings. Use this escalation format:

```
Review Consolidator checkpoint escalation to Queen:
- Checkpoint Auditor verdict: FAIL
- Findings that failed validation: {list with reasons per finding}
- Findings that passed: {list}
- Crumbs filed for validated findings: {ids or "none"}
- Action required: User decides whether to drop, adjust, or re-review failed findings.
```

**Crumb filing (validated findings only):**

File ONE crumb per root cause (not per finding, not per review).

**Important**: Crumbs filed during session review are standalone. Do NOT assign them to a specific trail via `crumb link --parent`. They represent session-wide findings, not trail-specific work.

```bash
_DESC_TMP="$(mktemp /tmp/crumb-desc-XXXXXX.md)"
cat > "$_DESC_TMP" << 'CRUMB_DESC'
## Root Cause
{What is specifically wrong — cite the code path, pattern, or design flaw.
Reference file:line locations where the issue originates. This must be
substantive analysis, NOT a restatement of the title.}

## Affected Surfaces
- `file1.py:L42` — {specific instance} (from clarity review)
- `file2.sh:L15` — {specific instance} (from edge-cases review)

## Fix
{Specific corrective action — what to change, where, and why.}

## Changes Needed
- `path/to/file1.py`: {what to change}
- `path/to/file2.sh`: {what to change}

## Acceptance Criteria
- [ ] {First independently testable criterion}
- [ ] {Second independently testable criterion}
- [ ] {Third independently testable criterion}
CRUMB_DESC

CRUMB_TITLE="{root-cause-title}"
CRUMB_PRIORITY="P{combined-priority}"
CRUMB_REVIEW_SOURCE="{primary-review-type}"
_CRUMB_JSON_TMP="$(mktemp /tmp/crumb-XXXXXX.json)"
python3 -c "
import json, pathlib, sys
title, priority, review_source = sys.argv[1], sys.argv[2], sys.argv[3]
desc = pathlib.Path(sys.argv[4]).read_text()
print(json.dumps({'type': 'bug', 'priority': priority, 'title': title, 'description': desc, 'review_source': review_source, 'acceptance_criteria': [], 'scope': {}, 'links': {}}))
" "$CRUMB_TITLE" "$CRUMB_PRIORITY" "$CRUMB_REVIEW_SOURCE" "$_DESC_TMP" > "$_CRUMB_JSON_TMP" || { echo "ERROR: JSON generation failed" >&2; exit 1; }
crumb create --from-file "$_CRUMB_JSON_TMP"
rm -f "$_DESC_TMP" "$_CRUMB_JSON_TMP"
```

### P3 Auto-Filing (Round 2+ Only)

In round 2+, Review Consolidator auto-files P3 findings to the "Future Work" trail without user involvement:

1. Find or create the "Future Work" trail:
   ```bash
   # Check if future-work trail exists
   crumb trail list | grep -i "future work"
   # If not found:
   crumb trail create --title "Future Work" --description "Low-priority polish and improvements from review sessions"
   ```

2. For each P3 root cause:
   ```bash
   _DESC_TMP="$(mktemp /tmp/crumb-desc-XXXXXX.md)"
   cat > "$_DESC_TMP" << 'CRUMB_DESC'
   ## Root Cause
   {What is wrong — file:line refs to the primary location.}

   ## Affected Surfaces
   - `file:line` — {instance} (from {reviewer})

   ## Acceptance Criteria
   - [ ] {testable criterion}
   CRUMB_DESC

   _CRUMB_TITLE="{root-cause-title}"
   _CRUMB_JSON_TMP="$(mktemp /tmp/crumb-XXXXXX.json)"
   python3 -c "
import json, pathlib, sys
title = sys.argv[1]
desc = pathlib.Path(sys.argv[2]).read_text()
print(json.dumps({'type': 'bug', 'priority': 'P3', 'title': title, 'description': desc, 'acceptance_criteria': [], 'scope': {}, 'links': {}}))
" "$_CRUMB_TITLE" "$_DESC_TMP" > "$_CRUMB_JSON_TMP" || { echo "ERROR: JSON generation failed" >&2; exit 1; }
   crumb create --from-file "$_CRUMB_JSON_TMP"
   crumb link <new-crumb-id> --parent <future-work-trail-id>
   rm -f "$_DESC_TMP" "$_CRUMB_JSON_TMP"
   ```

3. In the consolidated summary, list P3 crumbs in a separate section:
   ~~~markdown
   ## Auto-Filed P3s (Future Work)
   | Crumb ID | Title | Trail |
   |---------|-------|------|
   | {id} | {title} | Future Work |
   ~~~

4. Do NOT include P3 findings in the fix-or-defer prompt to the Queen. They appear only in the consolidated summary for the record.

**Round 1**: P3s are NOT auto-filed by Review Consolidator. They follow the existing "Handle P3 Issues" flow in the Queen's Step 3c below.

## The Queen's Checklists

### Reviewer Checklist (verify before launching team)

Before launching the review agent team, confirm:
- [ ] Review round number passed to Pantry (`Review round: {N}`)
- [ ] Round 1: All 4 Reviewer prompts include review scope; Round 2+: 2 prompts (Correctness, Edge Cases)
- [ ] Each Reviewer has focus areas specific to their review type
- [ ] Round 2+ reviewers include out-of-scope finding bar instructions from the Round 2+ Reviewer Instructions section
- [ ] Catalog phase instructions included (find all, group preliminarily)
- [ ] Report format instructions included (use standard Reviewer report format)
- [ ] Each prompt says "Do NOT file crumbs — Review Consolidator handles all crumb filing"
- [ ] Messaging guidelines included (what to share, what not to share)
- [ ] Reports write to `{session-dir}/review-reports/{review-type}-review-{timestamp}.md`
- [ ] Round 1: Team has 6 members (4 Reviewers + Review Consolidator + Checkpoint Auditor); Round 2+: persistent team re-tasked via SendMessage (NOT a new TeamCreate) — Correctness + Edge Cases + Review Consolidator + Checkpoint Auditor active; Clarity + Drift idle
- [ ] Round 2+: Review Consolidator prompt includes review round number and P3 auto-filing instructions

### Review Consolidator Consolidation Checklist (after all Reviewers finish)

Before filing crumbs, confirm Review Consolidator has:
- [ ] Read all reports listed in consolidation brief's `expected_paths` (count varies; typically 4 in round 1, 2 in round 2+, more if split instances present)
- [ ] Merged duplicate findings across reviews
- [ ] Grouped all findings by root cause (not per-occurrence)
- [ ] Written consolidated summary to `{session-dir}/review-reports/review-consolidated-{timestamp}.md`
- [ ] Sent consolidated report path to Checkpoint Auditor via SendMessage
- [ ] Received Checkpoint Auditor verdict (PASS or FAIL + specifics)
- [ ] On PASS: filed ONE crumb per root cause with all affected surfaces listed
- [ ] Round 2+ on PASS: P3 crumbs auto-filed to "Future Work" trail (not presented to user)
- [ ] On FAIL: escalated failed findings to Queen; filed crumbs only for validated findings

## After Consolidation Complete

**Prerequisite**: review-integrity must PASS before proceeding.

The Review Consolidator writes the consolidated summary to `{session-dir}/review-reports/review-consolidated-{timestamp}.md`.

This section documents the Queen's Step 3c (User Triage) workflow. **The Queen owns this step**, not the review agents.
The Queen reads the Review Consolidator's consolidated summary and follows the procedures below.

## Queen's Step 3c: User Triage on P1/P2 Issues

**Prerequisite**: review-integrity PASS + consolidated summary written by Review Consolidator

### Termination Check (zero P1/P2 findings)

If the consolidated summary shows zero P1 and zero P2 findings, the review loop has converged:

1. **Round 2+**: Review Consolidator has already auto-filed any P3 findings to "Future Work" trail — no action needed
2. **Round 1**: P3 findings follow the existing "Handle P3 Issues" flow below — the Queen files them to Future Work
3. Queen updates session state: `Termination: terminated (round N: 0 P1/P2)`
4. Proceed to RULES.md Step 4 (Documentation — update README and CLAUDE.md only)
   - Scribe authors the session CHANGELOG entry at Step 5

No user prompt needed — the loop simply ends.

### If P1 or P2 issues found:

The Queen determines the fix action based on RULES.md Step 3c decision tree:
- **Auto-fix** (round 1, ≤10 root causes): proceed directly to Fix Workflow below
- **Escalation** (round 1, >10 root causes): present to user, await decision
- **User prompt** (round 2+): present to user, "Fix now or defer?"
- **Defer**: P1/P2 crumbs stay open; document deferred items for the Scribe (Step 5 CHANGELOG); proceed to Step 4

### Fix Workflow

Triggered by auto-fix (round 1) or user choosing "fix now" (round 2+). Fix agents spawn **into the persistent reviewer team** (not as standalone Task agents) using the Task tool with `team_name: "reviewer-team"` so they can communicate directly with reviewers and iterate within the team via SendMessage.

#### Fix-Cycle Scout and Auto-Approval

Before spawning fix agents, the Queen runs a fix-cycle Scout to plan the fix strategy (which crumbs to fix, wave grouping, file conflict analysis).

**Auto-approval**: The fix-cycle Scout strategy is auto-approved — no user confirmation gate. The Scout's output feeds directly into fix agent spawning.

**startup-check gate**: startup-check still runs as a mechanical safety net on the Scout's strategy:
- startup-check PASS → proceed to fix agent spawning
- startup-check FAIL → re-run Scout with violations listed, max 1 retry; if still failing, escalate to user

#### Pantry and pre-spawn-check Skip Rationale

Fix briefs do **not** go through Pantry or pre-spawn-check. Reason:

- **Pantry skipped**: The Review Consolidator crumbs already contain root cause, affected surfaces, fix suggestion, and acceptance criteria — validated by review-integrity. The crumb IS the brief. Re-composing it through Pantry adds no value and wastes a round-trip.
- **pre-spawn-check skipped**: The crumb content passed review-integrity and the Scout's fix strategy passed startup-check. Two independent mechanical gates have already validated correctness. A third pre-spawn-check pass would be redundant.

Fix agents receive the crumb ID directly as their source of truth.

#### Fix Team Member Naming

Fix agents spawn into the Reviewer team with the following naming convention:

| Role | Round 1 name | Round 2+ name |
|---|---|---|
| Fix Crumb Gatherer N | `fix-cg-1`, `fix-cg-2`, ... | `fix-cg-r2-1`, `fix-cg-r2-2`, ... |
| Fix PC — Scope Verify | `fix-pc-scope-verify` | `fix-pc-scope-verify-r2` |
| Fix PC — Claims vs Code | `fix-pc-claims-vs-code` | `fix-pc-claims-vs-code-r2` |

Round suffix (`-r2`, `-r3`, etc.) increments with each review round to avoid name collisions within the persistent team.

#### Fix CG Prompt Structure

Fix Crumb Gatherers receive a lean prompt. The crumb is the source of truth — the CG does not need a full brief composed by the Queen.

```
You are fix-cg-N, a fix Crumb Gatherer in the Reviewer team.

Your task crumb: {crumb-id}
Run: crumb show <crumb-id>

The crumb contains root cause, affected surfaces, fix approach, and acceptance criteria.
Implement the fix. Follow the acceptance criteria exactly.

After committing:
1. Record your commit hash in your task crumb: crumb update <crumb-id> --note="commit: <hash>"
2. SendMessage to fix-pc-scope-verify: "Fix committed. Crumb: {crumb-id}. Commit: {hash}. Files changed: {list}."
Then go idle and wait.
```

The prompt is intentionally minimal. Crumb content drives the work, not the prompt text.

#### Fix Inner Loop Protocol

The fix inner loop runs between a fix DP and the two fix PCs within the team. The loop is fully asynchronous via SendMessage.

```
fix-cg-N  -->  [commit]  -->  SendMessage(fix-pc-scope-verify)
                                    |
                              fix-pc-scope-verify runs scope-verify check
                                    |
                         PASS ------+------ FAIL
                          |                   |
               SendMessage(fix-pc-claims-vs-code)   SendMessage(fix-cg-N) with specifics
                          |                   |
                    fix-pc-claims-vs-code  fix-cg-N iterates (max 2 retries total)
                    runs claims-vs-code        |
                          |             if retry limit hit → SendMessage(Queen) to escalate
                 PASS ----+---- FAIL
                  |              |
              fix-cg-N       SendMessage(fix-cg-N) with specifics
              goes idle       fix-cg-N iterates (max 2 retries total)
                              if retry limit hit → SendMessage(Queen) to escalate
```

**Retry limit**: Each fix CG has a maximum of 2 retries total across both scope-verify and claims-vs-code failures. On the third failure, the CG sends a message to the Queen with the failure details and goes idle. The Queen escalates to the user.

**fix-pc-scope-verify** (Haiku): Lightweight scope check — verifies the commit touches only the files listed in the crumb, no stray edits, and the commit message is well-formed. Fast and cheap.

**fix-pc-claims-vs-code** (Sonnet): Full claims-vs-code check — verifies the fix satisfies the crumb's acceptance criteria, tests pass, and no regressions introduced.

#### Wave Composition

Group fix agents by file using orchestration/reference/dependency-analysis.md to detect conflicts. Max 7 fix CGs per wave, no file overlap within a wave.

P1 and P2 fixes run in waves as follows:

```
Wave 1: [P1 fix-cg tasks] + [P2 fix-cg tasks]    (concurrent, no file overlap)
```

Unlike the old TDD workflow, P1 fixes do not require a separate test-writing wave in the persistent team design. The crumb's acceptance criteria serve as the verification specification; fix-pc-claims-vs-code enforces them.

Spawn fix-pc-scope-verify and fix-pc-claims-vs-code once per round (they serve all fix CGs in that round via SendMessage). Do not re-spawn them per CG.

#### Round Transition via SendMessage

After all fix CGs complete and fix-pc-claims-vs-code has issued PASS for each:

1. **Re-task Correctness reviewer**: SendMessage to `correctness` with:
   - Review round: N+1
   - Fix commit range: `{first-fix-commit}..{last-fix-commit}`
   - Changed files: `{list from git diff}`
   - Task IDs reviewed: `{crumb-ids fixed this round}`
   - Report output path: `{session-dir}/review-reports/correctness-r{N+1}-{timestamp}.md`

2. **Re-task Edge Cases reviewer**: SendMessage to `edge-cases` with:
   - Review round: N+1
   - Fix commit range: `{first-fix-commit}..{last-fix-commit}`
   - Changed files: `{list from git diff}`
   - Task IDs reviewed: `{crumb-ids fixed this round}`
   - Report output path: `{session-dir}/review-reports/edge-cases-r{N+1}-{timestamp}.md`

3. **Re-task Review Consolidator**: SendMessage to `ant-farm-review-consolidator` with:
   - Review round: N+1
   - Expected report paths: list the exact paths from step 1 and 2 above (consolidation brief's expected_paths is authoritative; typically correctness + edge cases, but include any split instances)
   - Report paths: paths from step 1 and 2 above
   - Output path: `{session-dir}/review-reports/review-consolidated-r{N+1}-{timestamp}.md`

4. **Clarity and Drift reviewers**: Leave idle after round 1. They are not re-tasked in subsequent rounds (round 2+ scopes only to fix commits, where style/drift issues are out of scope).

The loop continues until a round produces zero P1/P2 findings.

#### Re-Run Reviews (MANDATORY)

After all fix agents complete and SendMessage round-transition messages are sent:
- Correctness and Edge Cases reviewers produce round N+1 reports scoped to fix commits
- Review Consolidator consolidates and runs review-integrity
- review-integrity PASS + zero P1/P2 → loop ends; proceed to RULES.md Step 4
- review-integrity PASS + P1/P2 remain → return to "If P1 or P2 issues found" above (user prompt for round 2+)

### Handle P3 Issues (Queen's Step 3c)

> **Round 1 only.** In round 2+, P3s are auto-filed by Review Consolidator during consolidation (see "P3 Auto-Filing" above). This section applies only when round 1 terminates with P3 findings.

**Create "Future Work" trail if needed**:
```bash
# Check if future-work trail exists
crumb trail list | grep -i "future work" || \
crumb trail create --title "Future Work" --description "Low-priority polish and improvements from review sessions"
```

**File P3 crumbs under the trail**:
- All P3 crumbs from consolidation should be children of the future-work trail
- Use `crumb link <p3-crumb-id> --parent <future-work-trail-id>` for each P3 issue
- These can be addressed in future sessions
- No immediate action required — they're queued for later

After handling P3 issues, proceed to RULES.md Step 4 (Documentation — update README and CLAUDE.md only).
The Scribe authors the session CHANGELOG entry at Step 5.
