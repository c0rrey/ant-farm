# Review Loop Convergence Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add convergence mechanics to the review pipeline so fix cycles terminate instead of looping indefinitely.

**Architecture:** The Queen tracks a review round counter. Round 1 uses the existing 4-reviewer pipeline. Round 2+ narrows to 2 reviewers (Correctness + Edge Cases) scoped only to fix commits, with P3s auto-filed to a "Future Work" epic. The loop terminates when a round produces zero P1/P2 findings.

**Tech Stack:** Markdown templates (reviews.md, RULES.md, big-head-skeleton.md, nitpicker-skeleton.md, queen-state.md, pantry.md, checkpoints.md)

**Design doc:** `docs/plans/2026-02-19-review-loop-convergence-design.md`

**Important context for the implementing agent:**
- All files being modified are markdown templates read by AI agents at runtime, not executed code
- "The Pantry" composes briefs by reading template files (like reviews.md) and writing filled-in versions to session directories
- "Big Head" consolidates reviewer reports and files beads (issues)
- "Pest Control" runs verification checkpoints (CCO, WWD, DMVDC, CCB) against agent work
- Line numbers are provided as initial guidance only — after edits in earlier steps, locate sections by heading text, not line numbers
- reviews.md has two different things called "Step 4": one is Big Head's "Step 4: Checkpoint Gate" (in the Big Head Consolidation Protocol) and the other is the Queen's "Handle P3 Issues (Queen's Step 4)". Do not confuse them. RULES.md also has its own "Step 4: Documentation". These are three distinct steps in three different contexts.

---

### Task 1: Add review round counter to queen-state.md

**Files:**
- Modify: `orchestration/templates/queen-state.md`

**Step 1: Add the review round tracking section**

Add a `## Review Rounds` section after the `## Pest Control` table and before the `## Queue Position` section. This is what the Queen uses to decide round 1 vs round 2+ behavior.

```markdown
## Review Rounds
- **Current round**: <1 | 2 | 3 | ...>
- **Round 1 commit range**: <first-session-commit>..<last-impl-commit>
- **Fix commit range**: <first-fix-commit>..<HEAD> (set after fix cycle)
- **Termination**: <pending | terminated (round N: 0 P1/P2)>
```

**Step 2: Verify the template renders correctly**

Read the file back and confirm the new section fits between Pest Control and Queue Position without breaking the existing structure.

**Step 3: Commit**

```bash
git add orchestration/templates/queen-state.md
git commit -m "feat: add review round tracking to queen-state template"
```

---

### Task 2: Add Round-Aware Review Protocol section to reviews.md

**Files:**
- Modify: `orchestration/templates/reviews.md`

**Context:** This file is 689 lines. You will edit 5 distinct sections. After each edit, subsequent line numbers shift — always locate sections by their heading text (e.g., `## Agent Teams Protocol`, `### Team Setup`), not by line number. The line numbers below are pre-edit starting points only.

**Step 1: Insert the Round-Aware Review Protocol section**

Find the `## Review 1: Clarity (P3)` heading. Insert the following new section BEFORE it (after the Messaging Guidelines, before Review 1):

````markdown
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
````

**Step 2: Update the Team Setup section to be round-aware**

Find the `### Team Setup` heading. Replace everything from the `**Pre-spawn requirement**` line through the closing of the team member list (the line with `**Big Head is spawned as a team member...`) with the following. Keep the `### Messaging Guidelines` section that follows — do not delete it.

````markdown
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
````

**Step 3: Commit**

```bash
git add orchestration/templates/reviews.md
git commit -m "feat: add round-aware review protocol and team setup to reviews.md"
```

---

### Task 3: Update Big Head sections in reviews.md for round-awareness

**Files:**
- Modify: `orchestration/templates/reviews.md`

**Step 1: Update Big Head Step 0 report verification**

Find the `### Step 0: Verify All Reports Exist (MANDATORY GATE)` heading. Replace the text and bash block between that heading and the `### Step 0a` heading with:

````markdown
### Step 0: Verify All Reports Exist (MANDATORY GATE)

Before reading any reports, verify the expected files exist. The number of expected reports depends on the review round:

**Round 1**: Verify all 4 report files exist:

```bash
ls <session-dir>/review-reports/clarity-review-*.md \
   <session-dir>/review-reports/edge-cases-review-*.md \
   <session-dir>/review-reports/correctness-review-*.md \
   <session-dir>/review-reports/excellence-review-*.md
```

