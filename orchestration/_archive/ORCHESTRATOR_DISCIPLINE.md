# The Queen Discipline

When orchestrating multi-agent work sessions, Claude Code should follow these principles to preserve context and maximize efficiency.

## Core Principle: Information Diet

**The Queen's window is a monitoring hub, not an implementation workspace.**

### What TO Read (Metadata Only)
✅ Task definitions (`bd show <id>`)
✅ File lists (`ls`, `git status`, `git log --oneline`)
✅ Dependency graphs (`bd blocked`, `bd show <id>` for blocks/blockedBy)
✅ Agent progress notifications
✅ Commit messages and summaries
✅ High-level documentation (CLAUDE.md, README.md structure only)

### What NOT to Read (Implementation Details)
❌ Source code files (*.py, *.js, *.ts, etc.)
❌ Templates (*.html, *.jinja2, etc.)
❌ Data files (*.yaml, *.json, etc.) unless checking format
❌ Test files (test_*.py, *.spec.js, etc.)
❌ Configuration files (unless diagnosing agent spawn issues)

**Why:** Reading implementation files consumes valuable context window that should be reserved for:
1. Tracking multiple concurrent Dirt Pushers
2. Monitoring progress across task groups
3. Planning next waves of work
4. Handling errors and conflicts
5. Final documentation coordination

## Recent Improvements (Feb 2026 - Epic 74g Lessons)

**Failure Mode Discovered**: Epic 74g Wave 1 — work scrambling when 3 agents worked on same file in parallel without line-level boundaries.

