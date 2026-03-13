# Pest Control -- CCO (Pre-Spawn Prompt Audit) -- Wave 3

**Checkpoint**: Colony Cartography Office (CCO)
**Scope**: Wave 3 Dirt Pusher previews (2 tasks)
**Audited files**:
- `.beads/agent-summaries/_session-50c2c6/previews/task-ha7a.5-preview.md`
- `.beads/agent-summaries/_session-50c2c6/previews/task-ha7a.9-preview.md`

**Ground truth cross-references**:
- Task prompt files: `prompts/task-ha7a.5.md`, `prompts/task-ha7a.9.md`
- Source files verified: `orchestration/templates/reviews.md`, `orchestration/templates/pantry.md`
- Implementation plan: `docs/plans/2026-02-19-review-loop-convergence.md` Tasks 5, 9

---

## Task: ant-farm-ha7a.5 (Update review checklists for round-aware team composition)

### Check 1: Real Task IDs
**PASS** -- Preview contains `ant-farm-ha7a.5` throughout (lines 1, 8, 8, 12, 16, 23). No placeholders like `<task-id>` found.

### Check 2: Real File Paths
**PASS** -- Contains specific file paths with line numbers:
- `orchestration/templates/reviews.md:L703-725` (affected files)
- `orchestration/templates/reviews.md:L700-730` (read scope)
- `docs/plans/2026-02-19-review-loop-convergence.md` Task 5 (reference content)
- `.beads/agent-summaries/_session-50c2c6/summaries/ha7a.5.md` (output path)

No placeholder patterns like `<list from bead>` or `<file>` found.

### Check 3: Root Cause Text
**PASS** -- Contains specific root cause: "The Nitpicker Checklist and Big Head Consolidation Checklist in reviews.md were written for a single-round review flow and do not include round-aware checks. They need to be updated so orchestrators can verify round-dependent behavior (team size, prompt count, out-of-scope bar, P3 auto-filing) at runtime."

This is a concrete, actionable description -- not a placeholder.

### Check 4: All 6 Mandatory Steps Present
**PASS** -- All steps verified:
1. Step 1 (line 8): `bd show ant-farm-ha7a.5` + `bd update ant-farm-ha7a.5 --status=in_progress`
2. Step 2 (line 9): "4+ genuinely distinct approaches" with "MANDATORY" keyword
3. Step 3 (line 10): "Implement: Write clean, minimal code satisfying acceptance criteria"
4. Step 4 (line 11): "Review (MANDATORY): Re-read EVERY changed file" with "MANDATORY" keyword
5. Step 5 (line 12): `git pull --rebase && git add <changed-files> && git commit`
6. Step 6 (lines 13-16): Write to `.beads/agent-summaries/_session-50c2c6/summaries/ha7a.5.md`

### Check 5: Scope Boundaries
**PASS** -- Explicit scope boundaries present:
- Read ONLY: `orchestration/templates/reviews.md:L700-730`, `docs/plans/2026-02-19-review-loop-convergence.md` Task 5
- Do NOT edit: Any section outside the two checklists. Explicit exclusion list: Round-Aware Review Protocol, Big Head Consolidation Protocol, Agent Teams Protocol, review type sections (Review 1-4), P3 Auto-Filing, Queen's Step 3c sections.
- Focus section reiterates: "Your task is ONLY to replace the Nitpicker Checklist and Big Head Consolidation Checklist items"

### Check 6: Commit Instructions
**PASS** -- Step 5 (line 12) includes `git pull --rebase` before commit.

### Check 7: Line Number Specificity
**PASS** -- File paths include specific line ranges with section descriptors:
- `orchestration/templates/reviews.md:L703-725` with description "both operational checklists: Nitpicker Checklist and Big Head Consolidation Checklist"
- Read scope `L700-730` with description "the two checklist sections"

**Ground truth verification**: I read `reviews.md` lines 695-734. Lines 703-725 do contain the Nitpicker Checklist (L703-713) and Big Head Consolidation Checklist (L715-725). Line numbers confirmed accurate.

### Task ha7a.5 Verdict: PASS (7/7)

---

## Task: ant-farm-ha7a.9 (Update pantry review mode for round-aware brief composition)

### Check 1: Real Task IDs
**PASS** -- Preview contains `ant-farm-ha7a.9` throughout (lines 1, 8, 8, 12, 16, 24). No placeholders found.