**Round 2+**: Verify 2 report files exist (correctness and edge-cases only):

```bash
ls <session-dir>/review-reports/correctness-review-*.md \
   <session-dir>/review-reports/edge-cases-review-*.md
```

**All expected files MUST exist.** If any file is missing:
1. Identify which reviewer failed to produce output
2. Check if the reviewer is still running, errored, or wrote to the wrong path
3. Do NOT proceed with consolidation until all expected reports are present
````

**Step 2: Update Step 0a polling loop for round-awareness**

Find the `### Step 0a: Remediation Path for Missing Reports` heading. In the polling loop code block, replace the 4-variable check with a round-aware version. Replace the entire bash code block with:

````bash
# IMPORTANT: This entire block must execute in a single Bash invocation.
# Shell state (variables) does not persist across separate Bash tool calls.

# Poll up to 30 seconds total for missing reports
TIMEOUT=30
ELAPSED=0
POLL_INTERVAL=2
TIMED_OUT=1

# The brief specifies which reports to expect (4 for round 1, 2 for round 2+).
# Check only the expected reports. The Pantry writes the exact paths into the brief.

while [ $ELAPSED -lt $TIMEOUT ]; do
  # Round 1: check all 4
  # Round 2+: check only correctness and edge-cases
  # The brief lists the exact expected report paths. Check each with [ -f ].
  # head -1 ensures re-runs with multiple matching files don't break the check.
  ALL_FOUND=1

  # Always expected (both rounds):
  FOUND_CORRECTNESS=$(ls <session-dir>/review-reports/correctness-review-*.md 2>/dev/null | head -1)
  FOUND_EDGE=$(ls <session-dir>/review-reports/edge-cases-review-*.md 2>/dev/null | head -1)
  [ -f "$FOUND_CORRECTNESS" ] && [ -f "$FOUND_EDGE" ] || ALL_FOUND=0

  # Round 1 only (skip these checks in round 2+):
  # <IF ROUND 1>
  FOUND_CLARITY=$(ls <session-dir>/review-reports/clarity-review-*.md 2>/dev/null | head -1)
  FOUND_EXCELLENCE=$(ls <session-dir>/review-reports/excellence-review-*.md 2>/dev/null | head -1)
  [ -f "$FOUND_CLARITY" ] && [ -f "$FOUND_EXCELLENCE" ] || ALL_FOUND=0
  # </IF ROUND 1>

  if [ $ALL_FOUND -eq 1 ]; then
    TIMED_OUT=0
    break
  fi
  sleep $POLL_INTERVAL
  ELAPSED=$((ELAPSED + POLL_INTERVAL))
done

if [ $TIMED_OUT -eq 1 ]; then
  echo "TIMEOUT: Not all expected reports arrived within ${TIMEOUT}s"
fi
````

Add a note after the code block:

```markdown
**Pantry responsibility**: When composing the Big Head brief, the Pantry writes the concrete version of this polling loop with the round-specific checks. In round 1, all 4 report checks are included. In round 2+, only the correctness and edge-cases checks are included (the `<IF ROUND 1>` block is omitted). The template above shows the full structure for reference; the Pantry adapts it per round.
```

**Step 3: Update the consolidated summary template for round-awareness**

Find the `### Step 3: Write Consolidated Summary` heading. In the template block that follows, update the hardcoded references to be round-aware:

Replace:
```
**Reviews completed**: Clarity, Edge Cases, Correctness, Excellence
```

With:
```
**Reviews completed**: <Round 1: Clarity, Edge Cases, Correctness, Excellence | Round 2+: Correctness, Edge Cases>
```

Replace the 4-row Read Confirmation table with a round-aware note:
```markdown
**Reports read and processed by Big Head consolidation:**

Round 1: 4 reports (clarity, edge-cases, correctness, excellence)
Round 2+: 2 reports (correctness, edge-cases)

| Report Type | File | Status | Finding Count |
|-------------|------|--------|----------------|
| <for each report in this round> | <filename> | ✓ Read | <N> findings |
```

**Step 4: Commit**

```bash
git add orchestration/templates/reviews.md
git commit -m "feat: update Big Head verification and summary for round-aware report counts"
```

---

