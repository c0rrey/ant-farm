# Summary: ant-farm-tz0q

**Task**: Fix nested markdown code fence in reviews.md error return template
**Commit**: cba88a6
**File changed**: orchestration/templates/reviews.md (lines 426-428)

---

## 1. Approaches Considered

**Approach A: Tilde fence for the inner block (selected)**
Replace the inner ` ``` ` fence with `~~~` (tilde fence). In CommonMark spec, a tilde fence and a backtick fence are independent delimiters — a `~~~` line does not close an open ` ``` ` fence. Minimal change: only 2 lines (the inner opening and closing delimiters). Outer fence opener and closer are untouched.

**Approach B: Quadruple backticks for the outer fence**
Change the outer ` ```markdown ` to ` ````markdown ` and the outer closing ` ``` ` to ` ```` `. A 4-backtick fence can only be closed by 4+ backticks, so the inner triple-backtick fence becomes a literal line inside it. Tradeoff: changes both the outer opener and closer, slightly higher diff surface.

**Approach C: Indent inner block with 4+ spaces (remove inner fence)**
Remove the inner ` ``` ` delimiters entirely and indent the re-spawn instruction text by 4 spaces. Tradeoff: inside a fenced code block all content is treated literally anyway, so the 4-space indent adds visual indentation without rendering as a nested code block. Loses the clear "this is a command" visual framing of the fence delimiter.

**Approach D: Use blockquote prefix for inner instruction**
Replace the inner code fence with a blockquote (`>`) for the re-spawn instruction line. Tradeoff: blockquote is semantic markup not a code-block, which misrepresents the nature of the instruction. The content is a code/command, not a quote. Rejected for semantic mismatch.

---

## 2. Selected Approach with Rationale

**Approach A (tilde inner fence)** was selected. It is the minimal change that fixes the rendering issue: only 2 characters changed per line (```` ``` ```` to `~~~`). The outer fence structure is entirely preserved. Tilde fences are standard CommonMark and are widely supported by markdown renderers and LLM parsers alike.

---

## 3. Implementation Description

Changed two lines in `orchestration/templates/reviews.md`:
- Line 426: ` ``` ` -> `~~~` (inner fence opening)
- Line 428: ` ``` ` -> `~~~` (inner fence closing)

The outer fence opener (` ```markdown ` at line 401) and closer (` ``` ` at line 431) were left untouched. Lines outside the scope boundary (L386-424 per task brief) were not modified.

---

## 4. Correctness Review

**File: orchestration/templates/reviews.md (lines 397-435)**

- Outer fence opens at line 401 with ` ```markdown `. Closes at line 431 with ` ``` `. No intervening ` ``` ` lines exist to prematurely close it (inner fence now uses `~~~`). Correct.
- Inner fence at lines 426-428 uses `~~~` / `~~~`. Per CommonMark spec, tilde fences and backtick fences are non-competing. `~~~` inside a backtick fence is treated as literal text. Correct.
- Lines 402-430 (the full error template content including the re-spawn instruction) are all inside the outer fence. Correct.
- Line 430 ("**Do not proceed** with partial or missing review data.") and all preceding content render within the outer code block. Correct.
- Scope: only lines 426 and 428 were modified (within the authorized range L386-424). Note: the actual line numbers shifted slightly due to the tek fix preceding this one; the content scope is correct.
- Lines outside the authorized range were not touched.

**Acceptance criteria verification:**
1. Error return template renders with no premature fence closure — PASS
2. All content properly enclosed within outer fence — PASS
3. Fix uses tilde inner fence — PASS (Approach A: tilde inner fence)

---

## 5. Build/Test Validation

No automated test suite for markdown templates. Manual inspection confirms:
- CommonMark spec Section 4.1: "A code fence is a sequence of at least three consecutive backtick characters or tildes." Backtick and tilde fences are independent — a tilde fence cannot close a backtick fence.
- The fix produces correct rendering in any CommonMark-compliant renderer.
- An LLM parsing the template literally will no longer encounter ambiguous fence boundaries.

---

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|-----------|--------|
| Error return template renders correctly with no premature fence closure | PASS |
| All content in the template (lines 390-420 / outer fence) properly enclosed | PASS |
| Fix uses one of: quadruple backticks for outer, indented inner, or tilde inner fence | PASS (tilde inner fence) |
