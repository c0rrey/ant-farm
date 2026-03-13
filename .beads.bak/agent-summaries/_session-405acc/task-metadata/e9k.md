# Task: ant-farm-e9k
**Status**: success
**Title**: AGG-035: Add remediation path for missing Nitpicker reports
**Type**: task
**Priority**: P2
**Epic**: ant-farm-21d
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- `orchestration/templates/reviews.md` (Big Head Consolidation Protocol section, ~lines 321-480) — Big Head prerequisite gate logic; needs a remediation step added for missing reports

## Root Cause
reviews.md instructs Big Head not to proceed until all 4 reports are present but never says what to DO about a missing report. No messaging, no error return, no timeout specified.

## Expected Behavior
Big Head should return an error to the Queen listing missing reports and requesting re-spawn rather than waiting indefinitely.

## Acceptance Criteria
1. reviews.md Big Head section includes a remediation step for missing reports
2. The step specifies: return error to Queen, list missing reports, request re-spawn
3. A timeout or maximum wait is specified before triggering the remediation path
