Execute task for ant-farm-asdl.4.

Step 0: Read your task context from .beads/agent-summaries/_session-0ffcdc51/prompts/task-asdl4.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-asdl.4` + `bd update ant-farm-asdl.4 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-asdl.4)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-0ffcdc51/summaries/asdl4.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-asdl.4`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-asdl.4
**Task**: Update deprecated pantry.md Section 2 bead filing references
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-0ffcdc51/summaries/asdl4.md

## Context
- **Affected files**: orchestration/templates/pantry.md:L318-319 -- Replace bare bd create command with --body-file pattern and dedup instruction
- **Root cause**: The Pantry template has bead filing instructions in deprecated Section 2 at lines 318-319 that use bare `bd create --type=bug --priority=<combined-priority> --title="<root cause title>"` without --body-file. While Section 2 is deprecated, the instructions should be updated for consistency so that any reader or future reactivation uses the correct pattern.
- **Expected behavior**: Lines 318-319 should reference the canonical --body-file pattern from big-head-skeleton.md, mention the 5 required description fields, and include the dedup instruction.
- **Acceptance criteria**:
  1. Lines 318-319 of pantry.md no longer contain a bare bd create --title command
  2. The replacement text references big-head-skeleton.md as the canonical source for the --body-file pattern
  3. The replacement text mentions the 5 required description fields (Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria)
  4. The replacement text includes the dedup instruction (bd list --status=open)

## Scope Boundaries
Read ONLY: orchestration/templates/pantry.md:L310-325 (surrounding context of the affected lines), orchestration/templates/big-head-skeleton.md (read committed version for canonical pattern reference)
Do NOT edit: orchestration/templates/big-head-skeleton.md, orchestration/templates/reviews.md, agents/big-head.md, orchestration/templates/implementation.md, orchestration/templates/dirt-pusher-skeleton.md, orchestration/templates/nitpicker-skeleton.md, or any other file

## Focus
Your task is ONLY to update the bead filing instructions at pantry.md:L318-319 to reference --body-file and the canonical pattern.
Do NOT fix adjacent issues you notice in other parts of pantry.md or in other files. Note that Section 2 is deprecated -- keep the deprecation notice intact and make minimal changes.

## Canonical Pattern Reference
Before implementing, read the committed version of orchestration/templates/big-head-skeleton.md (after ant-farm-asdl.1's commit) to see the canonical pattern for --body-file description templates and cross-session dedup. Reference that pattern rather than duplicating it. The skeleton is the authoritative source; your changes should point to it.

## Additional Instructions
Ensure any beads created by Big Head have quality descriptions -- not just a title, but a meaningful description explaining what the issue is and why it matters. Even in deprecated code, the --body-file pattern should make it clear that structured descriptions with the 5 required fields are mandatory.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
