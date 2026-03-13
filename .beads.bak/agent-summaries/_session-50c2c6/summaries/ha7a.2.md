# Task Summary: ant-farm-ha7a.2

**Task**: Add round-aware review protocol and team setup to reviews.md
**Agent**: technical-writer
**Status**: COMPLETED
**Date**: 2026-02-19

## Approaches Considered

### Approach 1: Direct Line Number Insertion (Simple but Fragile)
Insert the new section at fixed line numbers (line 89 for Round-Aware Review Protocol, lines 49-75 for Team Setup update). Read the whole file, locate lines by number, and replace/insert.

**Pros**:
- Straightforward implementation
- Minimal code
- Fast execution

**Cons**:
- Brittle: line numbers shift if other edits occur
- Violates task context guidance: "Line numbers are provided as initial guidance only — after edits in earlier steps, locate sections by heading text, not line numbers"
- High risk of off-by-one errors if file structure changes

### Approach 2: Heading-Based Location with Precise String Matching (SELECTED)
Search for section headings (`## Review 1: Clarity (P3)` and `### Team Setup`) and use them as anchors for insertion. Use the Edit tool with exact string matching to replace the old Team Setup section and insert the new protocol section.

**Pros**:
- Robust to line number shifts
- Matches task context guidance explicitly
- Self-documenting: readers can understand what's being replaced
- Precise string matching prevents accidental edits to unintended sections
- Scales well across the project

**Cons**:
- Requires careful handling of multi-line strings with exact formatting
- More context needed in the old_string parameter

### Approach 3: Section-by-Section Assembly (Modular but Complex)
Read the file in parts (before Team Setup, Team Setup, between Team Setup and Review 1, Review 1 onwards). Modify each section independently and reassemble.

**Pros**:
- Explicit control over each modification
- Good for documentation
- Easy to debug individual sections

**Cons**:
- More code, higher complexity
- Requires multiple reads and writes
- Risk of introducing formatting inconsistencies between sections

### Approach 4: Piecemeal Inline Edits (Risky)
Make multiple small Edit tool calls to replace one bullet point at a time within Team Setup, then separately insert the protocol section.

**Pros**:
- Each edit is small and focused
- Less risk per individual edit

**Cons**:
- Multiple tool calls means multiple failure points
- Harder to verify correct result without reading whole file after each call
- Difficult to reason about cumulative effect on file structure

## Selected Approach

**Approach 2: Heading-Based Location with Precise String Matching**

**Rationale**:
The task context explicitly warns: "Line numbers are provided as initial guidance only — after edits in earlier steps, locate sections by heading text, not line numbers." This is the explicit guidance for the ant-farm project's review convergence implementation workflow. Using heading-based anchors:
- Ensures compliance with stated workflow
- Provides robustness across the multi-task implementation sequence
- Uses the Edit tool as intended (with meaningful context, not brittle line numbers)
- Demonstrates best practices for template maintenance in a codebase with multiple concurrent editors

The two Edit calls are:
1. Replace the old Team Setup section (anchored by `### Team Setup` heading)
2. Insert the Round-Aware Review Protocol section (anchored by `## Review 1: Clarity` heading)

This approach aligns with how the other tasks in the plan (Tasks 3-11) will modify the same file.

## Implementation Description

**File Modified**: `orchestration/templates/reviews.md`

**Changes Made**:

### Change 1: Updated Team Setup Section (Lines 49-75 → 49-96)

**Old Content**: Lines 49-75 showed a single 6-member team with all 4 reviewers.

**New Content**: Added round-awareness to the Team Setup section:
- **Round 1** subsection (lines 53-73): 6-member team with 4 reviewers, all 4 review types
- **Round 2+** subsection (lines 75-93): 4-member team with 2 reviewers (Correctness + Edge Cases only), fix-commit scope only, P3 auto-filing enabled

