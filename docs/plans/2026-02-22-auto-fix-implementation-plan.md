# Auto-Fix Review Findings Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Automatically fix P1/P2 review findings after round 1 without user prompt.

**Architecture:** Insert an auto-fix decision branch in RULES.md Step 3c (between round cap check and user prompt). Split the fix workflow in reviews.md into P1 TDD (with test specification) and P2 fix-only paths.

**Tech Stack:** Markdown orchestration documents (no code).

**Design doc:** `docs/plans/2026-02-22-auto-fix-review-findings-design.md`

---

### Task 1: Insert auto-fix branch in RULES.md Step 3c

**Files:**
- Modify: `orchestration/RULES.md:228-239` (Step 3c, after termination check, before Step 4)

**Step 1: Edit RULES.md Step 3c**

Replace the current "If P1 or P2 issues found" block (lines 228-239) with the new decision tree. The exact old text to replace:

```markdown
            **If P1 or P2 issues found**:
            **Round cap — escalate after round 4** (check this FIRST before any fix decision):
            - If current round >= 4 and P1/P2 findings are still present, do NOT start another round
            - Present full round history to user (round numbers, finding counts, bead IDs)
            - Ask user: "Review loop has not converged after 4 rounds. Continue or abort?"
            - Await user decision before taking any further action
            **Only if current round < 4**: proceed with fix-now/defer decision:
            - Present findings to user: "Reviews found X P1 and Y P2 issues. Fix now or defer?"
            - **If "fix now"**: Spawn fix tasks (see reviews.md), then re-run Step 3b with round N+1
              - Update session state: increment review round, record fix commit range
            - **If "defer"**: P1/P2 beads stay open; document in CHANGELOG; proceed to Step 4
            **Progress log (after triage decision):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_TRIAGED|round=<N>|p1=<count>|p2=<count>|decision=<fix_now|defer|terminated>" >> ${SESSION_DIR}/progress.log`
```

New text:

```markdown
            **If P1 or P2 issues found**:
            **Round cap — escalate after round 4** (check this FIRST before any fix decision):
            - If current round >= 4 and P1/P2 findings are still present, do NOT start another round
            - Present full round history to user (round numbers, finding counts, bead IDs)
            - Ask user: "Review loop has not converged after 4 rounds. Continue or abort?"
            - Await user decision before taking any further action
            **Only if current round < 4**: determine fix action:
            **Auto-fix (round 1, ≤5 root causes)**: If round == 1 AND total P1+P2 root causes ≤ 5:
            - Announce (do NOT wait for user input):
              "**Auto-fix**: Round 1 review found X P1 and Y P2 issues (Z root causes, within 5-threshold). Spawning fix tasks automatically."
            - Proceed directly to fix workflow (see reviews.md "Fix Workflow"):
              - P1 root causes → TDD workflow (test spec + implementation)
              - P2 root causes → fix-only workflow (direct implementation)
            - After fixes complete + DMVDC passes, re-run Step 3b with round N+1
            - Update session state: increment review round, record fix commit range
            **Escalation (round 1, >5 root causes)**: If round == 1 AND total P1+P2 root causes > 5:
            - Present findings to user: "Round 1 review found Z root causes (>5 threshold). This suggests a systemic issue. Fix now or defer?"
            - Await user decision (same as round 2+ behavior below)
            **User prompt (round 2+)**: If round >= 2:
            - Present findings to user: "Reviews found X P1 and Y P2 issues. Fix now or defer?"
            - **If "fix now"**: Spawn fix tasks (see reviews.md "Fix Workflow"), then re-run Step 3b with round N+1
              - Update session state: increment review round, record fix commit range
            - **If "defer"**: P1/P2 beads stay open; document in CHANGELOG; proceed to Step 4
            **Progress log (after triage decision):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_TRIAGED|round=<N>|p1=<count>|p2=<count>|decision=<auto_fix|fix_now|defer|terminated>|root_causes=<count>" >> ${SESSION_DIR}/progress.log`
