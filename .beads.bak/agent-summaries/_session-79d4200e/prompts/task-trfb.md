# Task Brief: ant-farm-trfb
**Task**: fix: one-TeamCreate-per-session constraint undocumented in operator-facing docs
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-79d4200e/summaries/trfb.md

## Context
- **Affected files**:
  - orchestration/RULES.md (Step 3b-iv, near team setup) -- add TeamCreate constraint note
  - CONTRIBUTING.md or orchestration/SETUP.md -- mention constraint for framework extenders
- **Root cause**: One-TeamCreate-per-session constraint was discovered empirically and captured in MEMORY.md but never propagated to RULES.md, CLAUDE.md, or CONTRIBUTING.md.
- **Expected behavior**: RULES.md should document the constraint near the Nitpicker team setup, explaining why PC is a team member.
- **Acceptance criteria**:
  1. RULES.md documents the one-TeamCreate-per-session constraint
  2. Note explains the architectural implication (PC must be team member, not separate spawn)
  3. CONTRIBUTING.md or SETUP.md mentions the constraint for framework extenders

## Scope Boundaries
Read ONLY: orchestration/RULES.md (Step 3b-iv section), CONTRIBUTING.md:L1-248, orchestration/SETUP.md:L1-269
Do NOT edit: CLAUDE.md, any template files, any script files

## Focus
Your task is ONLY to document the one-TeamCreate-per-session constraint in RULES.md and either CONTRIBUTING.md or SETUP.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
