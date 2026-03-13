# Task: ant-farm-fomy
**Status**: success
**Title**: Auto-approve Scout strategy in Step 1
**Type**: feature
**Priority**: P3
**Epic**: none
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md:90-101 — Step 1b SSV gate section; user approval gate after SSV PASS

## Root Cause
The Queen currently waits for user approval after SSV PASS before spawning agents. This adds latency to the workflow. The persistent review team design (ant-farm-ygmj) already auto-approves fix-cycle Scout strategies, establishing precedent.

## Expected Behavior
RULES.md Step 1b should auto-approve after SSV PASS instead of requiring user confirmation. A complexity threshold may gate auto-approval vs user prompt for larger sessions.

## Acceptance Criteria
1. RULES.md Step 1b no longer requires user approval after SSV PASS
2. Risk analysis documented: what could go wrong with auto-approval, what safety nets exist
3. Decision on complexity threshold documented (always auto-approve vs threshold-based)
