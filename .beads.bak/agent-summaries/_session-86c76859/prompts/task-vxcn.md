# Task Brief: ant-farm-vxcn
**Task**: Pantry skips writing preview file to previews/ directory
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-86c76859/summaries/vxcn.md

## Context
- **Affected files**:
  - orchestration/templates/pantry.md:L141-169 -- Step 3 (Write Combined Prompt Previews) and Step 4 (Write Session Summary) where the preview file is mentioned but not enforced as mandatory output
- **Root cause**: The Pantry agent writes the task brief to prompts/task-{suffix}.md but returns without writing the combined preview to previews/task-{suffix}-preview.md. The agent narrates the step but exits before executing it. The preview file is not clearly listed as a mandatory output artifact in the Pantry template, and there is no verification step that checks the file exists before returning.
- **Expected behavior**: The preview file should be a hard requirement in pantry.md with explicit verification before returning. Pantry must not return successfully without writing all preview files.
- **Acceptance criteria**:
  1. previews/ output is listed as a hard requirement in pantry.md
  2. Explicit verification step added before Pantry returns (check file exists)
  3. Pantry cannot return without writing preview files

## Scope Boundaries
Read ONLY:
- orchestration/templates/pantry.md:L141-210 (Step 3 through Step 5 -- the preview writing, session summary, and return steps)

Do NOT edit:
- orchestration/templates/pantry.md:L1-140 (Steps 1-2 -- task brief composition logic is working correctly)
- orchestration/templates/pantry.md:L214-418 (Section 2 Review Mode -- deprecated, not relevant)
- orchestration/RULES.md (Queen workflow)
- orchestration/templates/dirt-pusher-skeleton.md (skeleton template)
- orchestration/templates/implementation.md (implementation template)
- Any scripts/ files

## Focus
Your task is ONLY to add mandatory output enforcement and verification for preview files in pantry.md Steps 3-5.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
