# Task Summary: ant-farm-ha7a.3

**Task**: Update Big Head verification and summary for round-aware report counts
**File modified**: `orchestration/templates/reviews.md`
**Status**: Complete

---

## 1. Approaches Considered

### Approach A: Inline conditional prose with no code changes (documentation-only)

Add a prose paragraph before the bash block explaining that in round 2+ only 2 reports are needed, leaving the bash blocks and polling loop unchanged. Readers would have to mentally filter the code based on prose context.

**Tradeoff**: Low code-change risk, but creates an inconsistency where the explanatory text contradicts the literal bash commands. Big Head would still see a 4-variable poll loop when operating in round 2+, making the template actively misleading rather than informative.

### Approach B: Duplicate entire Step 0 and Step 0a sections (one per round)

Create separate `### Step 0 (Round 1)` and `### Step 0 (Round 2+)` heading blocks with full content in each. No conditional markers needed.

**Tradeoff**: Eliminates conditional logic from the template, making each round self-contained. However, it doubles the maintenance surface — any future change to the polling logic must be applied in two places. Also increases document length significantly and complicates navigation.

### Approach C: Round-aware blocks within existing sections with `<IF ROUND 1>` markers (selected)

Keep the existing section structure. In Step 0, replace the single bash block with two clearly labeled bash blocks (Round 1 and Round 2+). In Step 0a, restructure the polling loop to separate always-expected checks from round-1-only checks using `# <IF ROUND 1>` / `# </IF ROUND 1>` comment markers. Add a Pantry responsibility note explaining how the Pantry concretizes the template per round. In Step 3, replace the hardcoded reviewer list and 4-row table with round-aware placeholders.

**Tradeoff**: Single maintenance point for each section. Conditional markers are explicit and Pantry-actionable. Matches the implementation plan specification exactly. Requires the Pantry to correctly strip the `<IF ROUND 1>` block in round 2+ briefs, which is documented in the responsibility note.

### Approach D: Parameterized template variables (e.g., `${EXPECTED_REPORTS}`)

Replace all hardcoded counts and lists with variable placeholders that Pantry substitutes at brief-composition time. No inline conditional markers — instead, Pantry receives a separate round-config input.

**Tradeoff**: More abstract and tooling-friendly if Pantry were a script. However, the Pantry is an LLM agent reading a template; variable placeholders without conditional logic would require the Pantry to know the substitution rules separately, adding cognitive load. The `<IF ROUND 1>` marker approach is more self-documenting for an LLM consumer.

### Approach E: Move round-awareness entirely into big-head-skeleton.md

Keep reviews.md unchanged; update only the skeleton that Big Head actually reads at runtime to contain the round-aware logic.

