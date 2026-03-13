# Task: ant-farm-0bez
**Status**: success
**Title**: fix: GLOSSARY pre-push hook entry omits sync-to-claude.sh details
**Type**: bug
**Priority**: P3
**Epic**: ant-farm-908t
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- GLOSSARY.md:58 — pre-push hook definition entry

## Root Cause
GLOSSARY.md:58 defines the pre-push hook as syncing "agents/*.md to ~/.claude/agents/ and orchestration/ files to ~/.claude/orchestration/" but omits the _archive/ exclusion from rsync, selective script sync (only 2 of 6), the CLAUDE.md copy step, and the non-delete policy.

## Expected Behavior
GLOSSARY pre-push hook entry mentions all key behaviors documented in sync-to-claude.sh:23-44.

## Acceptance Criteria
1. GLOSSARY pre-push hook entry mentions _archive/ exclusion, selective script sync, CLAUDE.md copy, and non-delete policy
