# Pest Control - Checkpoint A: Pre-Spawn Prompt Audit
**Task**: ant-farm-yta
**Preview file**: `.beads/agent-summaries/_session-ae4401/previews/task-yta-preview.md`
**Timestamp**: 2026-02-17T12:25:36

---

## Check 1: Real Task IDs
**PASS**

The preview contains the real task ID `ant-farm-yta` in multiple locations:
- Line 1: "Execute task for ant-farm-yta."
- Line 8: `bd show ant-farm-yta` + `bd update ant-farm-yta --status=in_progress`
- Line 12: commit message template includes `(ant-farm-yta)`
- Line 19: `bd close ant-farm-yta`

No placeholders like `<task-id>` or `<id>` found.

---

## Check 2: Real File Paths
**PASS**

The preview references two concrete files:
- `~/.claude/orchestration/templates/pantry.md` -- confirmed exists, "Step 4: Compose Big Head Consolidation Data File" found at line 124
- `~/.claude/orchestration/templates/reviews.md` -- confirmed exists, "## Big Head Consolidation Protocol" found at line 315
- `.beads/agent-summaries/_standalone/yta.md` -- valid output path under the correct epic directory

No placeholder paths like `<list from bead>` or `<file>` found.

---

## Check 3: Root Cause Text
**PASS**

Root cause is specific and substantive (preview lines 32):
> "pantry.md Section 2, Step 4 lists what Big Head consolidation data should contain (4 report paths, dedup protocol, bead filing instructions, consolidated output path) but the actual format/structure lives in reviews.md Big Head Consolidation Protocol section. No explicit cross-reference pointer exists, so a fresh Pantry agent has to guess where the format specification lives."

This is a concrete description of a real documentation gap, not a placeholder.

---

## Check 4: All 6 Mandatory Steps Present
**PASS**

| Step | Required Content | Found | Evidence |
|------|-----------------|-------|----------|
| 1 | `bd show` + `bd update --status=in_progress` | Yes | Line 8: `bd show ant-farm-yta` + `bd update ant-farm-yta --status=in_progress` |
| 2 | "Design at least 4 approaches" (MANDATORY) | Yes | Line 9: "**Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs" |
| 3 | Implementation instructions | Yes | Line 10: "**Implement**: Write clean, minimal code satisfying acceptance criteria" |
| 4 | "Review EVERY file" (MANDATORY) | Yes | Line 11: "**Review** (MANDATORY): Re-read EVERY changed file" |
| 5 | Commit with `git pull --rebase` | Yes | Line 12: `git pull --rebase && git add <changed-files> && git commit` |
| 6 | Summary doc to `.beads/agent-summaries/{EPIC_ID}/` | Yes | Line 14: "Write to .beads/agent-summaries/_standalone/yta.md" |

All 6 steps present with mandatory keywords.

---

## Check 5: Scope Boundaries
**PASS**

Explicit scope limits found in multiple locations:
- Line 17: "SCOPE: Only edit files listed in the task context."
- Lines 40-41: "Read ONLY:" with exactly two files listed
- Lines 43-47: "Do NOT edit:" with explicit exclusions (reviews.md, any file other than pantry.md, any section other than Step 4)
- Lines 56-60: Additional focus constraints ("Do NOT fix adjacent issues", "Do NOT restructure Step 4 content", "Do NOT duplicate format content")

Not open-ended. Tightly constrained to one section of one file.

---

## Check 6: Commit Instructions
**PASS**

`git pull --rebase` appears twice:
- Line 12: In the commit step: `git pull --rebase && git add <changed-files> && git commit`
- Lines 52-53: Pre-implementation mandatory step with `git pull --rebase`

---

## Check 7: Line Number Specificity
**WARN (acceptable)**

The prompt uses section-level search markers instead of line numbers:
- pantry.md: "Search for 'Step 4: Compose Big Head Consolidation Data File' to locate"
- reviews.md: "Search for '## Big Head Consolidation Protocol' to locate"

The prompt explicitly justifies this (line 55): "Do NOT rely on any pre-supplied line numbers. Use text search to locate the relevant sections." because "Wave 1 and Wave 2 agents have modified pantry.md before you" (line 51).

This is a deliberate design decision: line numbers would be stale by execution time. The search strings are unique heading identifiers (confirmed: pantry.md has exactly one match at line 124, reviews.md has exactly one match at line 315). The edit scope is further narrowed to "Step 4 in Section 2" only.

Per checkpoint criteria, this falls between WARN ("file-level scope, acceptable if small file") and PASS ("specific line ranges"). Given the explicit rationale and unique search anchors, this is acceptable.

---

## Verdict: PASS

All 7 checks pass (Check 7 at WARN tier, within acceptable bounds due to deliberate stale-line-number mitigation).

| Check | Result |
|-------|--------|
| 1. Real task IDs | PASS |
| 2. Real file paths | PASS |
| 3. Root cause text | PASS |
| 4. All 6 mandatory steps | PASS |
| 5. Scope boundaries | PASS |
| 6. Commit instructions | PASS |
| 7. Line number specificity | WARN (acceptable) |

**Overall: PASS** -- Prompt is safe to spawn.
