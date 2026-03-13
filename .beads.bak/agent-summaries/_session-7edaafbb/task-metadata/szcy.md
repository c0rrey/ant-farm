# Task: ant-farm-szcy
**Status**: success
**Title**: sync-to-claude.sh script selection has no explanatory comment
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- scripts/sync-to-claude.sh:27-33 — script iteration without comment

## Root Cause
Iterates over two hardcoded script names without explaining why only these two are synced and not others.

## Expected Behavior
Comment should explain the script selection rationale.

## Acceptance Criteria
1. Comment explains the script selection rationale
