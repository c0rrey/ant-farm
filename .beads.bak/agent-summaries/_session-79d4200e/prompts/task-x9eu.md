# Task Brief: ant-farm-x9eu
**Task**: fix: README shows 5-member Nitpicker team but RULES.md requires 6 (Pest Control inside team)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-79d4200e/summaries/x9eu.md

## Context
- **Affected files**:
  - README.md:L59 -- describes Nitpicker team as "4 reviewers + Big Head" (5 members)
  - README.md:L218 -- flow diagram shows 5-member team + separate PC spawn
  - README.md:L201 -- separate PC spawn reference
- **Root cause**: README was written before Pest Control was added as a team member. The architectural change was applied to RULES.md but not propagated to README.
- **Expected behavior**: README should describe 6-member Nitpicker team (4 reviewers + Big Head + Pest Control).
- **Acceptance criteria**:
  1. README describes 6-member Nitpicker team (4 reviewers + Big Head + Pest Control)
  2. Flow diagram shows PC as team member, not separate spawn
  3. No reference to spawning PC separately after team completes

## Scope Boundaries
Read ONLY: README.md:L55-65 (team description), README.md:L195-225 (flow diagram and PC spawn reference)
Do NOT edit: Any file other than README.md

## Focus
Your task is ONLY to update README.md to reflect the 6-member Nitpicker team with Pest Control as a team member.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