### Check 2: Real File Paths
**PASS** -- Contains specific file paths with line numbers:
- `orchestration/templates/pantry.md:L199-281` with 6 sub-section line ranges: Input spec (L201), Brief composition (L229), Files-to-write (L239-243), Step 4 Big Head brief (L245-254), Step 5 Previews (L257-265), Step 6 Return table (L268-281)
- `docs/plans/2026-02-19-review-loop-convergence.md` Task 9 (reference content)
- `orchestration/templates/reviews.md:L146-154` (Round 2+ Reviewer Instructions, cross-reference)
- `.beads/agent-summaries/_session-50c2c6/summaries/ha7a.9.md` (output path)

No placeholder patterns found.

### Check 3: Root Cause Text
**PASS** -- Contains specific root cause: "pantry.md's review mode describes a fixed 4-brief flow with no concept of review rounds. It must be updated to accept a round number as input and branch behavior (4 briefs round 1, 2 briefs round 2+) so that the Pantry agent correctly composes round-appropriate review packages."

This is concrete and actionable.

### Check 4: All 6 Mandatory Steps Present
**PASS** -- All steps verified:
1. Step 1 (line 8): `bd show ant-farm-ha7a.9` + `bd update ant-farm-ha7a.9 --status=in_progress`
2. Step 2 (line 9): "4+ genuinely distinct approaches" with "MANDATORY" keyword
3. Step 3 (line 10): "Implement: Write clean, minimal code satisfying acceptance criteria"
4. Step 4 (line 11): "Review (MANDATORY): Re-read EVERY changed file" with "MANDATORY" keyword
5. Step 5 (line 12): `git pull --rebase && git add <changed-files> && git commit`
6. Step 6 (lines 13-16): Write to `.beads/agent-summaries/_session-50c2c6/summaries/ha7a.9.md`

### Check 5: Scope Boundaries
**PASS** -- Explicit scope boundaries present:
- Read ONLY: `orchestration/templates/pantry.md:L197-289` (Section 2: Review Mode), implementation plan Task 9, `orchestration/templates/reviews.md:L146-154` (Round 2+ Reviewer Instructions)
- Do NOT edit: Section 1 (Implementation Mode, L15-196), Section 3 (Error Handling, L283-289), content outside Section 2, term definitions, Section 1/Section 2 separator
- Focus section reiterates: "Your task is ONLY to update the 6 sections of pantry.md's review mode (Section 2)"

### Check 6: Commit Instructions
**PASS** -- Step 5 (line 12) includes `git pull --rebase` before commit.

### Check 7: Line Number Specificity
**PASS** -- File paths include granular line ranges with section descriptors:
- `pantry.md:L199-281` (overall Section 2 scope)
- Six sub-section line ranges: L201 (Input spec), L229 (Brief composition), L239-243 (Files-to-write), L245-254 (Step 4 Big Head brief), L257-265 (Step 5 Previews), L268-281 (Step 6 Return table)
- `reviews.md:L146-154` (Round 2+ Reviewer Instructions cross-reference)

**Ground truth verification**: I read `pantry.md` lines 195-289. Section 2 starts at L199, the Input spec is at L201, "Compose 4 review briefs" is at L229, files-to-write at L239-243, Step 4 at L245, Step 5 at L257 (with preview instructions at L258-265), Step 6 at L268-281. All line numbers confirmed accurate. I also read `reviews.md` L146-154 and confirmed "Round 2+ Reviewer Instructions" is at that exact location.

### Task ha7a.9 Verdict: PASS (7/7)

---

## Consistency Check (Cross-Preview)

Both previews share the same session directory (`.beads/agent-summaries/_session-50c2c6/`), the same 6-step workflow template, and correctly reference the shared implementation plan (`docs/plans/2026-02-19-review-loop-convergence.md`) at their respective task numbers (Task 5, Task 9). The prompt files (`prompts/task-ha7a.5.md`, `prompts/task-ha7a.9.md`) match the preview content exactly -- the task brief sections in the previews are byte-identical to the standalone prompt files.

The two tasks target different files (`reviews.md` checklists vs `pantry.md` review mode) with no overlapping edit scope, so there is no scope conflict risk between Wave 3 agents.

---

## Overall Verdict: PASS

Both Wave 3 Dirt Pusher previews pass all 7 CCO checks. No defects found. Clear to spawn.
