# Consolidated Review Summary

**Scope**: orchestration/PLACEHOLDER_CONVENTIONS.md
**Reviews completed**: Clarity, Edge Cases, Correctness, Excellence
**Reports verified**: clarity-review-20260217-163000.md, edge-cases-review-20260217-163000.md, correctness-review-20260217-163000.md, excellence-review-20260217-163000.md
**Total raw findings**: 17 across all reviews
**Root causes identified**: 10 after deduplication
**Beads filed**: 10

## Read Confirmation

**All 4 reports read and processed by Big Head consolidation:**

| Report Type | File | Status | Finding Count |
|-------------|------|--------|---------------|
| Clarity | clarity-review-20260217-163000.md | Read | 5 findings |
| Edge Cases | edge-cases-review-20260217-163000.md | Read | 5 findings |
| Correctness | correctness-review-20260217-163000.md | Read | 2 findings |
| Excellence | excellence-review-20260217-163000.md | Read | 5 findings |

**Total findings from all reports**: 17

## Root-Cause Grouping (Big Head Consolidation)

### Root Cause 1: Duplicate {EPIC_ID} entry in Tier 1 examples

- **Root cause**: `{EPIC_ID}` appears on both line 32 and line 37 of PLACEHOLDER_CONVENTIONS.md with slightly different wording. This is a copy-paste artifact that creates confusion about whether the two entries have different semantics.
- **Affected surfaces**:
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:32, 37 -- duplicate entries (from clarity review, Finding 1)
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:32, 37 -- inconsistent descriptions (from excellence review, Finding 1)
- **Combined priority**: P3 (both reviewers rated P3)
- **Fix**: Remove line 37 (the shorter duplicate). Keep line 32 which includes the example.
- **Merge rationale**: Both findings reference the exact same two lines and the exact same duplicate placeholder entry. Clarity notes it as a copy-paste artifact; excellence notes the inconsistent wording. Same content error.
- **Acceptance criteria**: `{EPIC_ID}` appears exactly once in the Tier 1 examples list.
- **Bead**: ant-farm-8ut (P3)

### Root Cause 2: Audit claims "All Files Pass" despite nitpicker-skeleton.md partial compliance

- **Root cause**: Three separate statements (lines 101, 110, 156) create a contradiction: line 101 says "No violations found", line 156 says "All Files Pass", but line 110 marks nitpicker-skeleton.md as "Partial (missing EPOCH/timestamp defs)". The document's own rule at line 40 states templates with `{UPPERCASE}` placeholders MUST include the full term definition block, so a partial block is at minimum a gap.
- **Affected surfaces**:
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:101, 110 -- "no violations" contradicts "Partial" (from clarity review, Finding 2)
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:110 -- partial term block marked PASS (from edge-cases review, Finding 3)
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:101, 110, 156 -- audit overstates compliance (from excellence review, Finding 2)
- **Combined priority**: P3 (all 3 reviewers rated P3)
- **Fix**: Either update nitpicker-skeleton.md to include the full term definitions block, or change the summary to "No violations found; 1 file has partial term definitions" and the status to "PASS WITH NOTE."
- **Merge rationale**: All 3 findings reference the same contradiction between lines 101/156 (claiming all pass) and line 110 (marking one file as partial). Same data, same inconsistency, same root cause: the summary was not updated to reflect the nuance in the audit table.
- **Acceptance criteria**: The summary accurately reflects the audit table. No contradictions between stated compliance and noted partial compliance.
- **Bead**: ant-farm-6i1 (P3)

### Root Cause 3: Shell example shows unquoted ${SESSION_DIR} variable

- **Root cause**: Line 94 shows `mkdir -p ${SESSION_DIR}/{task-metadata,previews,prompts}` with an unquoted variable. Since PLACEHOLDER_CONVENTIONS.md is a reference document, this example normalizes bad shell practices. Related to existing issue ant-farm-65i (same pattern in RULES.md).
- **Affected surfaces**:
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:94 -- unquoted variable in canonical example (from clarity review, Finding 3)
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:94 -- word splitting risk for adopters (from edge-cases review, Finding 4)
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:94 -- reference document should model best practices (from excellence review, Finding 4)
- **Combined priority**: P3 (all 3 reviewers rated P3)
- **Fix**: Quote the variable: `mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts}`. Aligns with ant-farm-65i fix.
- **Merge rationale**: All 3 findings reference the exact same line (94) and the exact same unquoted variable. Same code, same risk, same fix.
- **Acceptance criteria**: All shell variable references in PLACEHOLDER_CONVENTIONS.md examples are properly quoted.
- **Bead**: ant-farm-1yl (P3)