```

**Step 2: Verify edit**

Read the modified section back and confirm:
- Round cap check (≥4) is still first
- Auto-fix branch checks round == 1 AND ≤5
- Escalation branch checks round == 1 AND >5
- User prompt branch checks round >= 2
- Progress log includes `auto_fix` decision value and `root_causes` field

**Step 3: Commit**

```bash
git add orchestration/RULES.md
git commit -m "feat: add auto-fix branch to Step 3c for round 1 P1/P2 findings"
```

---

### Task 2: Split fix workflow in reviews.md

**Files:**
- Modify: `orchestration/templates/reviews.md:852-887` (fix workflow section)

**Step 1: Edit reviews.md fix workflow**

Replace the current "If P1 or P2 issues found" section (lines 852-887) with the split workflow. The exact old text to replace:

```markdown
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

   c. **Re-run reviews** (MANDATORY) —
      - After fix agents complete and pass DMVDC, re-run Step 3b with `Review round: <N+1>`
      - Round 2+ uses only Correctness + Edge Cases reviewers, scoped to fix commits
      - The loop continues until a round produces zero P1/P2 findings

4. **If user chooses "push and address later"**:
   - P1/P2 beads already filed during consolidation — they stay open
   - Document in CHANGELOG: "Known issues filed for future work: <list bead IDs>"
   - Proceed to Step 4 (Handle P3 Issues and Documentation)
```

New text:

```markdown
### If P1 or P2 issues found:

The Queen determines the fix action based on RULES.md Step 3c decision tree:
- **Auto-fix** (round 1, ≤5 root causes): proceed directly to Fix Workflow below
- **Escalation** (round 1, >5 root causes): present to user, await decision
- **User prompt** (round 2+): present to user, "Fix now or defer?"
- **Defer**: P1/P2 beads stay open; document in CHANGELOG; proceed to Step 4

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
```

**Step 2: Verify edit**

Read the modified section back and confirm:
- Decision tree references RULES.md Step 3c
- P1 TDD workflow includes test specification format
- P2 fix-only workflow skips test phase
- Wave composition shows P1 tests + P2 fixes concurrent
- Re-run reviews section preserved
- "Defer" option preserved for user-prompted rounds

**Step 3: Commit**

```bash
git add orchestration/templates/reviews.md
git commit -m "feat: split fix workflow into P1 TDD (test spec) and P2 fix-only paths"
```

---

### Task 3: Sync orchestration files to ~/.claude/

**Files:**
- Sync: `orchestration/RULES.md` → `~/.claude/orchestration/RULES.md`
- Sync: `orchestration/templates/reviews.md` → `~/.claude/orchestration/templates/reviews.md`

**Step 1: Copy files**

```bash
cp orchestration/RULES.md ~/.claude/orchestration/RULES.md
cp orchestration/templates/reviews.md ~/.claude/orchestration/templates/reviews.md
```

**Step 2: Verify sync**

```bash
diff orchestration/RULES.md ~/.claude/orchestration/RULES.md
diff orchestration/templates/reviews.md ~/.claude/orchestration/templates/reviews.md
```

Expected: no differences.

**Step 3: No commit needed** — `~/.claude/` files are not tracked in the repo.

---

### Task 4: Cross-reference verification

**Files:**
- Read: `orchestration/RULES.md` (verify Step 3c references "Fix Workflow" in reviews.md)
- Read: `orchestration/templates/reviews.md` (verify "Fix Workflow" references RULES.md Step 3c)
- Read: `docs/plans/2026-02-22-auto-fix-review-findings-design.md` (verify design matches implementation)

**Step 1: Verify RULES.md → reviews.md reference**

Confirm Step 3c says `see reviews.md "Fix Workflow"` (not the old section name).

**Step 2: Verify reviews.md → RULES.md reference**

Confirm the fix workflow section says `based on RULES.md Step 3c decision tree`.

**Step 3: Verify progress.log format**

Confirm the progress log template in RULES.md includes:
- `decision=auto_fix` as a valid value
- `root_causes=<count>` as a new field

**Step 4: Verify priority calibration alignment**

Confirm the P1/P2 definitions referenced in the fix workflow match the Priority Calibration section in RULES.md:
- P1 = build failure, broken links, data loss, security vulnerability → TDD workflow
- P2 = visual regression, accessibility issue, functional degradation → fix-only workflow

**Step 5: Final commit (if any cross-ref fixes needed)**

```bash
git add orchestration/RULES.md orchestration/templates/reviews.md
git commit -m "fix: align cross-references for auto-fix workflow"
```

If no fixes needed, skip this commit.
