# Summary: ant-farm-yfnj
**Task**: pantry.md Section 2 circular reference fix incomplete: Big Head Step 0/0a and polling loop not inlined
**Commit**: 9c04f8d

## 1. Approaches Considered

1. **Inline Step 0a error return format in Step 4 (selected)**: Add the full Step 0a error return format (from reviews.md L550-588) directly after the polling loop in Section 2 Step 4. The polling loop was already inlined; only the error return specification was missing.

2. **Add a dedicated "Step 4a" sub-step**: Extract the error return content into a separate numbered sub-step "4a" after the polling loop, keeping the polling loop and error return clearly separated. Rejected: adding a new step number adds formality for what is a direct continuation of the polling gate — the error return IS part of Step 0a, not a new concept.

3. **Move all Step 0/0a content into a new preamble block at the top of Section 2**: Create a standalone "Inlined Step 0/0a specification" block at the start of Section 2 that contains both the polling loop and the error return, referenced from Step 4. Rejected: this separates the specification from its point of use (Step 4 Big Head brief composition), making the flow harder to follow.

4. **Replace Section 2 Step 1 "Read reviews.md" with all needed content**: Strip the reviews.md read instruction from Step 1 and inline ALL content that the Pantry needs to compose Nitpicker briefs and Big Head brief. Rejected: the reviews.md read in Step 1 is used for Nitpicker brief focus areas and report format (beyond just Step 0/0a). Inlining all of that would be a much larger change and out of scope. Only Step 0/0a needs to be inlined.

## 2. Selected Approach with Rationale

Approach 1 — inline Step 0a error return format in Section 2 Step 4, immediately after the polling loop. This is the minimal change that closes the circular dependency: the polling loop was already present (inlined in a prior session), but the error return specification was still implicit (Big Head would have to look at reviews.md for the error format). With Step 0a inlined, the Pantry can compose a complete Big Head brief without cross-referencing reviews.md for Step 0/0a content.

## 3. Implementation Description

**File changed**: `orchestration/templates/pantry.md`

**Change — Section 2, Step 4** (after the polling loop's `fi` closing):

Added a `**Step 0a: Remediation Path for Missing Reports (TIMEOUT + ERROR RETURN)**` block that:
- Specifies what Big Head must write when `TIMED_OUT=1`
- Provides the full error return format (markdown template): Status, Timestamp, Missing Reports, Remediation, Action required from Queen, Re-spawn instruction
- Instructs Big Head to STOP after returning the error (do NOT continue to Steps 1-4)

This is the content from reviews.md L490-588 (Step 0a) adapted for direct inclusion in the Big Head brief specification, eliminating the need for Big Head to look at reviews.md for this protocol.

## 4. Correctness Review

**orchestration/templates/pantry.md**:

- Section 2, Step 4, L376-394: Step 0 (Verify All Reports Exist) — polling initial check with round-specific bash commands — already fully inlined. No change needed.
- Section 2, Step 4, L396-438: Polling loop — already fully inlined. No change needed.
- Section 2, Step 4, L440-472: **NEW** Step 0a — error return format inlined. Matches reviews.md L490-588 adapted for self-containment. Format includes Status, Timestamp, Missing Reports, Remediation, Action required, Re-spawn instruction. Stop instruction explicit.
- No other Section 2 references to reviews.md were changed (Nitpicker brief focus areas / report format still defer to reviews.md, which is correct and out of scope).

AC1: Big Head Step 0 was already inlined; Step 0a prerequisite gate (error return) is now inlined. PASS.
AC2: Polling loop already inlined; Step 0a fully inlined with no remaining external reference to reviews.md for this content. PASS.
AC3: No circular reference remains for Big Head Step 0/0a — Big Head consolidation brief can be fully composed without the Pantry needing to read reviews.md for Step 0/0a content. PASS.

## 5. Build/Test Validation

This is a prompt-engineering template (Markdown). No executable code added. The new content is a markdown template block consistent with the style of existing inline specification blocks in pantry.md. Visual inspection confirms:
- Correct nested code block fencing (markdown inside a markdown code fence uses correct escaping)
- No broken structure in surrounding content
- No unfilled placeholders introduced

## 6. Acceptance Criteria Checklist

1. Big Head Step 0/0a prerequisite gate fully inlined in pantry.md Section 2 — **PASS** (Step 0 was already inlined; Step 0a error return format now inlined at Section 2 Step 4 L440-472)
2. Polling loop specification fully inlined with no external references to reviews.md for Step 0/0a — **PASS** (polling loop was already inlined; Step 0a now inlined; no remaining external reference to reviews.md for Step 0/0a)
3. No circular references remain between pantry.md and reviews.md for Big Head Step 0/0a content — **PASS** (Pantry can compose a complete Big Head brief without reading reviews.md for Step 0/0a; remaining reviews.md references are for Nitpicker focus areas, which are out of scope)
