# Task: ant-farm-a5lq
**Status**: success
**Title**: Write /ant-farm:plan skill definition
**Type**: task
**Priority**: P2
**Epic**: ant-farm-r8ru
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-e7em (closed)]}

## Affected Files
- skills/plan.md — new file

## Root Cause
N/A — new feature. /ant-farm:plan slash command needed to trigger decomposition workflow.

## Expected Behavior
skills/plan.md exists with skill frontmatter, accepts spec path or inline text, classifies input, routes to RULES-decompose.md.

## Acceptance Criteria
1. skills/plan.md exists with correct skill frontmatter and trigger pattern
2. Accepts file path argument (reads file contents) or inline text
3. Input classification heuristic documented (structured vs freeform detection)
4. Routes to RULES-decompose.md workflow
5. Creates DECOMPOSE_DIR with timestamp-based naming
6. Error handling: missing file path, empty input, .crumbs/ not initialized