### Task 4: Add P3 auto-filing and update Queen's triage in reviews.md

**Files:**
- Modify: `orchestration/templates/reviews.md`

**Step 1: Add P3 Auto-Filing section**

Find the `**Bead filing (validated findings only):**` line and the `bd label add` line that follows the bead filing bash block. After that block (after the `bd label add` line), add:

````markdown
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
   bd create --type=bug --priority=3 --title="<root cause title>"
   bd dep add <bead-id> <future-work-epic-id> --type parent-child
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
````

**Step 2: Update the Queen's Step 3c — add termination path**

Find the `## Queen's Step 3c: User Triage on P1/P2 Issues` heading. Add a new subsection BEFORE the existing `### If P1 or P2 issues found:` heading:

```markdown
### Termination Check (zero P1/P2 findings)

If the consolidated summary shows zero P1 and zero P2 findings, the review loop has converged:

1. **Round 2+**: Big Head has already auto-filed any P3 findings to "Future Work" epic — no action needed
2. **Round 1**: P3 findings follow the existing "Handle P3 Issues" flow below — the Queen files them to Future Work
3. Queen updates session state: `Termination: terminated (round N: 0 P1/P2)`
4. Proceed to RULES.md Step 4 (Documentation — update CHANGELOG, README, CLAUDE.md)

No user prompt needed — the loop simply ends.
```

**Step 3: Update the "fix now" re-review option**

Find the `c. **Re-run reviews** (optional):` line in the "If user chooses 'fix now'" section. Replace it and its sub-bullets with:

```markdown
   c. **Re-run reviews** (MANDATORY):
      - After fix agents complete and pass DMVDC, re-run Step 3b with `Review round: <N+1>`
      - Round 2+ uses only Correctness + Edge Cases reviewers, scoped to fix commits
      - The loop continues until a round produces zero P1/P2 findings
```

**Step 4: Mark "Handle P3 Issues" section as Round 1 only**

Find the `### Handle P3 Issues (Queen's Step 4)` heading. Add this note immediately after the heading:

```markdown
> **Round 1 only.** In round 2+, P3s are auto-filed by Big Head during consolidation (see "P3 Auto-Filing" above). This section applies only when round 1 terminates with P3 findings.
```

**Step 5: Commit**

```bash
git add orchestration/templates/reviews.md
git commit -m "feat: add P3 auto-filing, termination check, and mandatory re-review to reviews.md"
```

---

### Task 5: Update checklists in reviews.md

**Files:**
- Modify: `orchestration/templates/reviews.md`

**Step 1: Update the Nitpicker Checklist**

Find the `### Nitpicker Checklist (verify before launching team)` heading. Replace the checklist items with:

```markdown
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
```

**Step 2: Update the Big Head Consolidation Checklist**

Find the `### Big Head Consolidation Checklist (after all Nitpickers finish)` heading. Replace the checklist items with:

```markdown
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
```

**Step 3: Commit**

```bash
git add orchestration/templates/reviews.md
git commit -m "feat: update review checklists for round-aware team composition"
```

---

### Task 6: Update RULES.md Step 3b/3c for round-aware reviews

**Files:**
- Modify: `orchestration/RULES.md`

**Step 1: Update Step 3b**

Find the `**Step 3b:**` line. Replace everything from that line through `no separate post-team Pest Control spawn is needed for those checks.` with:

```markdown
**Step 3b:** Review — pre-spawn directory setup:
              `mkdir -p ${SESSION_DIR}/review-reports`
            Gather review inputs from the Queen's state file:
            - **Review round**: read from session state (default: 1)
            - **Round 1 commit range**: first commit of the session through HEAD
            - **Round 2+ commit range**: first fix commit through HEAD (set after fix cycle in Step 3c)
            - File list: `git diff --name-only <commit-range>` (deduplicated)
            - Task IDs: round 1 = all task IDs; round 2+ = fix task IDs only
            - Epic IDs: all epics worked on this session (for context only)
            Then: spawn the Pantry (`pantry-review`) with `Review round: <N>` in its prompt.
            Spawn Pest Control for CCO on review previews.
            **Round 1**: Create Nitpicker team with 6 members: 4 reviewers
            (→ orchestration/templates/nitpicker-skeleton.md) + Big Head
            (→ orchestration/templates/big-head-skeleton.md) + Pest Control.
            **Round 2+**: Create Nitpicker team with 4 members: 2 reviewers
            (Correctness + Edge Cases only) + Big Head + Pest Control.
            Big Head MUST be a team member, NOT a separate Task agent.
            Pest Control MUST be a team member so Big Head can SendMessage to it directly.
            After team completes, DMVDC and CCB have already run inside the team.
```

