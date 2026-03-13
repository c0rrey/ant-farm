Execute task for ant-farm-99o.

Step 0: Read your task context from .beads/agent-summaries/_session-8ae30b/prompts/task-99o.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-99o` + `bd update ant-farm-99o --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-99o)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-8ae30b/summaries/99o.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-99o`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-99o
**Task**: Pantry told to read implementation.md but no explanation of what to extract
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8ae30b/summaries/99o.md

## Context
- **Affected files**: orchestration/templates/pantry.md:L20-23 (Section 1, Step 1 "Read Templates")
- **Root cause**: pantry.md Section 1 Step 1 tells the Pantry to read `implementation.md` but provides zero guidance on what data to extract or how the content shapes the Pantry's output. The instruction reads: "Read this file (you absorb the cost, not the Queen): ~/.claude/orchestration/templates/implementation.md". A fresh Pantry agent reading only pantry.md would not know whether this read is informational (absorb the template structure as background policy) or extractive (pull specific fields to use in task brief composition). In practice, the Pantry uses implementation.md as reference context for understanding the Summary Doc Sections format and the 6-step dirt-pusher workflow, but this purpose is never stated.
- **Expected behavior**: pantry.md Step 1 should clarify the purpose of reading implementation.md — either explicitly stating what fields/data to extract, or noting it is informational context that informs task brief composition (so the Pantry understands the dirt-pusher workflow it is composing briefs for).
- **Acceptance criteria**:
  1. pantry.md Step 1 explains why implementation.md is read and what to do with the information
  2. A fresh Pantry agent reading only pantry.md would know exactly how implementation.md shapes its output

## Scope Boundaries
Read ONLY: orchestration/templates/pantry.md:L20-23, ~/.claude/orchestration/templates/implementation.md (full file, for understanding what it contains)
Do NOT edit: Any file other than orchestration/templates/pantry.md. Do NOT edit Section 2 (Review Mode) or Section 3 (Error Handling). Do NOT edit any other template files.

## Focus
Your task is ONLY to clarify Step 1 of Section 1 in pantry.md so the purpose of reading implementation.md is explicit.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