**What Happened**:
- Agent 74g.6 (add comments) also removed foundingDate filter (74g.7's task)
- Agent 74g.7 (remove foundingDate filter) found it done, made sameAs conditional (74g.4's task)
- Agent 74g.4 (make sameAs conditional) found it done, only added data to site.yaml
- Result: All functional work complete, but work attribution scrambled and summary docs misleading

**Root Causes**:
1. No file-level locking or serialization for same-file tasks
2. Agents were "helpful" and fixed adjacent issues they noticed
3. No real-time scope verification between agent commits
4. Checkpoint A verified prompts but not line-level specificity

**Improvements Added**:
1. **Checkpoint A.5** (Post-Commit Scope Verification) — Lightweight haiku check after each commit verifies files changed match expected scope. Catches scope creep before next agent spawns.
2. **Enhanced Checkpoint A** — Now requires line number specificity (e.g., "lines 23-24" not just "file.py"). Prevents vague file-level scope that invites "while I'm here" fixes.
3. **Anti-Scope-Creep Prompt Template** — Aggressive boundary language ("DO NOT fix other issues EVEN IF obvious") with explicit "Adjacent Issues Found" documentation section.
4. **Conflict Risk Assessment** — Pre-flight file modification matrix analysis with LOW/MEDIUM/HIGH risk tiers and corresponding serialization strategies.

**When to Apply** (immediate effect for all future multi-agent sessions):
- ✅ Always use anti-scope-creep template for Dirt Pushers
- ✅ Always run Checkpoint A.5 after each commit in multi-agent waves
- ✅ Always assess file conflict risk before spawning (create modification matrix)
- ✅ Serialize tasks when 3+ agents touch the same file (HIGH risk)

## Agent Spawn Patterns

### Pattern 1: File-Based Grouping (Prevents Conflicts)

```python
# Group tasks by primary file modified
groups = {
    'build.py': [task1, task2, task3],      # Same agent
    'site.yaml': [task4, task5],            # Same agent
    'templates/index.html': [task6, task7], # Same agent
}

# Spawn one agent per group
for file, tasks in groups.items():
    spawn_agent(
        subagent_type=choose_specialist(file),
        tasks=tasks,
        instruction="Work on all tasks for {file} together to avoid conflicts"
    )
```

**Conflict Risk Assessment** (use BEFORE spawning):

1. **Create file modification matrix** from `bd show` outputs:
   ```
   templates/macros/jsonld.html:
     - 74g.4 (sameAs field, lines 95-96)
     - 74g.7 (foundingDate field, line 94)
     - 74g.9 (@id property, line 10)
     - 74g.10 (image property, lines 23-24)
     - 74g.11 (wrap blocks, lines 50-80)
   ```

2. **Assess conflict risk**:
   - **LOW**: Different files, or same file with non-overlapping line ranges >10 lines apart
   - **MEDIUM**: Same file, line ranges within 10 lines of each other
   - **HIGH**: 3+ tasks on same file, or overlapping line ranges

3. **Choose strategy**:
   - **LOW risk** → Parallel spawn (3-7 agents)
   - **MEDIUM risk** → Wave-based (2-3 agents per wave, serialize overlapping ranges)
   - **HIGH risk** → Serial execution (one agent at a time) OR bundle into single agent

**Known failure mode**: Epic 74g Wave 1 spawned 3 agents in parallel on `jsonld.html` without line range analysis. Result: work scrambling (74g.6 did 74g.7's work, 74g.7 did 74g.4's work). Prevention: Use wave-based or serial execution for HIGH risk scenarios.

### Pattern 2: Dependency-Aware Sequencing

```python
# Multi-file tasks must wait for single-file tasks
dependencies = {
    'cross-template-task': ['index-task', 'canvas-work-task'],
    'integration-test': ['all-unit-tests'],
}

# Spawn with explicit dependency waiting
spawn_agent_after_completion(
    task='cross-template-task',
    wait_for=['index-task', 'canvas-work-task'],
)
```

### Pattern 3: Priority Tier Batching

```bash
# P1 tasks (critical bugs) → spawn immediately, all parallel
# P2 tasks (high priority) → spawn after P1 OR in parallel if no file conflicts
# P3 tasks (polish) → spawn only after P1+P2 complete

# This session's pattern:
# Wave 1: 7 P1 tasks (original beads)
# Wave 2: 18 P2 tasks (edge cases from reviews) - 6 agents, file-grouped
# Wave 3: 30 P3 tasks (clarity + excellence) - 6 agents, file-grouped
```

## Information Diet for Agents

**CRITICAL**: Beads contain pre-digested context. Extract and provide it to agents to prevent wasteful exploration.

### What Beads Contain (Don't Make Agents Re-Discover)

Every bead description includes:
- ✅ **Root cause** - The exact problem and why it exists
- ✅ **Affected surfaces** - Specific files and line numbers
- ✅ **Expected vs actual behavior** - What should happen vs what does
- ✅ **Fix description** - High-level approach (agents still design 4+ detailed approaches)
- ✅ **Acceptance criteria** - Testable success conditions

### The Queen's Extraction Pattern

Before spawning an agent, extract this info from `bd show <id>`:

```bash
bd show <task-id>  # Read ONCE in the Queen's window

# Extract and provide to agent:
# - Affected files/lines from "Affected surfaces:" section
# - Root cause from "Root cause:" section
# - Acceptance criteria from "Acceptance criteria:" section
```

### Agent Prompt: What to Include

**✅ DO provide:**
- Exact file paths and line numbers from bead
- Root cause explanation from bead
- Acceptance criteria checklist from bead
- Scope boundaries: "Read ONLY: build.py lines 200-250, site.yaml contact section"

**❌ DON'T say:**
- "Read the codebase and understand the problem" (too broad)
- "Explore the templates to find usage" (bead already lists usage)
- "Investigate which files are affected" (bead already specifies)

### Example: Before vs After

**❌ BEFORE (wasteful):**
```markdown
Fix contact validation bug (hs_website-gat).
Read the codebase and understand what fields are missing from validation.
```

**✅ AFTER (surgical):**
```markdown
Fix contact validation bug (hs_website-gat).

**Scope**: build.py line 621 only
**Problem**: required_contact_fields missing 3 fields: sms_number, email_subject, message_template
**Evidence**: Templates reference these fields at:
- base.html:L15-17, L37, L40
- header.html:L31
- hero.html:L24
- index.html:L60
- canvas-work.html:L24

**Read ONLY**: build.py lines 610-630 (validation function)

Your task: Design 4+ approaches to add these 3 fields to validation, select best, implement, verify.
```

## Agent Prompt Template

⚠️ **MANDATORY**: Every spawned Dirt Pusher MUST receive ALL sections below. All 6 steps are required — skipping Step 2 (Design), Step 4 (Correctness Review), or Step 6 (Summary Doc) is a process failure. Copy this template verbatim and fill in the placeholders.

```markdown
Execute <task-type> for <file-or-component>:

Tasks: <task-id-1>, <task-id-2>, ...

## Context (from bead - do not re-discover)
- **Affected files**: <list from bead with line numbers>
- **Root cause**: <copy from bead>
- **Expected behavior**: <copy from bead>
- **Scope boundaries**: Read ONLY the files/lines listed above
- **Epic ID**: <epic-id or _standalone>
- **Summary output path**: `.beads/agent-summaries/<epic-id>/<task-id>.md`

---

For each task, execute these 6 steps in order:

## Step 1: Claim
- Run `bd show <id>` to get full details and acceptance criteria
- Run `bd update <id> --status=in_progress` to claim

## Step 2: Design (MANDATORY — do not skip)
Design at least 4 **genuinely distinct** approaches to solve the problem.

**"Distinct" means**: approaches must differ in algorithm, architecture, or data model — not just implementation detail. Each approach must identify a unique tradeoff (e.g., "optimizes for speed at cost of memory" vs. "optimizes for readability at cost of performance"). If two approaches have the same tradeoff profile, they are not distinct.

For each approach:
- Describe the strategy in 1-2 sentences
- List pros and cons
- Identify risks
- State the primary tradeoff this approach makes

Then select the best approach (or create a hybrid that combines strengths from multiple approaches). Document your choice and reasoning before writing any code. When rejecting an approach, reference at least one specific weakness from a rejected alternative.

## Step 3: Implement
Implement the chosen approach. Write clean, minimal code that satisfies the acceptance criteria.

## Step 4: Per-File Correctness Review (MANDATORY — do not skip)
After implementation, review EVERY file you changed or created:
- Re-read each file in full
- Verify it meets all acceptance criteria from `bd show`
- Check for logic errors, typos, missing edge cases
- Verify cross-file consistency (do references between files still work?)
- Run any available build/test commands to validate
- If you find issues, fix them before proceeding

**Assumptions audit** (MANDATORY): Document in your summary:
1. **Assumptions stated**: List what you assumed about input format, execution context, and dependencies
2. **What could go wrong**: List 3 specific failure scenarios for your implementation (not generic risks — scenarios specific to your code changes)
3. **Mitigation**: For each failure scenario, explain why your implementation handles it or why it's acceptable

## Step 5: Commit
- `git pull --rebase && git add <files> && git commit -m "<type>: <description> (<task-id>)"`
- **MANDATORY**: Include the task ID in parentheses at the end of the commit message (e.g., `fix: handle None input (hs_website-abc)`)
- Record your commit hash in the summary doc (Step 6) so Checkpoint B can identify your commits without scanning `git log`

## Step 6: Write Summary Doc (MANDATORY — do not skip)
Write a structured summary to `.beads/agent-summaries/<epic-id>/<task-id>.md` using the Write tool.
(Use `_standalone` if the task has no epic parent. Create the directory with `mkdir -p` if needed.)
The summary MUST contain ALL of these sections — incomplete summaries will be rejected:

```markdown
# Summary: <task-id>
**Task**: <title from bd show>
**Agent**: <subagent type>
**Status**: completed | failed
**Files changed**: <list>

## Approaches Considered
### 1. <approach name>
**Strategy**: <1-2 sentences>
**Pros**: <bullet list>
**Cons**: <bullet list>
### 2. <approach name>
...
### 3. <approach name>
...
### 4. <approach name>
...

## Selected Approach
**Choice**: <which approach or hybrid>
**Rationale**: <why this was best>

## Implementation
<brief description of what was done>

## Correctness Review
For each file changed:
### <filename>
- **Re-read**: yes
- **Acceptance criteria verified**: <list each criterion + PASS/FAIL>
- **Issues found**: <none, or describe what was found and fixed>
- **Cross-file consistency**: <verified against which files>

## Build/Test Validation
- **Command run**: <what was run>
- **Result**: <pass/fail + output summary>

## Acceptance Criteria
- [ ] <criterion 1> — PASS/FAIL
- [ ] <criterion 2> — PASS/FAIL
- [ ] ...
```

After all tasks in this batch:
- Run `git pull --rebase` to stack commits cleanly
- Close all tasks: `bd close <id1> <id2> ...`
- DO NOT push to remote (the Queen handles this)
- DO NOT modify documentation files (CHANGELOG, README, CLAUDE.md)

Focus: <specific guidance for this file/component>
```

### The Queen's Checklist (verify before spawning)

Before sending any agent prompt, confirm it includes:
- [ ] **Context section** with exact files/lines from bead (pre-digested, not "discover the problem")
- [ ] **Scope boundaries** limiting what files to read
- [ ] Root cause and acceptance criteria extracted from bead
- [ ] **Step 1**: `bd show` + `bd update --status=in_progress`
- [ ] **Step 2**: "Design at least 4 approaches" with pros/cons (MANDATORY)
- [ ] **Step 3**: Implementation instructions
- [ ] **Step 4**: "Review EVERY file you changed" with explicit checks (MANDATORY)
- [ ] **Step 5**: Commit instructions with `git pull --rebase`
- [ ] **Step 6**: Write summary doc to `.beads/agent-summaries/<epic-id>/<task-id>.md` (MANDATORY)

If any checkbox is missing, DO NOT spawn the agent — fix the prompt first.

**External validation**: After composing the prompt, run **Checkpoint A (Pre-Spawn Prompt Audit)** to independently verify this checklist. See "Verification Checkpoint System" section below.

### Anti-Scope-Creep Prompt Template

**When to use**: For all Dirt Pushers, especially when multiple tasks touch the same file.

**Why**: Agents are helpful by nature and will fix adjacent problems they notice ("while I'm here..."). This creates work attribution scrambling and misleading audit trails.

**Known failure mode**: Epic 74g Wave 1 — agents 74g.6, 74g.7, and 74g.4 did each other's work because no explicit boundaries prevented "helpful" adjacent fixes.

**Template** (insert after Context section, before Step 1):

```markdown
## 🚨 CRITICAL SCOPE BOUNDARY 🚨

Your task is ONLY to {specific task description}.

**DO NOT**:
- Fix other issues you notice in the same file
- Make "while you're here" improvements to adjacent code
- Combine this task with related work
- Edit lines/sections outside the specified range

**EVEN IF**:
- You see an obvious bug nearby
- You see inefficient code in the same file
- You see a related improvement opportunity
- The fix would be "trivial" or "just one line"

If you find other issues during your work:
1. Document them in your summary doc under "Adjacent Issues Found"
2. DO NOT FIX THEM
3. Let the Queen create separate tasks

**Acceptance criterion**: ONLY the files and line ranges listed in Step 3 may be edited. Any additional changes are a scope violation.
```

**Customization**:
- Replace `{specific task description}` with the actual task (e.g., "add the business_image field and update the image property")
- Add file-specific boundaries (e.g., "Edit lines 23-24 only" or "Only modify the sameAs field")
- List specific off-limit areas if needed (e.g., "Do NOT edit foundingDate, @id, or defensive guards")

### Nitpicker Checklist (verify before launching team)

Before launching the review agent team, confirm:
- [ ] All 4 teammate prompts include review scope (list of all files to review)
- [ ] Each teammate has focus areas specific to their review type
- [ ] Catalog phase instructions included (find all, group preliminarily)
- [ ] Report format instructions included (use standard teammate report format)
- [ ] Each prompt says "Do NOT file beads — Big Head handles all bead filing"
- [ ] Messaging guidelines included (what to share, what not to share)
- [ ] Reports write to `.beads/agent-summaries/<epic-id>/review-reports/<review-type>-review-<timestamp>.md`

### Lead Consolidation Checklist (after all teammates finish)

Before filing beads, confirm Big Head has:
- [ ] Read all 4 teammate reports
- [ ] Merged duplicate findings across reviews
- [ ] Grouped all findings by root cause (not per-occurrence)
- [ ] Filed ONE bead per root cause with all affected surfaces listed
- [ ] Written consolidated summary to `.beads/agent-summaries/<epic-id>/review-reports/review-consolidated-<timestamp>.md`

If any checkbox is missing, DO NOT proceed — complete the missing steps first.

## Monitoring Protocol

### Progress Tracking

Use the Task tool to create monitoring entries:

```python
TaskCreate(
    subject="Monitor: <agent-group-name>",
    description="Agent <id> working on <N> tasks for <file>",
    activeForm="Monitoring <agent-group-name> agent"
)

# Update when agent completes:
TaskUpdate(taskId=X, status="completed")
```

### When Agents Complete

1. ✅ Update tracking task to completed
2. ✅ Read agent summary from notification (don't re-read files!)
3. ✅ Check git log for new commits
4. ✅ **Spawn Checkpoint B (Substance Verification)** — cross-checks agent claims against actual code and git diffs (see "Verification Checkpoint System" below)
5. ✅ Note any errors or blockers
6. ✅ If queue has more work, spawn next agent to backfill

### When to Intervene

**Only read implementation files when:**
- Agent reports error you cannot diagnose from summary
- Agent produces unexpected result requiring investigation
- Verification agent reports FAIL on the summary doc
- User explicitly asks you to review specific code

Otherwise, trust agent summaries and commit messages.

### Mandatory Review Gate (NEVER SKIP)

**CRITICAL**: After ALL Dirt Pushers complete AND all Checkpoint B verifications pass, you MUST launch the Nitpickers (Step 3b). **This is NOT optional and does NOT require user permission.**

**Why reviews are mandatory**:
- Checkpoints verify process compliance and individual task claims
- Reviews verify cross-file integration, edge cases, and holistic code quality
- Multi-agent sessions can introduce subtle integration issues invisible to per-task verification
- Reviews catch architectural concerns and patterns that individual agents miss
- Second set of eyes on the complete changeset, not just individual commits

**Do NOT**:
- Ask user "should I run reviews?" - the answer is always YES
- Skip reviews because "checkpoints already passed" - checkpoints ≠ reviews
- Skip reviews for "small changes" - reviews scale efficiently via parallel execution

**Proceed directly to Step 3b** (Launch the Nitpickers with 4 parallel reviewers) after transition gate checklist passes.

## Verification Checkpoint System

Three checkpoints cross-check agent claims against ground truth (actual code, git diffs, bead records). This replaces the previous single-pass "Summary Doc Verification" which only checked structural completeness.

**Proof artifacts directory**: `.beads/agent-summaries/<epic-id>/verification/pest-control/` (all verification reports generated by Pest Control subagent)
(Cross-epic verification files are duplicated to each participating epic. Cross-epic batches and consolidations go to `_standalone/verification/pest-control/`.)

### Hard Gate Enforcement

Checkpoints are **hard gates**, not advisory. The Queen MUST NOT proceed past a gate until the checkpoint PASS artifact exists on disk.

| Gate | Blocks | Required Artifact |
|------|--------|-------------------|
| Checkpoint A PASS | Agent spawn | `.beads/agent-summaries/<epic-id>/verification/pest-control/pest-control-*-checkpoint-a-*.md` with PASS verdict |
| Checkpoint B PASS | Task closure (`bd close`) | `.beads/agent-summaries/<epic-id>/verification/pest-control/pest-control-*-checkpoint-b-*.md` with PASS verdict |
| Checkpoint C PASS | Presenting results to user | `.beads/agent-summaries/<epic-id>/verification/pest-control/pest-control-*-consolidation-checkpoint-c-*.md` with PASS verdict |

**Enforcement rule**: Before executing the blocked action, the Queen MUST:
1. Verify the artifact file exists (`ls` the path)
2. Read the verdict line and confirm it says PASS
3. If the artifact is missing or verdict is not PASS, stop and run/re-run the checkpoint

**Known failure mode**: In the Epic 3 session, Steps 2 (Design) and 4 (Correctness Review) were skipped entirely — a critical process failure that shipped unverified work. Hard gates exist to prevent this exact scenario.

### Retry and Timeout Limits

| Situation | Max Retries | After Limit |
|-----------|-------------|-------------|
| Agent fails Checkpoint B | 2 | Escalate to user with full context |
| Checkpoint C fails | 1 | Present to user with verification report attached |
| Agent hasn't committed within 15 turns | 0 | Check agent status; if stuck, escalate to user |
| Total retries across all agents per session | 5 | Stop spawning new work; triage existing failures with user |

**Budget tracking**: The Queen MUST track retry count in the session state file (see "Session State Persistence" below). If total retries reach 5, pause all new spawns and present the failure summary to the user.

### Session State Persistence

The Queen MUST maintain a session state file at `.beads/agent-summaries/_session-<session-id>/queen-state.md` to survive context compaction. Update this file after EVERY agent event (spawn, completion, checkpoint result, error).
This file lives in the session directory (`.beads/agent-summaries/_session-<session-id>/`), is session-scoped, and the entire session directory is deleted during "Landing the Plane" cleanup.

```markdown
# The Queen Session State
**Updated**: <timestamp>
**Session start**: <timestamp>
**Strategy**: <chosen execution strategy>

## Agent Registry
| Agent Name | Task IDs | Files Assigned | Status | Commit Hash | Checkpoint B |
|------------|----------|----------------|--------|-------------|--------------|
| <name>     | <ids>    | <files>        | spawned/completed/errored | <hash> | PASS/PENDING/FAIL |

## Checkpoint Status
| Checkpoint | Target | Result | Artifact Path |
|------------|--------|--------|---------------|
| A | <agent/team> | PASS/FAIL | <path> |
| B | <task-id> | PASS/PARTIAL/FAIL | <path> |
| C | consolidation | PASS/FAIL | <path> |

## Queue Position
- **Completed**: <N> of <total> tasks
- **In progress**: <list>
- **Remaining**: <list>
- **Retry budget**: <used>/<max 5>

## Error Log
- <timestamp>: <agent> — <error summary>
```

**Recovery**: After context compaction or `bd prime`, read this file to restore the Queen's state. Do not rely on conversation context alone.

### Epic ID Resolution for File Paths

When constructing paths that include `<epic-id>`, resolve the epic ID from the task ID:

| Task ID Pattern | Epic ID | Example |
|----------------|---------|---------|
| `hs_website-<X>.<N>` | `X` | `hs_website-74g.1` → `74g` |
| `<X>.<N>` (non-prefixed) | `X` | `74g.8` → `74g` |
| No epic parent | `_standalone` | `hs_website-596y` → `_standalone` |

**Directory creation**: Always run `mkdir -p .beads/agent-summaries/<epic-id>/verification/pest-control/` before writing verification artifacts. Always run `mkdir -p .beads/agent-summaries/<epic-id>/review-reports/` before writing review reports.

**The Queen's responsibility**: The Queen MUST include `**Epic ID**` and `**Summary output path**` in the agent prompt context section. For review prompts, include all participating epic IDs and instruct reviewers to write reports to each epic's `review-reports/` directory.

**Review timestamp convention**: The Queen generates a single timestamp per review cycle (format: `YYYYMMDD-HHMMSS`) and passes the exact output filenames to each reviewer and Big Head. This prevents reviewers from independently generating different timestamps.

### Known Failure Modes

Document past process failures to prevent recurrence.

#### Epic 3: Skipped Design and Review Steps
**What happened**: Dirt Pushers skipped Step 2 (Design 4+ approaches) and Step 4 (Per-File Correctness Review) entirely. No checkpoint caught this because checkpoints weren't enforced as hard gates at the time.
**Impact**: Unreviewed, undesigned work shipped. Quality was unknown.
**Root cause**: Steps marked "MANDATORY" in the template but nothing verified compliance.
**Fix applied**: Hard gate enforcement (see above) — Checkpoint B now verifies approach substance and review evidence before allowing task closure.

### Default Subagent Types

Recommended agent types by task category. Projects can override these in their CLAUDE.md or MEMORY.md.

| Task Category | Subagent Type | Rationale |
|---------------|---------------|-----------|
| Template/Jinja2 work | `python-pro` | Python ecosystem expertise |
| Build system changes | `python-pro` | Build scripts are Python |
| CSS/HTML implementation | `nextjs-developer` or `javascript-pro` | Frontend expertise |
| Build verification | `debugger` | Diagnostic and troubleshooting focus |
| Nitpickers (all 4) | `code-reviewer` / `sonnet` | Code analysis focus |
| Review lead (consolidation) | `opus` | Cross-report judgment, dedup, priority calibration |
| General implementation | Match specialist to primary file type | Best domain expertise |

### Pest Control: The Verification Subagent

All checkpoint verifications (A, B, C) are executed by **Pest Control**, a dedicated verification subagent that cross-checks orchestrator and agent work against ground truth.

**Pest Control responsibilities:**
- Pre-spawn prompt audits (Checkpoint A)
- Post-completion substance verification (Checkpoint B)
- Consolidation integrity audits (Checkpoint C)

**Artifact naming conventions:**
- **Task-specific checkpoints (A, B):** `pest-control-<task-id>-checkpoint-<step>-<timestamp>.md`
  - Example: `pest-control-74g1-checkpoint-a-20260215-001145.md`
  - Example: `pest-control-74g1-checkpoint-b-20260215-003422.md`
- **Consolidation audits (C):** `pest-control-<epic-id>-consolidation-checkpoint-c-<timestamp>.md`
  - Example: `pest-control-74g-consolidation-checkpoint-c-20260215-010520.md`
- **Storage:** All artifacts in `.beads/agent-summaries/<epic-id>/verification/pest-control/`
  Cross-epic verification files are duplicated to each participating epic's verification directory.

**Task ID format:**
- Use full task ID suffix (e.g., `74g1` from `hs_website-74g.1`) - epic is already embedded
- Use `standalone` for tasks without epic parent

**Epic ID format (Checkpoint C only):**
- Use 3-char epic suffix (e.g., `74g` from `hs_website-74g`)
- Use `multi` for consolidations spanning multiple epics

**Timestamp format:** `YYYYMMDD-HHMMSS`

**Backward compatibility:** All verification artifacts (including pre-Feb 2026 legacy files) have been migrated to epic subdirectories. Structure: `.beads/agent-summaries/<epic-id>/verification/pest-control/` for Pest Control artifacts, `.beads/agent-summaries/<epic-id>/verification/` for legacy (non-Pest Control) artifacts.

### Checkpoint A: Pre-Spawn Prompt Audit

**When**: After orchestrator composes agent prompt(s), BEFORE spawning
**Applies to**: Dirt Pushers AND the Nitpickers
**Model**: `haiku` (mechanical checklist — cheap, fast)
**Agent type**: `code-reviewer`

**Why**: The orchestrator has a self-policing checklist, but nobody audits the orchestrator. Catching prompt defects before spawn is 100x cheaper than catching them after.

#### Checkpoint A Prompt Template (Dirt Pushers)

```markdown
**Pest Control verification - Checkpoint A (Pre-Spawn Prompt Audit)**

You are **Pest Control**, the verification subagent. Your role is to audit the composed agent prompt before spawn. See "Pest Control: The Verification Subagent" section above for full conventions.

Audit the following Dirt Pusher prompt for completeness and correctness.
Do NOT execute the prompt — only verify its contents.

<prompt>
{paste the composed agent prompt here}
</prompt>

## Verify each item (PASS or FAIL with evidence):

1. **Real task IDs**: Contains actual task IDs (e.g., `hs_website-abc`), NOT placeholders like `<task-id>` or `<id>`
2. **Real file paths**: Contains actual file paths with line numbers (e.g., `build.py:L200`), NOT placeholders like `<list from bead>` or `<file>`
3. **Root cause text**: Contains a specific root cause description, NOT `<copy from bead>` or similar placeholders
4. **All 6 mandatory steps present**:
   - Step 1: `bd show` + `bd update --status=in_progress`
   - Step 2: "Design at least 4 approaches" (MANDATORY keyword present)
   - Step 3: Implementation instructions
   - Step 4: "Review EVERY file" or per-file correctness review (MANDATORY keyword present)
   - Step 5: Commit with `git pull --rebase`
   - Step 6: Write summary doc to `.beads/agent-summaries/<epic-id>/`
5. **Scope boundaries**: Contains explicit limits on which files to read (not open-ended "explore the codebase")
6. **Commit instructions**: Includes `git pull --rebase` before commit
7. **Line number specificity** (NEW - prevents scope creep): File paths include specific line ranges or section markers
   - ✅ PASS: "Edit templates/macros/jsonld.html lines 23-24 (image property only)"
   - ⚠️ WARN: "Edit templates/macros/jsonld.html (image property)" — file-level scope, acceptable if small file
   - ❌ FAIL: "Edit templates/macros/jsonld.html" — vague, high scope creep risk

## Verdict
- **PASS** — All 6 checks pass
- **FAIL: <list each failing check with evidence>**

Write your verification report to:
`.beads/agent-summaries/<epic-id>/verification/pest-control/pest-control-{task-id}-checkpoint-a-{timestamp}.md`

Where:
- task-id: Full task ID suffix (e.g., `74g1` from `hs_website-74g.1`), or `standalone` if no epic
- timestamp: YYYYMMDD-HHMMSS format
```

#### Checkpoint A Prompt Template (The Nitpickers)

See `QUALITY_REVIEW_TEMPLATES.md` "Verification Checkpoints" section for the review-specific version.

#### The Queen's Response to Checkpoint A

**On PASS**: Proceed to spawn the agent(s).

**On FAIL**: Fix the specific gaps in the prompt, then re-run Checkpoint A. Do NOT spawn until PASS.

---

### Checkpoint A.5: Post-Commit Scope Verification (Lightweight)

**When**: After agent commits, BEFORE spawning next agent in same wave
**Model**: `haiku` (mechanical file list comparison — cheap, fast)
**Agent type**: `code-reviewer`

**Why**: Catches scope creep in real-time between agents, before Checkpoint B runs. Prevents cascading work attribution errors when multiple agents work on related files.

**Known failure mode**: In Wave 1 of Epic 74g, agent 74g.6 (comment task) made functional changes belonging to 74g.7 (foundingDate filter), which cascaded into 74g.7 making changes belonging to 74g.4 (sameAs conditional). Checkpoint A.5 would have caught the first scope violation immediately.

#### Checkpoint A.5 Prompt Template

```markdown
**Pest Control verification - Checkpoint A.5 (Post-Commit Scope Verification)**

You are **Pest Control**, the verification subagent. Your role is to verify agent commits match task scope.

**Task ID**: {task-id}
**Expected files** (from `bd show {task-id}`): {list files from task description}

## Verification Steps

1. Run `git log --oneline -1` to get the latest commit hash
2. Run `git show --stat {commit-hash}` to list files changed
3. Compare changed files to expected files from task description

## Check

**Files changed match expected scope?**
- ✅ All changed files are in the expected list
- ⚠️ Extra files changed (e.g., regenerated HTML from template changes) — check if legitimate
- ❌ Unexpected files changed (e.g., different template, unrelated config)

## Verdict
- **PASS** — Files match expected scope (or extra files are legitimate build outputs)
- **WARN: <list extra files with rationale>** — Extra files need the Queen's review (e.g., "index.html regenerated from template change — legitimate")
- **FAIL: <list unexpected files>** — Agent edited files outside task scope (scope creep detected)

Write your verification report to:
`.beads/agent-summaries/<epic-id>/verification/pest-control/pest-control-{task-id}-checkpoint-a5-{timestamp}.md`
```

#### The Queen's Response to Checkpoint A.5

**On PASS**: Continue normally (run Checkpoint B, backfill queue).

**On WARN**: Review the extra files. If legitimate (e.g., HTML rebuild from template), accept and continue. If suspicious, escalate to user.

**On FAIL (scope creep detected)**:
1. Log the violation in the Queen's state
2. Mark task with scope creep note in final closure
3. Check if overlapping work affects queued agents (may need to adjust or cancel)
4. Continue but document for post-mortem

**Do NOT retry** — the code is already committed. Focus on documenting and preventing cascade effects.

---

### Checkpoint B: Substance Verification

**When**: After each agent completes (Dirt Pusher or Nitpicker)
**Model**: `sonnet` (needs judgment to compare claims against actual code)
**Agent type**: `code-reviewer`

**Why sonnet not haiku**: This checkpoint reads actual source code and compares it to report claims. "Is this finding description accurate for what's at build.py:L200?" requires understanding both the code and the claim. Haiku can check format; sonnet can check truth.

#### Checkpoint B Prompt Template (Dirt Pushers)

```markdown
**Pest Control verification - Checkpoint B (Substance Verification)**

You are **Pest Control**, the verification subagent. Your role is to cross-check agent claims against ground truth. See "Pest Control: The Verification Subagent" section above for full conventions.

Verify the substance of the Dirt Pusher's work by cross-checking claims against ground truth.

**Summary doc**: `.beads/agent-summaries/<epic-id>/{task-id}.md`
**Task ID**: {task-id}

Read the summary doc first, then perform these 4 checks:

## Check 1: Git Diff Verification
Run `git log --oneline -5` to identify the agent's commit(s), then run `git diff {before-commit}..{after-commit}` (or `git show {commit}` for single commits).
Compare the actual changes to the summary doc's "Files changed" and "Implementation" sections.
- Do the claimed file changes actually exist in the diff?
- Are there files changed in the diff but NOT listed in the summary?
- Are there files listed in the summary but NOT changed in the diff?

## Check 2: Acceptance Criteria Spot-Check
Run `bd show {task-id}` to get the task's acceptance criteria.
Pick the 2 most critical criteria. For each:
- Read the actual code that should satisfy this criterion
- Verify it's genuinely met (not just marked "PASS" in the summary)
- Quote the specific code that satisfies (or fails to satisfy) each criterion

## Check 3: Approaches Substance Check
Read the 4+ approaches in the summary doc.
- Are they genuinely distinct strategies? (e.g., different algorithms, different data structures, different architectural patterns)
- Or are they trivial variations? (e.g., "use a list" vs "use a tuple", or the same approach with minor cosmetic differences)
- Flag any approaches that are not meaningfully distinct

## Check 4: Correctness Review Evidence
The summary claims "Re-read: yes" for each file.
Pick 1 changed file and read the agent's correctness notes for it.
- Are the notes specific to the actual file content? (e.g., "verified that line 42 handles the None case")
- Or are they generic boilerplate? (e.g., "no issues found, code looks clean")
- Read the actual file and verify the notes are accurate

## Verdict
- **PASS** — All 4 checks confirm substance
- **PARTIAL: <list checks that failed with evidence>** — Some checks failed
- **FAIL: <list all failures with evidence>** — Multiple checks failed or critical fabrication detected

Write your verification report to:
`.beads/agent-summaries/<epic-id>/verification/pest-control/pest-control-{task-id}-checkpoint-b-{timestamp}.md`

Where:
- task-id: Full task ID suffix (e.g., `74g1` from `hs_website-74g.1`)
- timestamp: YYYYMMDD-HHMMSS format
```

#### Checkpoint B Prompt Template (Nitpickers)

See `QUALITY_REVIEW_TEMPLATES.md` "Verification Checkpoints" section for the review-specific version.

#### The Queen's Response to Checkpoint B

**On PASS**: Proceed normally (close task, backfill queue).

**On PARTIAL or FAIL**:
1. Log the failure and specific gaps
2. Resume the original agent (using its agent ID) with a prompt:
   ```
   Your work was substance-verified and gaps were found:
   <paste specific failures from verification report>
   Please address these gaps: re-do the missing work, update your summary doc, and recommit.
   ```
3. Re-run Checkpoint B after the agent updates
4. If it fails a second time, flag to user for manual review

---

### Checkpoint C: Consolidation Audit

**When**: After Big Head consolidation (after all 4 review reports merged and beads filed)
**Model**: `haiku` (mechanical counting + record-checking)
**Agent type**: `code-reviewer`

See `QUALITY_REVIEW_TEMPLATES.md` "Verification Checkpoints" section for the full prompt template (8 checks). Summary of what it validates:

0. **Report existence verification** — all 4 report files exist at expected paths
1. **Finding count reconciliation** — every finding accounted for (standalone, merged, or marked duplicate)
2. **Bead existence check** — `bd show <id>` confirms each filed bead exists
3. **Bead quality check** — each bead has root cause, file:line refs, acceptance criteria, suggested fix
4. **Priority calibration** — P1 beads describe genuinely blocking issues, not style preferences
5. **Traceability matrix** — Finding → Root Cause Group → Bead ID, no orphans
6. **Deduplication correctness** — merged groups share common code/pattern, merge rationale is coherent
7. **Bead provenance audit** — all open beads filed during consolidation, not during reviews

**Proof artifact**: `.beads/agent-summaries/<epic-id>/verification/pest-control/pest-control-{epic-id}-consolidation-checkpoint-c-{timestamp}.md`

## Prompt Preparation Optimization

**IMPORTANT**: Prepare and verify prompts for future waves WHILE waiting for current wave to complete. This eliminates spawn latency between waves.

### Workflow:
1. **During Wave N**: Compose prompts for Wave N+1 and Wave N+2
2. **Run Checkpoint A** on all future wave prompts (verify in parallel)
3. **When Wave N completes**: Immediately spawn Wave N+1 (prompts already verified)
4. **Repeat**: Prepare Wave N+2 prompts while Wave N+1 runs

### Benefits:
- Eliminates 2-5 minute prompt composition delay between waves
- Catches prompt defects early (before wave is ready to start)
- Keeps the Queen's context focused on monitoring during active waves
- Reduces total session time by 20-30%

### Example:
```
Wave 1 agents spawn (time = 0 min)
  ↓ (While Wave 1 runs...)
Compose + verify Wave 2 & 3 prompts (time = 5 min)
Wave 1 completes (time = 20 min)
  ↓ (Immediately spawn, no delay)
Wave 2 agents spawn (time = 20 min)
  ↓ Total latency saved: ~3-5 min per wave
```

## Quality Review Protocol

**CRITICAL**: Reviews MUST use **Agent Teams** (TeamCreate + SendMessage), NOT plain Task tool subagents.

After all Dirt Pushers complete, launch reviews using **TeamCreate** to create the Nitpickers with 4 specialized reviewers running in parallel. The team structure enables cross-pollination between reviewers via SendMessage.

**DO NOT**:
- Use plain Task tool for reviews (no cross-agent communication)
- Use agent teams for implementation (use Task tool with run_in_background for implementation)
- Skip reviews (mandatory for all multi-agent sessions)

**Why Agent Teams for Reviews**:
- Enables SendMessage between reviewers for pattern sharing
- Supports lead consolidation with teammate reports
- Allows reviewers to coordinate on duplicate findings
- Provides structured report handoff to lead

See `QUALITY_REVIEW_TEMPLATES.md` for the full protocol:
1. Launch the Nitpickers with TeamCreate (4 specialized code-reviewer Nitpickers in parallel)
2. Teammates produce reports using SendMessage (do NOT file beads)
3. Lead reads all 4 reports, deduplicates by root cause, files beads
4. Then spawn Dirt Pushers for review-discovered issues (group by file, same pattern as original work)

## Session Closure Checklist

```markdown
Before saying "done":

- [ ] All spawned agents completed or errored (none stuck)
- [ ] All task tracking entries marked completed
- [ ] All beads tasks closed (bd close <ids>)
- [ ] Git status clean (no uncommitted changes)
- [ ] CHANGELOG.md updated with all changes
- [ ] README.md updated if structure changed
- [ ] CLAUDE.md updated if architecture changed
- [ ] Cross-references verified (no broken links)
- [ ] `git pull --rebase` (check for remote changes)
- [ ] `bd sync` (sync beads with remote)
- [ ] `git push` (MANDATORY - work not done until pushed!)
- [ ] `git status` shows "up to date with origin/main"
- [ ] Build/test quality gates passed
```

## Context Preservation Metrics

Track these to stay within limits:

- **Token budget usage:** Aim to finish with >50% remaining
- **File reads in orchestrator:** Should be <10 for 40+ task sessions
- **Agent count:** Max 7 concurrent, typical 5-6
- **Commit count:** Aim for <20 commits per session (batch related work)

## Anti-Patterns to Avoid

❌ **Reading every agent's output files** - Trust summaries
❌ **Spawning agents one at a time** - Batch by file/priority
❌ **Doing implementation work in the Queen's window** - Delegate everything
❌ **Re-reading the same metadata** - Read once, take notes
❌ **Pushing mid-session** - Only push at end (atomic deployment)
❌ **Updating docs per-agent** - Batch all doc updates at end
❌ **Verbose agent prompts** - Be concise, agents read their task details

## Success Indicators

✅ The Queen finishes with >50% token budget
✅ Zero merge conflicts (proper file grouping)
✅ All agents commit successfully
✅ Clean git history (sequential, meaningful commits)
✅ Comprehensive documentation updated once at end
✅ Successful push to remote
✅ User can resume work in next session with full context
