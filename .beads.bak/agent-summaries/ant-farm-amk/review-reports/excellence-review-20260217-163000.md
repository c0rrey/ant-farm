# Report: Excellence Review

**Scope**: orchestration/PLACEHOLDER_CONVENTIONS.md
**Reviewer**: Excellence Review (code-reviewer)

## Findings Catalog

### Finding 1: EPIC_ID defined twice in Tier 1 examples with inconsistent descriptions
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md`:32, 37
- **Severity**: P3
- **Category**: excellence (maintainability)
- **Description**: `{EPIC_ID}` appears twice in the Tier 1 examples list. Line 32 defines it as "epic suffix only (e.g., `74g`), or `_standalone` for tasks with no epic". Line 37 defines it as "epic suffix or `_standalone`". These are the same placeholder with slightly different wording. The duplication is confusing for anyone using this as a reference -- they might wonder if the two entries describe different semantics or if one is outdated.
- **Suggested fix**: Remove the duplicate at line 37. The definition at line 32 is more complete (includes example) and should be the sole entry.

### Finding 2: Audit claims "All Files Pass" despite noted partial compliance
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md`:101, 110, 156
- **Severity**: P3
- **Category**: excellence (maintainability)
- **Description**: Line 101 states "No violations found. All files use the Tiered convention correctly." Line 156 declares "Compliance Status: All Files Pass". However, line 110 notes nitpicker-skeleton.md has a "Partial" term definition block, "missing EPOCH/timestamp defs." The document's own rule at line 40 states "Every template that uses `{UPPERCASE}` placeholders MUST include this block at the top." A partial block is not full compliance. The "all pass" claim overstates the audit result.
- **Suggested fix**: Either (a) change nitpicker-skeleton.md status to PASS WITH NOTE and update the summary to acknowledge the partial block, or (b) add a "Known Gaps" section listing the partial compliance items instead of claiming perfect compliance.

### Finding 3: Angle-bracket placeholder syntax is used but not formally defined
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md`:112-113
- **Severity**: P3
- **Category**: excellence (maintainability)
- **Description**: The file-by-file audit at lines 112-113 notes that reviews.md and implementation.md use "angle-bracket syntax `<epic-id>`, `<timestamp>` in text" but classifies this as not using curly-brace placeholders and gives them PASS. However, the document claims to define "the canonical placeholder conventions used across all orchestration templates" (line 3). Angle-bracket syntax is used in at least 2 major templates (reviews.md, implementation.md) and queen-state.md (line 114), making it a de facto fourth convention that should be documented.
- **Suggested fix**: Add a "Tier 0: Documentation Placeholders" or "Special Case: Angle-bracket Syntax" section explaining that `<placeholder>` is used in human-readable template prose and output format examples, distinct from the three machine-substituted tiers.

### Finding 4: Shell example shows unquoted variable expansion
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md`:94
- **Severity**: P3
- **Category**: excellence (best practices)
- **Description**: Line 94 shows `mkdir -p ${SESSION_DIR}/{task-metadata,previews,prompts}` with `${SESSION_DIR}` unquoted. This is the same pattern flagged in existing issue ant-farm-65i for RULES.md. Since PLACEHOLDER_CONVENTIONS.md is a reference document that models best practices, its code examples should follow shell best practices. An unquoted variable in a reference example implicitly endorses the pattern.
- **Suggested fix**: Quote the variable: `mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts}`. This also aligns with the fix suggested for ant-farm-65i.
- **Cross-reference**: Related to ant-farm-65i (same unquoted variable pattern in RULES.md)

### Finding 5: "Why No Changes Needed" section contains editorial commentary
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md`:194-201
- **Severity**: P3
- **Category**: excellence (maintainability)
- **Description**: Lines 196-198 state "The development team unconsciously implemented the Tiered Placeholder Convention correctly" and lines 200-201 say "The convention simply documents this existing best practice rather than imposing new restrictions." This is editorial commentary about the development process, not a technical reference. For a canonical conventions document, this adds no actionable information and may become misleading if future changes introduce violations.
- **Suggested fix**: Remove or condense the "Why No Changes Needed" subsection. If the historical context is valuable, move it to a brief note: "Note: This convention documents existing usage patterns. No files required refactoring when the convention was formalized."

## Preliminary Groupings

### Group A: Audit accuracy and completeness
- Finding 2, Finding 3 -- both relate to the file-by-file audit understating gaps
- **Suggested combined fix**: Update the audit section to acknowledge partial compliance (nitpicker-skeleton.md) and the undocumented angle-bracket convention. Change "All Files Pass" to a more nuanced summary.

### Group B: Reference document quality
- Finding 1 (duplicate definition), Finding 4 (unquoted variable), Finding 5 (editorial commentary) -- all relate to the document modeling best practices as a canonical reference
- **Suggested combined fix**: Clean up duplicates, fix shell examples, trim editorial content. The document should be a concise, accurate reference.

## Summary Statistics
- Total findings: 5
- By severity: P1: 0, P2: 0, P3: 5
- Preliminary groups: 2

## Cross-Review Messages

### Sent
- None

### Received
- None

### Deferred Items
- None

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/PLACEHOLDER_CONVENTIONS.md` | Findings: #1, #2, #3, #4, #5 | 237 lines, 9 sections examined (Overview, 3 Tier definitions, File-by-File Audit, Validation Rules, Compliance Status, Enforcement Strategy, Benefits, Exceptions) |

## Overall Assessment
**Score**: 7.5/10
**Verdict**: PASS WITH ISSUES
<!-- Verdict Rubric:
  PASS           = 0 P1 findings AND 0 P2 findings
  PASS WITH ISSUES = 0 P1 findings AND any P2 or P3 findings
  NEEDS WORK     = any P1 finding present

  Score formula: Start at 10, subtract 3 per P1, 1 per P2, 0.5 per P3 (floor at 0)
  10 - 0 - 0 - 5*0.5 = 7.5
-->
The placeholder conventions document successfully formalizes the three-tier system and provides useful grep patterns for validation. All findings are P3 polish items. The main concerns are that the audit section overstates compliance (claiming "all pass" despite noted partial compliance in nitpicker-skeleton.md) and the document omits the angle-bracket placeholder syntax used in multiple templates. The core convention design is sound and well-structured.
