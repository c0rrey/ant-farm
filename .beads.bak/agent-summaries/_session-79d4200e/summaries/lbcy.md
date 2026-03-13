# Task Summary: ant-farm-lbcy

**Task**: fix: double-brace placeholder tier {{SLOT}} absent from PLACEHOLDER_CONVENTIONS.md
**Agent**: technical-writer
**Status**: Complete

---

## 1. Approaches Considered

### Approach A: Surgical addition — new Tier 4 section + overview table row + audit table fix (SELECTED)
Add a row to the Overview table, a full `### Tier 4` section after Tier 3, a Pattern 5 validation rule, fix the reviews.md audit row, and update minor references to "three tiers" language. All edits confined to `orchestration/PLACEHOLDER_CONVENTIONS.md`.

**Tradeoffs**: Minimal surface area, exactly targets the gap, no risk of disrupting working content, all four acceptance criteria satisfied.

### Approach B: Renumber tiers globally — insert double-brace as Tier 2 for conceptual ordering
Reorder all tier numbers so that script-substituted slots come before runtime-derived placeholders in the conceptual sequence (Queen spawns → script fills → agent derives → shell executes).

**Tradeoffs**: Would require touching every section that mentions tier numbers, including the Compliance Status Key Findings entries. High disruption for speculative benefit. Violates the scope constraint (only edit PLACEHOLDER_CONVENTIONS.md) in spirit and exceeds the acceptance criteria footprint. Rejected.

### Approach C: Document {{DOUBLE_BRACE}} under "Exceptions and Special Cases" only
Add the double-brace convention as a named exception rather than a numbered tier, avoiding the need to update tier numbering or the overview table.

**Tradeoffs**: Buries the documentation in a lower-priority section. Does not satisfy acceptance criterion 1 which explicitly requires documenting a "tier." Less discoverable for new template authors. Rejected.

### Approach D: Holistic update of all tier-aware sections including Benefits, Enforcement, Compliance Status
In addition to adding Tier 4, comprehensively update every section in the document that references the number of tiers or lists tier-related characteristics.

**Tradeoffs**: More thorough but has a larger diff than needed. Creates risk of inadvertently changing content outside the acceptance criteria scope. Selected a middle path: updated the Benefits "Semantically rich" line and the Compliance Status Key Findings item 6 to be accurate, but did not rewrite sections that were functionally correct as-is.

---

## 2. Selected Approach with Rationale

**Selected**: Approach A (surgical addition), augmented with targeted secondary edits from Approach D for accuracy.

**Rationale**: The acceptance criteria are precise:
1. Document the `{{DOUBLE_BRACE}}` tier.
2. Identify `fill-review-slots.sh` as the substitution mechanism.
3. Fix the reviews.md audit row.
4. Account for all `{{SLOT}}` markers across templates.

Approach A satisfies all four criteria with the minimum number of changes. The secondary edits (updating "three tiers" to "four tiers" in Benefits, fixing Key Finding 6 to mention reviews.md Tier 4 usage) are necessary for internal consistency and correctness — they do not constitute scope creep.

---

## 3. Implementation Description

**File modified**: `/Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md`

**Changes made**:

1. **Overview section (L7)**: Changed "three distinct placeholder syntaxes" to "four distinct placeholder syntaxes."

2. **Overview table (L9-14)**: Added a fourth row:
   ```
   | `{{UPPERCASE}}` | Review slot markers | `fill-review-slots.sh` | When shell script composes review prompts | `{{REVIEW_ROUND}}`, `{{COMMIT_RANGE}}`, `{{CHANGED_FILES}}` |
   ```

3. **New Tier 4 section (after Tier 3, before the File-by-File Audit)**: Added `### Tier 4: Script-Substituted ({{DOUBLE_BRACE}})` with full documentation including:
   - Purpose and timing description
   - Characteristics (ALL CAPS double braces, filled by `fill-review-slots.sh`, skeleton templates only, guard behavior)
   - Examples: `{{REVIEW_ROUND}}`, `{{COMMIT_RANGE}}`, `{{CHANGED_FILES}}`, `{{TASK_IDS}}`
   - Rationale for double braces over single braces
   - Substitution mechanism (`sed -i` pattern)

4. **File-by-File Audit table**: Added "Tier 4 Placeholders" column to the table header. Updated all existing rows to include `None` in the new column. Fixed the `reviews.md` row Tier 4 cell to read: `{{REVIEW_ROUND}}` (L502, L506, L592) — substituted by `fill-review-slots.sh` before Big Head brief delivery.

5. **Validation Rules section**: Added Pattern 5 (`grep -rE '\{\{[A-Z][A-Z_]*\}\}'`) for detecting double-brace placeholders.

6. **Compliance Status Key Findings item 6**: Updated to explicitly note reviews.md's Tier 4 usage.

