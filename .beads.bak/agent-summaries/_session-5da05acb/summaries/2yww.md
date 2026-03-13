# Summary: ant-farm-2yww — Pantry-review deprecation not fully propagated to reader attributions

## 1. Approaches Considered

**Approach A — Global find-and-replace across all files**
Apply a single mechanical substitution of every occurrence of "Pantry (review mode)" and "Pantry in review mode" across all markdown files. Fast but risks missing nuanced prose that doesn't use the exact phrase (e.g., "or review templates" in GLOSSARY L82) and could introduce noise in archived or non-scope files.

**Approach B — Per-site targeted edits with context read before each change**
Read the exact surrounding lines for each of the 8 listed locations, understand the sentence structure, then make a targeted replacement that fits the local prose. More precise, avoids inadvertent changes to adjacent text, and allows the GLOSSARY role description edit ("or review templates" -> "implementation templates") to be treated as a separate concern from the attribution change.

**Approach C — Update only table cells, leave prose alone**
Tables are canonical reference material; prose is secondary. Updating only the structured table rows would satisfy most of the acceptance criteria, but it explicitly ignores README L252 (prose) and GLOSSARY L82 (prose in a table cell), both listed in the task scope. Incomplete by design — rejected.

**Approach D — Normalize to a single canonical replacement phrase and apply everywhere, treating GLOSSARY role description as a separate sub-task**
Define "build-review-prompts.sh" as the sole canonical reader of reviews.md and apply it to every attribution site; then separately fix the GLOSSARY Pantry role sentence to remove "or review templates". This is what Approach B does but with an explicit up-front design decision on the canonical phrase. Selected.

## 2. Selected Approach

Approach B + D: read each affected location precisely, apply targeted replacements fitting local prose style, use `build-review-prompts.sh` as the canonical reader attribution everywhere, and treat the GLOSSARY role description as a distinct sub-change requiring a sentence-level edit rather than a phrase substitution.

Rationale: the 8 affected locations span four different prose styles (bullet annotation, table cell, inline prose, role description). A mechanical phrase-swap would not produce grammatically clean results in all cases. Reading each site first ensures the replacement integrates naturally.

## 3. Implementation Description

Seven targeted edits were made across four files:

- **orchestration/RULES.md L47** — Changed "read by Pantry in review mode" to "read by build-review-prompts.sh" in the FORBIDDEN reads bullet annotation.
- **orchestration/RULES.md L440** — Changed "Review details (read by the Pantry)" to "Review details (read by build-review-prompts.sh)" in the Template Lookup table.
- **README.md L252** — Split the compound sentence "implementation.md and reviews.md are read by the Pantry" into two sentences: "implementation.md is read by the Pantry. reviews.md is read by build-review-prompts.sh." to accurately attribute each file to its correct reader.
- **README.md L301** — Changed "replaced by fill-review-slots.sh" to "replaced by build-review-prompts.sh" in the deprecated pantry-review row (this was also a stale script name that misidentified the replacement).
- **README.md L352** — Changed "The Pantry (review mode)" to "`build-review-prompts.sh`" in the File reference table reader column.
- **orchestration/GLOSSARY.md L82** — Changed "Reads implementation or review templates" to "Reads implementation templates" in the Pantry role description cell.
- **CONTRIBUTING.md L95** — Removed "Pantry (review mode)," from the "Read by" column for reviews.md, leaving only "`build-review-prompts.sh`".

## 4. Correctness Review

**orchestration/RULES.md L47**
Before: `— Review protocol (read by Pantry in review mode)`
After: `— Review protocol (read by build-review-prompts.sh)`
Correct: attribution now names the script, not the deprecated agent mode.

**orchestration/RULES.md L440**
Before: `| Review details (read by the Pantry) | orchestration/templates/reviews.md |`
After: `| Review details (read by build-review-prompts.sh) | orchestration/templates/reviews.md |`
Correct: table cell accurately reflects which process reads this file.

**README.md L252**
Before: `implementation.md and reviews.md are read by the Pantry.`
After: `implementation.md is read by the Pantry. reviews.md is read by build-review-prompts.sh.`
Correct: sentence now distinguishes the two files' readers accurately. Grammar is clean.

**README.md L301**
Before: `replaced by fill-review-slots.sh bash script`
After: `replaced by build-review-prompts.sh bash script`
Correct: names the actual replacement script (fill-review-slots.sh was a stale/wrong name).

**README.md L352**
Before: `The Pantry (review mode)`
After: `` `build-review-prompts.sh` ``
Correct: table reader column now names the script consistently with other tables.

**orchestration/GLOSSARY.md L82**
Before: `Reads implementation or review templates`
After: `Reads implementation templates`
Correct: the Pantry no longer reads review templates; that function moved to the script.

**CONTRIBUTING.md L95**
Before: `Pantry (review mode), build-review-prompts.sh`
After: `` `build-review-prompts.sh` ``
Correct: removed the deprecated co-reader, leaving only the current reader.

**Acceptance criteria verification**:
- AC1: No file in the repo attributes reviews.md readership to the Pantry — verified via grep; no matches in scope files.
- AC2: GLOSSARY Pantry role says "Reads implementation templates" — confirmed at L82.
- AC3: README file reference table names build-review-prompts.sh as the reader of reviews.md — confirmed at L353.

**Adjacent issues noticed (not fixed)**:
- `docs/plans/2026-02-19-review-loop-convergence.md` (L15, L620, L823) still describes the Pantry reading reviews.md. This is a historical planning document outside the task scope boundaries.
- GLOSSARY.md L28 pantry-review.md entry already had correct "(deprecated; see RULES.md Step 3b)" markup — no change needed there.

## 5. Build/Test Validation

Documentation-only changes. No build artifacts, tests, or scripts were modified. Manual verification:

```
grep -r "reviews\.md.*Pantry\|Pantry.*reviews\.md" --include="*.md" orchestration/ README.md CONTRIBUTING.md
# Result: No matches (only README.md L252 appears, where Pantry is correctly NOT attributed to reviews.md)
```

All changed files are valid markdown. No broken cross-references introduced.

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| 1. No file in the repo attributes reviews.md readership to the Pantry | PASS |
| 2. GLOSSARY Pantry role description says "Reads implementation templates" (not "or review templates") | PASS |
| 3. README file reference table names build-review-prompts.sh as the reader of reviews.md | PASS |
