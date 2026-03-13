# Task: ant-farm-x9eu
**Status**: success
**Title**: fix: README shows 5-member Nitpicker team but RULES.md requires 6 (Pest Control inside team)
**Type**: bug
**Priority**: P2
**Epic**: ant-farm-908t
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- README.md:59 — describes Nitpicker team as "4 reviewers + Big Head" (5 members)
- README.md:218 — flow diagram shows 5-member team + separate PC spawn
- README.md:201 — separate PC spawn reference

## Root Cause
README was written before Pest Control was added as a team member. The architectural change was applied to RULES.md but not propagated to README.

## Expected Behavior
README should describe 6-member Nitpicker team (4 reviewers + Big Head + Pest Control).

## Acceptance Criteria
1. README describes 6-member Nitpicker team (4 reviewers + Big Head + Pest Control)
2. Flow diagram shows PC as team member, not separate spawn
3. No reference to spawning PC separately after team completes
