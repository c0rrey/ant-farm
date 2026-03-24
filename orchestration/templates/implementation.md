<!-- Reader: the Prompt Composer (implementation mode). The Orchestrator does NOT read this file. -->
# Implementer Templates

## Agent Prompt Template

**(MANDATORY)**: Every spawned Implementer MUST receive ALL sections below. All 7 steps are required — skipping Step 2 (Design), Step 2.5 (Write Tests), Step 4 (Correctness Review), or Step 6 (Summary Doc) is a process failure. Copy this template verbatim and fill in the placeholders.

```markdown
Execute {task-type} for {file-or-component}:

Tasks: {TASK_ID_1}, {TASK_ID_2}, ...

## Context (from crumb - do not re-discover)
- **Affected files**: {list-from-crumb}
- **Root cause**: {copy-from-crumb}
- **Expected behavior**: {copy-from-crumb}
- **Scope boundaries**: Read ONLY the files/lines listed above
- **Summary output path**: `{session-dir}/summaries/{TASK_ID}.md`

---

For each task, execute these 7 steps in order:

## Step 1: Claim
- Use the `crumb_show` MCP tool with `crumb_id: "<id>"` to get full details and acceptance criteria (CLI fallback: `crumb show <id>`)
- Use the `crumb_update` MCP tool with `status: "in_progress"` to claim (CLI fallback: `crumb update <id> --status=in_progress`)

## Step 2: Design (MANDATORY)
Design at least 4 **genuinely distinct** approaches to solve the problem.

**"Distinct" means**: approaches must differ in **algorithm, data structure, or architectural pattern**. Cosmetic variations (same algorithm with different parameters or names) do not count. Example: QuickSort and MergeSort are distinct (different algorithms). QuickSort with different pivot strategies is not distinct (same algorithm, different implementation detail).

For each approach:
- Describe the strategy in 1-2 sentences
- List pros and cons
- Identify risks
- State the primary tradeoff this approach makes

Then select the best approach (or create a hybrid that combines strengths from multiple approaches). Document your choice and reasoning before writing any code. When rejecting an approach, reference at least one specific weakness from a rejected alternative.

## Step 2.5: Write Tests (MANDATORY)
Before writing any implementation code, write failing tests that cover the acceptance criteria.

- Identify the test files relevant to this task (check `tests/` or the test suite for the affected component)
- Write failing tests for each acceptance criterion — tests should assert the expected post-implementation behavior
- Run the tests to confirm they fail (red phase): `python -m pytest <test-file> -x` or equivalent
- Commit the test files before implementing: `git add <test-files> && git commit -m "test: write failing tests for <task-id>"`

If the task has no testable code changes (e.g., pure documentation or config), note this explicitly and skip to Step 3.

## Step 3: Implement
Implement the chosen approach. Write clean, minimal code that satisfies the acceptance criteria. Run your tests after implementation to confirm they pass (green phase).

## Step 4: Per-File Correctness Review (MANDATORY)
After implementation, review EVERY file you changed or created:
- Re-read each file in full
- Verify it meets all acceptance criteria from `crumb_show` (or `crumb show` CLI)
- Check for logic errors, typos, missing edge cases
- Verify cross-file consistency (do references between files still work?)
- Run any available build/test commands to validate
- If you find issues, fix them before proceeding

**Assumptions audit** (MANDATORY) — Document in your summary:
1. **Assumptions stated**: List what you assumed about input format, execution context, and dependencies
2. **What could go wrong**: List 3 specific failure scenarios for your implementation (not generic risks — scenarios specific to your code changes)
3. **Mitigation**: For each failure scenario, explain why your implementation handles it or why it's acceptable

## Step 5: Commit
- `git pull --rebase && git add <files> && git commit -m "<type>: <description> (<task-id>)"`
- (MANDATORY): Include the task ID in parentheses at the end of the commit message (e.g., `fix: handle None input (my-project-abc)`)
- (MANDATORY) **Conditional Re-Review**: If `git pull --rebase` resolves any merge conflicts, you MUST repeat Step 4 (Per-File Correctness Review) on all files affected by the conflict resolution before committing. Conflict resolution can silently change code semantics. Verify the merged files are correct before proceeding.
- Record your commit hash in the summary doc (Step 6) so the claims-vs-code checkpoint can identify your commits without scanning `git log`

## Step 6: Write Summary Doc (MANDATORY)
Write a structured summary to `{session-dir}/summaries/{TASK_ID}.md` using the Write tool.
(the Orchestrator creates this directory at session start.)
The summary MUST contain ALL of these sections — incomplete summaries will be rejected:

```markdown
# Summary: {TASK_ID}
**Task**: {title-from-crumb-show}
**Agent**: {subagent-type}
**Status**: completed | failed
**Files changed**: {list}

## Approaches Considered
### 1. {approach name}
**Strategy**: {1-2 sentences}
**Pros**: {bullet list}
**Cons**: {bullet list}
### 2. {approach name}
...
### 3. {approach name}
...
### 4. {approach name}
...

## Selected Approach
**Choice**: {which approach or hybrid}
**Rationale**: {why this was best}

## Implementation
{brief description of what was done}

## Correctness Review
For each file changed:
### {filename}
- **Re-read**: yes
- **Acceptance criteria verified**: {list each criterion + PASS/FAIL}
- **Issues found**: {none, or describe what was found and fixed}
- **Cross-file consistency**: {verified against which files}

