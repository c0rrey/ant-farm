# Summary: Task ant-farm-ha7a.10

**Task**: Update CCB checkpoint for round-aware report counts

**Agent**: technical-writer

**Status**: COMPLETE

---

## 1. Approaches Considered

### Approach 1: Conditional Blocks with Round Labels
Use explicit "Round 1:" and "Round 2+:" subsection headers to separate requirements by round. Each check would have two distinct content blocks.

**Pros**:
- Crystal clear what applies when
- Easy to scan and understand at a glance
- Minimal ambiguity about which files/counts to expect
- No preprocessing required; Pest Control simply reads round number and selects applicable block

**Cons**:
- Longer document
- Potential for minor duplication of explanatory text

### Approach 2: Inline Parametrization with Placeholders
Use placeholders like `{REPORT_COUNT}`, `{REPORT_LIST}`, `{DOCUMENT_COUNT}` that the Pantry fills in per round before passing the brief to Pest Control.

**Pros**:
- Single source of truth for the check logic
- Pantry handles all variation
- Template remains more compact

**Cons**:
- Requires Pantry to generate round-specific brief version
- Adds a preprocessing/template-fill step
- Harder to read the raw template
- Would require changes to Pantry's brief composition logic

### Approach 3: Conditional Logic with If/Else Notes
Add narrative notes inline like "If round 1: ...; if round 2+: ..." within each check description.

**Pros**:
- Keeps related information together
- Avoids duplication of check logic

**Cons**:
- Mixes procedural narrative with conditional logic
- Harder to scan visually
- Confusing for Pest Control to parse at runtime

### Approach 4: Separate Tables per Round
Create two distinct tables (Round 1 table, Round 2+ table) showing file counts, report lists, and counting rules side-by-side with clear visual separation.

**Pros**:
- Very explicit; easy to compare rounds
- No ambiguity about which row applies

**Cons**:
- Requires more document real estate
- Readers must find the right table for their round
- Potential for visual clutter

---

## 2. Selected Approach with Rationale

**Selected: Approach 1 (Conditional Blocks with Round Labels)**

**Rationale**:

1. **Specification alignment**: The convergence plan (docs/plans/2026-02-19-review-loop-convergence.md Task 10, lines 729-801) explicitly shows the expected format with "Round 1:" and "Round 2+:" subsection headers. This is the authoritative design.

2. **Consistency**: This pattern is already used throughout the round-aware sections in reviews.md (Round-Aware Review Protocol, Team Setup). Maintaining visual and structural consistency across templates improves readability.

3. **Runtime clarity**: Pest Control receives the review round number in its brief. With explicit "Round 1:" and "Round 2+:" blocks, the agent immediately knows which verification steps apply. No placeholder expansion or conditional logic to parse.

4. **No preprocessing**: Unlike Approach 2, this requires no changes to Pantry's brief composition. The template stands alone as documentation.

5. **Scanability**: Readers (and AI agents) can visually identify their round and focus on the relevant block. The bold headers make the structure immediately obvious.

6. **Maintainability**: Future readers and maintainers can see at a glance what CCB expects in each round without deciphering conditional syntax.

---

## 3. Implementation Description

Updated `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md` in the CCB (Colony Census Bureau) section:

### Changes made:

1. **CCB header (Line 453)**:
   - Original: `**When**: After Big Head consolidation (after all 4 review reports merged and beads filed)`
   - Updated: `**When**: After Big Head consolidation (after all review reports merged and beads filed — 4 reports in round 1, 2 in round 2+)`
   - Effect: Immediately establishes the round-dependent count expectation

2. **Individual reports list (Lines 467-479)**:
   - Original: Single flat list of 4 file paths with no round distinction
   - Updated: Two separate subsections:
     - **Round 1**: Lists 4 report files (clarity, edge-cases, correctness, excellence)
     - **Round 2+**: Lists 2 report files (correctness, edge-cases only)
   - Also updated the note: `(The Queen provides exact filenames and the review round number in the consolidation prompt.)` — added "and the review round number"
   - Updated document count line to: `Read all documents (round 1: 5 total = 4 reports + consolidated; round 2+: 3 total = 2 reports + consolidated), then perform these 8 checks:`

