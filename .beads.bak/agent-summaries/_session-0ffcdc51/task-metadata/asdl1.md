# Task: ant-farm-asdl.1
**Status**: success
**Title**: Add cross-session dedup step and description template to big-head-skeleton.md
**Type**: task
**Priority**: P1
**Epic**: ant-farm-asdl
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [ant-farm-asdl.2, ant-farm-asdl.3, ant-farm-asdl.4, ant-farm-asdl.5], blockedBy: []}

## Affected Files
- `orchestration/templates/big-head-skeleton.md:105-125` — Insert cross-session dedup step after step 6 (line 105), replace bd create in PASS branch (line 111), update P3 auto-filing (line 116), add to output requirements (lines 121-125)

## Root Cause
The Big Head skeleton template has bare `bd create` commands without `--description`/`--body-file`, and no step to check existing beads before filing. This causes beads with title-only descriptions and cross-session duplicate filings.

## Expected Behavior
Every `bd create` command should use `--body-file` with a structured description template (Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria). A cross-session dedup step should query existing beads before filing.

## Acceptance Criteria
1. No bare bd create command remains in big-head-skeleton.md -- every instance includes --body-file
2. The description template in the PASS branch contains all 5 sections: Root Cause, Affected Surfaces, Fix, Changes Needed, Acceptance Criteria
3. A cross-session dedup step exists before the write-summary step, containing 'bd list --status=open' and 'bd search'
4. The output requirements list includes 'Cross-session dedup log'
5. Step numbers are sequential with no gaps or duplicates, and all internal cross-references resolve correctly
