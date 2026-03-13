# Task: ant-farm-rja
**Status**: success
**Title**: sync-to-claude.sh agent glob fails silently when agents/ directory missing
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- scripts/sync-to-claude.sh — agent file glob pattern

## Root Cause
When agents/ directory does not exist, the glob pattern fails silently. No warning that agent files could not be synced.

## Expected Behavior
Missing agents/ directory should produce a warning or be handled gracefully.

## Acceptance Criteria
1. Missing agents/ directory produces a warning
2. Script continues normally when agents/ is absent
