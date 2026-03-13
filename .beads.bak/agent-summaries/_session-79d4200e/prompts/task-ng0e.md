# Task Brief: ant-farm-ng0e
**Task**: fix: DMVDC Nitpicker artifact naming in checkpoints.md does not match actual filenames
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-79d4200e/summaries/ng0e.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L475 -- DMVDC naming convention
  - orchestration/templates/checkpoints.md:L478 -- example TASK_SUFFIX values
- **Root cause**: Naming convention in checkpoints.md was written speculatively and never validated against actual Pest Control output.
- **Expected behavior**: checkpoints.md DMVDC Nitpicker naming should match actual artifact filenames.
- **Acceptance criteria**:
  1. checkpoints.md DMVDC Nitpicker naming matches actual artifact filenames
  2. Example TASK_SUFFIX values match actual Nitpicker review type names
  3. Querying pc/ with the documented pattern finds actual files

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md:L470-485 (DMVDC Nitpicker naming section), .beads/agent-summaries/ (scan for actual pc/ artifact filenames to validate naming)
Do NOT edit: Any other section of checkpoints.md, any other file

## Focus
Your task is ONLY to fix the DMVDC Nitpicker artifact naming convention and examples in checkpoints.md to match actual filenames.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
