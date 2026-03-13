# Summary: ant-farm-ss6 — Task ID Suffix Terminology Standardization

**Commit**: `03f6299`
**Task ID**: ant-farm-ss6
**Files changed**:
- `orchestration/RULES.md`
- `orchestration/templates/checkpoints.md`
- `orchestration/templates/dirt-pusher-skeleton.md`
- `orchestration/templates/pantry.md`

---

## 1. Approaches Considered

**Approach A: Uppercase-pair (`{TASK_ID}` / `{TASK_SUFFIX}`) with inline definitions**
- Define `{TASK_ID}` = full bead ID (e.g., `ant-farm-9oa`) and `{TASK_SUFFIX}` = suffix only (e.g., `9oa`)
- Add a term definitions block at the top of each template
- Replace all existing lowercase/angle-bracket variants with these two canonical terms
- Tradeoff: Requires updating every occurrence; produces a clean, unambiguous vocabulary that matches the existing uppercase placeholder convention in dirt-pusher-skeleton.md

**Approach B: Keep `{task-id-suffix}` but add definitions only**
- Leave existing lowercase `{task-id-suffix}` as-is throughout pantry.md and checkpoints.md
- Simply add a "Term Definitions" block explaining what each means
- Tradeoff: Minimal change risk, but still leaves `<task-id>` vs `{task-id}` vs `{task-id-suffix}` all in the wild — doesn't eliminate the confusion, only annotates it

**Approach C: Single term `{TASK_ID}` everywhere, drop suffix concept**
- Require every agent to derive the suffix by parsing the full ID themselves
- Tradeoff: Simpler vocabulary (one term, not two), but forces every downstream agent to perform error-prone string manipulation on IDs. High risk of format mistakes in artifact filenames.

**Approach D: Introduce a glossary in RULES.md, point all templates to it**
- RULES.md becomes the single authoritative source for terminology
- All other templates say "see RULES.md for term definitions"
- Tradeoff: Violates the acceptance criterion that "a fresh agent reading any single template knows the exact format without cross-referencing." Agents already have limited context windows and cross-file lookups are expensive.

**Approach E: Use `{TASK_ID_SUFFIX}` (verbose) and `{EPIC_ID_SUFFIX}` to make relationship explicit**
- Names are self-descriptive: `{TASK_ID_SUFFIX}` makes it unambiguous that it is derived from the task ID
- Tradeoff: More verbose than `{TASK_SUFFIX}`; adds length to every path expression in the files without improving clarity over the shorter form

---

## 2. Selected Approach

**Selected: Approach A — Uppercase-pair with inline definitions**

Rationale:
- Approach A is the only approach that both eliminates the inconsistency AND satisfies the acceptance criterion that each template is self-contained
- `{TASK_ID}` was already the established uppercase placeholder convention in dirt-pusher-skeleton.md; extending it with `{TASK_SUFFIX}` and `{EPIC_ID}` is the natural completion of that pattern
- Adding the term definitions block to every file means any agent reading only one file immediately knows all three concepts
- The ant-farm repo's canonical files differ significantly from the `~/.claude/` deployed copies (the ant-farm repo retains ant-themed checkpoint names: CCO, WWD, DMVDC, CCB). This refactor targets only the terminology, not the checkpoint naming, so ant-themed names are preserved.

---

## 3. Implementation Description

### Canonical terms introduced

| Term | Meaning | Example |
|------|---------|---------|
| `{TASK_ID}` | Full bead ID including project prefix | `ant-farm-9oa`, `hs_website-74g.1` |
| `{TASK_SUFFIX}` | Suffix only, no project prefix | `9oa`, `74g1` |
| `{EPIC_ID}` | Epic suffix only | `74g`, `_standalone` |

### Changes per file

**orchestration/templates/dirt-pusher-skeleton.md**
- Added term definitions block after the instruction header
- Added `{TASK_SUFFIX}` to the Placeholders list
- Replaced `{task-id-suffix}` in `{SUMMARY_OUTPUT_PATH}` example with `{TASK_SUFFIX}`
- Replaced `{epic-id}` in `{SUMMARY_OUTPUT_PATH}` example with `{EPIC_ID}`
- Simplified `{TASK_ID}` placeholder description (removed "NOT just the suffix" as that is now covered by the definitions block)

**orchestration/templates/pantry.md**
- Added term definitions block after the intro paragraph
- Replaced `{task-id-suffix}` with `{TASK_SUFFIX}` in all 3 occurrences (task-metadata read path, data file write path, preview write path)
- Replaced `{task-id}` in Task Brief template header with `{TASK_ID}`
- Replaced `{epic-id}` in Epic ID, Summary output path, review-reports path, and consolidated path with `{EPIC_ID}`

**orchestration/templates/checkpoints.md**
- Added term definitions block at top of file
- Renamed "Task ID format" section to "Task suffix derivation" (more accurate)
- Replaced all `<task-id>` angle-bracket usages in artifact paths with `{TASK_SUFFIX}`
- Replaced all `<epic-id>` angle-bracket usages in artifact paths and descriptions with `{EPIC_ID}`
- Replaced `{task-id}` (curly brace) in `bd show` commands with `{TASK_ID}` (full ID required for CLI)
- Replaced `{task-id}` in artifact filename positions with `{TASK_SUFFIX}`
- Replaced `{epic-id}` (curly brace) in artifact filename positions with `{EPIC_ID}`
- Updated "Where:" definition blocks to use canonical terms with inline explanations
- Updated summary doc path and report path references
- Preserved intentional negative example: `<task-id>` on CCO check 1 ("NOT placeholders like `<task-id>`") — this teaches Pest Control to reject that pattern

