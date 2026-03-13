# Task: ant-farm-7hl
**Status**: success
**Title**: AGG-018: Align landing instructions between CLAUDE.md and AGENTS.md
**Type**: task
**Priority**: P2
**Epic**: ant-farm-7hh
**Agent Type**: technical-writer
**Dependencies**: blocks: [], blockedBy: []

## Affected Files
- ~/.claude/CLAUDE.md — includes Review-findings gate (Step 3) and specific cleanup commands
- ~/.claude/AGENTS.md (or equivalent) — omits review gate, uses generic cleanup

## Root Cause
CLAUDE.md includes a Review-findings gate (Step 3) and specific cleanup commands. AGENTS.md omits the review gate and uses generic cleanup. An agent following AGENTS.md could skip the mandatory review gate.

## Expected Behavior
Both CLAUDE.md and AGENTS.md reference the same landing procedure steps with no contradictions in step sequence.

## Acceptance Criteria
1. Both CLAUDE.md and AGENTS.md reference the same landing procedure steps
2. The review-findings gate is present or cross-referenced in both files
3. diff of landing sections between files shows no contradictions in step sequence
