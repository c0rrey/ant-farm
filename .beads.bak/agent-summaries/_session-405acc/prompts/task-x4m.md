# Task Brief: ant-farm-x4m
**Task**: AGG-031: Add data file format specification to skeleton templates
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-405acc/summaries/x4m.md

## Context
- **Affected files**:
  - `orchestration/templates/dirt-pusher-skeleton.md:L29` — Step 0 section says "Read your task context from {DATA_FILE_PATH}" with no format spec
  - `orchestration/templates/nitpicker-skeleton.md:L19` — Step 0 section says "Read your full review brief from {DATA_FILE_PATH}" with no format spec
- **Root cause**: Skeleton templates reference {DATA_FILE_PATH} but never specify the file format. A cold agent might expect JSON or YAML instead of markdown.
- **Expected behavior**: Each skeleton should include a brief format note (e.g., "The data file is markdown with sections: Context, Scope Boundaries, Focus.") so agents know how to parse it.
- **Acceptance criteria**:
  1. dirt-pusher-skeleton.md specifies the data file format and expected sections
  2. nitpicker-skeleton.md specifies the data file format and expected sections
  3. Both skeletons explicitly state the file is markdown (not JSON/YAML)

## Scope Boundaries
Read ONLY:
- `orchestration/templates/dirt-pusher-skeleton.md:L23-L45` (template section below the --- separator)
- `orchestration/templates/nitpicker-skeleton.md:L13-L38` (template section below the --- separator)
- `orchestration/templates/pantry.md:L46-L75` (data file format reference — read only, do not edit)

Do NOT edit:
- `orchestration/templates/pantry.md` (read-only reference for understanding the data file format)
- `orchestration/templates/implementation.md` (unrelated template)
- `orchestration/templates/reviews.md` (unrelated template)
- `orchestration/templates/checkpoints.md` (unrelated template)
- Any file outside the two skeleton templates

## Focus
Your task is ONLY to add data file format specification (markdown format with expected section names) to the Step 0 instructions in both skeleton templates.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
