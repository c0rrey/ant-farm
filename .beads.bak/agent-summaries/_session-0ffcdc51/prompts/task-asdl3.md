# Task Brief: ant-farm-asdl.3
**Task**: Update agents/big-head.md with dedup instruction and --body-file reference
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-0ffcdc51/summaries/asdl3.md

## Context
- **Affected files**: agents/big-head.md:L22-23 -- Replace step 6 with two new steps (dedup + body-file filing), renumber step 7 to step 8
- **Root cause**: The Big Head agent definition at agents/big-head.md:L22 has prose saying to include descriptions but provides no concrete command example. Agents follow concrete examples over prose, so the instruction "File issues via `bd create` with: title, description..." is ignored in practice because no --body-file or structured template is shown.
- **Expected behavior**: Step 6 should be a concrete dedup instruction referencing 'bd list --status=open'. Step 7 should reference 'bd create --body-file'. Old step 7 (write consolidated report) should become step 8. Steps must be numbered 1-8 sequentially.
- **Acceptance criteria**:
  1. agents/big-head.md contains a dedup instruction referencing 'bd list --status=open' before the filing step
  2. agents/big-head.md references '--body-file' (not bare 'bd create') in the filing instruction
  3. Steps in the 'When consolidating:' list are sequentially numbered 1-8 with no gaps
  4. Old step 7 ('Write the consolidated report') is renumbered to step 8 with content unchanged

## Scope Boundaries
Read ONLY: agents/big-head.md:L1-36 (full file), orchestration/templates/big-head-skeleton.md (read committed version for canonical pattern reference)
Do NOT edit: orchestration/templates/big-head-skeleton.md, orchestration/templates/reviews.md, orchestration/templates/pantry.md, orchestration/templates/implementation.md, orchestration/templates/dirt-pusher-skeleton.md, orchestration/templates/nitpicker-skeleton.md, or any other file

## Focus
Your task is ONLY to update the step list in agents/big-head.md:L22-23 to add dedup and --body-file instructions and renumber steps.
Do NOT fix adjacent issues you notice in other parts of the file or in other files.

## Canonical Pattern Reference
Before implementing, read the committed version of orchestration/templates/big-head-skeleton.md (after ant-farm-asdl.1's commit) to see the canonical pattern for cross-session dedup and --body-file usage. The agent definition should reference this pattern concisely. The skeleton is the authoritative source; your changes should be consistent with it.

## Additional Instructions
Ensure any beads created by Big Head have quality descriptions -- not just a title, but a meaningful description explaining what the issue is and why it matters. The --body-file reference you add must make it clear that structured descriptions are required, not optional.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
