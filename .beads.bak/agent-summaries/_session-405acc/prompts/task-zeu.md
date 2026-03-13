# Task Brief: ant-farm-zeu
**Task**: (BUG) Templates lack explicit guards for missing or empty input artifacts
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-405acc/summaries/zeu.md

## Context
- **Affected files**:
  - `orchestration/templates/pantry.md:L26` — No validation that task-metadata files exist before reading (Step 2)
  - `orchestration/templates/pantry.md:L26-L32` — No handling for empty or malformed metadata fields
  - `orchestration/templates/pantry.md:L94` — Review mode has no handling for empty changed-file list (Step 4 return)
  - `orchestration/templates/big-head-skeleton.md:L23` — Step 1 says "FAIL immediately if any missing" but does not specify where to write a failure artifact
  - `orchestration/templates/checkpoints.md:L330` — DMVDC Check 2 runs `bd show {TASK_ID}` with no specification for handling bd show failures
- **Root cause**: Multiple templates assume their input artifacts exist and are well-formed without specifying explicit error behavior when they are missing or empty. Systematic gap across the template suite — happy path covered, missing-input path not specified.
- **Expected behavior**: Establish a convention across all templates: "If an expected input artifact is missing or empty, write a brief failure artifact to the expected output path explaining the issue, then return FAIL with error details."
- **Acceptance criteria**:
  1. Each affected template has explicit instructions for handling missing/empty inputs
  2. Failure artifacts are written to expected output paths so downstream consumers are not left guessing
  3. Infrastructure failures (tool unavailability) are distinguished from substance failures (agent quality)

## Scope Boundaries
Read ONLY:
- `orchestration/templates/pantry.md:L24-L35` (Step 2 metadata read section)
- `orchestration/templates/pantry.md:L92-L100` (Step 4 return section in review mode)
- `orchestration/templates/big-head-skeleton.md:L20-L30` (Step 1 fail-immediately instruction)
- `orchestration/templates/checkpoints.md:L329-L340` (DMVDC Check 2 bd show section)

Do NOT edit:
- `orchestration/templates/dirt-pusher-skeleton.md` (not listed in affected files)
- `orchestration/templates/nitpicker-skeleton.md` (not listed in affected files)
- `orchestration/templates/reviews.md` (not listed in affected files)
- `orchestration/templates/implementation.md` (not listed in affected files)
- Any sections of the affected files outside the specified line ranges

## Focus
Your task is ONLY to add explicit missing/empty input guards to the five affected locations listed above. Establish the convention: write a failure artifact to the expected output path, then return FAIL with error details. Distinguish infrastructure failures from substance failures.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
