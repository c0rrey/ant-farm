# Task: ant-farm-xtu9
**Status**: success
**Title**: Design and write Architect agent (definition + template + skeleton)
**Type**: task
**Priority**: P1
**Epic**: ant-farm-6w50
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [ant-farm-hlv6], blockedBy: [ant-farm-399a, ant-farm-y4hl]}
**Blocked by**: ant-farm-399a (Wave 1), ant-farm-y4hl (Wave 1)

## Affected Files
- agents/architect.md — new agent definition (frontmatter: name, description, model: opus, tools)
- orchestration/templates/decomposition.md — new detailed workflow template
- orchestration/templates/architect-skeleton.md — new prompt skeleton

## Root Cause
N/A — new feature. Architect agent needed for spec decomposition into trails and crumbs.

## Expected Behavior
Three files created: agent definition, workflow template, and prompt skeleton for the Architect agent that reads spec.md + research briefs + codebase, creates trails/crumbs via CLI, wires dependencies, assigns scope.

## Acceptance Criteria
1. agents/architect.md exists with correct frontmatter (name, description, model: opus, tools list)
2. orchestration/templates/decomposition.md contains full decomposition workflow with crumb CLI commands
3. orchestration/templates/architect-skeleton.md contains prompt template with input file placeholders
4. Prompt specifies 100% spec coverage requirement (every requirement maps to >=1 crumb acceptance criterion)
5. Scope budget (5-8 files per crumb) explicitly stated and enforced
6. Prompt includes explicit prohibitions: no code writing, no orphan crumbs, no circular deps, no vague scope, no unverifiable criteria
7. Brownfield vs greenfield handling documented
8. decomposition-brief.md output format specified
