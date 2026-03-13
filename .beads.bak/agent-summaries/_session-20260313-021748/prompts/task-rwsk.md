# Task Brief: ant-farm-rwsk
**Task**: Write RULES-decompose.md
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-20260313-021748/summaries/rwsk.md

## Context
- **Affected files**: orchestration/RULES-decompose.md (new file)
- **Root cause**: N/A — new feature. Decomposition workflow needs its own RULES document.
- **Expected behavior**: RULES-decompose.md contains the complete 7-step decomposition workflow with hard gates, concurrency rules, retry limits, and Planner read permissions.
- **Acceptance criteria**:
  1. orchestration/RULES-decompose.md exists with all 7 steps (0-6) documented
  2. Each step specifies: agent to spawn, model, input files, output files, hard gate conditions
  3. Hard gates table present: spec quality gate, research complete, TDV PASS
  4. Concurrency rules documented: max 4 Foragers, Surveyor/Architect run alone
  5. Retry limits table present with escalation paths
  6. Planner read permissions explicitly defined (reads spec.md and decomposition-brief.md only)
  7. Context budget target (15-20%) documented with rationale
  8. Brownfield vs greenfield detection heuristic documented (5+ non-config files = brownfield)

## Scope Boundaries
Read ONLY: orchestration/RULES.md (for existing RULES format/patterns), orchestration/templates/ (for workflow context)
Do NOT edit: orchestration/RULES.md, any existing templates, CLAUDE.md, CHANGELOG.md

## Focus
Your task is ONLY to create orchestration/RULES-decompose.md with the complete 7-step decomposition workflow.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
