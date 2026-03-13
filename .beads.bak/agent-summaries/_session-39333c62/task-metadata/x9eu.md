# Task: ant-farm-x9eu
**Status**: success
**Title**: fix: README shows 5-member Nitpicker team but RULES.md requires 6 (Pest Control inside team)
**Type**: bug
**Priority**: P2
**Epic**: ant-farm-908t
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- README.md:59 — change to 6-member team description
- README.md:218 — update flow diagram to show 6-member team
- README.md:201 — remove separate PC spawn; note DMVDC/CCB run inside team

## Root Cause
README was written before Pest Control was added as a team member. Architectural change was applied to RULES.md but not propagated to README.

## Expected Behavior
README describes 6-member Nitpicker team with PC inside, no separate PC spawn.

## Acceptance Criteria
1. README describes 6-member Nitpicker team (4 reviewers + Big Head + Pest Control)
2. Flow diagram shows PC as team member, not separate spawn
3. No reference to spawning PC separately after team completes