**Step 2: Update Step 3c**

Find the `**Step 3c:**` line. Replace everything from that line through `- **If no P1/P2 issues**: Skip to Step 4 directly` with:

```markdown
**Step 3c:** User triage — **after CCB PASS and Big Head consolidation completes**:
            1. Read the consolidated review summary
            2. Check finding counts: P1, P2, P3
            **Termination check**: If zero P1 and zero P2 findings:
            - Round 2+: P3s already auto-filed by Big Head to "Future Work" epic
            - Round 1: P3s filed via "Handle P3 Issues" flow in reviews.md
            - Update session state: `Termination: terminated (round N: 0 P1/P2)`
            - Proceed directly to Step 4 (documentation)
            **If P1 or P2 issues found**:
            - Present findings to user: "Reviews found X P1 and Y P2 issues. Fix now or defer?"
            - **If "fix now"**: Spawn fix tasks (see reviews.md), then re-run Step 3b with round N+1
              - Update session state: increment review round, record fix commit range
            - **If "defer"**: P1/P2 beads stay open; document in CHANGELOG; proceed to Step 4
```

**Step 3: Update the Hard Gates table**

Find the `| Reviews |` row in the Hard Gates table. Replace the description cell with:

```
Mandatory after ALL implementation completes; re-runs after fix cycles with reduced scope (round 2+)
```

**Step 4: Commit**

```bash
git add orchestration/RULES.md
git commit -m "feat: update RULES.md Step 3b/3c for round-aware review loop with termination"
```

---

### Task 7: Update big-head-skeleton.md for round-aware consolidation

**Files:**
- Modify: `orchestration/templates/big-head-skeleton.md`

**Step 1: Add the REVIEW_ROUND placeholder**

Find the placeholder list in the "Instructions for The Queen" section (the lines starting with `- \`{TASK_ID}\``). Add after the `{SESSION_DIR}` entry:

```markdown
- `{REVIEW_ROUND}`: review round number (1, 2, 3, ...). Determines report count and P3 handling.
```

**Step 2: Update the TeamCreate wiring instructions**

Find `Big Head is the 5th member; Pest Control is the 6th member.` and the TeamCreate example that follows. Replace from that line through the closing `)` of the example with:

````markdown
**Round 1**: Big Head is the 5th member; Pest Control is the 6th. Pass the filled-in template text as Big Head's `prompt`.

~~~
TeamCreate(
  name="nitpicker-team",
  members=[
    { "name": "clarity-reviewer",      "prompt": "<filled nitpicker template with REVIEW_TYPE=clarity>", "model": "sonnet" },
    { "name": "edge-cases-reviewer",   "prompt": "<filled nitpicker template with REVIEW_TYPE=edge-cases>", "model": "sonnet" },
    { "name": "correctness-reviewer",  "prompt": "<filled nitpicker template with REVIEW_TYPE=correctness>", "model": "sonnet" },
    { "name": "excellence-reviewer",   "prompt": "<filled nitpicker template with REVIEW_TYPE=excellence>", "model": "sonnet" },
    { "name": "big-head",              "prompt": "<filled big-head template with all 4 expected report paths embedded>", "model": "{MODEL}" },
    { "name": "pest-control",          "prompt": "<pest-control prompt>", "model": "sonnet" }
  ]
)
~~~

**Round 2+**: Big Head is the 3rd member; Pest Control is the 4th. Only Correctness and Edge Cases reviewers are spawned.

~~~
TeamCreate(
  name="nitpicker-team",
  members=[
    { "name": "correctness-reviewer",  "prompt": "<filled nitpicker template with REVIEW_TYPE=correctness>", "model": "sonnet" },
    { "name": "edge-cases-reviewer",   "prompt": "<filled nitpicker template with REVIEW_TYPE=edge-cases>", "model": "sonnet" },
    { "name": "big-head",              "prompt": "<filled big-head template with 2 expected report paths embedded>", "model": "{MODEL}" },
    { "name": "pest-control",          "prompt": "<pest-control prompt>", "model": "sonnet" }
  ]
)
~~~
````

