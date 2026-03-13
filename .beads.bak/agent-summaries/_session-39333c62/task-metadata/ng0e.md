# Task: ant-farm-ng0e
**Status**: success
**Title**: fix: DMVDC Nitpicker artifact naming in checkpoints.md does not match actual filenames
**Type**: bug
**Priority**: P2
**Epic**: ant-farm-908t
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/checkpoints.md:475 — change naming pattern to match actual convention
- orchestration/templates/checkpoints.md:478 — update example values

## Root Cause
Naming convention in checkpoints.md was written speculatively and never validated against actual Pest Control output.

## Expected Behavior
checkpoints.md DMVDC Nitpicker naming matches actual artifact filenames.

## Acceptance Criteria
1. checkpoints.md DMVDC Nitpicker naming matches actual artifact filenames
2. Example TASK_SUFFIX values match actual Nitpicker review type names
3. Querying pc/ with the documented pattern finds actual files
