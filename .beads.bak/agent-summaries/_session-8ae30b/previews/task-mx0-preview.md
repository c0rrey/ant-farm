Execute bug for ant-farm-mx0.

Step 0: Read your task context from .beads/agent-summaries/_session-8ae30b/prompts/task-mx0.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-mx0` + `bd update ant-farm-mx0 --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-mx0)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-8ae30b/summaries/mx0.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-mx0`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-mx0
**Task**: (BUG) prompts/ directory creation is redundant between RULES.md Step 0 and pantry.md Review Mode
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8ae30b/summaries/mx0.md

## Context
- **Affected files**:
  - `~/.claude/orchestration/RULES.md:L122` — mkdir -p includes prompts/ via brace expansion: `mkdir -p ${SESSION_DIR}/{task-metadata,previews,prompts,pc,summaries}`
  - `~/.claude/orchestration/templates/pantry.md:L119` — Review Mode Step 3 says "Create the prompts directory if needed: `{session-dir}/prompts/`"
- **Root cause**: RULES.md Step 0 (L122) creates the prompts/ directory via brace expansion in mkdir. pantry.md Review Mode Step 3 (L119) also says "Create the prompts directory if needed." The redundancy is harmless (mkdir -p is idempotent) but creates confusion about who owns directory creation.
- **Expected behavior**: The intentional redundancy is documented with a comment in pantry.md noting that the Queen pre-creates this directory at Step 0, but create if needed as a safety net.
- **Acceptance criteria**:
  1. pantry.md contains a comment clarifying the intentional redundancy: "The Queen pre-creates this directory at Step 0, but create if needed as a safety net"

## Scope Boundaries
Read ONLY:
- `~/.claude/orchestration/templates/pantry.md` (focus on L119, Review Mode Step 3)
- `~/.claude/orchestration/RULES.md` (focus on L122, Session Directory section)

Do NOT edit:
- RULES.md (read only for reference, do not edit)
- pantry.md Section 1 (Implementation Mode, L12-80)
- pantry.md Section 3 (Error Handling, L176-180)
- Any files other than pantry.md

## Focus
Your task is ONLY to add a clarifying comment to pantry.md Review Mode Step 3 (L119) documenting the intentional redundancy with RULES.md Step 0 directory creation.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
