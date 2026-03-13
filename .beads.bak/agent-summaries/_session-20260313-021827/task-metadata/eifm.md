# Task: ant-farm-eifm
**Status**: success
**Title**: Migrate queen-state and session plan templates (mechanical)
**Type**: task
**Priority**: P2
**Epic**: ant-farm-irgq
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: [ant-farm-e7em (closed)]}

## Affected Files
- orchestration/templates/queen-state.md — .beads/agent-summaries/ paths, bd close, bd sync
- orchestration/templates/SESSION_PLAN_TEMPLATE.md — bd close, bd sync references

## Root Cause
Queen-state and session plan templates contain bd command references and .beads/ paths needing mechanical substitution.

## Expected Behavior
All bd references replaced with crumb; .beads/agent-summaries/ replaced with .crumbs/sessions/; bd sync references removed.

## Acceptance Criteria
1. queen-state.md: all .beads/agent-summaries/ paths replaced with .crumbs/sessions/
2. SESSION_PLAN_TEMPLATE.md: bd close -> crumb close, bd sync references removed
3. grep -c '\bbd\b' on both files returns 0
4. All 'beads' terminology updated to 'crumbs'
5. Session directory naming convention updated (_session-* pattern preserved)
