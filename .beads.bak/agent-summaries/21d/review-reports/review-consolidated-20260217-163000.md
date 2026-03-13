# Consolidated Review Summary

**Scope**: orchestration/templates/scout.md, orchestration/templates/pantry.md
**Reviews completed**: Clarity, Edge Cases, Correctness, Excellence
**Reports verified**: clarity-review-20260217-163000.md, edge-cases-review-20260217-163000.md, correctness-review-20260217-163000.md, excellence-review-20260217-163000.md
**Total raw findings**: 16 across all reviews (1 positive observation excluded)
**Root causes identified**: 9 after deduplication
**Beads filed**: 9

## Read Confirmation

**All 4 reports read and processed by Big Head consolidation:**

| Report Type | File | Status | Finding Count |
|-------------|------|--------|---------------|
| Clarity | clarity-review-20260217-163000.md | Read | 4 findings + 1 positive observation |
| Edge Cases | edge-cases-review-20260217-163000.md | Read | 6 findings |
| Correctness | correctness-review-20260217-163000.md | Read | 2 findings |
| Excellence | excellence-review-20260217-163000.md | Read | 4 findings |

**Total findings from all reports**: 16 (excluding 1 positive observation)

## Root-Cause Grouping (Big Head Consolidation)

### Root Cause 1: Scout error metadata template lacks context fields present in success template

- **Root cause**: The error metadata file format (scout.md:192-196) contains only Status and Error Details, while the success format (scout.md:69-92) includes Title, Type, Priority, Epic, Agent Type, Dependencies, and multiple sections. Downstream consumers (Pantry, Queen, debug logs) cannot identify which task errored without a separate lookup. The asymmetry also creates parsing risk if the Pantry reads fields sequentially before hitting the Status check.
- **Affected surfaces**:
  - `orchestration/templates/scout.md`:186-196 -- error format minimal vs success format (from clarity review, Finding 1)
  - `orchestration/templates/scout.md`:186-196 -- Pantry parsing could fail on missing Title before reaching Status (from edge-cases review, Finding 1)
  - `orchestration/templates/scout.md`:186-196 -- minor completeness gap (from correctness review, Finding 2)
  - `orchestration/templates/scout.md`:192-196 -- maintenance risk from format asymmetry (from excellence review, Finding 3)
- **Combined priority**: P2 (edge-cases rated P2; clarity, correctness, excellence all rated P3)
- **Fix**: Add minimal context fields to the error template: `**Title**: {title if available, else full-task-id}` and `**Epic**: {epic-id or unknown}`. Also document in pantry.md that the `**Status**: error` check must be the FIRST check performed, before reading any other fields.
- **Merge rationale**: All 4 findings reference the exact same lines (scout.md:186-196) and the exact same structural gap (error metadata missing fields that the success metadata has). The clarity reviewer notes the contrast is confusing, edge-cases identifies a parsing failure mode, correctness notes a completeness gap, and excellence flags maintenance risk -- all driven by the same asymmetric template design.
- **Acceptance criteria**: Error metadata template includes at least Title and Epic fields. Pantry explicitly checks Status before other fields.
- **Bead**: ant-farm-lhq (P2)

### Root Cause 2: Pantry fail-fast check uses redundant "missing, does not exist" phrasing

- **Root cause**: pantry.md:27 says "If the file is missing, does not exist, or contains **Status**: error" -- "missing" and "does not exist" are semantically identical, wasting context tokens and potentially confusing cold agents into thinking there are three distinct failure conditions.
- **Affected surfaces**:
  - `orchestration/templates/pantry.md`:27 -- redundant disjunction (from clarity review, Finding 2)
  - `orchestration/templates/pantry.md`:27 -- unnecessary verbosity (from excellence review, Finding 1)
- **Combined priority**: P3 (both reviewers rated P3)
- **Fix**: Simplify to: "If the file does not exist or contains `**Status**: error`:"
- **Merge rationale**: Both findings reference the exact same line (pantry.md:27) and the exact same wording issue ("missing" and "does not exist" are synonyms). One root cause: a redundant phrase was included when writing the fail-fast condition.
- **Acceptance criteria**: pantry.md fail-fast condition uses non-redundant phrasing with exactly two conditions.
- **Bead**: ant-farm-qql (P3)

