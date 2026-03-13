# Pest Control -- CCO Pre-Spawn Prompt Audit (Implementation Wave 1)

**Checkpoint**: Colony Cartography Office (CCO)
**Scope**: 3 Dirt Pusher prompts for implementation wave 1
**Auditor**: Pest Control
**Date**: 2026-02-19

---

## Prompts Audited

| Preview File | Task ID | Task Title |
|---|---|---|
| `task-x4m-preview.md` | `ant-farm-x4m` | AGG-031: Add data file format specification to skeleton templates |
| `task-e9k-preview.md` | `ant-farm-e9k` | AGG-035: Add remediation path for missing Nitpicker reports |
| `task-zeu-preview.md` | `ant-farm-zeu` | (BUG) Templates lack explicit guards for missing or empty input artifacts |

---

## Check 1: Real Task IDs (not placeholders)

**Criterion**: Contains actual task IDs (e.g., `ant-farm-abc`), NOT placeholders like `<task-id>`.

| Prompt | Verdict | Evidence |
|---|---|---|
| task-x4m | PASS | Uses `ant-farm-x4m` throughout (lines 1, 8, 16, 24) |
| task-e9k | PASS | Uses `ant-farm-e9k` throughout (lines 1, 8, 16, 24) |
| task-zeu | PASS | Uses `ant-farm-zeu` throughout (lines 1, 8, 16, 24) |

**Overall**: PASS

---

## Check 2: Real File Paths (not placeholders)

**Criterion**: Contains actual file paths with line numbers, NOT placeholders like `<list from bead>`.

| Prompt | Verdict | Evidence |
|---|---|---|
| task-x4m | PASS | Lists `orchestration/templates/dirt-pusher-skeleton.md:L29`, `orchestration/templates/nitpicker-skeleton.md:L19`. Scope Boundaries list `dirt-pusher-skeleton.md:L23-L45`, `nitpicker-skeleton.md:L13-L38`, `pantry.md:L46-L75`. All real paths confirmed to exist. |
| task-e9k | PASS | Lists `orchestration/templates/reviews.md:L321-L480`. Scope Boundaries list `reviews.md:L321-L480`, `big-head-skeleton.md:L47-L71`, `checkpoints.md:L444-L546`. All real paths confirmed (reviews.md L321 is Big Head Consolidation Protocol header). |
| task-zeu | PASS | Lists 5 affected locations: `pantry.md:L26`, `pantry.md:L26-L32`, `pantry.md:L94`, `big-head-skeleton.md:L23`, `checkpoints.md:L330`. Scope Boundaries list `pantry.md:L24-L35`, `pantry.md:L92-L100`, `big-head-skeleton.md:L20-L30`, `checkpoints.md:L329-L340`. All confirmed to exist with matching content. |

**Overall**: PASS

---

## Check 3: Root Cause Text (not placeholders)

**Criterion**: Contains a specific root cause description, NOT `<copy from bead>` or similar.

| Prompt | Verdict | Evidence |
|---|---|---|
| task-x4m | PASS | Root cause: "Skeleton templates reference {DATA_FILE_PATH} but never specify the file format. A cold agent might expect JSON or YAML instead of markdown." -- Specific and actionable. |
| task-e9k | PASS | Root cause: "reviews.md instructs Big Head not to proceed until all 4 reports are present (Step 0, lines 337-353) but never says what to DO about a missing report. No messaging, no error return, no timeout specified. Big Head could wait indefinitely." -- Specific, references exact lines. |
| task-zeu | PASS | Root cause: "Multiple templates assume their input artifacts exist and are well-formed without specifying explicit error behavior when they are missing or empty. Systematic gap across the template suite -- happy path covered, missing-input path not specified." -- Specific and well-scoped. |

**Overall**: PASS

---

## Check 4: All 6 Mandatory Steps Present

**Criterion**: Steps 1-6 as defined in the skeleton template must all be present.

Checking each preview against the skeleton requirements:

### task-x4m-preview.md
- Step 1 (`bd show` + `bd update --status=in_progress`): PRESENT -- line 8: `bd show ant-farm-x4m` + `bd update ant-farm-x4m --status=in_progress`
- Step 2 ("Design at least 4" / "4+ genuinely distinct"): PRESENT -- line 9: "4+ genuinely distinct approaches with tradeoffs"
- Step 3 (Implementation instructions): PRESENT -- line 10: "Write clean, minimal code satisfying acceptance criteria"
- Step 4 ("Re-read EVERY changed file" / per-file review): PRESENT -- line 11: "Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit."
- Step 5 (Commit with `git pull --rebase`): PRESENT -- line 12: `git pull --rebase && git add <changed-files> && git commit`
- Step 6 (Write summary doc to session dir): PRESENT -- line 13-14: "Write to .beads/agent-summaries/_session-405acc/summaries/x4m.md"

**Verdict**: PASS

### task-e9k-preview.md
- Step 1: PRESENT -- line 8
- Step 2: PRESENT -- line 9: "4+ genuinely distinct approaches"
- Step 3: PRESENT -- line 10
- Step 4: PRESENT -- line 11: "Re-read EVERY changed file"
- Step 5: PRESENT -- line 12: `git pull --rebase`
- Step 6: PRESENT -- line 13-14: summary to `.beads/agent-summaries/_session-405acc/summaries/e9k.md`

**Verdict**: PASS

