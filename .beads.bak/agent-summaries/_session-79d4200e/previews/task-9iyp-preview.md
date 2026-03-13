Execute bug for ant-farm-9iyp.

Step 0: Read your task context from .beads/agent-summaries/_session-79d4200e/prompts/task-9iyp.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-9iyp` + `bd update ant-farm-9iyp --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-9iyp)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-79d4200e/summaries/9iyp.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-9iyp`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-9iyp
**Task**: fix: remove 3 dead artifact entries from RULES.md Session Directory list
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-79d4200e/summaries/9iyp.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L345-347 -- 3 dead artifact entries (orchestrator-state*.md, step3b-transition-gate.md, HANDOFF-*.md)
  - orchestration/RULES.md:L343-349 -- missing briefing.md and session-summary.md entries
- **Root cause**: RULES.md Session Directory list contains 3 entries describing artifacts that were never created in any session, and is missing 2 entries for artifacts that ARE produced in every session (briefing.md, session-summary.md).
- **Expected behavior**: Session Directory list should only contain artifacts that actually exist, plus the 2 missing ones.
- **Acceptance criteria**:
  1. No dead artifact entries remain in RULES.md Session Directory list
  2. briefing.md listed with note "written by Scout (Step 1a)"
  3. session-summary.md listed with note "written by Pantry (optional)"
  4. Every artifact listed in RULES.md can be found in at least one actual session directory

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L340-370 (Session Directory section and surrounding context)
Do NOT edit: Any other section of RULES.md, any other file

## Focus
Your task is ONLY to remove dead artifact entries and add missing artifact entries in the RULES.md Session Directory list.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