### Root Cause 3: Pantry "report to Queen immediately" misleading for Task subagent model

- **Root cause**: pantry.md:30 says "Report to the Queen immediately" but the Pantry is a Task subagent that cannot send mid-execution messages. "Immediately" is misleading -- the error will only be seen when the Pantry returns its final output.
- **Affected surfaces**:
  - `orchestration/templates/pantry.md`:30 -- no mechanism for mid-composition abort (from edge-cases review, Finding 3)
  - `orchestration/templates/pantry.md`:30 -- "immediately" misleading in subagent context (from excellence review, Finding 2)
- **Combined priority**: P3 (both reviewers rated P3)
- **Fix**: Rephrase to: "Include in your return output: `TASK FAILED: {TASK_ID} -- Scout metadata error: {error details}`. Continue processing remaining tasks."
- **Merge rationale**: Both findings reference the exact same line (pantry.md:30) and the exact same problem: the word "immediately" implies a real-time message capability that Task subagents do not have. One root cause: the instruction was written as if the Pantry had SendMessage capability.
- **Acceptance criteria**: Pantry fail-fast instruction uses return-output framing instead of "immediately."
- **Bead**: ant-farm-6e1 (P3)

### Root Cause 4: Scout ready mode has gaps in downstream step adjustments and documentation

- **Root cause**: Ready mode (added in commit 55c8401, outside nr2 scope) tells the Scout to skip `bd ready`/`bd blocked` (line 32), but Step 4 (line 114) still references `bd blocked` output for dependency chain analysis. The skip assumption ("tasks are already unblocked") is undocumented. The ready mode addition was not covered by a task's acceptance criteria.
- **Affected surfaces**:
  - `orchestration/templates/scout.md`:32, 114 -- Step 4 references data not gathered in ready mode (from edge-cases review, Finding 4)
  - `orchestration/templates/scout.md`:24-26 -- out-of-scope addition without task coverage (from correctness review, Finding 1)
  - `orchestration/templates/scout.md`:32 -- undocumented assumption about bd ready behavior (from excellence review, Finding 4)
- **Combined priority**: P3 (all 3 reviewers rated P3)
- **Fix**: Add to Step 4: "In ready mode, skip dependency chain analysis (tasks from `bd ready` are unblocked by definition). Set all dependency chains to empty." Add a note documenting the bd ready assumption. File a retrospective task for the ready mode addition.
- **Merge rationale**: All 3 findings relate to the same feature (ready mode) and the same root cause: it was added without fully adjusting downstream steps (Step 4 dependency analysis) or documenting the assumptions that justify skipping certain operations. The correctness finding is process-level (no task ID), while edge-cases and excellence are code-level, but all stem from the incomplete ready mode integration.
- **Acceptance criteria**: Ready mode has explicit step-by-step notes for all 7 Scout steps. The assumption about `bd ready` returning only unblocked tasks is documented.
- **Bead**: ant-farm-cev (P3)

### Root Cause 5: Scout Step 2.5 silently skips agent files with invalid frontmatter

- **Root cause**: scout.md:43-44 says "skip files without valid frontmatter" but does not specify logging a warning. This contradicts the template's own error handling philosophy (added in nr2) which was specifically designed to prevent silent dropping. An agent file with a YAML typo would be silently excluded from recommendations with no trace.
- **Affected surfaces**:
  - `orchestration/templates/scout.md`:43-44 -- no logging for skipped agent files (from clarity review, Finding 5)
  - Confirmed by edge-cases cross-review message as a valid failure mode
- **Combined priority**: P3
- **Fix**: Add: "Log a warning in the briefing's Errors section for agent files with missing or invalid frontmatter."
- **Merge rationale**: Single reviewer finding, confirmed by edge-cases cross-review. No merge needed.
- **Acceptance criteria**: Skipped agent files produce a visible warning in the briefing output.
- **Bead**: ant-farm-hrt (P3)

### Root Cause 6: Scout {MODE} placeholder parsing convention undocumented for compound modes

