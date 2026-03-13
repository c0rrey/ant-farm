# Task Summary: ant-farm-ha7a.8

**Task**: Add round-aware scope instructions to nitpicker-skeleton
**Status**: COMPLETED
**Commit Hash**: (pending commit)

## Approaches Considered

### Approach 1: Direct Insertion (SELECTED)
- Add `{REVIEW_ROUND}` placeholder directly after line 11
- Insert scope instructions after "Perform a {REVIEW_TYPE} review" line on line 17
- Preserves template minimalism and readability
- Minimal changes, clear intent
- **Tradeoff**: Line-based editing requires precision but specification is exact

### Approach 2: Rewrite Entire Placeholder Block
- Delete lines 8-11, rewrite all placeholders including REVIEW_ROUND
- Ensures consistent formatting and completeness
- **Tradeoff**: More invasive; though low risk given small block size, unnecessary for single addition

### Approach 3: Add Placeholder with Context Comments
- Insert REVIEW_ROUND with inline comments explaining purpose
- Makes template self-documenting
- **Tradeoff**: Extra lines must be removed during template instantiation by Pantry; adds complexity

### Approach 4: Structured Placeholder Format
- Convert bullet list to numbered or table format for all placeholders
- Makes future additions clearer and more maintainable
- **Tradeoff**: Breaks consistency with current minimalist style; requires coordination across templates

## Selected Approach & Rationale

**Selected**: Approach 1 (Direct Insertion)

The specification exactly defines two insertion points. The nitpicker-skeleton maintains a minimalist, readable structure with a simple bullet-list placeholder block and a clear agent-facing template below the `---` separator. Direct insertion:
- Adds the `{REVIEW_ROUND}` placeholder to the list (line 12)
- Inserts round-aware scope instructions immediately after the "Perform a" line (line 20-21)
- Requires only two targeted edits
- Maintains existing formatting and structure
- Aligns perfectly with the specification in docs/plans/2026-02-19-review-loop-convergence.md Task 8

## Implementation Description

**File modified**: `orchestration/templates/nitpicker-skeleton.md`

**Edit 1 - Add placeholder (lines 8-12)**:
```markdown
Placeholders:
- {REVIEW_TYPE}: clarity / edge-cases / correctness / excellence
- {DATA_FILE_PATH}: from the Pantry (review mode) verdict table
- {REPORT_OUTPUT_PATH}: from the Pantry verdict table (session-scoped)
- {REVIEW_ROUND}: 1, 2, 3, ... (determines scope instructions; filled by Pantry)
```

**Edit 2 - Add agent template scope instructions (lines 18-21)**:
```markdown
Perform a {REVIEW_TYPE} review of the completed work.

**Review round**: {REVIEW_ROUND}
If round 2+: Your scope is limited to fix commits only. You may read full files for context, but your mandate is: did these fixes land correctly and not break anything? Out-of-scope findings are only reportable if they would cause a runtime failure or silently wrong results. Do NOT report naming, style, docs, or improvement opportunities outside fix scope.
```

Both changes integrate seamlessly into the existing template structure:
- Placeholder block unchanged in header/intent
- Agent template remains clear with added context
- Template instantiation by Pantry only requires literal placeholder substitution

## Correctness Review

### File: orchestration/templates/nitpicker-skeleton.md

**Header & instructions (L1-L7)**:
- ✓ Untouched; placeholder section title and description remain clear
- ✓ "Fill in all {PLACEHOLDER} values" instruction still accurate

**Placeholder list (L8-L12)**:
- ✓ `{REVIEW_TYPE}` line unchanged
- ✓ `{DATA_FILE_PATH}` line unchanged
- ✓ `{REPORT_OUTPUT_PATH}` line unchanged
- ✓ `{REVIEW_ROUND}` added after last placeholder with correct format
- ✓ Matches specification: "1, 2, 3, ... (determines scope instructions; filled by Pantry)"

**Template header (L14-L16)**:
- ✓ "## Template (send everything below this line)" untouched
- ✓ `---` separator intact