**Tradeoff**: The skeleton defers to reviews.md as the authoritative source (stated in Step 0a's existing authoritative-source blockquote). Putting round logic only in the skeleton would violate that authoritativeness contract and leave reviews.md as a misleading reference for anyone reading the template directly.

---

## 2. Selected Approach

**Approach C** — Round-aware blocks within existing sections with `<IF ROUND 1>` markers.

**Rationale**: This approach satisfies all five acceptance criteria verbatim, matches the implementation plan specification in `docs/plans/2026-02-19-review-loop-convergence.md:L174-297`, maintains a single section per concern, and makes Pantry's adaptation responsibility explicit in the template itself. The `<IF ROUND 1>` markers are the exact convention specified by the implementation plan, and the Pantry responsibility note closes the loop on how the template is operationalized.

---

## 3. Implementation Description

Three targeted edits to `orchestration/templates/reviews.md`, all within the Big Head Consolidation Protocol section:

**Edit 1 — Step 0 (Verify All Reports Exist)**

Replaced the single introductory sentence and single bash block with:
- A new introductory sentence: "The number of expected reports depends on the review round:"
- A `**Round 1**` labeled bash block listing all 4 report types
- A `**Round 2+**` labeled bash block listing only correctness and edge-cases
- Updated the "All X files MUST exist" bullet to say "All expected files MUST exist"

**Edit 2 — Step 0a (Remediation Path polling loop)**

Replaced the original 4-variable polling loop bash block with a restructured version that:
- Adds an explanatory comment about round-awareness at the top
- Introduces an `ALL_FOUND=1` accumulator variable
- Separates always-expected checks (correctness, edge-cases) from round-1-only checks (clarity, excellence)
- Wraps the round-1-only checks with `# <IF ROUND 1>` and `# </IF ROUND 1>` comment markers
- Updates the timeout echo message to say "Not all expected reports" (removing the hardcoded "4")
- Adds a `**Pantry responsibility**` paragraph immediately after the code block, explaining how the Pantry concretizes the template per round

**Edit 3 — Step 3 (Write Consolidated Summary template)**

Within the markdown template block:
- Replaced `**Reviews completed**: Clarity, Edge Cases, Correctness, Excellence` with `**Reviews completed**: <Round 1: Clarity, Edge Cases, Correctness, Excellence | Round 2+: Correctness, Edge Cases>`
- Removed the `**Reports verified**: ...` line (replaced by the Read Confirmation block below)
- Replaced `**All 4 reports read and processed by Big Head consolidation:**` with `**Reports read and processed by Big Head consolidation:**`
- Added two prose lines: "Round 1: 4 reports (clarity, edge-cases, correctness, excellence)" and "Round 2+: 2 reports (correctness, edge-cases)"
- Replaced the 4 fixed table rows with a single `<for each report in this round>` template row

---

## 4. Correctness Review

### File: `orchestration/templates/reviews.md`

**Step 0 section review:**
- The introductory sentence now explicitly states round-dependence. Matches acceptance criterion 1.
- The `**Round 1**` bash block is identical to the original (all 4 report types listed). No regression.
- The `**Round 2+**` bash block correctly lists only correctness and edge-cases. Matches the plan.
- "All expected files MUST exist" is a clean generalization of the original "All 4 files MUST exist."
- The three remediation bullets are preserved verbatim, updated only to say "all expected reports."

**Step 0a section review:**
- The `**Timeout specification**` paragraph still says "all 4 reports" in its preamble — this is a pre-existing phrase in the prose above the bash block that is technically outside the changed bash block. Per scope rules this is an adjacent issue, not fixed here. Documented below.
- The polling loop restructuring is logically equivalent to the original for round 1 (all 4 variables are checked; `ALL_FOUND` goes to 0 if any are missing; the `if [ $ALL_FOUND -eq 1 ]` check replaces the chained `&&` check).
- For round 2+, the Pantry omits the `<IF ROUND 1>` block, leaving only correctness and edge-cases checks. Logic is correct.
- The `# </IF ROUND 1>` closing marker is present. Matches acceptance criterion 2.
- The `**Pantry responsibility**` note is present immediately after the bash code block fence. Matches acceptance criterion 3.
- The error return block and post-error prose are unchanged (not in scope).

**Step 3 section review:**
- `**Reviews completed**` line now uses `<Round 1: ... | Round 2+: ...>` format. Matches acceptance criterion 4.
- The `**Reports verified**` line (which was a hard-coded 4-item list) has been removed; it was superseded by the Read Confirmation block.
- The Read Confirmation block heading is updated to remove the "All 4" hardcode.
- The two prose lines correctly enumerate report counts per round.
- The table now contains a single `<for each report in this round>` row. Matches acceptance criterion 5.
- The `**Total findings from all reports**: <N>` line is preserved after the table.

**Adjacent issues noted (not fixed per scope):**
- `### Verification Pipeline Design Rationale` (L396-404): Still says "ensures all 4 expected reports exist" in the Big Head Step 0 description. This is adjacent context prose, not in scope.
- `**Timeout specification:**` preamble in Step 0a (L437): Still says "all 4 reports to appear." This is prose above the bash block, not named in the acceptance criteria. Adjacent issue.
- The error return markdown template (L494-524) still references "all 4 Nitpicker team members" and lists 4 report types. Not in scope for this task.

**Assumptions audit:**
- Assumption: "Round 2+" in the plan means all rounds after round 1 consistently use exactly 2 reports (correctness + edge-cases). Confirmed by implementation plan L197-203.
- Assumption: The `<IF ROUND 1>` marker convention is a Pantry-processed template convention, not shell syntax. Confirmed by implementation plan and Pantry responsibility note.
- Assumption: Removing the `**Reports verified**` line from Step 3 is correct because its content has been subsumed into the restructured Read Confirmation block. Verified: the plan's replacement block does not include a `**Reports verified**` line.

---

## 5. Build/Test Validation

This task modifies documentation templates only. There are no compilation steps, unit tests, or linting pipelines applicable to Markdown template files in this project.

Manual validation performed:
- Re-read the entire changed region (Step 0 through Step 3) after each edit to confirm no surrounding content was disturbed.
- Confirmed that Step 1, Step 2, Step 4, and the error return block are unchanged.
- Confirmed that the bash code block fence markers are properly closed in all three edits.
- Confirmed that the Markdown table structure in Step 3 is valid (header row + separator row + one data row).

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Step 0 text says "The number of expected reports depends on the review round" with separate "**Round 1**" and "**Round 2+**" bash blocks | PASS |
| 2 | Step 0a polling loop contains `# <IF ROUND 1>` and `# </IF ROUND 1>` comment markers wrapping the clarity/excellence variable checks | PASS |
| 3 | A `**Pantry responsibility**` note follows the Step 0a code block | PASS |
| 4 | Consolidated summary reviews-completed line shows `<Round 1: ... | Round 2+: ...>` format (not hardcoded 4 reviewers) | PASS |
| 5 | Read Confirmation table uses `<for each report in this round>` (not fixed 4 rows) | PASS |

All 5 acceptance criteria: PASS.

---

## Commit

Committed with: `feat: update Big Head verification and summary for round-aware report counts (ant-farm-ha7a.3)`

Commit hash: (recorded after commit executes)
