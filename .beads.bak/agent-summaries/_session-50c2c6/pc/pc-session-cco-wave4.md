# Pest Control -- CCO (Pre-Spawn Prompt Audit)

**Task**: ant-farm-ha7a.11
**Preview file**: `.beads/agent-summaries/_session-50c2c6/previews/task-ha7a.11-preview.md`
**Prompt data file**: `.beads/agent-summaries/_session-50c2c6/prompts/task-ha7a.11.md`

---

## Check 1: Real Task IDs

**PASS**

The prompt uses the real task ID `ant-farm-ha7a.11` throughout:
- Line 1 of preview: "Execute task for ant-farm-ha7a.11."
- Step 1: `bd show ant-farm-ha7a.11` + `bd update ant-farm-ha7a.11 --status=in_progress`
- Step 5 commit message: `(ant-farm-ha7a.11)`
- Step 6: `bd close ant-farm-ha7a.11`

No placeholders like `<task-id>` or `<id>` found.

---

## Check 2: Real File Paths

**PASS**

The prompt contains actual file paths with line numbers for all 7 target files:
- `orchestration/templates/queen-state.md:L33-37`
- `orchestration/templates/reviews.md:L49-96`, `reviews.md:L110-154`, `reviews.md:L394-488`, etc. (7 line ranges)
- `orchestration/RULES.md:L89-121`, `RULES.md:L138`
- `orchestration/templates/big-head-skeleton.md:L13`, `big-head-skeleton.md:L26-54`, etc.
- `orchestration/templates/nitpicker-skeleton.md:L12`, `nitpicker-skeleton.md:L18-21`
- `orchestration/templates/pantry.md:L201`, `pantry.md:L229-251`, etc.
- `orchestration/templates/checkpoints.md:L453`, `checkpoints.md:L467-478`, etc.

All 7 files confirmed to exist on disk. Spot-checked 4 line references against actual content:
- `reviews.md:L49` = "### Team Setup" -- CONFIRMED
- `RULES.md:L89` = "**Step 3b:** Review" -- CONFIRMED
- `big-head-skeleton.md:L13` = REVIEW_ROUND placeholder line -- CONFIRMED
- `checkpoints.md:L453` = CCB header with round-aware text -- CONFIRMED

No placeholders like `<list from bead>` or `<file>` found.

---

## Check 3: Root Cause Text

**PASS**

The prompt contains a specific root cause description (preview line 16 / prompt data line 16):

> "Tasks 1-10 each modified a separate file or section to add round-aware review patterns. These changes must be mutually consistent across all 7 files: team member counts, report counts, placeholder names, termination semantics, P3 handling paths, and cross-references must all agree."

This is specific and contextual -- not a placeholder or generic text.

---

## Check 4: All 6 Mandatory Steps Present

**PASS**

All 6 steps confirmed in preview lines 8-16:

1. **Step 1 -- Claim**: `bd show ant-farm-ha7a.11` + `bd update ant-farm-ha7a.11 --status=in_progress` (preview line 8)
2. **Step 2 -- Design**: "4+ genuinely distinct approaches" (preview line 9). MANDATORY keyword: "MANDATORY" is not literally present in Step 2 line, but the preview line 9 states "(MANDATORY)" -- actually, checking again: preview line 9 says `**Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs.` -- CONFIRMED, keyword present.
3. **Step 3 -- Implement**: "Write clean, minimal code satisfying acceptance criteria." (preview line 10)
4. **Step 4 -- Review**: "Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit." (preview line 11). MANDATORY keyword: "(MANDATORY)" present on line 11. "EVERY" keyword present.
5. **Step 5 -- Commit**: `git pull --rebase && git add <changed-files> && git commit` (preview line 12). Includes `git pull --rebase`.
6. **Step 6 -- Summary doc**: "Write to .beads/agent-summaries/_session-50c2c6/summaries/ha7a.11.md with all required sections" (preview lines 13-14). Path uses actual session dir and task suffix.

Additionally: `bd close ant-farm-ha7a.11` is in Step 6 (preview line 16).

---

## Check 5: Scope Boundaries

**PASS**

Explicit scope boundaries are defined in the "Scope Boundaries" section (preview lines 33-35 / prompt lines 33-35):

> "Read ONLY: orchestration/templates/queen-state.md, orchestration/templates/reviews.md, orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/checkpoints.md"
> "Do NOT edit: any file (this is a read-only audit)."

The "Focus" section (lines 38-40) further constrains scope:

> "Your task is ONLY to verify cross-file consistency..."
> "Do NOT fix adjacent issues you notice -- document them under 'Adjacent Issues Found'"

This is a closed, explicit file list -- not open-ended.

---

## Check 6: Commit Instructions

**PASS**

Preview line 12 contains: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-ha7a.11)"`

The `git pull --rebase` instruction is present.

---

## Check 7: Line Number Specificity

**PASS**

Every file reference includes specific line ranges or section markers. Examples:

- `queen-state.md:L33-37` (Review Rounds section) -- specific 5-line range with section name
- `reviews.md:L49-96` (Team Setup, round-aware) -- specific range with section description
- `reviews.md:L110-154` (Round-Aware Review Protocol) -- specific range
- `RULES.md:L89-121` (Step 3b/3c round-aware review loop) -- specific range
- `big-head-skeleton.md:L13` (REVIEW_ROUND placeholder) -- specific single line
- `nitpicker-skeleton.md:L12` (REVIEW_ROUND placeholder) -- specific single line
- `pantry.md:L201` (review round in input spec) -- specific single line
- `checkpoints.md:L453` (CCB header round-aware) -- specific single line

The acceptance criteria section is even more granular, referencing specific lines within each file for each invariant check (e.g., `reviews.md:L53`, `RULES.md:L100`, `big-head-skeleton.md:L26`).

No vague file-only references found.

---

## Additional Observations (not criteria failures)

1. **Internal tension in scope instructions**: The Scope Boundaries section says "Do NOT edit: any file (this is a read-only audit)" but the Focus section says "If you find inconsistencies, fix them and commit." This is contradictory -- the agent is told both to not edit and to fix inconsistencies. This is not a CCO criteria failure but could confuse the agent.

2. **Preview vs. prompt data duplication**: The preview file (task-ha7a.11-preview.md) includes both the wrapper instructions (Steps 0-6) AND the full task brief content, which is also stored separately in `prompts/task-ha7a.11.md`. The task brief in the preview (lines 23-71) is identical to the standalone prompt data file. This is correct -- the preview is the composed prompt that includes the data file content.

---

## Verdict

**PASS** -- All 7 checks pass.

| Check | Criterion | Result |
|-------|-----------|--------|
| 1 | Real task IDs | PASS |
| 2 | Real file paths | PASS |
| 3 | Root cause text | PASS |
| 4 | All 6 mandatory steps | PASS |
| 5 | Scope boundaries | PASS |
| 6 | Commit instructions | PASS |
| 7 | Line number specificity | PASS |

**Advisory**: Note the internal tension between "Do NOT edit" (Scope Boundaries) and "fix them and commit" (Focus section). Not a CCO failure, but the Queen should resolve the contradiction before spawn.
