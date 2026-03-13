# Task Brief: ant-farm-o058
**Task**: compose-review-skeletons.sh extract_agent_section includes YAML frontmatter body
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/o058.md

## Context
- **Affected files**: scripts/compose-review-skeletons.sh:L71-74 -- extract_agent_section awk pattern
- **Root cause**: Uses awk '/^---$/{found=1; next} found{print}' to extract after first '---'. But YAML frontmatter uses paired '---' delimiters. Pattern starts printing after first --- including frontmatter content, when it should only start after the closing --- of the frontmatter block.
- **Expected behavior**: Only content after closing --- of frontmatter should be extracted.
- **Acceptance criteria**:
  1. Only content after closing --- of frontmatter is extracted
  2. Frontmatter fields are not included in skeleton body

## Scope Boundaries
Read ONLY: scripts/compose-review-skeletons.sh:L1-227 (full file, focus on L71-74 extract_agent_section function)
Do NOT edit: scripts/fill-review-slots.sh, scripts/parse-progress-log.sh, any other scripts

## Focus
Your task is ONLY to fix the extract_agent_section awk pattern to skip YAML frontmatter correctly.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
