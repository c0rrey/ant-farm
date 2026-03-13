# Task Brief: ant-farm-h2gu
**Task**: Migrate checkpoints.md (semantic)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/h2gu.md

## Context
- **Affected files**: orchestration/templates/checkpoints.md:L157,L294,L311,L378,L380-385,L478,L481,L556,L615,L681,L685-693,L701,L706,L775,L806-822,L888 (bd references across 6 checkpoint definitions: SSV, CCO, WWD, DMVDC, CCB, ESV)
- **Root cause**: Checkpoints template contains bd command references across 6 checkpoint definitions. ESV checkpoint has a semantic flag change (--after syntax differs).
- **Expected behavior**: All 6 checkpoint definitions updated with crumb commands; ESV --after flag updated to crumb syntax.
- **Acceptance criteria**:
  1. All 6 checkpoint definitions (SSV, CCO, WWD, DMVDC, CCB, ESV) have bd -> crumb command updates
  2. ESV --after flag updated: bd list --status=open --after={date} -> crumb list --open --after {date}
  3. Checkpoint verification logic (pass/fail criteria) remains unchanged
  4. grep -c '\bbd\b' orchestration/templates/checkpoints.md returns 0
  5. All command examples in checkpoints reflect valid crumb CLI syntax

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md (full file)
Do NOT edit: Any file other than orchestration/templates/checkpoints.md. Do not change pass/fail logic, checkpoint ordering, or verification workflows.

## Focus
Your task is ONLY to migrate bd CLI commands to crumb CLI equivalents in checkpoints.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
