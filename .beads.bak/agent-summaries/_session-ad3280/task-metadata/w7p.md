# Task: ant-farm-w7p
**Status**: success
**Title**: (BUG) Improve Scout agent type tie-breaking with deeper catalog reads and explicit fallback
**Type**: bug
**Priority**: P2
**Epic**: ant-farm-6k0
**Agent Type**: technical-writer
**Dependencies**: blocks: [], blockedBy: []

## Affected Files
- `orchestration/templates/scout.md` — Step 2.5 catalog build (add deep-read-on-tie logic), Step 3 agent type selection (update tie handling), Step 5 strategy presentation (update format for tied types)

## Root Cause
When the Scout cannot clearly differentiate between agent types for a task, it falls back to returning 'group' as the agent type — an opaque label with no information about which types were tied or why. The Scout's agent catalog (Step 2.5) only reads YAML frontmatter — one sentence of description per agent — providing insufficient signal for 'description match' (selection criterion 3), making ties more likely than necessary.

## Expected Behavior
Two-pronged fix: (1) When selection criteria produce a tie, Scout reads full agent MD files for ONLY the tied candidates. If the tie persists after deeper reads, proceed to step 2. (2) When a tie cannot be broken, list all tied agent types in format: '{task-id}: {task-title} — PICK ONE: [type-a | type-b]' instead of 'group'.

## Acceptance Criteria
1. Scout reads full agent MD files for tied candidates (and only tied candidates) before falling back
2. Unresolved ties surface in strategy as '{task-id}: {task-title} — PICK ONE: [type-a | type-b]' instead of 'group'
3. Each task with a tie lists its own candidates independently
4. No increase in Scout context usage when there are no ties (frontmatter-only reads remain the default)