**Step 3: Update the agent-facing template**

Find the line `Consolidate the 4 Nitpicker reports into a unified summary.` (below the `---` separator). Replace it with:

```markdown
Consolidate the Nitpicker reports into a unified summary.

**Review round**: {REVIEW_ROUND}
- Round 1: expect 4 reports (clarity, edge-cases, correctness, excellence)
- Round 2+: expect 2 reports (correctness, edge-cases only)
```

Find the line starting with `9. Await Pest Control verdict:`. After the FAIL escalation line, add step 10:

```markdown
10. **Round 2+ only — P3 auto-filing**: After filing P1/P2 beads, auto-file P3 findings to "Future Work" epic:
    - Find or create the epic: `bd list --status=open | grep -i "future work"` or `bd epic create --title="Future Work" --description="Low-priority polish and improvements from review sessions"`
    - For each P3: `bd create --type=bug --priority=3 --title="<title>"` then `bd dep add <id> <epic-id> --type parent-child`
    - Mark P3s as "auto-filed, no action required" in the consolidated summary
    - Do NOT include P3 findings in the fix-or-defer prompt to the Queen
    - In round 1, skip this step — P3s are handled by the Queen's existing flow
```

**Step 4: Commit**

```bash
git add orchestration/templates/big-head-skeleton.md
git commit -m "feat: add round-aware consolidation and P3 auto-filing to big-head-skeleton"
```

---

### Task 8: Update nitpicker-skeleton.md for round-aware scope

**Files:**
- Modify: `orchestration/templates/nitpicker-skeleton.md`

**Step 1: Add the REVIEW_ROUND placeholder**

Find the placeholder list (lines starting with `- {REVIEW_TYPE}:`). Add after the last placeholder:

```markdown
- {REVIEW_ROUND}: 1, 2, 3, ... (determines scope instructions; filled by Pantry)
```

**Step 2: Add round-aware scope to the agent-facing template**

Find the line `Perform a {REVIEW_TYPE} review of the completed work.` (below the `---` separator). Replace it with:

```markdown
Perform a {REVIEW_TYPE} review of the completed work.

**Review round**: {REVIEW_ROUND}
If round 2+: Your scope is limited to fix commits only. You may read full files for context, but your mandate is: did these fixes land correctly and not break anything? Out-of-scope findings are only reportable if they would cause a runtime failure or silently wrong results. Do NOT report naming, style, docs, or improvement opportunities outside fix scope.
```

**Step 3: Commit**

```bash
git add orchestration/templates/nitpicker-skeleton.md
git commit -m "feat: add round-aware scope instructions to nitpicker-skeleton"
```

---

### Task 9: Update pantry.md review mode for round-awareness

The Pantry reads reviews.md and composes review briefs. It needs to know the round number to decide which reviewers to compose briefs for and how to adapt the polling loop.

**Files:**
- Modify: `orchestration/templates/pantry.md`

**Step 1: Update the input spec**

Find the `**Input from the Queen**:` line in the Section 2 header area. Add `review round number (1, 2, 3, ...)` to the end of the input list.

**Step 2: Add round-aware composition rules**

Find the line that starts `Compose 4 review briefs` (in Step 3). Replace the paragraph starting with `Compose 4 review briefs, each containing:` with:

```markdown
**Round-aware composition:**
- **Round 1**: Compose 4 review briefs (clarity, edge-cases, correctness, excellence)
- **Round 2+**: Compose 2 review briefs (correctness, edge-cases only). Include the out-of-scope finding bar from the "Round 2+ Reviewer Instructions" section of reviews.md in each brief.

Each brief contains:
```

Keep the existing bullet list of brief contents that follows.

**Step 3: Update the files-to-write list**

Find the `Files to write:` line and the 4-item list that follows. Replace with:

```markdown
Files to write:
- **Round 1**:
  - `{session-dir}/prompts/review-clarity.md`
  - `{session-dir}/prompts/review-edge-cases.md`
  - `{session-dir}/prompts/review-correctness.md`
  - `{session-dir}/prompts/review-excellence.md`
- **Round 2+**:
  - `{session-dir}/prompts/review-edge-cases.md`
  - `{session-dir}/prompts/review-correctness.md`
```

**Step 4: Update the Big Head brief composition**

