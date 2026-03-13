# Task: ant-farm-vxcn
**Status**: success
**Title**: Pantry skips writing preview file to previews/ directory
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/pantry.md:141-169 — Step 3 (Write Combined Prompt Previews) where the preview file is mentioned but not enforced as mandatory output

## Root Cause
The Pantry agent writes the task brief to prompts/task-{suffix}.md but returns without writing the combined preview to previews/preview-{suffix}.md. The agent narrates the step but exits before executing it. The preview file is not clearly listed as a mandatory output artifact in the Pantry template.

## Expected Behavior
The preview file should be a hard requirement in pantry.md with explicit verification before returning. Pantry must not return successfully without writing all preview files.

## Acceptance Criteria
1. previews/ output is listed as a hard requirement in pantry.md
2. Explicit verification step added before Pantry returns (check file exists)
3. Pantry cannot return without writing preview files
