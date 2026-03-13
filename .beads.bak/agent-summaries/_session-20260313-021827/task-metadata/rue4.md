# Task: ant-farm-rue4
**Status**: success
**Title**: Migrate RULES.md (semantic)
**Type**: task
**Priority**: P2
**Epic**: ant-farm-f4h5
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-e7em (closed)]}

## Affected Files
- orchestration/RULES.md — Queen's workflow specification, crash recovery, landing-the-plane, session paths

## Root Cause
RULES.md is the Queen's workflow specification requiring structural changes beyond bd -> crumb: crash recovery paths, exec-summary copy addition, bd sync removal, session directory references.

## Expected Behavior
All bd references replaced; crash recovery paths updated; exec-summary copy step added; bd sync removed; session paths migrated.

## Acceptance Criteria
1. All bd command references replaced with crumb equivalents
2. Crash recovery paths updated from .beads/agent-summaries/ to .crumbs/sessions/
3. Landing-the-plane includes exec-summary copy step to .crumbs/history/
4. bd sync references removed from landing-the-plane workflow
5. Session directory creation uses .crumbs/sessions/_session-{timestamp}/ pattern
6. grep -c '\bbd\b' orchestration/RULES.md returns 0 (excluding any _archive references)
