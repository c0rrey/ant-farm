# Task: ant-farm-ha7a.4
**Status**: success
**Title**: Add P3 auto-filing, termination check, and mandatory re-review to reviews.md
**Type**: task
**Priority**: P2
**Epic**: ant-farm-ha7a
**Agent Type**: technical-writer
**Dependencies**: blocks: [ant-farm-ha7a.11, ant-farm-ha7a.5], blockedBy: [ant-farm-ha7a.2]

## Affected Files
- `orchestration/templates/reviews.md:475-688` — Big Head consolidation block and Queen's Step 3c/4 sections; adds P3 Auto-Filing section, Termination Check subsection, changes "optional" to "MANDATORY", and adds Round 1 only blockquote

## Root Cause
The review loop has no termination condition and no automatic P3 filing for round 2+. Round 2+ P3 findings need to be auto-filed without user involvement, and the loop needs a termination check (zero P1/P2 = done). Also, re-running reviews after fixes is currently "optional" but must be mandatory.

## Expected Behavior
- `### P3 Auto-Filing (Round 2+ Only)` section exists after the bead filing block, contains `bd epic create` and `bd dep add ... --type parent-child`
- `### Termination Check (zero P1/P2 findings)` subsection exists in Queen's Step 3c, positioned before `### If P1 or P2 issues found:`
- "Re-run reviews" changed from "(optional)" to "(MANDATORY)"
- `### Handle P3 Issues (Queen's Step 4)` is followed immediately by `> **Round 1 only.**` blockquote

## Acceptance Criteria
1. `grep "### P3 Auto-Filing (Round 2+ Only)" orchestration/templates/reviews.md` returns a match
2. P3 Auto-Filing section contains both `bd epic create` and `bd dep add` with `--type parent-child`
3. `grep "### Termination Check" orchestration/templates/reviews.md` returns a match, positioned before `### If P1 or P2 issues found:`
4. `grep "Re-run reviews.*MANDATORY" orchestration/templates/reviews.md` returns a match (not "optional")
5. `### Handle P3 Issues (Queen's Step 4)` is followed immediately by a `> **Round 1 only.**` blockquote
