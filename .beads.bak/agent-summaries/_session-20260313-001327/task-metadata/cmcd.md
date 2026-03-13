# Task: ant-farm-cmcd
**Status**: success
**Title**: Implement crumb update, close, reopen commands
**Type**: task
**Priority**: P1
**Epic**: ant-farm-e7em
**Agent Type**: python-pro
**Dependencies**: {blocks: [], blockedBy: [ant-farm-l7pk]}
**Blocked by**: ant-farm-l7pk (Wave 2)

## Affected Files
- crumb.py -- add update, close, reopen subcommands with field mutation, timestamped notes, status transitions

## Root Cause
N/A (new feature)

## Expected Behavior
Mutation commands: crumb update for field changes and note appending, crumb close for multi-ID closing with closed_at stamps (idempotent), crumb reopen for closed-to-open transitions. Invalid transitions exit 1 with guidance.

## Acceptance Criteria
1. crumb update <id> --status in_progress changes status field in tasks.jsonl entry
2. crumb update <id> --note 'test note' appends timestamped entry to notes array
3. crumb close <id1> <id2> closes both crumbs, each gets closed_at timestamp
4. crumb close <already-closed-id> exits 0 without error (idempotent)
5. crumb reopen <id> sets status back to open and clears closed_at field
6. Attempting closed to in_progress exits 1 with stderr guidance to use reopen first
