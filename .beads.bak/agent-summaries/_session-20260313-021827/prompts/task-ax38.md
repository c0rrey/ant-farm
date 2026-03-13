# Task Brief: ant-farm-ax38
**Task**: Migrate CLAUDE.md files (semantic)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/ax38.md

## Context
- **Affected files**:
  - CLAUDE.md:L38,L67,L72 (bd references and .beads/ paths in project-level system prompt)
  - ~/.claude/CLAUDE.md:L38,L67,L72 (global system prompt, must stay in sync with project CLAUDE.md)
- **Root cause**: CLAUDE.md files are system prompts loaded at conversation start. They contain bd references (L38: bd show/ready/list/blocked prohibition; L67: bd sync in landing-the-plane) and .beads/ paths (L72: session artifacts path) that need semantic migration.
- **Expected behavior**: Both CLAUDE.md files updated with crumb references, bd sync removed, .beads/ -> .crumbs/ paths, beads -> crumbs terminology.
- **Acceptance criteria**:
  1. Project CLAUDE.md: all bd references replaced with crumb, bd sync removed from landing-the-plane
  2. Global ~/.claude/CLAUDE.md: matching changes applied (files should stay in sync)
  3. .beads/ paths updated to .crumbs/ in both files
  4. 'beads'/'Beads' terminology updated to 'crumbs'/'Crumbs'
  5. grep -c '\bbd\b' on both CLAUDE.md files returns 0
  6. Landing-the-plane workflow no longer references bd sync

## Scope Boundaries
Read ONLY: CLAUDE.md (full file), ~/.claude/CLAUDE.md (full file)
Do NOT edit: Any orchestration templates, RULES.md, or any other file. Only touch the two CLAUDE.md files.

## Focus
Your task is ONLY to migrate bd CLI references and .beads/ paths in both CLAUDE.md files to crumb equivalents.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
