# Summary: ant-farm-4vg

**Task**: AGG-027 — Standardize review type naming between display titles and short names
**Agent**: technical-writer
**Status**: Complete

---

## 1. Approaches Considered

### Approach A: Drop "Redux" — rename display title to "Correctness Review"
Align the display title with the existing short name by removing "Redux" from all headers and team setup listings. The agent instruction body retains the phrase "second-pass correctness review" so the semantic distinction is not lost.

**Pros**: Simplest change. No file path or placeholder changes. Satisfies all three acceptance criteria.
**Cons**: Loses the "Redux" label that some readers may have used as a visual signal for the second-pass nature of this review.

### Approach B: Adopt "Redux" fully — change short names and filenames to "correctness-redux"
Rename `correctness-review-<timestamp>.md` to `correctness-redux-review-<timestamp>.md` throughout. Change the `{REVIEW_TYPE}` placeholder value from `correctness` to `correctness-redux`.

**Pros**: The display label and short name would exactly match.
**Cons**: Highly invasive. Changes file path patterns referenced in reviews.md, checkpoints.md (read-only scope), big-head-skeleton.md (read-only scope), and pantry.md (read-only scope). Creates a wave of adjacent issues. Violates the scope boundary of this task.

### Approach C: Keep both forms, add mapping table only
Add a mapping table that documents the short-name → display-title correspondence without changing any existing text. The inconsistency between "Correctness Redux" (display) and "correctness" (short) remains but is documented.

**Pros**: Zero risk of regression — no existing text is modified.
**Cons**: Does not satisfy acceptance criterion 1 ("one canonical name used in both templates and filenames") or criterion 3 ("no template uses a review type name that differs from the canonical form without explanation"). The inconsistency persists.

### Approach D: Standardize all four types and add mapping table (SELECTED)
Remove "Redux" from all display-title contexts in reviews.md (team setup, section header, agent instruction opener). Add a "Review Type Canonical Names" mapping table in the Agent Teams Protocol section that formally defines short-name → display-title for all four review types. Update nitpicker-skeleton.md's placeholder comment to point to the mapping table.

**Pros**: Satisfies all three acceptance criteria. Adds permanent documentation that prevents future drift. The agent instruction body retains the "second-pass" semantic description at the paragraph level — no information is lost. Changes are confined to the two in-scope files.
**Cons**: Slightly more changes than Approach A, but all changes are in-scope. The "Redux" label disappears from headings and team listings, which is the intended outcome.

---

## 2. Selected Approach with Rationale

**Selected: Approach D**

The short names (`clarity`, `edge-cases`, `correctness`, `excellence`) are the load-bearing identifiers used in: `{REVIEW_TYPE}` template placeholders, file output paths, report file names, and checkpoints.md shell script checks. The display titles are human-readable expansions of those identifiers. "Correctness Redux" diverged from its short name without any documented justification, creating parsing friction when readers mentally mapped between the team listing ("Correctness Redux Review") and the file path (`correctness-review-*.md`).

Approach D resolves the mismatch at the source, adds a canonical table for all four types, and preserves the "second-pass" semantic content within the review agent's instruction body. The scope is cleanly bounded to the two in-scope files.

---

## 3. Implementation Description

### Changes to `orchestration/templates/reviews.md`

1. **Added "Review Type Canonical Names" subsection** between "Model Assignments" and "Team Setup" in the Agent Teams Protocol section. The subsection contains a four-row table mapping short name → display title → priority → file output pattern for all four review types, plus an explanatory sentence establishing the short name as the authoritative identifier.

2. **L69 (Round 1 team listing)**: Changed `3. Correctness Redux Review (P1-P2)` to `3. Correctness Review (P1-P2)`.

3. **L90 (Round 2+ team listing)**: Changed `1. Correctness Redux Review (P1-P2)` to `1. Correctness Review (P1-P2)`.

4. **L227 (section header)**: Changed `## Review 3: Correctness Redux (P1-P2)` to `## Review 3: Correctness (P1-P2)`.

5. **L234 (agent instruction opener inside fenced block)**: Changed `Perform a CORRECTNESS REDUX review of the completed work in this session.` to `Perform a CORRECTNESS review of the completed work in this session.` The following line (`This is a second-pass correctness review focusing on logic and requirements.`) was preserved unchanged, retaining the semantic distinction at the description level.

### Changes to `orchestration/templates/nitpicker-skeleton.md`

1. **Placeholder comment for `{REVIEW_TYPE}`**: Added a cross-reference line below the short names list: `(These are the canonical short names. See "Review Type Canonical Names" in reviews.md for the full short-name → display-title mapping.)` This connects the skeleton's placeholder values to the authoritative table.

