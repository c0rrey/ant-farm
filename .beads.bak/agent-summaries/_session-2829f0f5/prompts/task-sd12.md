# Task Brief: ant-farm-sd12
**Task**: fix: remove archived pantry-review from scout.md exclusion list
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2829f0f5/summaries/sd12.md

## Context
- **Affected files**:
  - orchestration/templates/scout.md:L63 -- agent exclusion list
- **Root cause**: scout.md:L63 lists `pantry-review` in the agent exclusion list but the pantry-review agent is archived and has no file in agents/. The reference is harmless (it would not appear in the Scout's catalog anyway) but signals the list was not updated on deprecation.
- **Expected behavior**: scout.md exclusion list no longer references pantry-review.
- **Acceptance criteria**:
  1. scout.md exclusion list no longer references pantry-review

## Scope Boundaries
Read ONLY: orchestration/templates/scout.md:L55-70
Do NOT edit: Any file other than orchestration/templates/scout.md. Do not change any other entries in the exclusion list.

## Focus
Your task is ONLY to remove the pantry-review entry from the scout.md exclusion list.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
