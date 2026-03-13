# Task Brief: ant-farm-e9k
**Task**: AGG-035: Add remediation path for missing Nitpicker reports
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-405acc/summaries/e9k.md

## Context
- **Affected files**:
  - `orchestration/templates/reviews.md:L321-L480` — Big Head Consolidation Protocol section; contains prerequisite gate logic that needs a remediation step for missing reports
- **Root cause**: reviews.md instructs Big Head not to proceed until all 4 reports are present (Step 0, lines 337-353) but never says what to DO about a missing report. No messaging, no error return, no timeout specified. Big Head could wait indefinitely.
- **Expected behavior**: Big Head should return an error to the Queen listing missing reports and requesting re-spawn rather than waiting indefinitely.
- **Acceptance criteria**:
  1. reviews.md Big Head section includes a remediation step for missing reports
  2. The step specifies: return error to Queen, list missing reports, request re-spawn
  3. A timeout or maximum wait is specified before triggering the remediation path

## Scope Boundaries
Read ONLY:
- `orchestration/templates/reviews.md:L321-L480` (Big Head Consolidation Protocol section)
- `orchestration/templates/big-head-skeleton.md:L47-L71` (Big Head template for cross-reference)
- `orchestration/templates/checkpoints.md:L444-L546` (CCB section — read only, for understanding the downstream audit)

Do NOT edit:
- `orchestration/templates/big-head-skeleton.md` (read-only cross-reference)
- `orchestration/templates/checkpoints.md` (read-only cross-reference)
- `orchestration/templates/dirt-pusher-skeleton.md` (unrelated)
- `orchestration/templates/nitpicker-skeleton.md` (unrelated)
- `orchestration/templates/pantry.md` (unrelated)
- Any section of reviews.md outside the Big Head Consolidation Protocol (lines 321-480)

## Focus
Your task is ONLY to add a remediation path (error return, missing report listing, re-spawn request, and timeout specification) to the Big Head Consolidation Protocol's Step 0 in reviews.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