**Key updates**:
- Changed code fence markers from ` ``` ` to ` ~~~ ` to properly nest within markdown
- Added "Round 1:" and "Round 2+:" labels for clarity
- Updated member counts: 6 for round 1, 4 for round 2+
- Updated review list: all 4 types for round 1, 2 types for round 2+
- Updated scope: all commits for round 1, fix commits only for round 2+
- Added P3 auto-filing note for round 2+

### Change 2: Inserted Round-Aware Review Protocol Section (New, Lines 110-154)

**Location**: Between `### Messaging Guidelines` (lines 98-108) and `## Review 1: Clarity (P3)` (now line 156).

**Content**: New section with 4 subsections:
1. **Round 1 (Full Review)** (lines 114-121):
   - Lists 4 reviewers, all session commits scope, 6-member team
   - States "This is the existing protocol — no changes to round 1 behavior"

2. **Round 2+ (Fix Verification)** (lines 123-133):
   - Lists 2 reviewers, fix-commit scope only, 4-member team
   - Defines in-scope findings (runtime failures, silently wrong results)
   - Defines out-of-scope findings (naming, style, docs, improvements)
   - Notes P3 auto-filing

3. **Termination Rule** (lines 135-144):
   - States termination condition: 0 P1/P2 findings
   - Explains P3 handling differs by round
   - States "no user prompt needed — the loop simply ends"
   - Notes no hard cap on rounds

4. **Round 2+ Reviewer Instructions** (lines 146-154):
   - Provides scope constraint text for reviewers
   - Explains out-of-scope finding bar
   - Notes `[OUT-OF-SCOPE]` tag usage

**Method**: Used two Edit tool calls with exact string matching:
1. Replaced lines containing Team Setup with new round-aware version
2. Inserted new protocol section before Review 1 heading

## Correctness Review

### File: orchestration/templates/reviews.md

**Structural Verification**:

1. **Team Setup Section (Lines 49-96)**:
   - Pre-modification: Single "The Queen creates..." paragraph with 6 members and 4 reviews
   - Post-modification: Two labeled subsections (Round 1 and Round 2+) with different team sizes and reviewer counts
   - Messaging Guidelines section still immediately follows (line 98): ✓

2. **Round-Aware Review Protocol Section (Lines 110-154)**:
   - Inserted before `## Review 1: Clarity (P3)` (now line 156): ✓
   - Contains all 4 required subsections: ✓
   - Proper markdown hierarchy: ## for section, ### for subsections: ✓

3. **Content Accuracy** (verified line-by-line):
   - Round 1: 4 reviewers, 6 members, all commits: ✓
   - Round 2+: 2 reviewers, 4 members, fix commits only: ✓
   - Termination rule references "0 P1/P2 findings": ✓
   - P3 auto-filing in round 2+ section: ✓
   - Out-of-scope finding bar included: ✓

4. **Cross-Reference Verification**:
   - Team Setup correctly states "**Round 1**: ... **6 members**" (line 53): ✓
   - Team Setup correctly states "**Round 2+**: ... **4 members**" (line 75): ✓
   - Protocol section explains 6-member composition for round 1 (line 119): ✓
   - Protocol section explains 4-member composition for round 2+ (line 127): ✓

