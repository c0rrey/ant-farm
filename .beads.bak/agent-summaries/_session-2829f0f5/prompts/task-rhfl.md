# Task Brief: ant-farm-rhfl
**Task**: fix: MEMORY.md Project Structure still lists colony-tsa.md as being eliminated
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2829f0f5/summaries/rhfl.md

## Context
- **Affected files**:
  - ~/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md:L28 -- Project Structure section
- **Root cause**: MEMORY.md Project Structure lists "orchestration/templates/colony-tsa.md -- Colony TSA (being eliminated, see HANDOFF)" but colony-tsa.md was archived months ago. The "Completed: Colony TSA Eliminated" section later in MEMORY.md correctly records the completion, but the Project Structure was never updated.
- **Expected behavior**: MEMORY.md Project Structure shows colony-tsa.md at its archived path with completed status.
- **Acceptance criteria**:
  1. MEMORY.md Project Structure shows colony-tsa.md at its archived path with completed status

## Scope Boundaries
Read ONLY: ~/.claude/projects/-Users-correy-projects-ant-farm/memory/MEMORY.md:L24-35
Do NOT edit: Any file other than MEMORY.md. Do not restructure or rewrite other MEMORY.md sections.

## Focus
Your task is ONLY to update the Project Structure entry for colony-tsa.md in MEMORY.md to reflect its archived status.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
