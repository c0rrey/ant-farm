# Task: ant-farm-ha7a.6
**Status**: success
**Title**: Update RULES.md Step 3b/3c for round-aware review loop
**Type**: task
**Priority**: P2
**Epic**: ant-farm-ha7a
**Agent Type**: technical-writer
**Dependencies**: blocks: [ant-farm-ha7a.11], blockedBy: [ant-farm-ha7a.1]

## Affected Files
- `orchestration/RULES.md:89-135` — Step 3b and Step 3c sections and Hard Gates table; replace with round-aware versions that read review round from session state and support termination check and re-run path

## Root Cause
RULES.md Step 3b/3c contain stale hardcoded review protocol (always 6-member team, no round tracking, no termination path). Must be updated so the Queen reads review round from session state, passes it to Pantry, and handles termination (0 P1/P2 = proceed) vs. fix-and-rerun path.

## Expected Behavior
- Step 3b contains `**Review round**: read from session state (default: 1)` and both `**Round 1**:` and `**Round 2+**:` team composition instructions
- Step 3c contains `**Termination check**: If zero P1 and zero P2 findings:` with round-specific P3 handling
- Step 3c fix-now path says `re-run Step 3b with round N+1` and mentions `increment review round, record fix commit range`
- `grep "L631" orchestration/RULES.md` returns NO match (stale reference removed)
- Hard Gates Reviews row contains "re-runs after fix cycles with reduced scope (round 2+)"

## Acceptance Criteria
1. Step 3b contains `**Review round**: read from session state (default: 1)` and both `**Round 1**:` and `**Round 2+**:` team composition instructions
2. Step 3c contains `**Termination check**: If zero P1 and zero P2 findings:` with round-specific P3 handling
3. Step 3c fix-now path says `re-run Step 3b with round N+1` and mentions `increment review round, record fix commit range`
4. `grep "L631" orchestration/RULES.md` returns NO match (stale reference removed)
5. Hard Gates Reviews row contains "re-runs after fix cycles with reduced scope (round 2+)"
