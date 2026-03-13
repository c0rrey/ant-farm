# Summary: ant-farm-5dt

**Task**: (BUG) pantry.md Review Mode does not generate Big Head preview file for CCO audit
**Agent**: technical-writer
**Status**: completed
**Files changed**: orchestration/templates/pantry.md

## Approaches Considered

### 1. Generate Big Head Preview in Step 5 (Parallel with Nitpicker)
**Strategy**: After generating the 4 (or 2 for round 2+) Nitpicker previews, add a separate code block to construct and write a Big Head preview by combining big-head-skeleton.md with the Big Head consolidation data file, just like the Nitpicker previews.

**Pros**:
- Parallels the existing Nitpicker preview pattern exactly
- Complete symmetry: if Nitpicker previews exist, Big Head preview exists
- CCO auditing is uniform (all 5 prompts available for review)

**Cons**:
- Adds ~15 lines to Step 5 (increases complexity slightly)
- Requires reading big-head-skeleton.md in Step 5 (alongside nitpicker-skeleton.md)
- If big-head-skeleton.md doesn't exist or is incompatible, the Step 5 logic becomes more complex

**Primary tradeoff**: Optimizes for consistency and complete auditing at cost of minor code complexity

---

### 2. Generate Big Head Preview with Conditional Round Logic
**Strategy**: Extend Step 5 to generate Big Head preview for both Round 1 and Round 2+, with conditional logic handling the fact that Round 2+ only generates 2 Nitpicker previews. Big Head consolidation brief exists for both rounds, so the preview should exist for both.

**Pros**:
- Handles round-specific logic cleanly (no special cases)
- Big Head preview availability matches Big Head consolidation data availability
- Clearer separation of Nitpicker round-specific logic from Big Head (which is always present)

**Cons**:
- Adds conditional branching to Step 5 (slightly higher complexity)
- Must carefully manage which skeletons are read for which rounds
- Requires documenting round-specific preview behavior in comments

**Primary tradeoff**: Optimizes for round-aware consistency at cost of conditional logic

---

### 3. Explicitly Document Exclusion with Rationale (No Preview Generated)
**Strategy**: Instead of generating a Big Head preview, add a comment in Step 5 explaining that Big Head consolidation is NOT audited via CCO and why. This documents the deliberate choice, making it clear this is intentional, not an oversight.

**Pros**:
- Minimal code change (just a comment)
- Makes the exclusion explicit and rationale transparent
- Future maintainers understand the design decision