## Build/Test Validation
- **Command run**: {what was run}
- **Result**: {pass/fail + output summary}

## Acceptance Criteria
- [ ] {criterion 1} — PASS/FAIL
- [ ] {criterion 2} — PASS/FAIL
- [ ] ...
```

After all tasks in this batch:
- Run `git pull --rebase` to stack commits cleanly
- Close all tasks: use the `crumb_close` MCP tool with `ids: ["<id1>", "<id2>", ...]` (CLI fallback: `crumb close <id1> <id2> ...`)
- DO NOT push to remote (the Orchestrator handles this)
- DO NOT modify documentation files (CHANGELOG, README, CLAUDE.md)

Focus: {specific guidance for this file/component}
```

## Scope Boundary Insert

**When to use**: For all Implementers, especially when multiple tasks touch the same file.

**Why**: Agents are helpful by nature and will fix adjacent problems they notice ("while I'm here..."). When multiple agents touch the same file without explicit scope boundaries, they scramble attribution and create misleading audit trails.

**Template** (insert after Context section, before Step 1):

```markdown
## CRITICAL SCOPE BOUNDARY

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
3. Let the Orchestrator create separate tasks

**Acceptance criterion**: ONLY the files and line ranges listed in Step 3 may be edited. Any additional changes are a scope violation.
```

**Customization**:
- Replace `{specific task description}` with the actual task (e.g., "add the business_image field and update the image property")
- Add file-specific boundaries (e.g., "Edit lines 23-24 only" or "Only modify the sameAs field")
- List specific off-limit areas if needed (e.g., "Do NOT edit foundingDate, @id, or defensive guards")

## The Orchestrator's Pre-Spawn Checklist

Before sending any agent prompt, confirm it includes:
- [ ] **Context section** with exact files/lines from crumb (pre-digested, not "discover the problem")
- [ ] **Scope boundaries** limiting what files to read
- [ ] Root cause and acceptance criteria extracted from crumb
- [ ] **Step 1**: `crumb_show` MCP tool + `crumb_update` with `status: "in_progress"` (CLI fallback: `crumb show` + `crumb update --status=in_progress`)
- [ ] **Step 2**: "Design at least 4 approaches" with pros/cons (MANDATORY)
- [ ] **Step 2.5**: "Write failing tests" before implementation (MANDATORY)
- [ ] **Step 3**: Implementation instructions
- [ ] **Step 4**: "Review EVERY file you changed" with explicit checks (MANDATORY)
- [ ] **Step 5**: Commit instructions with `git pull --rebase`
- [ ] **Step 6**: Write summary doc to `{session-dir}/summaries/{TASK_ID}.md` (MANDATORY)

If any checkbox is missing, DO NOT spawn the agent — fix the prompt first.

**External validation**: After composing the prompt, run the **pre-spawn-check** (Checkpoint Auditor) to independently verify this checklist. See templates/checkpoints/pre-spawn-check.md.

## Information Diet for Agents

**CRITICAL**: Crumbs contain pre-digested context. Extract and provide it to agents to prevent wasteful exploration.

### What Crumbs Contain (Don't Make Agents Re-Discover)

Every crumb description includes:
- ✅ **Root cause** - The exact problem and why it exists
- ✅ **Affected surfaces** - Specific files and line numbers
- ✅ **Expected vs actual behavior** - What should happen vs what does
- ✅ **Fix description** - High-level approach (agents still design 4+ detailed approaches)
- ✅ **Acceptance criteria** - Testable success conditions

### The Orchestrator's Extraction Pattern

Before spawning an agent, extract this info from the `crumb_show` MCP tool (or `crumb show <id>` CLI fallback):

```bash
# CLI fallback (if MCP tools unavailable):
crumb show <task-id>  # Read ONCE in the Orchestrator's window

# Extract and provide to agent:
# - Affected files/lines from "Affected surfaces:" section
# - Root cause from "Root cause:" section
# - Acceptance criteria from "Acceptance criteria:" section
```

### Agent Prompt: What to Include

**✅ DO provide:**
- Exact file paths and line numbers from crumb
- Root cause explanation from crumb
- Acceptance criteria checklist from crumb
- Scope boundaries: "Read ONLY: build.py lines 200-250, site.yaml contact section"

**❌ DON'T say:**
- "Read the codebase and understand the problem" (too broad)
- "Explore the templates to find usage" (crumb already lists usage)
- "Investigate which files are affected" (crumb already specifies)

### Example: Before vs After

**❌ BEFORE (wasteful):**
```markdown
Fix contact validation bug (my-project-gat).
Read the codebase and understand what fields are missing from validation.
```

**✅ AFTER (surgical):**
```markdown
Fix contact validation bug (my-project-gat).

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

## Prompt Preparation Optimization

**IMPORTANT**: Prepare and verify prompts for future waves WHILE waiting for current wave to complete. This eliminates spawn latency between waves.

### Workflow:
1. **During Wave N**: Compose prompts for Wave N+1 and Wave N+2
2. **Run pre-spawn-check** on all future wave prompts (verify in parallel)
3. **When Wave N completes**: Immediately spawn Wave N+1 (prompts already verified)
4. **Repeat**: Prepare Wave N+2 prompts while Wave N+1 runs

### Benefits:
- Eliminates 2-5 minute prompt composition delay between waves
- Catches prompt defects early (before wave is ready to start)
- Keeps the Orchestrator's context focused on monitoring during active waves
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