3. **Check 0: Report Existence Verification (Lines 481-494)**:
   - Original: Single hardcoded block verifying "exactly 4 report files"
   - Updated: Two conditional blocks with explicit round labels:
     - **Round 1** — verify exactly 4 report files with all 4 file paths listed
     - **Round 2+** — verify exactly 2 report files with only correctness and edge-cases paths
   - Kept the failure condition: "If any expected file is missing, FAIL immediately"

4. **Check 1: Finding Count Reconciliation (Lines 496-500)**:
   - Original: `Count total findings across all 4 individual reports` (hardcoded "4")
   - Updated: `Count total findings across all individual reports (4 in round 1, 2 in round 2+)`
   - Updated math reporting line from: `"Clarity: N, Edge Cases: N, Correctness: N, Excellence: N = TOTAL total. Consolidated references TOTAL findings across N root causes. N findings merged as duplicates. RECONCILED / NOT RECONCILED — {list orphaned findings}"`
   - To: `"Round 1: Clarity: N, Edge Cases: N, Correctness: N, Excellence: N = TOTAL total. Round 2+: Correctness: N, Edge Cases: N = TOTAL total. Consolidated references TOTAL findings across N root causes. N findings merged as duplicates. RECONCILED / NOT RECONCILED — {list orphaned findings}"`
   - Effect: Pest Control now reports the math broken down by round, matching the actual report count

### Scope adherence:
- Updated ONLY the sections specified: CCB header, Individual reports list, Check 0, Check 1
- Left unchanged: Checks 2-7 and the Verdict section (as per task scope boundary)
- Did not edit the pre-CCB sections (CCO, WWD, DMVDC checkpoints) or any other files

---

## 4. Correctness Review

### Per-file verification:

**File: orchestration/templates/checkpoints.md (Lines 450-543)**

- **Lines 453**: Header updated with round counts ✓
- **Lines 467-479**: Individual reports section has both Round 1 and Round 2+ subsections with correct file counts (4 and 2 respectively) ✓
- **Lines 481-494**: Check 0 has both "Round 1 — verify exactly 4 report files:" and "Round 2+ — verify exactly 2 report files:" blocks ✓
- **Lines 496-500**: Check 1 updated to mention both round counts in first line and split math format with "Round 1:" and "Round 2+:" ✓
- **Lines 502-541**: Checks 2-7 and Verdict remain unchanged as required ✓

### Acceptance Criteria Verification:

1. **CCB header line contains "4 reports in round 1, 2 in round 2+"**
   - ✓ Line 453: `**When**: ... — 4 reports in round 1, 2 in round 2+)`

2. **Individual reports section has "Round 1:" (4 files) and "Round 2+:" (2 files) subsections**
   - ✓ Lines 469-473: Round 1 with clarity, edge-cases, correctness, excellence
   - ✓ Lines 475-477: Round 2+ with correctness, edge-cases

3. **Document count says "round 1: 5 total = 4 reports + consolidated; round 2+: 3 total = 2 reports + consolidated"**
   - ✓ Line 479: `Read all documents (round 1: 5 total = 4 reports + consolidated; round 2+: 3 total = 2 reports + consolidated)`

4. **Check 0 has "Round 1" — verify exactly 4 report files:" and "Round 2+" — verify exactly 2 report files:"**
   - ✓ Lines 484-488: Round 1 block with 4 files
   - ✓ Lines 490-492: Round 2+ block with 2 files

5. **Check 1 math format includes both "Round 1:" and "Round 2+:" counting patterns in the "Report the math" line**
   - ✓ Line 500: Math includes both patterns: `"Round 1: Clarity: N, Edge Cases: N, Correctness: N, Excellence: N = TOTAL total. Round 2+: Correctness: N, Edge Cases: N = TOTAL total. ..."`

### Cross-file consistency:
- Round counts (4 in round 1, 2 in round 2+) match reviews.md team composition and big-head-skeleton.md examples
- Format matches the pattern established in reviews.md Round-Aware Review Protocol section
- File list format is consistent with the specifications in docs/plans/2026-02-19-review-loop-convergence.md Task 10
- The round-aware pattern enables Pest Control to correctly adapt its verification based on the review round number provided by the Queen