### Root Cause 4: Angle-bracket placeholder syntax not documented or validated

- **Root cause**: Lines 112-113 acknowledge that reviews.md and implementation.md use angle-bracket syntax (`<epic-id>`, `<timestamp>`), but the document's 3-tier system only covers curly-brace placeholders. No validation pattern exists for angle-brackets. This means the "canonical placeholder conventions" document does not actually cover all placeholder conventions in use.
- **Affected surfaces**:
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:112-113 -- no validation patterns for angle-bracket syntax (from edge-cases review, Finding 5)
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:112-113 -- de facto fourth convention undocumented (from excellence review, Finding 3)
- **Combined priority**: P3 (both reviewers rated P3)
- **Fix**: Add a "Special Case: Angle-bracket Syntax" section explaining when `<placeholder>` is used (human-readable template prose, output format examples) and how it differs from the three machine-substituted tiers. Optionally add a validation pattern.
- **Merge rationale**: Both findings reference the same lines (112-113) and the same gap: angle-bracket syntax is acknowledged but not formally documented. Edge-cases frames it as a validation gap; excellence frames it as an undocumented convention. Same coverage hole.
- **Acceptance criteria**: Angle-bracket syntax is documented with usage guidance and at least a note on when it is appropriate.
- **Bead**: ant-farm-w6m (P3)

### Root Cause 5: Enforcement Strategy mixes completed and aspirational items

- **Root cause**: Lines 206-211 list 5 enforcement items with no distinction between what is done (item 1: add document to repo) and what remains (items 2-5: update templates, grep in CI, add to RULES.md, code review checklist).
- **Affected surfaces**:
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:206-211 -- no completion markers (from clarity review, Finding 4)
- **Combined priority**: P3
- **Fix**: Mark item 1 as completed and items 2-5 as TODO, or split into "Completed" and "Next Steps" subsections.
- **Merge rationale**: Single reviewer finding. No merge needed.
- **Acceptance criteria**: Each enforcement item is marked as completed or TODO.
- **Bead**: ant-farm-t0n (P3)

### Root Cause 6: Compliance Status section is verbose and redundant with audit table

- **Root cause**: Lines 156-201 repeat information from the audit table (lines 99-118) in per-file prose subsections, adding ~45 lines of redundant content. The "Why No Changes Needed" subsection (lines 194-201) adds editorial commentary about the development process rather than technical reference information.
- **Affected surfaces**:
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:156-201 -- per-file compliance restates audit table (from clarity review, Finding 5)
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:194-201 -- editorial commentary (from excellence review, Finding 5)
- **Combined priority**: P3 (both reviewers rated P3)
- **Fix**: Remove or collapse the per-file compliance subsections (lines 162-192). Condense the "Why No Changes Needed" section to a single note: "This convention documents existing usage patterns. No files required refactoring."
- **Merge rationale**: Both findings target the same section (lines 156-201) and both recommend trimming. Clarity says the per-file prose is redundant with the table; excellence says the editorial commentary is not appropriate for a reference document. Same section, same root cause: excessive content that restates what the audit table already shows.
- **Acceptance criteria**: Compliance Status section adds information beyond what the audit table provides, or is removed entirely. No redundant per-file restatements.
- **Bead**: ant-farm-3yw (P3)

### Root Cause 7: Validation regex Pattern 4 has false negatives for mixed casing

- **Root cause**: Pattern 4 (line 149) claims to detect "invalid mixed casing" but the regex does not catch all mixed-case forms. Complex patterns like `{ABCdef_GHI}` would slip through.
- **Affected surfaces**:
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:149 -- regex false negatives (from edge-cases review, Finding 1)
- **Combined priority**: P3
- **Fix**: Either use a more robust pattern that matches anything not purely uppercase or purely lowercase-kebab, or add a "Known Limitations" note acknowledging the pattern is not exhaustive.
- **Merge rationale**: Single reviewer finding. No merge needed.
- **Acceptance criteria**: Pattern 4 either catches all mixed-case forms or documents its limitations.
- **Bead**: ant-farm-yh4 (P3)

