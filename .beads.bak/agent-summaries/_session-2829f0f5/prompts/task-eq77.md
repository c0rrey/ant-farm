# Task Brief: ant-farm-eq77
**Task**: fix: docs don't clarify code-reviewer is a custom agent outside the repo
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2829f0f5/summaries/eq77.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L17 -- code-reviewer agent type reference
  - SETUP.md -- possibly needs note about code-reviewer setup (Scout note: no specific line; content to be added)
  - orchestration/RULES.md:L278-286 -- Agent Types table (code-reviewer absent)
- **Root cause**: checkpoints.md references `code-reviewer` as the agent type Pest Control spawns, but it exists only at ~/.claude/agents/code-reviewer.md (user global), not in the repo. sync-to-claude.sh does not deploy it. New adopters would not have it. Decision depends on DRIFT-002 (ant-farm-h94m) resolution, which is already closed.
- **Expected behavior**: code-reviewer deployment path is documented OR agent moved into repo agents/. Decision aligns with DRIFT-002 resolution.
- **Acceptance criteria**:
  1. code-reviewer deployment path is documented OR agent moved into repo agents/
  2. Decision aligns with DRIFT-002 resolution

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md:L10-25, orchestration/RULES.md:L270-290, SETUP.md (full file, to find insertion point), ~/.claude/agents/code-reviewer.md (reference only)
Do NOT edit: ~/.claude/agents/code-reviewer.md, scripts/sync-to-claude.sh, or any code files. This is a documentation-only task.

## Focus
Your task is ONLY to document the code-reviewer deployment path so new adopters know where it comes from.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
