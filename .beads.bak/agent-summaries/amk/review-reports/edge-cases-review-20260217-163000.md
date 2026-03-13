# Report: Edge Cases Review

**Scope**: orchestration/PLACEHOLDER_CONVENTIONS.md
**Reviewer**: Edge Cases Review (code-reviewer)

## Findings Catalog

### Finding 1: Validation regex Pattern 4 (mixed casing) produces false negatives for certain placeholder forms

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md:149
- **Severity**: P3
- **Category**: edge-case
- **Description**: Pattern 4 on line 149 is `\{[A-Z]+[a-z_\-]+\}|\{[a-z\-]*[A-Z]+\}` and claims to detect "invalid mixed casing." However, this pattern does not catch all mixed-case forms. For example, `{MyVar}` would match (uppercase then lowercase), but `{mYvAR}` would also match. However, `{ABCdef_GHI}` (uppercase block, lowercase block, uppercase block) would NOT match because the first alternation requires `[A-Z]+` followed by `[a-z_\-]+` with no additional uppercase, and the second alternation requires lowercase start. A more thorough pattern would be needed for all mixed-case forms. This is a minor gap in the validation tooling.
- **Suggested fix**: Simplify the description: "This pattern catches common mixed-case violations but is not exhaustive. Manual review is recommended for complex cases." Or use a more robust pattern: `\{(?![A-Z_]+\}$)(?![a-z\-]+\}$)[A-Za-z_\-]+\}` (matches anything that is neither all-uppercase nor all-lowercase-kebab).

### Finding 2: Tier 2 lowercase placeholder {session-dir} vs Tier 1 {SESSION_DIR} creates substitution ambiguity

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md:64
- **Severity**: P3
- **Category**: edge-case
- **Description**: Line 64 defines `{session-dir}` as "Derived from `{SESSION_DIR}` at runtime; used in agent-facing instructions to show 'the session dir you were given' in relative terms." This means the same conceptual value (the session directory path) appears in two placeholder tiers with different names. A template author adding a new instruction might not know whether to write `{SESSION_DIR}` (Queen fills it in) or `{session-dir}` (agent uses the value it was given). The document explains the distinction but the naming overlap makes it easy to pick the wrong tier. In scout.md, both forms appear: `{SESSION_DIR}` on line 10 (Tier 1, Queen-provided) and `{session-dir}` on lines 166-167 (Tier 2, output format).
- **Suggested fix**: Add a callout box or FAQ: "Q: When do I use {SESSION_DIR} vs {session-dir}? A: Use {SESSION_DIR} in skeleton templates that the Queen fills in before spawn. Use {session-dir} in agent-facing prose that describes what the agent does with the path it received."

### Finding 3: File-by-file audit table shows nitpicker-skeleton.md as "Partial" term definition block

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md:110
- **Severity**: P3
- **Category**: edge-case
- **Description**: Line 110 notes that `nitpicker-skeleton.md` has "Partial (L8-12, missing EPOCH/timestamp defs)" for its Term Definition Block, yet the overall status is "PASS." The document claims "All files audited. No violations found." (line 101) and "Compliance Status: All Files Pass" (line 156), but a partial term definition block is a gap -- not a violation per se, but it contradicts the "All Files Pass" claim. If the convention requires every template with `{UPPERCASE}` placeholders to include the term definitions block (line 40: "MUST include this block"), then a partial block is a violation.
- **Suggested fix**: Either (a) update nitpicker-skeleton.md to include the full term definitions block, or (b) change the audit status to "PASS WITH NOTE" and acknowledge the gap, or (c) clarify that the MUST on line 40 applies only to TASK_ID/TASK_SUFFIX/EPIC_ID and not to all uppercase placeholders.

### Finding 4: Shell variable example on line 94 uses unquoted ${SESSION_DIR} in mkdir

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md:94
- **Severity**: P3
- **Category**: edge-case
- **Description**: Line 94 shows `mkdir -p ${SESSION_DIR}/{task-metadata,previews,prompts}` with an unquoted `${SESSION_DIR}`. While the SESSION_DIR value is a deterministic hash path (no spaces), this example serves as a template for users writing new scripts. An adopter might follow this pattern with a different variable that contains spaces, leading to word splitting. This is the same issue as ant-farm-65i (SESSION_DIR variable not quoted in shell mkdir command in RULES.md).
- **Suggested fix**: Quote the variable: `mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts}`. This costs nothing and prevents the example from teaching bad shell habits.
- **Cross-reference**: Matches existing issue ant-farm-65i.

