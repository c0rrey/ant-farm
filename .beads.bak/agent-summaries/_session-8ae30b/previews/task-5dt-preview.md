Execute bug for ant-farm-5dt.

Step 0: Read your task context from .beads/agent-summaries/_session-8ae30b/prompts/task-5dt.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-5dt` + `bd update ant-farm-5dt --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-5dt)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-8ae30b/summaries/5dt.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-5dt`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-5dt
**Task**: (BUG) pantry.md Review Mode does not generate Big Head preview file for CCO audit
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8ae30b/summaries/5dt.md

## Context
- **Affected files**: orchestration/templates/pantry.md:L389-400 (Section 2, Step 5 "Write Combined Review Previews")
- **Root cause**: pantry.md Review Mode Step 5 (lines 389-400) creates preview files for the 4 Nitpicker review types by combining nitpicker-skeleton.md with each review data file. However, no preview is generated for Big Head's consolidation prompt. The Big Head consolidation data file is written in Step 4 (lines 297-387), and a big-head-skeleton.md template exists at ~/.claude/orchestration/templates/big-head-skeleton.md, but Step 5 never combines them into a preview file. If CCO is meant to audit all prompts before team creation, the Big Head prompt is excluded from preview-based auditing.
- **Expected behavior**: Either (a) Step 5 generates a Big Head preview by combining big-head-skeleton.md with the Big Head consolidation data file and writing to `{session-dir}/previews/review-big-head-preview.md`, or (b) the exclusion is explicitly documented with rationale explaining why Big Head does not need CCO auditing.
- **Acceptance criteria**:
  1. Either a Big Head preview file is generated in Step 5 (combining big-head-skeleton.md + Big Head consolidation data file), or the exclusion is explicitly documented with rationale in pantry.md

## Scope Boundaries
Read ONLY: orchestration/templates/pantry.md:L297-428 (Section 2 Steps 4-6), ~/.claude/orchestration/templates/big-head-skeleton.md (full file), ~/.claude/orchestration/templates/nitpicker-skeleton.md (full file, for understanding preview pattern)
Do NOT edit: Any file other than orchestration/templates/pantry.md. Do NOT edit Section 1 (Implementation Mode) or Section 3 (Error Handling). Do NOT edit big-head-skeleton.md, nitpicker-skeleton.md, or any other template files.

## Focus
Your task is ONLY to fix the missing Big Head preview generation in pantry.md Review Mode Step 5 (or explicitly document its exclusion with rationale).
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
