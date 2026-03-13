# Task Brief: ant-farm-39zq
**Task**: fill-review-slots.sh fill_slot spawns separate awk per slot substitution
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/39zq.md

## Context
- **Affected files**: scripts/fill-review-slots.sh:L151-183 -- fill_slot function
- **Root cause**: fill_slot is called once per slot, spawning awk + temp file I/O each time. For round 1: 7 slots x 4 types + 5 for big-head = 33 awk invocations. Could be simplified to a single pass per file.
- **Expected behavior**: Slot filling should use fewer process spawns per file via batched awk passes.
- **Acceptance criteria**:
  1. Slot filling uses fewer process spawns per file
  2. Output is identical to current approach

## Scope Boundaries
Read ONLY: scripts/fill-review-slots.sh:L1-183 (full file, focus on L151-183 fill_slot function)
Do NOT edit: scripts/compose-review-skeletons.sh, orchestration/ templates, any other scripts

## Focus
Your task is ONLY to reduce process spawns in fill_slot by batching awk substitutions into fewer passes.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
