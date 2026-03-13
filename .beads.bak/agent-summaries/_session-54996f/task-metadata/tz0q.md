# Task: ant-farm-tz0q
**Status**: success
**Title**: Nested markdown code fences in reviews.md error return template break rendering
**Type**: bug
**Priority**: P2
**Epic**: _standalone
**Agent Type**: technical-writer
**Dependencies**: blocks: [], blockedBy: []

## Affected Files
- orchestration/templates/reviews.md:390-420 — Error return template containing a nested triple-backtick code fence that prematurely closes the outer fence; inner fence at lines 414-416 uses same delimiter as outer fence at line 390

## Root Cause
The error return template in reviews.md Step 0a (lines 390-420) contains a nested markdown code fence. The outer fence opens at line 390 with triple backticks. The inner fence at lines 414-416 (for the re-spawn instruction) uses the same triple backticks, which prematurely closes the outer fence in standard markdown rendering. Lines 417-420 render as regular text instead of inside the code block. An agent parsing this template literally could misinterpret the template boundaries.

## Expected Behavior
Use quadruple backticks for the outer fence, or indent the inner block with 4+ spaces, or use tildes for the inner fence to avoid premature closure.

## Acceptance Criteria
1. The error return template renders correctly with no premature fence closure
2. All content in the template (lines 390-420) is properly enclosed within the outer fence
3. Fix uses one of: quadruple backticks for outer, indented inner block, or tilde inner fence
