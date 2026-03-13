# Task Brief: ant-farm-ygmj.2
**Task**: Add bead-list handoff to Big Head skeleton
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-20260222-225628/summaries/ygmj2.md

## Context
- **Affected files**:
  - orchestration/templates/big-head-skeleton.md:L1-187 -- Big Head skeleton template; add handoff step after bead filing
- **Root cause**: Big Head files beads from review findings but does not send a structured handoff to the Queen. The Queen has to infer what was filed from the consolidated report. The handoff message makes the interface explicit and machine-readable.
- **Expected behavior**: Big Head sends a structured bead-list handoff message via SendMessage to the Queen after filing beads, including bead IDs with priorities and root cause titles, P1/P2/P3 counts, and consolidated report path.
- **Acceptance criteria**:
  1. big-head-skeleton.md contains a handoff step after bead filing that sends a structured message to the Queen
  2. Handoff message format includes bead IDs, priorities, root cause titles, and consolidated report path
  3. Message is sent via SendMessage (not written to file) so the Queen receives it as a team notification
  4. P3 beads are included in the count but clearly separated from P1/P2 (Queen only acts on P1/P2 for fixes)
  5. Handoff step is clearly labeled and sequenced after CCB PASS confirmation

## Scope Boundaries
Read ONLY:
- orchestration/templates/big-head-skeleton.md:L1-187 (entire file -- needed to understand template structure and find correct insertion point after bead filing)

Do NOT edit:
- Steps 1-10 of the Big Head workflow (existing logic for report consolidation, dedup, bead filing)
- The "Instructions for the Queen" header section (L1-61)
- orchestration/templates/checkpoints.md, reviews.md, RULES.md, or any other template files

## Focus
Your task is ONLY to add the bead-list handoff step to big-head-skeleton.md after bead filing.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
