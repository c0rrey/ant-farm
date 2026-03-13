# Task Brief: ant-farm-ti6g
**Task**: fill-review-slots.sh accepts review round 0 as valid input
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/ti6g.md

## Context
- **Affected files**: scripts/fill-review-slots.sh:L78-83 -- round validation regex
- **Root cause**: Validates review round with regex '^[0-9]+$' which accepts 0. Review system uses 1-based rounds. Round 0 would silently fall into the round 2+ branch.
- **Expected behavior**: Round 0 should be rejected with an error message.
- **Acceptance criteria**:
  1. Round 0 is rejected with an error message
  2. Round 1 and higher continue to work

## Scope Boundaries
Read ONLY: scripts/fill-review-slots.sh:L1-183 (full file, focus on L78-83 round validation)
Do NOT edit: scripts/compose-review-skeletons.sh, orchestration/ templates, any other scripts

## Focus
Your task is ONLY to fix the round validation regex to reject round 0.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
