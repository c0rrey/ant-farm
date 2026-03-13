# Task: ant-farm-zeu
**Status**: success
**Title**: (BUG) Templates lack explicit guards for missing or empty input artifacts
**Type**: bug
**Priority**: P3
**Epic**: ant-farm-21d
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- `orchestration/templates/pantry.md` (line 26) — No validation that task-metadata files exist before reading (Step 2)
- `orchestration/templates/pantry.md` (lines 26-32) — No handling for empty or malformed metadata fields
- `orchestration/templates/pantry.md` (line 94) — Review mode has no handling for empty changed-file list
- `orchestration/templates/big-head-skeleton.md` (line 23) — Step 1 says 'FAIL immediately if any missing' but doesn't specify where to write a failure artifact
- `orchestration/templates/checkpoints.md` (line 259) — No specification for handling bd show failures in Checkpoint B

## Root Cause
Multiple templates assume their input artifacts exist and are well-formed without specifying explicit error behavior when they are missing or empty. Systematic gap across the template suite — happy path covered, missing-input path not specified.

## Expected Behavior
Establish a convention across all templates: "If an expected input artifact is missing or empty, write a brief failure artifact to the expected output path explaining the issue, then return FAIL with error details."

## Acceptance Criteria
1. Each template has explicit instructions for handling missing/empty inputs
2. Failure artifacts are written to expected output paths so downstream consumers are not left guessing
3. Infrastructure failures (tool unavailability) are distinguished from substance failures (agent quality)