### Finding 5: reviews.md and implementation.md listed as using angle-bracket syntax but no validation pattern covers this

- **File(s)**: /Users/correy/projects/ant-farm/orchestration/PLACEHOLDER_CONVENTIONS.md:112-113
- **Severity**: P3
- **Category**: edge-case
- **Description**: Lines 112-113 note that `reviews.md` and `implementation.md` use angle-bracket syntax (`<epic-id>`, `<timestamp>`) rather than curly-brace placeholders, and these are marked as "PASS." However, the Validation Rules section (lines 122-152) only provides grep patterns for curly-brace placeholders (Tiers 1-3). No validation pattern exists for angle-bracket placeholders. This means the convention document defines a 3-tier system but reviews.md and implementation.md operate outside it entirely, with no enforcement or detection mechanism.
- **Suggested fix**: Either (a) add a Pattern 5 for angle-bracket placeholders with guidance on when they are acceptable, or (b) document that angle-bracket syntax is legacy/informal and not covered by the placeholder convention, or (c) migrate reviews.md and implementation.md to curly-brace syntax.

## Preliminary Groupings

### Group A: Validation tooling completeness
- Finding 1 (regex false negatives), Finding 5 (no angle-bracket validation) -- both relate to gaps in the validation rules that leave certain placeholder forms undetected
- **Suggested combined fix**: Add a "Known Limitations" section to the Validation Rules acknowledging: (1) Pattern 4 is not exhaustive for mixed casing, (2) angle-bracket placeholders in reviews.md and implementation.md are not covered by any pattern.

### Group B: Naming overlap between tiers
- Finding 2 (SESSION_DIR vs session-dir) -- standalone confusion risk from same-concept-different-tier naming
- **Suggested combined fix**: Add a FAQ or callout clarifying when to use each form.

### Group C: Audit accuracy
- Finding 3 (partial term block marked PASS) -- standalone audit inconsistency
- **Suggested combined fix**: Align audit status with the MUST requirement or clarify the requirement scope.

### Group D: Example quality
- Finding 4 (unquoted shell variable) -- standalone example hygiene issue
- **Suggested combined fix**: Quote the variable in the example.

## Summary Statistics
- Total findings: 5
- By severity: P1: 0, P2: 0, P3: 5
- Preliminary groups: 4

## Cross-Review Messages

### Sent
- None.

### Received
- None.

### Deferred Items
- None.

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| orchestration/PLACEHOLDER_CONVENTIONS.md | Findings: #1, #2, #3, #4, #5 | 237 lines, all 7 sections examined: Overview (1-13), Detailed Definitions (15-96 across 3 tiers), File-by-File Audit (99-118), Validation Rules (122-152), Compliance Status (156-201), Enforcement Strategy (205-211), Benefits (215-222), Exceptions (226-236). Every validation pattern tested mentally against edge cases. |

## Overall Assessment
**Score**: 7.5/10
**Verdict**: PASS WITH ISSUES
<!-- Verdict Rubric:
  PASS           = 0 P1 findings AND 0 P2 findings
  PASS WITH ISSUES = 0 P1 findings AND any P2 or P3 findings
  NEEDS WORK     = any P1 finding present

  Score formula: Start at 10, subtract 3 per P1, 1 per P2, 0.5 per P3 (floor at 0)
  10 - 0(P1) - 0(P2) - 2.5(P3) = 7.5
-->
The PLACEHOLDER_CONVENTIONS.md document is well-structured and provides a clear 3-tier system that correctly documents the existing codebase conventions. The edge cases found are all P3 polish items: the validation regex has false negative gaps, the SESSION_DIR/session-dir naming overlap could confuse template authors, the audit table has one file marked "Partial" despite claiming all pass, the shell example uses an unquoted variable, and the angle-bracket syntax used by two files has no validation coverage. None of these would cause functional failures but they weaken the document's claim of comprehensive convention coverage.