### Root Cause 8: Tier 2 {session-dir} vs Tier 1 {SESSION_DIR} naming ambiguity

- **Root cause**: The same conceptual value (session directory path) appears in two tiers with different names: `{SESSION_DIR}` (Tier 1, Queen-substituted) and `{session-dir}` (Tier 2, agent-derived). Template authors may not know which to use without reading the full tier explanation.
- **Affected surfaces**:
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:64 -- naming overlap (from edge-cases review, Finding 2)
- **Combined priority**: P3
- **Fix**: Add a FAQ or callout: "Q: When do I use {SESSION_DIR} vs {session-dir}? A: Use {SESSION_DIR} in skeleton templates that the Queen fills in. Use {session-dir} in agent-facing prose describing what the agent does with the path it received."
- **Merge rationale**: Single reviewer finding. No merge needed.
- **Acceptance criteria**: The document includes clear guidance on when to use each form of the session directory placeholder.
- **Bead**: ant-farm-3a0 (P3)

### Root Cause 9: Audit table line numbers will become stale without commit reference

- **Root cause**: Lines 103-118 include specific line number references for each file (e.g., "L10,62,66"). These are accurate at audit time but will become stale as referenced files are edited. The table presents as authoritative without noting it is a point-in-time snapshot.
- **Affected surfaces**:
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:103-118 -- stale line references (from correctness review, Finding 1)
- **Combined priority**: P3
- **Fix**: Add a commit hash or date to the audit header: "File-by-File Audit (as of commit 1f656e7, 2026-02-17)". Or remove line-number specificity and keep only file-level pass/fail.
- **Merge rationale**: Single reviewer finding. No merge needed.
- **Acceptance criteria**: Audit table either includes a snapshot reference or does not include line numbers.
- **Bead**: ant-farm-d1u (P3)

### Root Cause 10: Document not cross-referenced from RULES.md or any template

- **Root cause**: The Enforcement Strategy (line 207-211) lists "Document pattern in RULES.md referencing this document" as step 4, but this cross-reference has not been added. A grep for "PLACEHOLDER" in RULES.md returns no matches. The convention is not discoverable from the workflow entry points.
- **Affected surfaces**:
  - `orchestration/PLACEHOLDER_CONVENTIONS.md`:207-211 -- enforcement step 4 not completed (from correctness review, Finding 2)
- **Combined priority**: P3
- **Fix**: Add a one-line reference in RULES.md pointing to `orchestration/PLACEHOLDER_CONVENTIONS.md` as the canonical placeholder reference.
- **Merge rationale**: Single reviewer finding. No merge needed.
- **Acceptance criteria**: RULES.md contains a reference to PLACEHOLDER_CONVENTIONS.md. The document is discoverable from the main workflow entry point.
- **Bead**: ant-farm-t6f (P3)

## Deduplication Log

17 raw findings consolidated into 10 root causes. 7 findings were merged (duplicates eliminated).

| Raw Finding | Root Cause | Merge Rationale |
|-------------|------------|-----------------|
| Clarity F1 (duplicate EPIC_ID P3) | RC1 (ant-farm-8ut) | Same lines (32, 37), same duplicate entry |
| Excellence F1 (duplicate EPIC_ID P3) | RC1 (ant-farm-8ut) | Same lines, same duplicate |
| Clarity F2 (audit vs partial P3) | RC2 (ant-farm-6i1) | Same contradiction (lines 101, 110, 156) |
| Edge Cases F3 (partial marked PASS P3) | RC2 (ant-farm-6i1) | Same lines, same contradiction |
| Excellence F2 (all pass overstated P3) | RC2 (ant-farm-6i1) | Same lines, same overstatement |
| Clarity F3 (unquoted variable P3) | RC3 (ant-farm-1yl) | Same line (94), same unquoted variable |
| Edge Cases F4 (unquoted variable P3) | RC3 (ant-farm-1yl) | Same line, same variable |
| Excellence F4 (unquoted variable P3) | RC3 (ant-farm-1yl) | Same line, same variable |
| Edge Cases F5 (angle-bracket gap P3) | RC4 (ant-farm-w6m) | Same lines (112-113), same coverage gap |
| Excellence F3 (angle-bracket undocumented P3) | RC4 (ant-farm-w6m) | Same lines, same gap |
| Clarity F4 (enforcement strategy P3) | RC5 (ant-farm-t0n) | Standalone |
| Clarity F5 (verbose compliance P3) | RC6 (ant-farm-3yw) | Same section (156-201), same redundancy |
| Excellence F5 (editorial commentary P3) | RC6 (ant-farm-3yw) | Same section, same trimming needed |
| Edge Cases F1 (regex false negatives P3) | RC7 (ant-farm-yh4) | Standalone |
| Edge Cases F2 (naming ambiguity P3) | RC8 (ant-farm-3a0) | Standalone |
| Correctness F1 (stale line numbers P3) | RC9 (ant-farm-d1u) | Standalone |
| Correctness F2 (no cross-reference P3) | RC10 (ant-farm-t6f) | Standalone |