**Cons**:
- Asymmetrical auditing (4 Nitpicker prompts audited, 1 Big Head prompt not)
- If the decision to exclude Big Head was itself a mistake, this formalizes the mistake
- CCO audit is incomplete (doesn't cover all prompts generated)
- May indicate a gap in the review process

**Primary tradeoff**: Optimizes for minimal change at cost of incomplete auditing and possible asymmetry

---

### 4. Generate Big Head Preview with Separate Helper Function
**Strategy**: Create a reusable helper logic pattern for generating combined previews (skeleton + data file), then call it for both Nitpicker and Big Head previews. This abstracts the preview generation logic, making it DRY and easier to maintain.

**Pros**:
- No code duplication (DRY principle)
- Easier to maintain if preview generation logic changes
- Extensible: if new review types added later, the pattern is already established
- Makes the structure clearer

**Cons**:
- Requires defining and documenting the helper pattern
- Might be over-engineering if Big Head is the only non-Nitpicker preview
- Adds indirection (readers must follow the helper to understand what's happening)

**Primary tradeoff**: Optimizes for maintainability and extensibility at cost of added abstraction

---

### 5. Hybrid – Direct Implementation with Clear Comments (Selected)
**Strategy**: Add Big Head preview generation directly in Step 5 after Nitpicker previews, using the same pattern as Nitpicker but with clear comments explaining that Big Head is always generated (both Round 1 and Round 2+) and appears in the return tables.

**Pros**:
- Simple and direct (no helper functions or over-abstraction)
- Clear, readable code with explicit comments
- Complete symmetry: all 5 prompts have previews, all 5 appear in return tables
- Auditing is uniform (CCO reviews all generated prompts)

**Cons**:
- Adds ~15 lines to Step 5 (not significant)
- Minor code duplication with Nitpicker pattern (but acceptable for clarity)

**Primary tradeoff**: Optimizes for clarity and completeness at minimal cost to code volume

---

## Selected Approach

**Choice**: Approach 5 (Hybrid – Direct Implementation with Clear Comments)

**Rationale**:
- The task brief explicitly states that "a big-head-skeleton.md template exists" and the expected behavior is that CCO should audit "all prompts before team creation," indicating Big Head preview generation was intended but overlooked.
- Approach 1 would work but lacks round-aware comments.
- Approach 2 is correct but adds unnecessary conditional complexity (Big Head consolidation brief exists for both rounds, so the preview should always exist without conditions).
- Approach 3 documents an exclusion that appears to be a bug, not an intentional design choice (the root cause specifically mentions the template exists, implying it should be used).
- Approach 4 is over-engineered for a single additional preview.
- Approach 5 is direct, clear, and maintainable. It adds the missing preview generation with explicit comments explaining that Big Head is always generated for all rounds, making the code self-documenting. The fix directly serves CCO auditing completeness.

The acceptance criteria explicitly allow either (a) generating Big Head preview OR (b) documenting the exclusion. Approach 5 generates the preview, which is the correct fix for the incomplete prompt coverage gap.

## Implementation

Added Big Head preview generation to Section 2 Step 5, ensuring complete CCO audit coverage:

1. **Updated Step 5 introductory read instruction** (line 406): Now reads both `nitpicker-skeleton.md` AND `big-head-skeleton.md`

2. **Added Big Head preview generation logic** (lines 415-420):
   - Numbered as item 4 in Step 5 (after Nitpicker items 1-3)
   - Explicitly labeled: "Big Head preview (generated for all rounds)"
   - Specifies exact skeleton file, placeholder names, and output path
   - Follows the same pattern as Nitpicker previews for consistency

3. **Updated Round 1 return table** (line 436): Added Big Head row:
   - Brief: `{session-dir}/prompts/review-big-head-consolidation.md`
   - Preview File: `{session-dir}/previews/review-big-head-preview.md`
   - Report Output Path: `{session-dir}/review-reports/review-consolidated-{timestamp}.md`

4. **Updated Round 2+ return table** (line 445): Added matching Big Head row with same structure

The implementation ensures:
- Big Head preview is generated for ALL rounds (not just Round 1)
- CCO can audit all 5 prompts (4 Nitpicker + 1 Big Head) before team creation
- Return tables show complete prompt coverage for both round structures
- Placeholder substitution is correct (`DATA_FILE_PATH`, `CONSOLIDATED_OUTPUT_PATH`)

## Correctness Review

### orchestration/templates/pantry.md

- **Re-read**: yes (full Section 2 Steps 4-6 reviewed, lines 312-446)
- **Acceptance criteria verified**:
  - ✅ **Criterion 1**: Either a Big Head preview file is generated in Step 5 OR the exclusion is documented — PASS (Big Head preview is now generated at lines 415-420)
  - Step 5 now reads big-head-skeleton.md (line 406)
  - Big Head preview combines skeleton + consolidation data file (lines 415-420)
  - Output written to correct path: `{session-dir}/previews/review-big-head-preview.md`
  - Both return tables updated to include Big Head preview paths (lines 436, 445)

- **Issues found**: None. The implementation correctly:
  - Reads all required templates at the start of Step 5
  - Generates Nitpicker previews per round (lines 407-413)
  - Generates Big Head preview with explicit "(generated for all rounds)" label (lines 415-420)
  - Maintains consistent placeholder substitution with big-head-skeleton.md template
  - Updates return tables to show complete prompt coverage

- **Cross-file consistency**: Verified against:
  - big-head-skeleton.md (placeholder names {DATA_FILE_PATH} and {CONSOLIDATED_OUTPUT_PATH} are correct per template)
  - Step 4 (Big Head consolidation data file path matches: `{session-dir}/prompts/review-big-head-consolidation.md`)
  - Both return table structures (identical columns, Big Head row follows Nitpicker pattern)

### Assumptions audit

**Assumptions stated**:
1. big-head-skeleton.md exists at `~/.claude/orchestration/templates/big-head-skeleton.md` with expected placeholders (verified by reading file)
2. Big Head consolidation data file is written in Step 4 and available for reading in Step 5
3. Big Head preview should be generated for BOTH Round 1 and Round 2+ (unlike Nitpicker previews which vary by round)
4. CCO auditing requires all 5 prompts available as preview files before team creation

**What could go wrong**:
1. **Scenario 1**: Big Head consolidation data file unavailable when Step 5 reads it. Mitigation: Step 5 executes after Step 4 (which writes the file). The Pantry should validate file existence before reading (consistent with existing fail-fast patterns in Step 2).

2. **Scenario 2**: big-head-skeleton.md uses different placeholder names. Mitigation: Placeholder names are verified from the actual template file, so instructions are precise. Current instruction correctly names both placeholders.

3. **Scenario 3**: Future round changes affect Nitpicker logic but Big Head should remain constant. Mitigation: Explicit comment "(generated for all rounds)" makes this resilient to round structure changes.

## Build/Test Validation

- **Command run**: Manual verification of pantry.md structure, Markdown syntax, and placeholder consistency
- **Result**: PASS. File parses correctly with no syntax errors. Step 5 logic is well-formatted and clear. Return tables are consistent across both round variants. Placeholder names match big-head-skeleton.md template.

## Acceptance Criteria

- [x] **Criterion 1** — Either a Big Head preview file is generated in Step 5 (combining big-head-skeleton.md + Big Head consolidation data file), or the exclusion is explicitly documented with rationale — PASS
  - Big Head preview is now generated (lines 415-420)
  - Combines big-head-skeleton.md template with `review-big-head-consolidation.md` data file
  - Written to `{session-dir}/previews/review-big-head-preview.md`
  - Both return tables include Big Head row, confirming complete CCO audit coverage

---

**Commit hash**: (awaiting git push)
**Files modified**: 1 file
- orchestration/templates/pantry.md (lines 404-446 expanded/updated for Big Head preview generation)
