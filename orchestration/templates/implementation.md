<!-- Reader: the Pantry (implementation mode). The Queen does NOT read this file. -->
# Dirt Pusher Templates

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
- Record your commit hash in the summary doc (Step 6) so Dirt Moved vs Dirt Claimed (DMVDC) can identify your commits without scanning `git log`

## Step 6: Write Summary Doc (MANDATORY — do not skip)
Write a structured summary to `.beads/agent-summaries/<epic-id>/<task-id>.md` using the Write tool.
(Use `_standalone` if the task has no epic parent. The Queen pre-creates this directory at Step 2.)
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

## Scope Boundary Insert

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

## The Queen's Pre-Spawn Checklist

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

**External validation**: After composing the prompt, run **Colony Cartography Office (CCO)** to independently verify this checklist. See templates/checkpoints.md.

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

## Prompt Preparation Optimization

**IMPORTANT**: Prepare and verify prompts for future waves WHILE waiting for current wave to complete. This eliminates spawn latency between waves.

### Workflow:
1. **During Wave N**: Compose prompts for Wave N+1 and Wave N+2
2. **Run CCO** on all future wave prompts (verify in parallel)
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
