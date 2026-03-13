# Task Brief: ant-farm-rue4
**Task**: Migrate RULES.md (semantic)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/rue4.md

## Context
- **Affected files**: orchestration/RULES.md:L16,L21,L58,L70,L96-97,L198,L215,L231,L242,L301,L389 (bd command references, .beads/ paths, crash recovery, session directory creation)
- **Root cause**: RULES.md is the Queen's workflow specification requiring structural changes beyond bd -> crumb: crash recovery paths, exec-summary copy addition, bd sync removal, session directory references.
- **Expected behavior**: All bd references replaced; crash recovery paths updated; exec-summary copy step added; bd sync removed; session paths migrated.
- **Acceptance criteria**:
  1. All bd command references replaced with crumb equivalents
  2. Crash recovery paths updated from .beads/agent-summaries/ to .crumbs/sessions/ (L70, L301, L389)
  3. Landing-the-plane includes exec-summary copy step to .crumbs/history/
  4. bd sync references removed from landing-the-plane workflow (L215)
  5. Session directory creation uses .crumbs/sessions/_session-{timestamp}/ pattern (L301)
  6. grep -c '\bbd\b' orchestration/RULES.md returns 0 (excluding any _archive references)

## Scope Boundaries
Read ONLY: orchestration/RULES.md (full file)
Do NOT edit: Any file other than orchestration/RULES.md. Do not change workflow step ordering, hard gates, concurrency rules, or template lookup table beyond the command/path migrations.

## Focus
Your task is ONLY to migrate bd CLI commands, .beads/ paths, and related terminology in RULES.md to crumb/.crumbs/ equivalents.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
