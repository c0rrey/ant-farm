# Task: ant-farm-lhq
**Status**: success
**Title**: Scout error metadata template lacks context fields (Title, Epic) present in success template
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- ~/.claude/orchestration/templates/scout.md — error metadata template section

## Root Cause
The error metadata template in scout.md only includes Status and Error Details fields. The success template includes Title, Type, Priority, Epic, Agent Type, Dependencies, etc. When bd show fails, downstream agents lose context about the task.

## Expected Behavior
Error metadata template should include as many context fields as possible (at minimum Title and Epic from the task listing).

## Acceptance Criteria
1. Error metadata template includes Title and Epic fields (from bd list output)
2. Error template clearly marks which fields could not be populated