### Assumptions audit:
- **Assumption 1**: The Queen will always include the review round number in the Pest Control brief.
  - Status: Documented in line 467; consistent with RULES.md Step 3b which says round number comes from session state
- **Assumption 2**: Pest Control will read the round number and select the appropriate verification block.
  - Status: Clear from context; agent has round number in brief
- **Assumption 3**: Timestamps follow the `{timestamp}` placeholder format throughout the codebase.
  - Status: Confirmed by existing usage in same file and other templates

---

## 5. Build/Test Validation

**Markdown syntax validation**:
- All files remain valid Markdown
- Heading structure preserved (## Check 0, ## Check 1, etc. remain at correct nesting level)
- Code block formatting maintained for bash examples
- Bullet lists properly formatted with correct indentation

**Logical validation**:
- Round 1 always expects 4 report files; round 2+ always expects 2
- File paths are correct (clarity, edge-cases, correctness, excellence in round 1; correctness, edge-cases in round 2+)
- Document totals are correct: 5 in round 1 (4 reports + 1 consolidated), 3 in round 2+ (2 reports + 1 consolidated)
- Check 0 and Check 1 properly reference the expected count for each round
- The changes enable Pest Control to perform correct verification without hardcoding round assumptions

**Integration points**:
- Pest Control receives review round number in its brief (per RULES.md Step 3b)
- Big Head fills in the consolidated summary path and report filenames
- Queen provides round number to Pest Control via the consolidation prompt
- No changes to Pest Control's actual verification logic needed; it simply reads different file counts based on round

---

## 6. Acceptance Criteria Checklist

- [x] **Criterion 1**: CCB header line contains "4 reports in round 1, 2 in round 2+"
  - **PASS**: Line 453 explicitly states this in the "When" condition

- [x] **Criterion 2**: Individual reports section has "Round 1:" (4 files) and "Round 2+:" (2 files) subsections
  - **PASS**: Lines 469-477 show both subsections with correct file counts

- [x] **Criterion 3**: Document count says "round 1: 5 total = 4 reports + consolidated; round 2+: 3 total = 2 reports + consolidated"
  - **PASS**: Line 479 includes the exact wording specified

- [x] **Criterion 4**: Check 0 has "**Round 1** — verify exactly 4 report files:" and "**Round 2+** — verify exactly 2 report files:"
  - **PASS**: Lines 484-494 show both round blocks with proper formatting

- [x] **Criterion 5**: Check 1 math format includes both "Round 1:" and "Round 2+:" counting patterns in the "Report the math" line
  - **PASS**: Line 500 includes both round patterns in the math reporting instruction

---

## Implementation Artifacts

**File modified**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md`

**Commit hash**: (to be recorded after: git add orchestration/templates/checkpoints.md && git commit -m "fix: update CCB checkpoint for round-aware report counts (ant-farm-ha7a.10)")

**Lines changed**:
- Line 453: CCB header
- Lines 467-479: Individual reports list and document count
- Lines 481-494: Check 0: Report Existence Verification
- Lines 496-500: Check 1: Finding Count Reconciliation

**Total lines affected**: 5 distinct sections, approximately 47 lines changed (including added subsections and restructuring)

---

## Notes and Observations

1. **Design clarity**: The explicit "Round 1:" and "Round 2+:" subsection headers make the template self-documenting. Future readers immediately understand what applies when.

2. **Zero breaking changes**: These updates only add clarification; they do not remove or break existing functionality. Round 1 behavior is unchanged.

3. **Termination compatibility**: These changes support the termination rule from reviews.md — when a round produces zero P1/P2 findings, CCB verifies the consolidation and the loop ends.

4. **No Pantry changes needed**: Unlike some other round-aware updates, this checkpoint doesn't require the Pantry to preprocess the brief. The template is complete as-is.

5. **Ready for test**: A future test round can verify that Pest Control correctly identifies expected file counts based on the review round number provided in its brief.

---

## Related Issues and Adjacent Work

**No adjacent issues filed** — the task scope was clear and bounded. CCB now correctly handles both round 1 and round 2+ report counts.

**Future work**: If additional round modes (round 3, round 4, etc.) are added, this template will scale without modification — agents will simply match their round number against the appropriate labeled block.