Find the `### Step 4: Compose Big Head Consolidation Brief` heading. In the list of what the brief should contain, add these items:

```markdown
- Review round number (so Big Head knows how many reports to expect and whether to auto-file P3s)
- Round 1: all 4 report paths; Round 2+: 2 report paths (correctness, edge-cases)
- Round 2+ P3 auto-filing instructions (from reviews.md "P3 Auto-Filing" section)
```

Also add this note about the polling loop:

```markdown
**Polling loop adaptation**: When composing the Big Head brief, adapt the Step 0a polling loop from reviews.md for the current round. In round 1, include all 4 report checks. In round 2+, include only correctness and edge-cases checks (omit the clarity and excellence variables and their `[ -f ]` check).
```

**Step 5: Update the preview composition**

Find the `### Step 5: Write Combined Review Previews` heading. Update the instruction to note round-dependent count:

```markdown
1. Read `~/.claude/orchestration/templates/nitpicker-skeleton.md`
2. **Round 1**: For each of 4 reviews, construct a combined prompt preview
   **Round 2+**: For each of 2 reviews (correctness, edge-cases), construct a combined prompt preview
3. For each review:
   a. Take the skeleton template text (below the `---` separator)
   b. Fill in `{UPPERCASE}` placeholders (including `{REVIEW_ROUND}`)
   c. Append the review brief content below it
   d. Write to `{session-dir}/previews/review-{type}-preview.md`
```

**Step 6: Update the return table**

Find the `### Step 6: Return File Paths` heading and the return table that follows. Replace the table with:

```markdown
**Round 1 return table:**
| Review Type | Brief | Preview File | Report Output Path |
|-------------|-------|--------------|-------------------|
| clarity     | {session-dir}/prompts/review-clarity.md | {session-dir}/previews/review-clarity-preview.md | {session-dir}/review-reports/clarity-review-{timestamp}.md |
| edge-cases  | {session-dir}/prompts/review-edge-cases.md | {session-dir}/previews/review-edge-cases-preview.md | {session-dir}/review-reports/edge-cases-review-{timestamp}.md |
| correctness | {session-dir}/prompts/review-correctness.md | {session-dir}/previews/review-correctness-preview.md | {session-dir}/review-reports/correctness-review-{timestamp}.md |
| excellence  | {session-dir}/prompts/review-excellence.md | {session-dir}/previews/review-excellence-preview.md | {session-dir}/review-reports/excellence-review-{timestamp}.md |

**Round 2+ return table:**
| Review Type | Brief | Preview File | Report Output Path |
|-------------|-------|--------------|-------------------|
| correctness | {session-dir}/prompts/review-correctness.md | {session-dir}/previews/review-correctness-preview.md | {session-dir}/review-reports/correctness-review-{timestamp}.md |
| edge-cases  | {session-dir}/prompts/review-edge-cases.md | {session-dir}/previews/review-edge-cases-preview.md | {session-dir}/review-reports/edge-cases-review-{timestamp}.md |

Big Head consolidation data: {session-dir}/prompts/review-big-head-consolidation.md (includes round number)
Big Head consolidated output: {session-dir}/review-reports/review-consolidated-{timestamp}.md
```

**Step 7: Commit**

```bash
git add orchestration/templates/pantry.md
git commit -m "feat: update pantry review mode for round-aware brief composition"
```

---

### Task 10: Update checkpoints.md CCB for round-aware report counts

**Files:**
- Modify: `orchestration/templates/checkpoints.md`

**Context:** The CCB (Colony Census Bureau) checkpoint verifies Big Head's consolidation. Check 0 currently hardcodes "exactly 4 report files" and Check 1 hardcodes "all 4 individual reports." These must be round-aware.

**Step 1: Update the CCB header**

Find the line `**When**: After Big Head consolidation (after all 4 review reports merged and beads filed)`. Replace with:

```markdown
**When**: After Big Head consolidation (after all review reports merged and beads filed — 4 reports in round 1, 2 in round 2+)
```

**Step 2: Update the Individual reports list**

Find the `**Individual reports**:` line and the 4-item list that follows. Replace with:

```markdown
**Individual reports**: (The Queen provides exact filenames and the review round number in the consolidation prompt.)

Round 1:
- `{SESSION_DIR}/review-reports/clarity-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/edge-cases-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/correctness-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/excellence-review-{timestamp}.md`

Round 2+:
- `{SESSION_DIR}/review-reports/correctness-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/edge-cases-review-{timestamp}.md`
```

