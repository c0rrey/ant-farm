# Task Brief: ant-farm-r8m
**Task**: checkpoints.md {checkpoint} placeholder not defined in term definitions block
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/r8m.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L20 -- {checkpoint} used in filename pattern without definition
  - orchestration/templates/checkpoints.md:L4-7 -- Term definitions block
- **Root cause**: The filename pattern on line 20 of checkpoints.md uses {checkpoint} as a placeholder, but this is not defined in the term definitions block (lines 4-7). While its meaning is inferable from context, it breaks the convention of all placeholders being explicitly defined.
- **Expected behavior**: {checkpoint} is defined in the term definitions block or has an explanatory note.
- **Acceptance criteria**:
  1. {checkpoint} is defined in the term definitions block or has an explanatory note

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md:L1-35 (header, term definitions, and Pest Control Overview including artifact naming)
Do NOT edit: Any checkpoint section below line 42 (Verdict Thresholds Summary, CCO, WWD, DMVDC, CCB)

## Focus
Your task is ONLY to define the {checkpoint} placeholder in the term definitions block.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
