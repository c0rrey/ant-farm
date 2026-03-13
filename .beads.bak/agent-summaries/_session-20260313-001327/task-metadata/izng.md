# Task: ant-farm-izng
**Status**: success
**Title**: Implement crumb doctor command
**Type**: task
**Priority**: P2
**Epic**: ant-farm-e7em
**Agent Type**: python-pro
**Dependencies**: {blocks: [], blockedBy: [ant-farm-h7af]}
**Blocked by**: ant-farm-h7af (Wave 3)

## Affected Files
- crumb.py -- add doctor subcommand for JSONL integrity validation and optional --fix auto-repair

## Root Cause
N/A (new feature)

## Expected Behavior
Data validation and repair: crumb doctor checks for malformed JSON lines, dangling blocked_by references (warning), dangling parent links (error), duplicate IDs (error), orphan crumbs (warning). Optional --fix removes dangling references.

## Acceptance Criteria
1. crumb doctor reports malformed JSON lines with line numbers
2. Dangling blocked_by references are flagged as warnings (not errors)
3. Dangling parent links (pointing to non-existent trail) are flagged as errors
4. Duplicate IDs are flagged as errors
5. Orphan crumbs (no parent trail) are flagged as warnings
6. crumb doctor --fix removes dangling blocked_by references and reports fixes applied
7. Clean data produces 'No issues found' and exits 0