Update the `Read all 5 documents` line to say:

```markdown
Read all documents (round 1: 5 total = 4 reports + consolidated; round 2+: 3 total = 2 reports + consolidated), then perform these 8 checks:
```

**Step 3: Update Check 0**

Find `## Check 0: Report Existence Verification`. Replace the check text and the 4-item file list with:

```markdown
## Check 0: Report Existence Verification
Verify the expected report files exist at their paths. The expected count depends on the review round:

**Round 1** — verify exactly 4 report files:
- `{SESSION_DIR}/review-reports/clarity-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/edge-cases-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/correctness-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/excellence-review-{timestamp}.md`

**Round 2+** — verify exactly 2 report files:
- `{SESSION_DIR}/review-reports/correctness-review-{timestamp}.md`
- `{SESSION_DIR}/review-reports/edge-cases-review-{timestamp}.md`

If any expected file is missing, FAIL immediately — consolidation should not have proceeded.
```

**Step 4: Update Check 1**

Find `## Check 1: Finding Count Reconciliation`. Replace `Count total findings across all 4 individual reports.` with:

```markdown
Count total findings across all individual reports (4 in round 1, 2 in round 2+).
```

Replace the `Report the math:` line — update `"Clarity: N, Edge Cases: N, Correctness: N, Excellence: N = TOTAL total."` with:

```markdown
Report the math: "Round 1: Clarity: N, Edge Cases: N, Correctness: N, Excellence: N = TOTAL total. Round 2+: Correctness: N, Edge Cases: N = TOTAL total. Consolidated references TOTAL findings across N root causes. N findings merged as duplicates. RECONCILED / NOT RECONCILED — {list orphaned findings}"
```

**Step 5: Commit**

```bash
git add orchestration/templates/checkpoints.md
git commit -m "feat: update CCB checkpoint for round-aware report counts"
```

---

### Task 11: Verify cross-file consistency

**Files:**
- Read: all 7 modified files

**Step 1: Cross-reference check**

Read each file end-to-end and verify these invariants:

| Invariant | Source | Must match |
|-----------|--------|------------|
| Round 1 = 6 team members, Round 2+ = 4 | reviews.md Team Setup | RULES.md Step 3b, big-head-skeleton.md TeamCreate examples |
| Round 1 = 4 reports, Round 2+ = 2 | reviews.md Step 0 | checkpoints.md Check 0, big-head-skeleton.md template, pantry.md brief composition |
| Termination = 0 P1/P2 → proceed to RULES.md Step 4 | reviews.md Queen's Step 3c | RULES.md Step 3c |
| Round 1 P3s → Queen's "Handle P3 Issues" flow | reviews.md | RULES.md Step 3c |
| Round 2+ P3s → Big Head auto-files to Future Work | reviews.md P3 Auto-Filing | big-head-skeleton.md step 10 |
| `{REVIEW_ROUND}` placeholder in skeleton | nitpicker-skeleton.md, big-head-skeleton.md | pantry.md fills it during brief composition |
| Queen state file has review round counter | queen-state.md | RULES.md Step 3b reads it, Step 3c updates it |
| Pantry adapts polling loop per round | pantry.md Step 4 note | reviews.md Step 0a polling loop template |
| CCB expects round-dependent report count | checkpoints.md Check 0, Check 1 | reviews.md Step 0 |
| Re-review is MANDATORY after fixes (not optional) | reviews.md "fix now" path | RULES.md Step 3c |
| "Handle P3 Issues" section marked Round 1 only | reviews.md | Should not conflict with P3 Auto-Filing section |

**Step 2: Check for stale line references**

Search all modified files for hardcoded line number references (e.g., `L485-514`, `line 322`). If any reference points to a section that has shifted due to our edits, update it to reference by section heading instead.

**Step 3: Check for stale member counts**

Search all modified files for strings like "all 4", "4 report", "5 member", "4 individual". Verify each instance is either:
- In a round 1 context (correct), or
- Updated to be round-aware

**Step 4: Commit any fixes**

If any inconsistencies found, fix and commit:

```bash
git add <files>
git commit -m "fix: resolve cross-file inconsistencies in review convergence implementation"
```
