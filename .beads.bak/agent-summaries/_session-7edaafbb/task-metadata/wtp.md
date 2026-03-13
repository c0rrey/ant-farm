# Task: ant-farm-wtp
**Status**: success
**Title**: scrub-pii.sh does not re-stage issues.jsonl when run standalone outside pre-commit
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- scripts/scrub-pii.sh — standalone execution path
- scripts/install-hooks.sh — git add in generated hook

## Root Cause
When run standalone (not as pre-commit hook), scrub-pii.sh modifies issues.jsonl in place but does not re-stage it. The git add is in install-hooks.sh's generated hook, not in scrub-pii.sh itself.

## Expected Behavior
Script should detect non-hook context and print reminder to run 'git add .beads/issues.jsonl'.

## Acceptance Criteria
1. Standalone execution prints reminder about re-staging
2. Pre-commit hook behavior unchanged