**orchestration/RULES.md**
- Replaced `<epic>` with `{EPIC_ID}` in all four Hard Gates table artifact paths
- Replaced `<epic-id>` with `{EPIC_ID}` in Steps 2 and 3b mkdir examples
- Replaced `<epic-id>` with `{EPIC_ID}` in Epic Artifact Directories section and surrounding prose

### Note on the `~/.claude/orchestration/` copies

The task's files (`~/.claude/orchestration/`) are deployed copies synced from the ant-farm repo via a pre-push hook. They are NOT git-tracked. The canonical source is the ant-farm repo's `orchestration/` directory. This refactor targets the git-tracked canonical source.

---

## 4. Correctness Review

### dirt-pusher-skeleton.md
- Re-read: yes
- Term definitions block is present and correct
- `{TASK_ID}` placeholder: correctly described as full bead ID
- `{TASK_SUFFIX}` placeholder: newly added, correctly described
- `{SUMMARY_OUTPUT_PATH}` example: now uses `{EPIC_ID}/{TASK_SUFFIX}` — consistent with definitions
- Template agent-facing section: `{TASK_ID}` used in claim commands (correct — `bd show` needs full ID)
- Acceptance criteria check: no mixed terminology remains

### pantry.md
- Re-read: yes
- Term definitions block is present and correct
- Task-metadata read path: `{TASK_SUFFIX}` — correct (file is named by suffix)
- Data file write path: `task-{TASK_SUFFIX}.md` — correct
- Template output block: `{TASK_ID}` in header (correct — Task Brief shows full ID for agent reference), `{EPIC_ID}` and `{TASK_SUFFIX}` in paths — correct
- Review mode paths: `{EPIC_ID}/review-reports/...` — correct
- No mixed terminology remains

### checkpoints.md
- Re-read: yes
- Term definitions block is present and correct
- Artifact naming conventions: `{TASK_SUFFIX}` and `{EPIC_ID}` — correct
- "Task suffix derivation" section replaces old "Task ID format" — more accurate naming
- CCO Dirt Pushers: `bd show` uses `{TASK_ID}` (full ID needed for CLI) — correct; artifact path uses `{TASK_SUFFIX}` — correct
- WWD: `bd show {TASK_ID}` — correct; artifact path uses `{TASK_SUFFIX}` — correct
- DMVDC: `bd show {TASK_ID}` — correct; summary doc path uses `{EPIC_ID}/{TASK_SUFFIX}` — correct; artifact path uses `{TASK_SUFFIX}` — correct
- CCB: artifact path uses `{EPIC_ID}` — correct
- Negative example on line 78 (`<task-id>`) preserved intentionally
- All "Where:" clauses updated to define `{TASK_SUFFIX}` and `{EPIC_ID}` inline

### RULES.md
- Re-read: yes
- Hard Gates table: all four rows use `{EPIC_ID}` — consistent
- Step 2 mkdir: `{EPIC_ID}` — correct
- Step 3b mkdir: `{EPIC_ID}` — correct
- Epic Artifact Directories section: `{EPIC_ID}` in command, prose, and surrounding explanation — correct
- No mixed `<epic>` / `<epic-id>` / `{epic-id}` terminology remains

---

## 5. Build/Test Validation

These are documentation-only template files — no automated tests exist for them. Validation performed manually:

1. Pattern search: `grep` for `<task-id>`, `<epic-id>`, `{task-id}`, `{task-id-suffix}`, `{epic-id}` across all four files — zero matches except the intentional negative example in checkpoints.md
2. Pattern search: `grep` for `TASK_ID`, `TASK_SUFFIX`, `EPIC_ID` confirms new terms are present and used consistently
3. Full re-read of all four changed files — no remaining old-format references found
4. Verified functional content (checkpoint logic, step descriptions, agent commands) is unchanged

---

## 6. Acceptance Criteria Checklist

**AC 1: One term is chosen and defined for each concept**
- `{TASK_ID}` = full bead ID (e.g., `ant-farm-9oa`) — defined in each file's term definitions block
- `{TASK_SUFFIX}` = suffix only (e.g., `9oa`) — defined in each file's term definitions block
- `{EPIC_ID}` = epic suffix (e.g., `74g`) or `_standalone` — defined in each file's term definitions block
- **PASS**

**AC 2: All three primary files use the chosen terms consistently — no mixed terminology**
- dirt-pusher-skeleton.md: uses `{TASK_ID}`, `{TASK_SUFFIX}`, `{EPIC_ID}` — **PASS**
- pantry.md: uses `{TASK_ID}`, `{TASK_SUFFIX}`, `{EPIC_ID}` — **PASS**
- checkpoints.md: uses `{TASK_ID}` (for bd show commands), `{TASK_SUFFIX}` (for artifact names), `{EPIC_ID}` (for paths) — **PASS**
- **PASS**

**AC 3: RULES.md either defines canonical format or uses consistent terminology**
- RULES.md uses `{EPIC_ID}` consistently in all path and command references — **PASS**
- Term definitions are in each individual template file (not RULES.md), satisfying the self-contained criterion — **PASS**

**AC 4: A fresh agent reading any single template knows the format without cross-referencing**
- Every modified file has a "Term definitions" block at the top, defining all three canonical terms with examples before any instruction content
- **PASS**
