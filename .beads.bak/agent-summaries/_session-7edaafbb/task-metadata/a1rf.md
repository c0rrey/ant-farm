# Task: ant-farm-a1rf
**Status**: success
**Title**: Bash scripting edge cases under set -euo pipefail
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- scripts/scrub-pii.sh:52-55 — grep -c/set -e interaction
- orchestration/RULES.md:146-148 — tr+sed whitespace check
- scripts/install-hooks.sh:27-31 — backup cp failure

## Root Cause
Multiple bash scripts use constructs that are correct but subtly platform-sensitive under strict error handling. grep -c returns non-zero on no match, which triggers set -e. tr+sed whitespace check is fragile. backup cp failure not gracefully handled.

## Expected Behavior
Add clarifying comments; simplify whitespace check; wrap backup cp gracefully.

## Acceptance Criteria
1. grep -c usage has clarifying comment or is wrapped to prevent set -e exit
2. Whitespace check simplified
3. Backup cp wrapped with graceful failure handling
