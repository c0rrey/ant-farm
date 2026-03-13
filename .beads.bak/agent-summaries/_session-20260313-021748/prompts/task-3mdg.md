# Task Brief: ant-farm-3mdg
**Task**: Define Planner orchestrator behavior
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-20260313-021748/summaries/3mdg.md

## Context
- **Affected files**: orchestration/RULES-decompose.md (new section or new file — no existing line numbers; this is a new-feature task)
- **Root cause**: N/A — new feature. Planner orchestrator behavior needs documentation defining read permissions, state tracking, context budget, and distinction from Queen.
- **Expected behavior**: Planner orchestrator behavior documented with read permissions, state tracking, context budget, and distinction from Queen.
- **Acceptance criteria**:
  1. Planner orchestrator behavior documented (within RULES-decompose.md or separate file)
  2. Read permissions explicitly stated: spec.md and decomposition-brief.md only
  3. Prohibited reads listed: research briefs content, task JSONL, source code
  4. State tracking mechanism defined (step + retry count, not queen-state.md)
  5. Context budget target (15-20%) with reasoning documented
  6. Distinction from Queen explicitly called out (permissions, state, budget)

## Scope Boundaries
Read ONLY: orchestration/RULES-decompose.md (full file — understand existing structure before adding Planner section)
Do NOT edit: orchestration/RULES.md, orchestration/templates/*, CLAUDE.md, any source code files

## Focus
Your task is ONLY to define Planner orchestrator behavior documentation.
Do NOT fix adjacent issues you notice.

NOTE: This task depends on ant-farm-rwsk (Wave 3) which modifies orchestration/RULES-decompose.md. The file may have been recently changed — read the current state before designing your additions.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
