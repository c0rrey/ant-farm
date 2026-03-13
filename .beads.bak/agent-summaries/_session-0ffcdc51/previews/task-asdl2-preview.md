Execute task for ant-farm-asdl.2.

Step 0: Read your task context from .beads/agent-summaries/_session-0ffcdc51/prompts/task-asdl2.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-asdl.2` + `bd update ant-farm-asdl.2 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-asdl.2)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-0ffcdc51/summaries/asdl2.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-asdl.2`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-asdl.2
**Task**: Add cross-session dedup and description template to reviews.md Big Head Consolidation Protocol
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-0ffcdc51/summaries/asdl2.md

## Context
- **Affected files**: orchestration/templates/reviews.md:L672-797 -- Insert Step 2.5 dedup section (after line 672), replace bare bd create block (lines 775-779), update P3 auto-filing (lines 793-797)
- **Root cause**: The reviews.md Big Head Consolidation Protocol has bare `bd create` commands (lines 775-779, 793-797) and no cross-session dedup step, mirroring the same issues as big-head-skeleton.md. This produces beads with title-only descriptions and risks filing duplicates of issues already tracked.
- **Expected behavior**: A Step 2.5 "Deduplicate Against Existing Beads" section should exist between Step 2 and Step 3 in the Big Head Consolidation Protocol. All bd create commands should use --body-file with structured descriptions containing the 5 required fields.
- **Acceptance criteria**:
  1. A 'Step 2.5: Deduplicate Against Existing Beads' section exists between Step 2 and Step 3 in the Big Head Consolidation Protocol, containing 'bd list --status=open' and 'bd search'
  2. No bare bd create command remains in the bead filing section (lines 769-800) -- every instance includes --body-file
  3. The description template in the bead filing section contains all 5 sections: Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria
  4. The P3 auto-filing section (lines 793-797) uses --body-file with at minimum Root Cause, Affected Surfaces, and Acceptance Criteria

## Scope Boundaries
Read ONLY: orchestration/templates/reviews.md:L672-797 (Big Head Consolidation Protocol section), orchestration/templates/big-head-skeleton.md (read committed version for canonical pattern reference)
Do NOT edit: orchestration/templates/big-head-skeleton.md, agents/big-head.md, orchestration/templates/pantry.md, orchestration/templates/implementation.md, orchestration/templates/dirt-pusher-skeleton.md, orchestration/templates/nitpicker-skeleton.md, or any other file

## Focus
Your task is ONLY to add a cross-session dedup step and update bd create commands with --body-file in reviews.md lines 672-797.
Do NOT fix adjacent issues you notice in other sections of reviews.md or in other template files.

## Canonical Pattern Reference
Before implementing, read the committed version of orchestration/templates/big-head-skeleton.md (after ant-farm-asdl.1's commit) to see the canonical pattern for cross-session dedup steps and --body-file description templates. Mirror that pattern to reviews.md. The skeleton is the authoritative source; your changes should be consistent with it.

## Additional Instructions
Ensure any beads created by Big Head have quality descriptions -- not just a title, but a meaningful description explaining what the issue is and why it matters. The --body-file pattern you add must enforce this by requiring structured content (Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria) rather than leaving description quality to chance.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
