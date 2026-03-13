Execute task for ant-farm-asdl.3.

Step 0: Read your task context from .beads/agent-summaries/_session-0ffcdc51/prompts/task-asdl3.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-asdl.3` + `bd update ant-farm-asdl.3 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-asdl.3)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-0ffcdc51/summaries/asdl3.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-asdl.3`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

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
