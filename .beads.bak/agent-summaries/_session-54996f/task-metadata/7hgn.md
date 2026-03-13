# Task: ant-farm-7hgn
**Status**: success
**Title**: Delay Big Head bead filing until after Pest Control checkpoint validation
**Type**: task
**Priority**: P2
**Epic**: ant-farm-753
**Agent Type**: prompt-engineer
**Dependencies**: blocks: [], blockedBy: []

## Affected Files
- orchestration/templates/reviews.md — Update Big Head Consolidation Protocol to add checkpoint gate before bead filing
- orchestration/templates/big-head-skeleton.md — Add wait-for-PC step between consolidation and bead filing (or reference agents/big-head.md)
- orchestration/RULES.md — Update review team composition to include Pest Control (6 members)
- orchestration/templates/pantry.md — Section 2: Big Head data file needs to reference the PC coordination step

## Root Cause
Big Head currently files beads for review findings before CCD and DMVDC checkpoints run. If checkpoints identify invalid findings (hallucinated, misattributed, doesn't match actual diff), those beads already exist and require manual cleanup. This pollutes the issue tracker with unvalidated findings.

## Expected Behavior
Big Head consolidates and writes the report but holds off on bd create calls until Pest Control confirms the findings pass checkpoints. On PASS: Big Head files all beads. On FAIL: Big Head flags failures to the Queen; only validated findings are filed.

## Acceptance Criteria
1. Big Head does not file any beads until Pest Control confirms checkpoint validation
2. Pest Control is spawned as part of the Nitpicker team, not as a separate Queen-orchestrated agent
3. On checkpoint pass, all consolidated findings are filed as beads
4. On checkpoint fail, only validated findings are filed; failures are escalated to Queen with specifics
5. No review report content enters the Queen's context window during this process