- **Root cause**: scout.md:11 declares `{MODE}` as input, but mode values include embedded arguments (e.g., `epic <epic-id>`, `tasks <id1>, <id2>, ...`). How the Queen splits the placeholder into mode name and argument is undefined.
- **Affected surfaces**:
  - `orchestration/templates/scout.md`:11, 24-30 -- compound mode format undefined (from clarity review, Finding 3)
- **Combined priority**: P3
- **Fix**: Document the parsing convention: "The first word is the mode name; remaining words are the argument." Or split into `{MODE}` and `{MODE_ARG}` placeholders.
- **Merge rationale**: Single reviewer finding. No merge needed.
- **Acceptance criteria**: Mode parsing convention is documented or the placeholder is split into mode + argument.
- **Bead**: ant-farm-hpi (P3)

### Root Cause 7: Scout briefing format lacks optional Errors section placement

- **Root cause**: scout.md:186-188 instructs writing errors to a `## Errors` section in the briefing, but the briefing format template (lines 131-168) does not include this section. A Scout agent must improvise its placement.
- **Affected surfaces**:
  - `orchestration/templates/scout.md`:186-188 vs 131-168 -- format mismatch (from edge-cases review, Finding 2)
- **Combined priority**: P3
- **Fix**: Add `## Errors` as an optional section in the briefing format template, positioned between `## Task Inventory` and `## File Modification Matrix`.
- **Merge rationale**: Single reviewer finding. No merge needed.
- **Acceptance criteria**: Briefing format template includes an optional `## Errors` section with documented placement.
- **Bead**: ant-farm-a86 (P3)

### Root Cause 8: Pantry review mode has no fail-fast for empty changed-file list

- **Root cause**: pantry.md review mode (line 107) accepts a "list of changed files" but has no check for an empty list. An empty list would produce 4 review data files with nothing to review, wasting a full Nitpicker cycle.
- **Affected surfaces**:
  - `orchestration/templates/pantry.md`:107 -- no empty-input guard (from edge-cases review, Finding 5)
- **Combined priority**: P3
- **Fix**: Add a check: "If the changed-file list is empty, return immediately with: `NO FILES TO REVIEW: commit range {first}..{last} produced no changed files.`"
- **Merge rationale**: Single reviewer finding. No merge needed.
- **Acceptance criteria**: Pantry review mode returns early with a clear message when the file list is empty.
- **Bead**: ant-farm-zvl (P3)

### Root Cause 9: Scout metadata write-each-immediately has no truncation/atomicity check downstream

- **Root cause**: scout.md:104 instructs "Write each file immediately after extraction -- do not batch." If the Scout crashes mid-write, a partially written metadata file could exist on disk. The Pantry only checks for `**Status**: error` or file absence, not for truncated files missing required sections.
- **Affected surfaces**:
  - `orchestration/templates/scout.md`:104 + `orchestration/templates/pantry.md`:27 -- truncated file passes fail-fast (from edge-cases review, Finding 6)
- **Combined priority**: P3
- **Fix**: Add to Pantry fail-fast: "Also check for missing required sections (## Root Cause, ## Acceptance Criteria). If any required section is absent, treat as metadata error."
- **Merge rationale**: Single reviewer finding. No merge needed.
- **Acceptance criteria**: Pantry validates presence of required sections in metadata files, not just Status field.
- **Bead**: ant-farm-laq (P3)

## Deduplication Log

16 raw findings consolidated into 9 root causes. 7 findings were merged (duplicates eliminated).

