# Task Brief: ant-farm-4g7
**Task**: install-hooks.sh generated hook lacks descriptive error on sync script failure
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/4g7.md

## Context
- **Affected files**: scripts/install-hooks.sh:L44-46 -- generated pre-push hook error handling (WARNING message when sync-to-claude.sh fails)
- **Root cause**: Generated pre-push hook does not produce a descriptive error message when sync-to-claude.sh fails. Line 45 only says "WARNING: sync-to-claude.sh failed -- push continuing without sync." with no indication of what went wrong or how to fix it.
- **Expected behavior**: Hook should print a clear error message explaining what failed and how to fix it.
- **Acceptance criteria**:
  1. Generated hook includes descriptive error message on sync failure
  2. Error message suggests remediation steps

## Scope Boundaries
Read ONLY: scripts/install-hooks.sh:L1-99 (full file, focus on L33-47 generated pre-push hook heredoc)
Do NOT edit: scripts/sync-to-claude.sh, scripts/scrub-pii.sh, any other scripts

## Focus
Your task is ONLY to improve the error message in the generated pre-push hook when sync fails.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
