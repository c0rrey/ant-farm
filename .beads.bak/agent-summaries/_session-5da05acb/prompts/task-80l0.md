# Task Brief: ant-farm-80l0
**Task**: README Hard Gates table missing SSV checkpoint
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-5da05acb/summaries/80l0.md

## Context
- **Affected files**:
  - README.md:L258-263 — Hard Gates table missing SSV row
- **Root cause**: When SSV (Scout Strategy Verification) was added as the fifth hard gate, the README Hard Gates table was not updated. It still lists only 4 gates while RULES.md and GLOSSARY correctly list 5 including SSV.
- **Expected behavior**: README Hard Gates table should list 5 checkpoints matching RULES.md (SSV, CCO, WWD, DMVDC, CCB).
- **Acceptance criteria**:
  1. README Hard Gates table lists 5 checkpoints matching RULES.md (SSV, CCO, WWD, DMVDC, CCB)
  2. SSV row includes correct gate target (Pantry spawn) and model (haiku)

## Scope Boundaries
Read ONLY: README.md:L250-270, orchestration/RULES.md (SSV checkpoint definition for reference)
Do NOT edit: orchestration/RULES.md, orchestration/GLOSSARY.md, orchestration/templates/checkpoints.md

## Focus
Your task is ONLY to add the missing SSV row to the README Hard Gates table.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
