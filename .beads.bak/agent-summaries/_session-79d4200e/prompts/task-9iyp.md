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
