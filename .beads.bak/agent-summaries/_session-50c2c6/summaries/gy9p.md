# Fix Summary: ant-farm-gy9p

## Issue
Round cap in RULES.md Step 3c was placed after the fix-now action, allowing round 5 to start before the cap fired.

## Root Cause
In Step 3c, the "Round cap — escalate after round 4" block appeared at the bottom of the "If P1 or P2 issues found" branch — after the "fix now" decision path. This meant: if round 4 had P1/P2 findings and the user picked "fix now", the fix ran, round 5 started (Step 3b re-run), and only after round 5 completed did the cap check fire. The cap never prevented round 5 from starting.

## Fix Applied
File: `orchestration/RULES.md`, Step 3c

Reordered the logic so the round cap check appears BEFORE the fix-now/defer decision:

1. Termination check (zero P1/P2 → proceed to Step 4) — unchanged
2. If P1 or P2 found: **Round cap check FIRST** — if current round >= 4, escalate to user immediately, do NOT proceed
3. Only if current round < 4: present the fix-now/defer decision to the user

Key wording added: "check this FIRST before any fix decision" and "Only if current round < 4: proceed with fix-now/defer decision"

## Acceptance Criteria Met
1. Round cap check appears BEFORE the fix-now/defer decision in Step 3c: YES
2. Cap prevents round 5 from starting (user must explicitly approve continuation): YES — the cap now fires before any fix task is spawned
3. Logic is clear — check cap first, then decide on fixes: YES

## Commit
`fix: reorder round cap before fix-now decision in Step 3c (ant-farm-gy9p)`