### Files NOT changed (per scope boundaries)

- `orchestration/templates/checkpoints.md` — downstream consumer; no review-type naming issues found in L475-500 scope
- `orchestration/templates/implementation.md` — not a review naming concern
- `orchestration/templates/big-head-skeleton.md` — downstream consumer
- `orchestration/templates/pantry.md` — downstream consumer
- `orchestration/templates/SESSION_PLAN_TEMPLATE.md` — out of scope; contains "Correctness Redux Review" at L211 (documented as adjacent issue below)

---

## 4. Correctness Review (per-file)

### `orchestration/templates/reviews.md`

**Verification of all affected lines:**

- L49-60 (new "Review Type Canonical Names" section): Table is accurate. Short names match the file output patterns already present throughout the document. Display titles match the section headers directly below (Clarity Review, Edge Cases Review, Correctness Review, Excellence Review). Priority column matches the priority annotations on each review section. No conflicts with existing content.

- L82 (Round 1 listing): "Correctness Review (P1-P2)" — consistent with mapping table row `correctness | Correctness Review | P1-P2`.

- L103 (Round 2+ listing): "Correctness Review (P1-P2)" — consistent with mapping table.

- L240 (section header): "## Review 3: Correctness (P1-P2)" — consistent with short name `correctness` and display title "Correctness Review".

- L247 (agent instruction): "Perform a CORRECTNESS review" — consistent with short name. L251 ("This is a second-pass correctness review focusing on logic and requirements.") preserves the second-pass semantic.

- L266 (file output path): `correctness-review-<timestamp>.md` — unchanged, still consistent with short name `correctness`.

**Grep confirmation**: No instances of "Correctness Redux" or "CORRECTNESS REDUX" remain in reviews.md.

**Grep confirmation**: All `correctness-review-<timestamp>.md` file path references remain intact and consistent.

**Acceptance criteria check against reviews.md**:
- AC1: Each review type has one canonical name used in both templates and filenames — PASS. All four types use their short name in file paths. Display titles now match the expanded form of the short name (no "Redux" divergence).
- AC2: Mapping table exists — PASS. "Review Type Canonical Names" table added.
- AC3: No template uses a review type name differing from canonical form without explanation — PASS. "Correctness Redux" is fully removed.

### `orchestration/templates/nitpicker-skeleton.md`

**Verification:**

- L9: `{REVIEW_TYPE}: clarity / edge-cases / correctness / excellence` — unchanged (already correct).
- L10 (new): Cross-reference to "Review Type Canonical Names" in reviews.md — accurate pointer to the new subsection.

**Acceptance criteria check against nitpicker-skeleton.md**:
- AC1: Short names listed are the canonical short names consistent with the mapping table — PASS.
- AC2: Cross-reference to mapping table added — PASS.
- AC3: No divergent naming — PASS.

### Adjacent Issues (documented, not fixed)

- `orchestration/templates/SESSION_PLAN_TEMPLATE.md:L211` — contains "Correctness Redux Review". This file is outside the scope of this task. The inconsistency should be addressed in a follow-up task targeting SESSION_PLAN_TEMPLATE.md.

---

## 5. Build/Test Validation

These are Markdown template files with no executable code, build system, or automated test suite. Validation was performed by:

1. Grep search for "Correctness Redux" and "CORRECTNESS REDUX" across the two changed files — zero matches found.
2. Grep search for "correctness-review" — all file path references intact, consistent with short name `correctness`.
3. Full re-read of both changed files to verify context integrity (no adjacent text disturbed).
4. Cross-check: the mapping table entries were verified against the actual section headers (Review 1-4), priority annotations, and file output patterns already present in the document.

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Each review type has one canonical name used in both templates and filenames | PASS | Short names (`clarity`, `edge-cases`, `correctness`, `excellence`) are now used consistently in team setup listings, section headers, and file output patterns. "Correctness Redux" eliminated from all display contexts. |
| 2 | If display and short forms both exist, a mapping table documents the correspondence | PASS | "Review Type Canonical Names" table added to reviews.md Agent Teams Protocol section, mapping short name → display title → priority → file output pattern for all four review types. |
| 3 | No template uses a review type name that differs from the canonical form without explanation | PASS | Zero instances of "Correctness Redux" remain in reviews.md or nitpicker-skeleton.md. nitpicker-skeleton.md placeholder comment cross-references the mapping table. |

---

## Commit

**Files changed**:
- `orchestration/templates/reviews.md`
- `orchestration/templates/nitpicker-skeleton.md`

**Conventional commit message**: `docs: standardize correctness review type naming, add canonical names table (ant-farm-4vg)`
