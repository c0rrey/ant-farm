# Task: ant-farm-vjhe
**Status**: success
**Title**: Migrate project documentation (mechanical)
**Type**: task
**Priority**: P2
**Epic**: ant-farm-irgq
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-e7em (closed)]}

## Affected Files
- README.md — 10+ bd references, beads terminology, .beads/ paths
- AGENTS.md — 7 bd references
- CONTRIBUTING.md — 1 bd reference
- docs/installation-guide.md — 1 bd reference

## Root Cause
Project documentation contains bd references and beads terminology needing mechanical substitution.

## Expected Behavior
All bd references replaced; beads -> crumbs terminology; .beads/ -> .crumbs/ paths; installation instructions updated.

## Acceptance Criteria
1. README.md: all 10+ bd references replaced, beads -> crumbs terminology, .beads/ -> .crumbs/ paths
2. AGENTS.md: all 7 bd references replaced with crumb equivalents
3. CONTRIBUTING.md: bd reference replaced with crumb equivalent
4. docs/installation-guide.md: bd reference replaced with crumb equivalent
5. grep -rl '\bbd\b' across all four files returns 0
6. No broken links or references to removed Beads/Dolt tools