5. **Markdown Syntax**:
   - All section headers properly formatted: ✓
   - Code fences use ~~~ (not ``` for nested markdown): ✓
   - List items properly indented: ✓
   - Block quotes (>) properly formatted: ✓

**No syntax errors detected. All content matches specification exactly.**

## Build/Test Validation

The modified file is a markdown template used at runtime by the Pantry agent to compose review briefs. Validation approach:

1. **Markdown Syntax Validation**:
   - All section headers properly formatted (`## Round-Aware Review Protocol`, etc.)
   - No unclosed or mismatched fences
   - All lists properly indented
   - No broken cross-references
   - File is readable and parseable

2. **Specification Compliance Check**:
   - Verified against `docs/plans/2026-02-19-review-loop-convergence.md` Task 2 specification (lines 53-170)
   - Round 1 subsection includes all required details: ✓
   - Round 2+ subsection includes all required details: ✓
   - Termination Rule subsection matches specification word-for-word: ✓
   - Round 2+ Reviewer Instructions included: ✓
   - Team Setup updated with round labels and member counts: ✓
   - Messaging Guidelines section still present immediately after Team Setup: ✓

3. **Acceptance Criteria Validation**:
   - Criterion 1: grep "## Round-Aware Review Protocol" returns match: ✓ (line 110)
   - Criterion 2: Section before `## Review 1: Clarity (P3)`: ✓ (line 110 before line 156)
   - Criterion 3: Contains all 4 subsections: ✓ (lines 114, 123, 135, 146)
   - Criterion 4: Team Setup shows "**Round 1**: ... **6 members**": ✓ (line 53)
   - Criterion 4: Team Setup shows "**Round 2+**: ... **4 members**": ✓ (line 75)
   - Criterion 5: Messaging Guidelines still exists immediately after Team Setup: ✓ (line 98)

No unit tests or continuous build applies to this template file. Validation is structural and specification-based, both of which pass completely.

## Acceptance Criteria Checklist

- [x] **Criterion 1**: `grep "## Round-Aware Review Protocol" orchestration/templates/reviews.md` returns a match
  - Result: PASS
  - Evidence: grep found "## Round-Aware Review Protocol" at line 110 in the file

- [x] **Criterion 2**: The section appears before `## Review 1: Clarity (P3)` (verify heading order)
  - Result: PASS
  - Evidence: Round-Aware Review Protocol at line 110, Review 1: Clarity at line 156
  - Order: Protocol (line 110) is before Review 1 (line 156) ✓

- [x] **Criterion 3**: The section contains all 4 subsections:
  - Round 1 (Full Review): line 114 ✓
  - Round 2+ (Fix Verification): line 123 ✓
  - Termination Rule: line 135 ✓
  - Round 2+ Reviewer Instructions: line 146 ✓
  - Result: PASS

- [x] **Criterion 4**: Team Setup shows round-dependent team sizes
  - "**Round 1**: The Queen creates the Nitpicker team with **6 members**": line 53 ✓
  - "**Round 2+**: The Queen creates the Nitpicker team with **4 members**": line 75 ✓
  - Result: PASS

- [x] **Criterion 5**: `### Messaging Guidelines` section still exists immediately after Team Setup
  - Pre-Team-Setup: ends at line 96 with "The Queen fills in the skeleton..."
  - Messaging Guidelines: starts at line 98 with "### Messaging Guidelines"
  - Immediately follows: ✓
  - Result: PASS

**Overall Result: ALL CRITERIA PASS**

## Commit Information

**Commit Command**:
```bash
git pull --rebase
git add orchestration/templates/reviews.md
git commit -m "feat: add round-aware review protocol and team setup to reviews.md (ant-farm-ha7a.2)"
```

**Commit Type**: feat (feature)
**Files Changed**: 1 (orchestration/templates/reviews.md)
**Lines Added**:
- Round-Aware Review Protocol section: 45 lines (110-154)
- Team Setup Round 2+ subsection: 19 lines (75-93)
- Total net: ~55 lines added

**Commit Hash**: [To be populated after execution]

## Summary

This task successfully added round-aware review protocol and team setup to the reviews.md template. The implementation introduces two key concepts:

1. **Round-Aware Review Protocol** section (new, 45 lines) that documents:
   - Round 1 behavior (4 reviewers, all commits, 6-member team)
   - Round 2+ behavior (2 reviewers, fix commits only, 4-member team)
   - Termination condition (0 P1/P2 findings)
   - Reviewer instructions for out-of-scope findings

2. **Updated Team Setup** section that shows:
   - Round 1: 6-member team with all 4 reviewer types
   - Round 2+: 4-member team with 2 reviewer types, P3 auto-filing

The implementation used heading-based location with precise string matching (Approach 2), ensuring robustness across the multi-task implementation sequence and compliance with project workflow guidance.

All five acceptance criteria have been verified and pass. The changes are minimal, focused, and maintain consistency with the existing template structure and markdown syntax. The file remains valid and ready for use by the Pantry agent during review briefing composition.
