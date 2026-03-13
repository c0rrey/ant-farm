# Summary: ant-farm-wiq

**Task**: Checkpoints CCO FAIL verdict format has no example

## 1. Approaches Considered

**Approach A: Add FAIL example directly after the FAIL verdict line in the Verdict section (inside the template block).**
Insert a blockquote-formatted example immediately after the FAIL verdict bullet, showing a complete FAIL output with check numbers, names, and evidence.
- Pros: Example is exactly where the Pest Control agent reads verdict options. Inside the template block, so visible during execution. Immediately actionable.
- Cons: Makes the verdict section slightly longer.

**Approach B: Add FAIL example in the Verdict Thresholds section (outside the template block).**
Add the example in the `#### Verdict Thresholds for CCO` section (lines 110-121) alongside the existing WARN/FAIL threshold examples.
- Pros: Groups with the existing WARN examples.
- Cons: Outside the template block -- the Pest Control agent executing the template may not see this section. The existing examples there are about threshold classification, not output formatting.

**Approach C: Add a separate "Example Verdicts" subsection after the template closing block.**
Create a new subsection after line 178 showing both PASS and FAIL example outputs.
- Pros: Comprehensive reference section with multiple examples.
- Cons: Outside the template block -- not visible to the executing agent. Also, the brief says to add a FAIL example, not a full examples section.

**Approach D: Add FAIL example inline within the FAIL verdict bullet.**
Embed the example directly in the bullet text (no separate block).
- Pros: Tightly coupled.
- Cons: Hard to read -- long bullet with embedded multi-line example. Blockquote formatting inside a code block is cleaner.

## 2. Selected Approach

**Approach A** -- Add a FAIL example in the Verdict section inside the template block.

Rationale: The Pest Control agent reads the template block to understand how to format its output. Placing the FAIL example directly after the verdict bullets (and inside the template block) ensures the agent sees the expected format when deciding how to write a FAIL verdict. The blockquote format visually distinguishes the example from the instructions.

## 3. Implementation Description

**File changed**: `orchestration/templates/checkpoints.md`

Added a FAIL verdict example (lines 159-169) inside the CCO Dirt Pushers template block, after the three verdict bullets and before "Write your verification report to":

The example shows:
- **Verdict header**: "Verdict: FAIL" (matching the PASS/WARN/FAIL pattern)
- **Failed checks**: Two checks (Check 2 and Check 5) with check number, name in parentheses, and specific evidence
- **Passing checks**: Listed by number for completeness
- **Recommendation**: Actionable next step for the Queen

Evidence examples are realistic:
- Check 2 failure: placeholder `<list from bead>` instead of actual file paths (a common CCO failure mode)
- Check 5 failure: vague scope "explore the codebase for related issues" (a common prompt defect)

## 4. Correctness Review

**orchestration/templates/checkpoints.md**:
- Re-read: yes
- Lines 159-169: FAIL example is inside the template block (block starts line 123, ends line 178).
- The example uses check numbers (2, 5) that correspond to actual checks in the template: Check 2 is "Real file paths" (line 138), Check 5 is "Scope boundaries" (line 148) -- confirmed match.
- The check names in the example ("Real file paths", "Scope boundaries") exactly match the bold labels in the check list.
- Evidence is specific and realistic: placeholder text and vague scope language are documented failure modes.
- The blockquote format (`>`) makes the example visually distinct from instructions.
- No edits were made outside the CCO Dirt Pushers section (lines 100-178).

## 5. Build/Test Validation

No build or test infrastructure applies to this markdown template file. Validation is structural: the FAIL example is within the template block, uses real check numbers and names, and provides concrete evidence.

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|---|---|
| CCO section includes a FAIL verdict example with check number, name, and evidence | PASS |
