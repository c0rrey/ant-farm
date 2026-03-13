# Summary: ant-farm-wi0 — AGG-022: Standardize variable naming across templates

**Commit**: `89c2ec0`
**Status**: Closed

---

## 1. Approaches Considered

### Approach A: Minimal surgical replacement (Selected)
Replace only the specific deprecated strings in-place. In `scout.md`: change `{task-id-suffix}` → `{task-suffix}` and `{full-task-id}` → `{task-id}` at L78, L81, L254. In `PLACEHOLDER_CONVENTIONS.md`: replace the `{task-id-suffix}` Tier 2 example with `{task-id}` and `{task-suffix}`, and update the audit table and Key Findings accordingly.

Tradeoffs: Minimal diff, easiest to review, zero risk of disturbing adjacent prose. Does not add a brand-new glossary section (the existing Tier Definitions sections already serve that role). Each change is atomic and directly traceable to an acceptance criterion.

### Approach B: Add dedicated canonical variable glossary section
Add a new `## Canonical Variable Glossary` section to `PLACEHOLDER_CONVENTIONS.md` with a two-column table mapping every canonical name (Tier 1 + Tier 2 equivalent + description), then do the scout.md renames.

Tradeoffs: More comprehensive but duplicates content already present in the "Detailed Definitions" section. Risk of contradicting the existing Tier 1/Tier 2 structure. Higher maintenance surface.

### Approach C: Add deprecated-to-canonical mapping table
Add a migration table to `PLACEHOLDER_CONVENTIONS.md` showing old → new mappings (`{task-id-suffix}` → `{task-suffix}`, `{full-task-id}` → `{task-id}`), then do the scout.md renames.

Tradeoffs: Preserves migration history, which aids understanding of changes over time. However, any table that lists the deprecated names by exact string would cause the acceptance-criterion grep to continue finding matches, requiring the strings to be written in a way that avoids exact literal hits. This creates awkward phrasing and ongoing maintenance risk.

### Approach D: Remove deprecated Tier 2 example without replacement
Remove `{task-id-suffix}` from PLACEHOLDER_CONVENTIONS.md Tier 2 examples without adding replacements, relying on `{session-dir}` to illustrate the Tier 2 pattern. Do the scout.md renames.

Tradeoffs: Cleanest removal with smallest diff in PLACEHOLDER_CONVENTIONS.md. However, the Tier 2 examples section becomes less representative — it won't show that task-related concepts also have Tier 2 equivalents, which is non-obvious. The new scout.md usage of `{task-id}` and `{task-suffix}` would have no definition in the conventions doc.

---

## 2. Selected Approach with Rationale

**Selected: Approach A — Minimal surgical replacement.**

Rationale:
- The acceptance criteria require (a) no synonym usage, (b) a glossary defining canonical names, and (c) zero grep matches for deprecated names. Approach A satisfies all three with minimal churn.
- The PLACEHOLDER_CONVENTIONS.md Tier 2 Examples list is exactly the right place for the new `{task-id}` and `{task-suffix}` entries — it mirrors how `{session-dir}` is already defined there as the Tier 2 equivalent of `{SESSION_DIR}`.
- Approach A avoids the risks of B (duplication/contradiction) and C (grep-polluting literal strings) while being more informative than D.

---

## 3. Implementation Description

### Changes to `orchestration/templates/scout.md`

**L78**: `{task-id-suffix}` → `{task-suffix}` in the metadata file path template.
- Before: `Write to {SESSION_DIR}/task-metadata/{task-id-suffix}.md`
- After: `Write to {SESSION_DIR}/task-metadata/{task-suffix}.md`

**L81**: `{full-task-id}` → `{task-id}` in the markdown file header template.
- Before: `# Task: {full-task-id}`
- After: `# Task: {task-id}`

**L254**: `{full-task-id}` → `{task-id}` in the error-handling example metadata file.
- Before: `# Task: {full-task-id}`
- After: `# Task: {task-id}`

