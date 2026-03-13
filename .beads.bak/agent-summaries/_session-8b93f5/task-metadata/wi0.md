# Task: ant-farm-wi0
**Status**: success
**Title**: AGG-022: Standardize variable naming across templates
**Type**: task
**Priority**: P1
**Epic**: ant-farm-amk
**Agent Type**: refactoring-specialist
**Dependencies**: blocks: [], blockedBy: [ant-farm-b61 (done), ant-farm-p33 (done)]

## Affected Files
- orchestration/templates/*.md — All template files using variable names ({task-id-suffix}, {TASK_SUFFIX}, standalone, _standalone)
- orchestration/RULES.md — May contain variable references
- orchestration/PLACEHOLDER_CONVENTIONS.md — Canonical placeholder definitions

## Root Cause
The same concepts use different variable names across files: {task-id-suffix} vs {TASK_SUFFIX}, standalone vs _standalone, and task ID vs bead ID. This creates confusion and drift.

## Expected Behavior
All templates use canonical variable names: {TASK_ID} for full ID, {TASK_SUFFIX} for suffix, {SESSION_DIR} for session directory. A shared glossary defines each canonical variable. Deprecated variable names removed.

## Acceptance Criteria
1. All templates use the same variable name for each concept (no synonyms like task-id-suffix vs TASK_SUFFIX)
2. A glossary section defines each canonical variable name with its meaning
3. grep for deprecated variable names across orchestration/ returns zero matches
