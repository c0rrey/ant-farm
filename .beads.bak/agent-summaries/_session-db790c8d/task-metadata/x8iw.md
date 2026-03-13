# Task: ant-farm-x8iw
**Status**: success
**Title**: fix: Scout agent frontmatter declares model: sonnet, contradicting RULES.md model: opus
**Type**: bug
**Priority**: P1
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- agents/scout-organizer.md:5 -- frontmatter model field says "sonnet", should say "opus"
- orchestration/GLOSSARY.md:80 -- Scout row model says "sonnet", should say "opus"
- orchestration/GLOSSARY.md:81 -- Pantry row model says "sonnet", should say "opus"
- README.md:75 -- says "a sonnet subagent", should say "an opus subagent"

## Root Cause
When the Scout was promoted from sonnet to opus (for orchestration complexity), the RULES.md Model Assignments table was updated but the agent frontmatter was not. The same stale model value propagated to GLOSSARY.md and README.md.

## Expected Behavior
All references to Scout and Pantry model tier should say "opus", matching RULES.md Model Assignments table.

## Acceptance Criteria
1. agents/scout-organizer.md frontmatter says model: opus
2. orchestration/GLOSSARY.md Scout row says opus
3. orchestration/GLOSSARY.md Pantry row says opus
4. README.md Scout description says "opus" not "sonnet"
5. No other files reference Scout or Pantry as sonnet-tier agents (grep verification)
