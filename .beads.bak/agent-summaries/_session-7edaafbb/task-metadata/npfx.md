# Task: ant-farm-npfx
**Status**: success
**Title**: parse-progress-log.sh hardening gaps (overwrite, dead branch, corruption)
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- scripts/parse-progress-log.sh:117-124 — no validation for corrupted/malformed log lines
- scripts/parse-progress-log.sh:148-151 — redundant dead branch with misleading comment
- scripts/parse-progress-log.sh:157-224 — silently overwrites existing resume-plan.md

## Root Cause
First-pass implementation handles happy path but lacks defensive coding for edge scenarios.

## Expected Behavior
Overwrite produces stderr notice. Dead branch comment is accurate. Malformed lines rejected with timestamp validation.

## Acceptance Criteria
1. Overwrite produces stderr notice
2. Dead branch comment is accurate
3. Malformed lines rejected with timestamp validation
