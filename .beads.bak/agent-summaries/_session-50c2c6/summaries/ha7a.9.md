# Summary: ant-farm-ha7a.9

**Task**: Update pantry review mode for round-aware brief composition
**File modified**: `orchestration/templates/pantry.md` (Section 2: Review Mode, L199-281)

---

## 1. Approaches Considered

**Approach A: In-place sentence expansion**
Expand existing sentences inline (e.g., "Compose 4 or 2 review briefs depending on round"). Pro: minimal diff. Con: produces run-on, ambiguous instructions that are harder for an AI agent to parse at runtime, especially when branching on a condition embedded in prose.

**Approach B: Structured `**Round 1** / **Round 2+**` branching blocks (selected)**
Replace each relevant sentence or list with clearly labeled bold-header pairs. This is what the implementation plan prescribes and matches the established style used in reviews.md's Team Setup section and big-head-skeleton.md's TeamCreate examples. Pro: unambiguous, scannable, consistent with the existing pattern in the codebase. Con: adds a few extra lines per section.

**Approach C: Conditional-note footnotes**
Keep the main body written for round 1, add "Round 2+ exception:" callout blocks at the bottom of each step. Pro: preserves current readability for round 1. Con: an AI agent reading linearly may take action before reaching the footnote, producing incorrect round 2+ behavior. Risky for runtime correctness.

**Approach D: New parallel subsection headers per step**
Restructure each step into `#### Step N (Round 1)` and `#### Step N (Round 2+)` subsections. Pro: completely unambiguous. Con: significant restructuring changes section numbering and the template's established heading hierarchy, adds cognitive load when reading, and goes beyond the implementation plan's specified changes.

---

## 2. Selected Approach with Rationale

**Approach B** was selected. The implementation plan (Task 9 of `docs/plans/2026-02-19-review-loop-convergence.md`) explicitly prescribes bold `**Round 1**:` / `**Round 2+**:` branching blocks for all 6 sections. This pattern is already established in reviews.md (Team Setup section) and big-head-skeleton.md (TeamCreate examples) for the same feature set, so the Pantry agent's runtime parsing follows a consistent structure across all orchestration templates.

---

## 3. Implementation Description

Six targeted edits were made to `orchestration/templates/pantry.md`, all within Section 2: Review Mode (L199-281). Section 1 (Implementation Mode) and Section 3 (Error Handling) were not touched.

**Edit 1 — Input spec (L201)**: Appended `review round number (1, 2, 3, ...)` to the end of the existing comma-separated input list.

**Edit 2 — Brief composition (L229-237)**: Replaced the `Compose 4 review briefs, each containing:` paragraph with a `**Round-aware composition:**` block containing `**Round 1**` and `**Round 2+**` bullets, followed by `Each brief contains:` as the header for the existing bullet list. The Round 2+ entry references the "Round 2+ Reviewer Instructions" section of reviews.md for the out-of-scope finding bar.

**Edit 3 — Files-to-write (L239-243)**: Replaced the flat 4-item list under `Files to write:` with a `**Round 1**:` group (4 files) and `**Round 2+**:` group (2 files: edge-cases and correctness only).

**Edit 4 — Step 4 Big Head brief (L249-254)**: Added three new bullet items to the existing list: round number, round-conditional report paths, and Round 2+ P3 auto-filing instructions. Added a `**Polling loop adaptation**` paragraph specifying that the Pantry adapts the Step 0a polling loop from reviews.md per round (4 checks in round 1, 2 checks in round 2+).

**Edit 5 — Step 5 Previews (L258-263)**: Restructured the 2-item list into a 3-item list. Item 2 now shows `**Round 1**:` (4 reviews) and `**Round 2+**:` (2 reviews) as adjacent lines. Item 3 preserves the per-review steps (a-d) and adds `{REVIEW_ROUND}` as an explicitly named placeholder to fill in step b.

**Edit 6 — Step 6 Return table (L268-281)**: Replaced the single table inside a fenced block with two labeled tables: `**Round 1 return table:**` (4 data rows: clarity, edge-cases, correctness, excellence) and `**Round 2+ return table:**` (2 data rows: correctness, edge-cases). Both tables include a `Big Head consolidation data:` footer line with `(includes round number)` appended.

---

## 4. Correctness Review

**File: `orchestration/templates/pantry.md`**

- Section 1 (L15-196): Untouched. Confirmed no edits leaked into Implementation Mode.
- Section 2 separator (`---` at L197): Intact.
- Section 2 header and input spec (L199-201): Input spec ends with `review round number (1, 2, 3, ...)`. Correct.
- Step 3 guard block (L216-227): Untouched. SUBSTANCE FAILURE guard preserved.
- Step 3 composition rules (L229-241): `**Round-aware composition:**` block present with `**Round 1**` and `**Round 2+**` bullets. `Each brief contains:` header present, followed by unchanged bullet list.
- Step 3 files-to-write (L243-251): `**Round 1**:` group has 4 indented files; `**Round 2+**:` group has 2 indented files (edge-cases, correctness).
- Step 4 Big Head brief (L253-267): Existing 5 bullets preserved; 3 new bullets added. `**Polling loop adaptation**` paragraph present. "Review round number" mentioned. "P3 auto-filing" mentioned.
- Step 5 previews (L269-280): 3-item list structure correct. `{REVIEW_ROUND}` present in step 3b. Round-conditional count explicit in step 2.
- Step 6 return table (L282-308): `**Round 1 return table:**` header present with 4 data rows. `**Round 2+ return table:**` header present with 2 data rows. Both have footer lines including `(includes round number)`.
- Section 3 (L312-315): Untouched. Error handling intact.

**Assumptions audit**: No assumptions were made that deviate from the implementation plan. The "All 4 report paths" bullet in Step 4 was retained as-is (it predates this task and applies to the round 1 case); the new bullets clarify the round-conditional behavior without removing the original bullet, which is acceptable because the plan says "add these items."

---

## 5. Build/Test Validation

These are markdown templates read by AI agents at runtime, not executed code. No build or test suite applies. Validation consists of:

- Read-back of the modified section (L197-315) confirmed all 6 edits are present and structurally correct.
- Checked that Section 1, the Section 1/2 separator, and Section 3 are unchanged.
- Checked that `{REVIEW_ROUND}` placeholder is spelled correctly and consistently with the plan specification.
- Checked that "**Round 1 return table:**" and "**Round 2+ return table:**" headings are correctly bolded and labeled.
- Verified that the Round 2+ files-to-write list matches the plan (edge-cases first, then correctness — matching the plan's L655-656 ordering).

---

## 6. Acceptance Criteria Checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Input spec includes "review round number (1, 2, 3, ...)" | PASS |
| 2 | Brief composition has `**Round 1**: Compose 4 review briefs` and `**Round 2+**: Compose 2 review briefs` | PASS |
| 3 | Files-to-write section shows "**Round 1**:" (4 files) and "**Round 2+**:" (2 files) | PASS |
| 4 | Step 4 mentions "Review round number", "P3 auto-filing", and "**Polling loop adaptation**" | PASS |
| 5 | Step 5 mentions `{REVIEW_ROUND}` placeholder | PASS |
| 6 | Step 6 has "**Round 1 return table:**" (4 data rows) and "**Round 2+ return table:**" (2 data rows) | PASS |

All 6 acceptance criteria: PASS.

---

## Commit

To be recorded after `git commit` completes.