### Changes to `orchestration/PLACEHOLDER_CONVENTIONS.md`

**Tier 2 Examples (L63)**: Replaced `{task-id-suffix}` with two properly defined entries:
- Added: `{task-id}` — Tier 2 equivalent of `{TASK_ID}`; the full bead ID used in agent output templates
- Added: `{task-suffix}` — Tier 2 equivalent of `{TASK_SUFFIX}`; task suffix for output filenames

**File-by-File Audit table (L102)**: Updated the `scout.md` row's Tier 2 Placeholders column to include `{task-id}` (L81,254) and `{task-suffix}` (L78).

**Key Findings for scout.md (L159-162)**: Updated to accurately reflect the current state:
- Updated Tier 2 list to include `{task-id}` and `{task-suffix}`
- Added note: "Non-canonical synonyms corrected to `{task-suffix}` and `{task-id}` (AGG-022)"

---

## 4. Correctness Review (per-file, with acceptance criteria verification)

### `orchestration/templates/scout.md`

- **L78**: `{SESSION_DIR}/task-metadata/{task-suffix}.md` — correct. `{task-suffix}` is Tier 2 (agent-derives the value at runtime from the task ID given to it). Consistent with how `{session-dir}` relates to `{SESSION_DIR}`.
- **L81**: `# Task: {task-id}` — correct. `{task-id}` is the Tier 2 form of the full bead ID in an output format specification.
- **L254**: `# Task: {task-id}` — correct. Same concept as L81, in the error-handling example template.
- **Term Definitions block (L12-14)**: Uses canonical Tier 1 names `{TASK_ID}`, `{TASK_SUFFIX}`, `{SESSION_DIR}` — unchanged, already correct.
- No other occurrences of deprecated names remain.

### `orchestration/PLACEHOLDER_CONVENTIONS.md`

- **Tier 2 Examples (L62-68)**: Now includes `{task-id}` and `{task-suffix}` with explicit Tier 1 mappings and usage examples. The examples reference actual usage in scout.md (e.g., `{SESSION_DIR}/task-metadata/{task-suffix}.md`).
- **Audit table (L102)**: scout.md row now lists `{task-id}` and `{task-suffix}` with correct line references.
- **Key Findings (L159-162)**: Accurately describes scout.md's current state, including the correction made by this task.
- No literal `{task-id-suffix}` or `{full-task-id}` strings remain anywhere in the file.

### Assumptions audit

- The Tier 2 names `{task-id}` and `{task-suffix}` follow the established Tier 2 convention (lowercase-kebab) and directly mirror their Tier 1 counterparts (`{TASK_ID}`, `{TASK_SUFFIX}`) — consistent with the `{SESSION_DIR}` → `{session-dir}` precedent already in the file.
- No other files needed changes per the scope boundaries in the task context. Confirmed by grep across all non-archive orchestration files.

---

## 5. Build/Test Validation

No executable code was changed. The changes are documentation/template text. Validation performed via grep:

```
grep -rn "{task-id-suffix}\|{full-task-id}" orchestration/ --exclude-dir=_archive
```

Result: no output (zero matches). Acceptance criterion 3 passes.

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | All templates use the same variable name for each concept (no synonyms like `{task-id-suffix}` vs `{TASK_SUFFIX}` for the suffix concept, or `{full-task-id}` vs `{TASK_ID}` for the full ID concept) | PASS — scout.md now uses `{task-suffix}` (L78) and `{task-id}` (L81, L254) consistently |
| 2 | A glossary section defines each canonical variable name with its meaning (complete for Tier 1 and Tier 2 canonical names) | PASS — PLACEHOLDER_CONVENTIONS.md Tier 2 Examples now explicitly defines `{task-id}` and `{task-suffix}` with Tier 1 mappings; Tier 1 section already fully defined |
| 3 | `grep` for deprecated variable names (`{task-id-suffix}`, `{full-task-id}`) across `orchestration/` (excluding `_archive/`) returns zero matches | PASS — verified: zero matches |
