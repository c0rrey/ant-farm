# Task: ant-farm-y4hl
**Status**: success
**Title**: Design and write Forager agent (definition + template + skeleton)
**Type**: task
**Priority**: P1
**Epic**: ant-farm-6w50
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [ant-farm-xtu9], blockedBy: [ant-farm-e7em (closed)]}

## Affected Files
- agents/forager.md — new agent definition (frontmatter: name, description, model: sonnet, tools)
- orchestration/templates/forager.md — new workflow template (NOTE: existing forager.md may need replacement)
- orchestration/templates/forager-skeleton.md — new prompt skeleton

## Root Cause
N/A — new feature. Forager agent needed for parallel research across 4 focus areas.

## Expected Behavior
Three files created: agent definition, workflow template, and prompt skeleton for the Forager agent that runs 4 parallel instances (Stack, Architecture, Pitfall, Pattern) with 100-line hard cap.

## Acceptance Criteria
1. agents/forager.md exists with correct frontmatter (name, description, model: sonnet, tools list)
2. orchestration/templates/forager.md contains workflow for all 4 focus areas with clear scope boundaries
3. orchestration/templates/forager-skeleton.md contains prompt template with {FOCUS_AREA} placeholder
4. Prompt includes explicit prohibitions: no cross-reading, max 100 lines, no contradicting spec decisions, no alternative recommendations
5. Pattern Forager skip logic documented for greenfield projects
6. Source hierarchy (official docs > web > training data) explicitly stated in prompt
7. Each focus area has concrete examples of good/bad research output
