Execute task for ant-farm-7ob.

Step 0: Read your task context from .beads/agent-summaries/_session-8ae30b/prompts/task-7ob.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-7ob` + `bd update ant-farm-7ob --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-7ob)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-8ae30b/summaries/7ob.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-7ob`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-7ob
**Task**: RULES.md pantry.md section references not explicit
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8ae30b/summaries/7ob.md

## Context
- **Affected files**:
  - `~/.claude/orchestration/RULES.md:L33-34` — Step 2 references "templates/pantry.md" without specifying Section 1
  - `~/.claude/orchestration/RULES.md:L55` — Step 3b references "pantry-review" which uses pantry.md without specifying Section 2
- **Root cause**: pantry-impl.md references "pantry.md, Section 1" and pantry-review.md references "pantry.md, Section 2", but RULES.md Steps 2 and 3b just say "templates/pantry.md" (L34) and "the Pantry (pantry-review)" (L55) without section numbers. This reduces traceability when debugging which section applies to which workflow step.
- **Expected behavior**: RULES.md Steps 2 and 3b include section numbers when referencing pantry.md, matching the explicitness of pantry-impl.md and pantry-review.md.
- **Acceptance criteria**:
  1. RULES.md Steps 2 and 3b reference pantry.md with explicit section numbers (e.g., "pantry.md, Section 1" and "pantry.md, Section 2")
  2. References are consistent with section numbering in pantry.md itself (Section 1 = Implementation Mode, Section 2 = Review Mode)

## Scope Boundaries
Read ONLY:
- `~/.claude/orchestration/RULES.md` (focus on L33-34 Step 2 and L48-62 Step 3b)
- `~/.claude/orchestration/templates/pantry.md` (L12 and L104 for section headings)

Do NOT edit:
- RULES.md Steps 0, 1, 3, 4, 5, 6
- RULES.md Hard Gates, Information Diet, Agent Types, or any section below Concurrency Rules
- pantry.md (read only for reference, do not edit)
- Any files other than RULES.md

## Focus
Your task is ONLY to add explicit section numbers to RULES.md Steps 2 and 3b when referencing pantry.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
