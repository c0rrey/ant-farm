Execute bug for ant-farm-dwfe.

Step 0: Read your task context from .beads/agent-summaries/_session-2829f0f5/prompts/task-dwfe.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-dwfe` + `bd update ant-farm-dwfe --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-dwfe)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-2829f0f5/summaries/dwfe.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-dwfe`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-dwfe
**Task**: fix: MEMORY.md custom agent minimum file requirements TBD caveat may be stale
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2829f0f5/summaries/dwfe.md

## Context
- **Affected files**:
  - ~/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md:L17 -- TBD caveat about agent file size
- **Root cause**: MEMORY.md:L17 states minimum file requirements are "still TBD" with 9-line files failing. All current agent files exceed 200 lines. If file size is no longer a constraint, the TBD caveat is misleading.
- **Expected behavior**: MEMORY.md TBD caveat resolved (removed or updated with findings).
- **Acceptance criteria**:
  1. MEMORY.md TBD caveat resolved (removed or updated with findings)

## Scope Boundaries
Read ONLY: ~/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md:L12-22
Do NOT edit: Any file other than MEMORY.md. Do not restructure or rewrite other MEMORY.md sections.

## Focus
Your task is ONLY to resolve the TBD caveat about custom agent minimum file requirements in MEMORY.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
