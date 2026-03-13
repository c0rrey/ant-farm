# Task: ant-farm-7yv
**Status**: success
**Title**: Pre-commit hook silently allows PII when scrub script not executable
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- scripts/install-hooks.sh:72-75 — exits 0 when scrub script not executable
- scripts/scrub-pii.sh — needs chmod +x during installation

## Root Cause
The generated pre-commit hook in install-hooks.sh:72-75 checks if scrub-pii.sh is executable and exits 0 (allows commit) with only a WARNING if it's not. This means a missing or non-executable scrub script silently allows PII-containing issues.jsonl into git history.

## Expected Behavior
PII cannot enter git history when scrub script is missing/non-executable. install-hooks.sh ensures scrub-pii.sh is executable after installation.

## Acceptance Criteria
1. PII cannot enter git history when scrub script is missing/non-executable
2. install-hooks.sh ensures scrub-pii.sh is executable after installation
