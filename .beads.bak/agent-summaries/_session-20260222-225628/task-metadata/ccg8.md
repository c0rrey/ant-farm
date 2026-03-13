# Task: ant-farm-ccg8
**Status**: success
**Title**: ESV Check 2 git log no guard for repo root commit
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/checkpoints.md:791-795 — ESV Check 2 git log range

## Root Cause
ESV Check 2 in `checkpoints.md:L791-L795` uses `git log --oneline {SESSION_START_COMMIT}^..{SESSION_END_COMMIT}`. The `^` suffix requires the commit's parent to exist. If `{SESSION_START_COMMIT}` is the repo's first commit (no parent), git errors.

## Expected Behavior
ESV Check 2 handles the case where SESSION_START_COMMIT has no parent by falling back to `git log {SESSION_START_COMMIT}..{SESSION_END_COMMIT}` with a note.

## Acceptance Criteria
1. ESV Check 2 handles the case where SESSION_START_COMMIT has no parent
2. The fallback command still covers the correct commit range
3. The guard is documented in the check instructions
