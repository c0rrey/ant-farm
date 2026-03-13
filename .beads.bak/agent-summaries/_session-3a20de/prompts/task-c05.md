# Task Brief: ant-farm-c05
**Task**: Checkpoint A.5 relies on Queen-provided file list with no independent scope validation
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/c05.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L189 -- Checkpoint A.5 expected file list placeholder (inside the CCO Nitpickers template)
- **Root cause**: Checkpoint A.5 uses {list files from task description} as the expected file list, provided by the Queen. If the Queen passes an incomplete or incorrect list, A.5 will produce false positives or false negatives.
- **Expected behavior**: Either A.5 has an independent scope reference, or the limitation is explicitly documented.
- **Acceptance criteria**:
  1. Either A.5 has an independent scope reference, or the limitation is explicitly documented

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md:L165-225 (CCO Nitpickers section)
Do NOT edit: CCO Dirt Pushers section (L97-163), WWD section (L235-303), DMVDC section (L306-454), CCB section (L457-572)

## Focus
Your task is ONLY to add independent scope validation to Checkpoint A.5 or document its limitation.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