7. **Why No Changes Needed paragraph**: Added bullet for `{{REVIEW_ROUND}}` double-brace convention.

8. **Benefits section**: Updated "Semantically rich" item to say "Four tiers map to four workflow phases."

---

## 4. Correctness Review

### Per-file review

**`orchestration/PLACEHOLDER_CONVENTIONS.md`** — the only file changed.

- Overview table: Now lists four rows, one per tier. The `{{UPPERCASE}}` row correctly identifies `fill-review-slots.sh` as the substitution agent. Examples match the actual markers found in reviews.md and referenced in CONTRIBUTING.md.
- Tier 4 section: Terminology is internally consistent with Tier 1 ("ALL CAPS with underscores" characteristic is shared but the double-brace wrapping is the distinguishing feature). The "Why double braces" subsection explains the design rationale clearly, grounding it in the existing Tier 1 clash. The substitution mechanism code block uses `sed -i` which is idiomatic for the described shell script.
- File-by-File Audit table: The reviews.md row previously stated "None" for Tier 1, which was correct (reviews.md does not use single-brace uppercase placeholders). The new Tier 4 column correctly reports `{{REVIEW_ROUND}}` with verified line references (L502, L506, L592 confirmed by grep). All other rows correctly show `None` for the new Tier 4 column — confirmed by grep search showing no other double-brace markers in the orchestration directory.
- Pattern 5: The regex `\{\{[A-Z][A-Z_]*\}\}` correctly matches `{{REVIEW_ROUND}}` and similar patterns. It does not false-positive on single-brace Tier 1 markers. The grep command syntax is consistent with Patterns 1-4.
- Cross-reference check: CONTRIBUTING.md (L95, L101) references `{{COMMIT_RANGE}}`, `{{CHANGED_FILES}}`, `{{TASK_IDS}}` as double-brace markers. All three are listed in the Tier 4 Examples section.

### Acceptance criteria verification

1. **PLACEHOLDER_CONVENTIONS.md documents the {{DOUBLE_BRACE}} tier** — PASS. Full Tier 4 section added with description, characteristics, examples, rationale, and substitution mechanism.

2. **Tier 4 description identifies fill-review-slots.sh as the substitution mechanism** — PASS. Stated in the section intro, Characteristics bullet, and the Substitution mechanism code block.

3. **File-by-File Audit table for reviews.md reflects the double-brace usage** — PASS. reviews.md row now shows `{{REVIEW_ROUND}}` (L502, L506, L592) in the Tier 4 Placeholders column.

4. **All {{SLOT}} markers across templates are accounted for in the new tier description** — PASS. Grep confirmed `{{REVIEW_ROUND}}` is the only currently-instantiated double-brace marker in reviews.md. The CONTRIBUTING.md cross-reference (L101) lists `{{COMMIT_RANGE}}`, `{{CHANGED_FILES}}`, `{{TASK_IDS}}` as additional markers; all four are documented in the Tier 4 Examples section.

### Assumptions audit

- **Path discrepancy**: The task brief cited `orchestration/templates/PLACEHOLDER_CONVENTIONS.md` but the file exists at `orchestration/PLACEHOLDER_CONVENTIONS.md`. Edited the correct file. This is a stale path reference in the task brief, not a file location issue to fix.
- **reviews.md line numbers**: Grep confirmed the double-brace `{{REVIEW_ROUND}}` appears at L502 (assignment), L506 (error message string), and L592 (explanatory note). These are the lines documented in the audit table row.
- **Other template files**: Grep search of `\{\{[A-Z][A-Z_]*\}\}` across the orchestration directory confirmed no other files contain double-brace markers. The `None` entries in the Tier 4 column for all other audit table rows are accurate.

---

## 5. Build/Test Validation

This task modifies only documentation (markdown). There are no compilation or test suite steps to run.

**Manual validation performed**:
- Grep `\{\{[A-Z][A-Z_]*\}\}` against `orchestration/` — confirms `{{REVIEW_ROUND}}` appears only in `reviews.md` at L502, L506, L592. All instances documented in the audit table.
- Read the full modified file to confirm no stray edits, no broken markdown table syntax, no accidental overwrite of existing content.
- Cross-referenced CONTRIBUTING.md L93-101 to confirm the double-brace markers listed in Tier 4 examples match what CONTRIBUTING.md documents.

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | PLACEHOLDER_CONVENTIONS.md documents the {{DOUBLE_BRACE}} tier | PASS |
| 2 | Tier 4 description identifies fill-review-slots.sh as the substitution mechanism | PASS |
| 3 | File-by-File Audit table for reviews.md reflects the double-brace usage | PASS |
| 4 | All {{SLOT}} markers across templates are accounted for in the new tier description | PASS |

**Commit**: `docs: add Tier 4 double-brace placeholder documentation and fix reviews.md audit row (ant-farm-lbcy)`
