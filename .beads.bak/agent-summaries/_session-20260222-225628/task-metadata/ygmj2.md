# Task: ant-farm-ygmj.2
**Status**: success
**Title**: Add bead-list handoff to Big Head skeleton
**Type**: task
**Priority**: P2
**Epic**: ant-farm-ygmj
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [ant-farm-ygmj.4], blockedBy: []}

## Affected Files
- orchestration/templates/big-head-skeleton.md:L1-187 — Big Head skeleton template; add handoff step after bead filing

## Root Cause
Big Head files beads from review findings but does not send a structured handoff to the Queen. The Queen has to infer what was filed from the consolidated report. The handoff message makes the interface explicit and machine-readable.

## Expected Behavior
Big Head sends a structured bead-list handoff message via SendMessage to the Queen after filing beads, including bead IDs with priorities and root cause titles, P1/P2/P3 counts, and consolidated report path.

## Acceptance Criteria
1. big-head-skeleton.md contains a handoff step after bead filing that sends a structured message to the Queen
2. Handoff message format includes bead IDs, priorities, root cause titles, and consolidated report path
3. Message is sent via SendMessage (not written to file) so the Queen receives it as a team notification
4. P3 beads are included in the count but clearly separated from P1/P2 (Queen only acts on P1/P2 for fixes)
5. Handoff step is clearly labeled and sequenced after CCB PASS confirmation