### task-zeu-preview.md
- Step 1: PRESENT -- line 8
- Step 2: PRESENT -- line 9: "4+ genuinely distinct approaches"
- Step 3: PRESENT -- line 10
- Step 4: PRESENT -- line 11: "Re-read EVERY changed file"
- Step 5: PRESENT -- line 12: `git pull --rebase`
- Step 6: PRESENT -- line 13-14: summary to `.beads/agent-summaries/_session-405acc/summaries/zeu.md`

**Verdict**: PASS

**Overall**: PASS

---

## Check 5: Scope Boundaries

**Criterion**: Contains explicit limits on which files to read (not open-ended "explore the codebase").

| Prompt | Verdict | Evidence |
|---|---|---|
| task-x4m | PASS | Explicit "Read ONLY" list (3 file:line-range entries), explicit "Do NOT edit" list (5 entries including `pantry.md`, `implementation.md`, `reviews.md`, `checkpoints.md`, "Any file outside the two skeleton templates"), plus "SCOPE: Only edit files listed in the task context." |
| task-e9k | PASS | Explicit "Read ONLY" list (3 file:line-range entries), explicit "Do NOT edit" list (6 entries), plus global scope constraint. Section scope also specified: "Any section of reviews.md outside the Big Head Consolidation Protocol (lines 321-480)". |
| task-zeu | PASS | Explicit "Read ONLY" list (4 file:line-range entries), explicit "Do NOT edit" list (5 entries), plus global scope constraint. Also includes: "Any sections of the affected files outside the specified line ranges". |

**Overall**: PASS

---

## Check 6: Commit Instructions

**Criterion**: Includes `git pull --rebase` before commit.

| Prompt | Verdict | Evidence |
|---|---|---|
| task-x4m | PASS | Line 12: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-x4m)"` |
| task-e9k | PASS | Line 12: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-e9k)"` |
| task-zeu | PASS | Line 12: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-zeu)"` |

**Overall**: PASS

---

## Check 7: Line Number Specificity

**Criterion**: File paths include specific line ranges or section markers.

### task-x4m-preview.md
- Affected files: `dirt-pusher-skeleton.md:L29` (specific line), `nitpicker-skeleton.md:L19` (specific line) -- PASS
- Scope Boundaries: `dirt-pusher-skeleton.md:L23-L45` (line range with context note), `nitpicker-skeleton.md:L13-L38` (line range with context note), `pantry.md:L46-L75` (line range, read-only) -- PASS

**Verdict**: PASS

### task-e9k-preview.md
- Affected files: `reviews.md:L321-L480` (line range with section description) -- PASS
- Scope Boundaries: `reviews.md:L321-L480` (range + "Big Head Consolidation Protocol section"), `big-head-skeleton.md:L47-L71` (range + "Big Head template"), `checkpoints.md:L444-L546` (range + "CCB section") -- PASS

**Verdict**: PASS

### task-zeu-preview.md
- Affected files: `pantry.md:L26` (specific line), `pantry.md:L26-L32` (line range), `pantry.md:L94` (specific line), `big-head-skeleton.md:L23` (specific line), `checkpoints.md:L330` (specific line) -- PASS
- Scope Boundaries: `pantry.md:L24-L35` (range), `pantry.md:L92-L100` (range), `big-head-skeleton.md:L20-L30` (range), `checkpoints.md:L329-L340` (range) -- PASS

**Verdict**: PASS

**Overall**: PASS

---

## Cross-Prompt Consistency Checks (Bonus)

These are not part of the 7-check CCO rubric but are noted for completeness:

### Data File Consistency
Each preview references a data file at `{SESSION_DIR}/prompts/task-{suffix}.md`. Verified all three data files exist at:
- `.beads/agent-summaries/_session-405acc/prompts/task-x4m.md`
- `.beads/agent-summaries/_session-405acc/prompts/task-e9k.md`
- `.beads/agent-summaries/_session-405acc/prompts/task-zeu.md`

The content in each preview (below the `---` separator) exactly matches the corresponding data file content. This means the preview IS the composed prompt (skeleton + data file merged). CONFIRMED.

### Scope Overlap Risk
- task-x4m edits `dirt-pusher-skeleton.md` and `nitpicker-skeleton.md`
- task-e9k edits `reviews.md` (lines 321-480 only)
- task-zeu edits `pantry.md`, `big-head-skeleton.md`, and `checkpoints.md`

No file overlap between any pair of tasks. All three can run concurrently without merge conflicts. CONFIRMED.

### Summary Output Path Consistency
- x4m: `.beads/agent-summaries/_session-405acc/summaries/x4m.md` -- matches skeleton convention
- e9k: `.beads/agent-summaries/_session-405acc/summaries/e9k.md` -- matches skeleton convention
- zeu: `.beads/agent-summaries/_session-405acc/summaries/zeu.md` -- matches skeleton convention

All paths follow `{SESSION_DIR}/summaries/{TASK_SUFFIX}.md` pattern. CONFIRMED.

---

## Verdict Table

| # | Check | x4m | e9k | zeu |
|---|---|---|---|---|
| 1 | Real task IDs | PASS | PASS | PASS |
| 2 | Real file paths | PASS | PASS | PASS |
| 3 | Root cause text | PASS | PASS | PASS |
| 4 | All 6 mandatory steps | PASS | PASS | PASS |
| 5 | Scope boundaries | PASS | PASS | PASS |
| 6 | Commit instructions | PASS | PASS | PASS |
| 7 | Line number specificity | PASS | PASS | PASS |

## Overall Verdict: PASS

All 7 checks pass for all 3 Dirt Pusher prompts. No scope overlap detected between tasks. Prompts are ready for spawn.