**Agent template (L18-L21)**:
- ✓ "Perform a {REVIEW_TYPE} review of the completed work." line preserved at L18
- ✓ New line L20: `**Review round**: {REVIEW_ROUND}` inserted immediately after with blank separator
- ✓ Lines L21: Round 2+ scope instructions with all required phrases:
  - "Your scope is limited to fix commits only" — restricts round 2+ to fix-only review
  - "did these fixes land correctly and not break anything?" — defines mandate clearly
  - "runtime failure" — exception criterion for out-of-scope findings
  - "silently wrong results" — second exception criterion
  - "Do NOT report naming, style, docs, or improvement opportunities" — clear guardrails

**Workflow steps (L23 onward)**:
- ✓ "Step 0: Read your full review brief from {DATA_FILE_PATH}" follows scope instructions
- ✓ All downstream sections (workflow steps, report format) untouched
- ✓ L41: "Do NOT file beads" instruction preserved

**Assumption checks**:
- ✓ Placeholder list format consistent (bullet + description)
- ✓ Agent template maintains logical flow: review type → review round → instructions → steps
- ✓ No breaking changes to downstream template sections
- ✓ Placeholder tokens remain in curly braces for Queen substitution
- ✓ Specification compliance verified line-by-line against docs/plans/2026-02-19-review-loop-convergence.md L585-L614

## Build/Test Validation

No build or automated tests apply to this template file. Validation is functional:

**Placeholder extraction**:
```bash
grep "REVIEW_ROUND" orchestration/templates/nitpicker-skeleton.md
```
Returns 2 matches:
- Line 12: Placeholder definition in list
- Line 20: Placeholder reference in agent template

**Grep validation confirms**:
```
12:- {REVIEW_ROUND}: 1, 2, 3, ... (determines scope instructions; filled by Pantry)
20:**Review round**: {REVIEW_ROUND}
```

**Round 2+ scope text verification**:
```bash
grep -E "(fix commits only|runtime failure|silently wrong results)" orchestration/templates/nitpicker-skeleton.md
```
Returns 1 match with all three required phrases in single line L21, confirming all keyword requirements met.

**Template structure integrity**:
- Line counts: Original 38 lines → Modified 41 lines (3 lines added: blank separator + 2 scope instruction lines)
- No structural damage to header, placeholder section, or workflow steps
- All downstream sections present and intact

## Acceptance Criteria Checklist

1. **Placeholder grep test**: `grep "REVIEW_ROUND" orchestration/templates/nitpicker-skeleton.md` returns matches in both placeholder list and agent template
   - **PASS** ✓ Two matches: line 12 (placeholder list), line 20 (agent template)

2. **Placeholder format**: Placeholder entry reads `{REVIEW_ROUND}: 1, 2, 3, ... (determines scope instructions; filled by Pantry)`
   - **PASS** ✓ Line 12 matches specification exactly

3. **Agent template round indicator**: Template contains `**Review round**: {REVIEW_ROUND}` after the "Perform a {REVIEW_TYPE} review" line
   - **PASS** ✓ Line 20 inserted directly after line 18's "Perform a..." with proper blank line separation

4. **Round 2+ scope keywords**: Round 2+ scope text mentions "fix commits only", "runtime failure", and "silently wrong results"
   - **PASS** ✓ All three phrases present in line 21:
     - "fix commits only" ✓
     - "runtime failure" ✓
     - "silently wrong results" ✓

## Summary

The nitpicker-skeleton template now includes round-aware scope instructions enabling the Pantry agent to inject review round information into reviewer prompts. Round 2+ reviewers will receive clear scope constraints limiting them to fix commits only, with defined exception criteria for out-of-scope findings (runtime failures and silently wrong results). All acceptance criteria met; no adjacent issues identified or fixed (per scope boundaries).

**Files changed**: 1
- orchestration/templates/nitpicker-skeleton.md (3 lines added)

**Commit message**: `feat: add round-aware scope instructions to nitpicker-skeleton (ant-farm-ha7a.8)`
