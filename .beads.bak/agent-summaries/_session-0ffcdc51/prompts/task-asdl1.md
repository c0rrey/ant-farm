# Task Brief: ant-farm-asdl.1
**Task**: Add cross-session dedup step and description template to big-head-skeleton.md
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-0ffcdc51/summaries/asdl1.md

## Context
- **Affected files**: orchestration/templates/big-head-skeleton.md:L90,L95 (bare `bd create` commands without `--description`/`--body-file`), L105-125 (insertion zone for cross-session dedup step and updated output requirements -- currently beyond EOF at L104, so these are appended lines)
- **Root cause**: The Big Head skeleton template has bare `bd create` commands without `--description`/`--body-file`, and no step to check existing beads before filing. This causes beads with title-only descriptions and cross-session duplicate filings.
- **Expected behavior**: Every `bd create` command should use `--body-file` with a structured description template (Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria). A cross-session dedup step should query existing beads before filing.
- **Acceptance criteria**:
  1. No bare `bd create` command remains in big-head-skeleton.md -- every instance includes `--body-file`
  2. The description template in the PASS branch contains all 5 sections: Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria
  3. A cross-session dedup step exists before the write-summary step, containing `bd list --status=open` and `bd search`
  4. The output requirements list includes "Cross-session dedup log"
  5. Step numbers are sequential with no gaps or duplicates, and all internal cross-references resolve correctly

## Scope Boundaries
Read ONLY: orchestration/templates/big-head-skeleton.md:L1-104 (full file)
Do NOT edit: orchestration/templates/implementation.md, orchestration/templates/dirt-pusher-skeleton.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/reviews.md, orchestration/templates/pantry.md, or any other template file

## Focus
Your task is ONLY to add a cross-session dedup step and description template to big-head-skeleton.md.
Do NOT fix adjacent issues you notice in other template files.

## Additional Instructions
Ensure any beads created by Big Head have quality descriptions -- not just a title, but a meaningful description explaining what the issue is and why it matters. The description template you add must enforce this by requiring structured content (Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria) rather than leaving description quality to chance.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
