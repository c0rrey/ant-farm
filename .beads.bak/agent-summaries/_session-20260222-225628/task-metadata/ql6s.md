# Task: ant-farm-ql6s
**Status**: success
**Title**: Wrong team name 'nitpickers' in reviews.md Fix Workflow (should be 'nitpicker-team')
**Type**: bug
**Priority**: P1
**Epic**: none
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/reviews.md:985 — `team_name: "nitpickers"` should be `"nitpicker-team"`

## Root Cause
`reviews.md:985` uses `team_name: "nitpickers"` for spawning fix agents into the persistent Nitpicker team. The canonical team name established in `big-head-skeleton.md:30` and used consistently across `RULES.md` (lines 237, 319, 339, 341, 343, 536, 537, 538, 649) is `"nitpicker-team"`. Using the wrong name causes the Task tool to target a non-existent team, causing all fix agent spawns to fail at runtime.

## Expected Behavior
Fix agents spawn into the correct persistent Nitpicker team using `team_name: "nitpicker-team"`.

## Acceptance Criteria
1. `reviews.md:985` uses `team_name: "nitpicker-team"`
2. No remaining occurrences of `"nitpickers"` as a team name value in any orchestration file
3. Fix agent spawn instructions in the Fix Workflow section reference the correct canonical team name
