# Task: ant-farm-rwsk
**Status**: success
**Title**: Write RULES-decompose.md
**Type**: task
**Priority**: P2
**Epic**: ant-farm-89un
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [ant-farm-3mdg], blockedBy: [ant-farm-6w50]}
**Blocked by**: ant-farm-6w50 (Epic 5 must complete first — Wave 1+2)

## Affected Files
- orchestration/RULES-decompose.md — new file

## Root Cause
N/A — new feature. Decomposition workflow needs its own RULES document.

## Expected Behavior
RULES-decompose.md contains the complete 7-step decomposition workflow with hard gates, concurrency rules, retry limits, and Planner read permissions.

## Acceptance Criteria
1. orchestration/RULES-decompose.md exists with all 7 steps (0-6) documented
2. Each step specifies: agent to spawn, model, input files, output files, hard gate conditions
3. Hard gates table present: spec quality gate, research complete, TDV PASS
4. Concurrency rules documented: max 4 Foragers, Surveyor/Architect run alone
5. Retry limits table present with escalation paths
6. Planner read permissions explicitly defined (reads spec.md and decomposition-brief.md only)
7. Context budget target (15-20%) documented with rationale
8. Brownfield vs greenfield detection heuristic documented (5+ non-config files = brownfield)