| Raw Finding | Root Cause | Merge Rationale |
|-------------|------------|-----------------|
| Clarity F1 (error metadata minimal P3) | RC1 (ant-farm-lhq) | Same lines (scout.md:186-196), same format asymmetry |
| Edge Cases F1 (error metadata parsing risk P2) | RC1 (ant-farm-lhq) | Same lines, same missing fields |
| Correctness F2 (error metadata incomplete P3) | RC1 (ant-farm-lhq) | Same lines, same completeness gap |
| Excellence F3 (error metadata maintenance risk P3) | RC1 (ant-farm-lhq) | Same lines, same asymmetry |
| Clarity F2 (redundant phrasing P3) | RC2 (ant-farm-qql) | Same line (pantry.md:27), same wording |
| Excellence F1 (redundant phrasing P3) | RC2 (ant-farm-qql) | Same line, same wording |
| Edge Cases F3 (report immediately P3) | RC3 (ant-farm-6e1) | Same line (pantry.md:30), same communication model issue |
| Excellence F2 (report immediately P3) | RC3 (ant-farm-6e1) | Same line, same issue |
| Edge Cases F4 (ready mode Step 4 gap P3) | RC4 (ant-farm-cev) | Same feature (ready mode), incomplete integration |
| Correctness F1 (ready mode scope creep P3) | RC4 (ant-farm-cev) | Same feature, no task coverage |
| Excellence F4 (ready mode assumption P3) | RC4 (ant-farm-cev) | Same feature, undocumented assumption |
| Clarity F5 (silent agent skip P3) | RC5 (ant-farm-hrt) | Standalone, confirmed by edge-cases cross-review |
| Clarity F3 (mode parsing P3) | RC6 (ant-farm-hpi) | Standalone |
| Edge Cases F2 (errors section P3) | RC7 (ant-farm-a86) | Standalone |
| Edge Cases F5 (empty file list P3) | RC8 (ant-farm-zvl) | Standalone |
| Edge Cases F6 (truncation risk P3) | RC9 (ant-farm-laq) | Standalone |

## Root Causes Filed

| Bead ID | Priority | Title | Contributing Reviews | Surfaces |
|---------|----------|-------|---------------------|----------|
| ant-farm-lhq | P2 | Scout error metadata lacks context fields | clarity, edge-cases, correctness, excellence | 1 file (scout.md:186-196) |
| ant-farm-qql | P3 | Pantry fail-fast redundant phrasing | clarity, excellence | 1 file (pantry.md:27) |
| ant-farm-6e1 | P3 | Pantry "report immediately" misleading | edge-cases, excellence | 1 file (pantry.md:30) |
| ant-farm-cev | P3 | Scout ready mode gaps | edge-cases, correctness, excellence | 1 file (scout.md:24-32, 114) |
| ant-farm-hrt | P3 | Scout silent agent file skipping | clarity | 1 file (scout.md:43-44) |
| ant-farm-hpi | P3 | Scout {MODE} parsing undocumented | clarity | 1 file (scout.md:11, 24-30) |
| ant-farm-a86 | P3 | Scout briefing Errors section unspecified | edge-cases | 1 file (scout.md:131-168 vs 186-188) |
| ant-farm-zvl | P3 | Pantry review mode no empty-file-list guard | edge-cases | 1 file (pantry.md:107) |
| ant-farm-laq | P3 | Scout metadata truncation risk in Pantry | edge-cases | 2 files (scout.md:104, pantry.md:27) |

## Priority Breakdown

- **P1 (blocking)**: 0 beads
- **P2 (important)**: 1 bead
  - ant-farm-lhq: Scout error metadata template gaps (found by all 4 reviewers)
- **P3 (polish)**: 8 beads
  - ant-farm-qql: Redundant phrasing (2 reviewers)
  - ant-farm-6e1: Communication model mismatch (2 reviewers)
  - ant-farm-cev: Ready mode gaps (3 reviewers)
  - ant-farm-hrt: Silent agent skip (1 reviewer)
  - ant-farm-hpi: Mode parsing convention (1 reviewer)
  - ant-farm-a86: Errors section placement (1 reviewer)
  - ant-farm-zvl: Empty file list guard (1 reviewer)
  - ant-farm-laq: Metadata truncation risk (1 reviewer)

## Verdict

**PASS WITH ISSUES**

The nr2 error handling additions to scout.md and pantry.md are well-designed and effectively solve the silent task-dropping problem that motivated the work. All 3 acceptance criteria for task nr2 are verified as met. The single P2 finding (error metadata template lacking context fields) is a completeness gap that could cause parsing issues in edge cases but does not break the core error-detection flow. The 8 P3 findings are polish items: redundant wording, misleading communication framing, ready mode integration gaps, and defensive checks for boundary conditions. The overall architecture is sound -- these are refinements, not structural problems.