## Root Causes Filed

| Bead ID | Priority | Title | Contributing Reviews | Surfaces |
|---------|----------|-------|---------------------|----------|
| ant-farm-8ut | P3 | Duplicate {EPIC_ID} in Tier 1 | clarity, excellence | 1 file |
| ant-farm-6i1 | P3 | Audit "All Pass" contradicts partial compliance | clarity, edge-cases, excellence | 1 file |
| ant-farm-1yl | P3 | Shell example unquoted ${SESSION_DIR} | clarity, edge-cases, excellence | 1 file |
| ant-farm-w6m | P3 | Angle-bracket syntax undocumented | edge-cases, excellence | 1 file |
| ant-farm-t0n | P3 | Enforcement Strategy mixed status | clarity | 1 file |
| ant-farm-3yw | P3 | Compliance Status verbose/redundant | clarity, excellence | 1 file |
| ant-farm-yh4 | P3 | Validation regex false negatives | edge-cases | 1 file |
| ant-farm-3a0 | P3 | session-dir naming ambiguity | edge-cases | 1 file |
| ant-farm-d1u | P3 | Audit line numbers stale risk | correctness | 1 file |
| ant-farm-t6f | P3 | No cross-reference from RULES.md | correctness | 1 file |

## Priority Breakdown

- **P1 (blocking)**: 0 beads
- **P2 (important)**: 0 beads
- **P3 (polish)**: 10 beads
  - ant-farm-8ut: Duplicate entry (2 reviewers)
  - ant-farm-6i1: Audit overstatement (3 reviewers)
  - ant-farm-1yl: Unquoted variable (3 reviewers)
  - ant-farm-w6m: Angle-bracket gap (2 reviewers)
  - ant-farm-t0n: Enforcement status (1 reviewer)
  - ant-farm-3yw: Verbose compliance (2 reviewers)
  - ant-farm-yh4: Regex limitations (1 reviewer)
  - ant-farm-3a0: Naming ambiguity (1 reviewer)
  - ant-farm-d1u: Stale line numbers (1 reviewer)
  - ant-farm-t6f: Missing cross-reference (1 reviewer)

## Traceability Matrix

All 17 raw findings accounted for. 0 findings excluded.

- 2 findings merged into RC1 (duplicate EPIC_ID)
- 3 findings merged into RC2 (audit overstatement)
- 3 findings merged into RC3 (unquoted variable)
- 2 findings merged into RC4 (angle-bracket gap)
- 1 finding standalone as RC5 (enforcement strategy)
- 2 findings merged into RC6 (verbose compliance)
- 1 finding standalone as RC7 (regex)
- 1 finding standalone as RC8 (naming ambiguity)
- 1 finding standalone as RC9 (stale line numbers)
- 1 finding standalone as RC10 (missing cross-reference)

**Total**: 17 raw findings in, 10 root causes out, 0 excluded.

## Verdict

**PASS**

The PLACEHOLDER_CONVENTIONS.md document (task p33) is well-structured and effectively codifies the existing three-tier placeholder system. All 3 acceptance criteria are verified as met. All 10 findings are P3 polish items -- no P1 or P2 issues. The most notable themes are: the audit section overstates compliance (claiming "all pass" despite a partial entry), the shell example normalizes unquoted variables, and the angle-bracket placeholder syntax used in multiple templates is not formally documented. These are refinements to an already-functional reference document.
