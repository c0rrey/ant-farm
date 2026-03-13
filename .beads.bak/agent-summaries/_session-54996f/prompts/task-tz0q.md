# Task Brief: ant-farm-tz0q
**Task**: Nested markdown code fences in reviews.md error return template break rendering
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-54996f/summaries/tz0q.md

## Context
- **Affected files**: orchestration/templates/reviews.md:L390-420 -- Error return template containing a nested triple-backtick code fence that prematurely closes the outer fence; inner fence at lines 414-416 uses same delimiter as outer fence at line 390
- **Root cause**: The error return template in reviews.md Step 0a (lines 390-420) contains a nested markdown code fence. The outer fence opens at line 390 with triple backticks. The inner fence at lines 414-416 (for the re-spawn instruction) uses the same triple backticks, which prematurely closes the outer fence in standard markdown rendering. Lines 417-420 render as regular text instead of inside the code block. An agent parsing this template literally could misinterpret the template boundaries.
- **Expected behavior**: Use quadruple backticks for the outer fence, or indent the inner block with 4+ spaces, or use tildes for the inner fence to avoid premature closure.
- **Acceptance criteria**:
  1. The error return template renders correctly with no premature fence closure
  2. All content in the template (lines 390-420) is properly enclosed within the outer fence
  3. Fix uses one of: quadruple backticks for outer, indented inner block, or tilde inner fence

## Scope Boundaries
Read ONLY: orchestration/templates/reviews.md:L386-424 (error return template section)
Do NOT edit: Any lines outside L386-424 in reviews.md; the polling loop section (L354-385); any other files

## Focus
Your task is ONLY to fix the nested markdown code fence issue in the error return template (reviews.md lines 390-420) so that the outer and inner fences use different delimiters.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
