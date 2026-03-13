# Task: ant-farm-3mdg
**Status**: success
**Title**: Define Planner orchestrator behavior
**Type**: task
**Priority**: P2
**Epic**: ant-farm-89un
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-rwsk]}
**Blocked by**: ant-farm-rwsk (Wave 3)

## Affected Files
- orchestration/RULES-decompose.md — section within, OR separate file (potential overlap with rwsk)

## Root Cause
N/A — new feature. Planner orchestrator behavior needs documentation.

## Expected Behavior
Planner orchestrator behavior documented with read permissions, state tracking, context budget, and distinction from Queen.

## Acceptance Criteria
1. Planner orchestrator behavior documented (within RULES-decompose.md or separate file)
2. Read permissions explicitly stated: spec.md and decomposition-brief.md only
3. Prohibited reads listed: research briefs content, task JSONL, source code
4. State tracking mechanism defined (step + retry count, not queen-state.md)
5. Context budget target (15-20%) with reasoning documented
6. Distinction from Queen explicitly called out (permissions, state, budget)

NOTE: May modify orchestration/RULES-decompose.md (same file as rwsk). Must run after rwsk completes.
