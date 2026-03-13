Execute task for ant-farm-eifm.

Step 0: Read your task context from .beads/agent-summaries/_session-20260313-021827/prompts/task-eifm.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-eifm` + `bd update ant-farm-eifm --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-eifm)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-20260313-021827/summaries/eifm.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-eifm`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-eifm
**Task**: Migrate queen-state and session plan templates (mechanical)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/eifm.md

## Context
- **Affected files**:
  - orchestration/templates/queen-state.md:L8,L74 — .beads/agent-summaries/ paths, bd close, bd sync
  - orchestration/templates/SESSION_PLAN_TEMPLATE.md:L271,L288,L291 — bd close, bd sync references
- **Root cause**: Queen-state and session plan templates contain bd command references and .beads/ paths needing mechanical substitution.
- **Expected behavior**: All bd references replaced with crumb; .beads/agent-summaries/ replaced with .crumbs/sessions/; bd sync references removed.
- **Acceptance criteria**:
  1. queen-state.md: all .beads/agent-summaries/ paths replaced with .crumbs/sessions/
  2. SESSION_PLAN_TEMPLATE.md: bd close -> crumb close, bd sync references removed
  3. grep -c '\bbd\b' on both files returns 0
  4. All 'beads' terminology updated to 'crumbs'
  5. Session directory naming convention updated (_session-* pattern preserved)

## Scope Boundaries
Read ONLY: orchestration/templates/queen-state.md (full file), orchestration/templates/SESSION_PLAN_TEMPLATE.md (full file)
Do NOT edit: Any other template files, RULES.md, scout.md, implementation.md, or any file outside these two

## Focus
Your task is ONLY to replace bd command references with crumb equivalents and .beads/ paths with .crumbs/ in queen-state.md and SESSION_PLAN_TEMPLATE.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
