Execute bug for ant-farm-s2g.

Step 0: Read your task context from .beads/agent-summaries/_session-8ae30b/prompts/task-s2g.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-s2g` + `bd update ant-farm-s2g --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-s2g)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-8ae30b/summaries/s2g.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-s2g`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-s2g
**Task**: AGG-017: Remove circular reference in Pantry Big Head data file instructions
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8ae30b/summaries/s2g.md

## Context
- **Affected files**:
  - `~/.claude/orchestration/templates/pantry.md:L137-145` — Section 2 Step 4 instructs Pantry to read reviews.md before composing Big Head data file, creating a circular dependency
  - `~/.claude/orchestration/templates/reviews.md:L320-469` — Big Head Consolidation Protocol section; may cross-reference pantry.md
- **Root cause**: pantry.md Section 2 Step 4 (L139) contains a "See also" directive telling the Pantry to read reviews.md Big Head Consolidation Protocol before composing the Big Head data file. But pantry.md Section 2 IS the review mode instructions, so the Pantry is already reading pantry.md, which says "read reviews.md", which may reference pantry.md. This circular dependency means a cold Pantry agent cannot compose the Big Head data file from pantry.md alone.
- **Expected behavior**: pantry.md Section 2 is self-contained for Big Head data file composition with no circular references. A cold Pantry agent can compose the Big Head data file by reading only pantry.md.
- **Acceptance criteria**:
  1. pantry.md Section 2 is self-contained for Big Head data file composition (no circular refs)
  2. If reviews.md is still referenced, the reference specifies exactly which section to read and why
  3. A cold Pantry agent can compose the Big Head data file by reading only pantry.md

## Scope Boundaries
Read ONLY:
- `~/.claude/orchestration/templates/pantry.md` (focus on L137-145, Section 2 Step 4)
- `~/.claude/orchestration/templates/reviews.md` (focus on L320-469, Big Head Consolidation Protocol)

Do NOT edit:
- pantry.md Section 1 (Implementation Mode, L12-80)
- pantry.md Section 3 (Error Handling, L176-180)
- reviews.md Reviews 1-4 definitions (L86-243)
- reviews.md Nitpicker Report Format (L245-318)
- Any files other than pantry.md and reviews.md

## Focus
Your task is ONLY to remove the circular reference in pantry.md Section 2 Step 4 Big Head data file instructions so that a cold Pantry agent can compose the Big Head data file without circular dependencies.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
