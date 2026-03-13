# Task: ant-farm-trfb
**Status**: success
**Title**: fix: one-TeamCreate-per-session constraint undocumented in operator-facing docs
**Type**: bug
**Priority**: P2
**Epic**: ant-farm-908t
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md — Step 3b-iv: add TeamCreate constraint note
- CONTRIBUTING.md or SETUP.md — mention constraint for framework extenders

## Root Cause
The one-TeamCreate-per-session constraint was discovered empirically and captured in MEMORY.md but never propagated to RULES.md, CLAUDE.md, or CONTRIBUTING.md.

## Expected Behavior
RULES.md documents the constraint and explains why PC must be a team member rather than a separate spawn.

## Acceptance Criteria
1. RULES.md documents the one-TeamCreate-per-session constraint
2. Note explains the architectural implication (PC must be team member, not separate spawn)
3. CONTRIBUTING.md or SETUP.md mentions the constraint for framework extenders
