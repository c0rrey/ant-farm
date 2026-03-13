# Task Brief: ant-farm-3mg
**Task**: install-hooks.sh does not ensure sync-to-claude.sh is executable after clone
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/3mg.md

## Context
- **Affected files**: scripts/install-hooks.sh:L91-98 -- currently only ensures scrub-pii.sh is executable, does not check sync-to-claude.sh
- **Root cause**: After fresh clone, sync-to-claude.sh may not have execute permissions. install-hooks.sh ensures scrub-pii.sh is executable (L92-98) but does not do the same for sync-to-claude.sh, which is called by the pre-push hook (L37).
- **Expected behavior**: install-hooks.sh should chmod +x sync-to-claude.sh (and other script dependencies).
- **Acceptance criteria**:
  1. install-hooks.sh ensures sync-to-claude.sh is executable
  2. Other referenced scripts also checked for execute permission

## Scope Boundaries
Read ONLY: scripts/install-hooks.sh:L1-99 (full file, focus on L91-98 chmod section)
Do NOT edit: scripts/sync-to-claude.sh, scripts/scrub-pii.sh, any other scripts

## Focus
Your task is ONLY to add chmod +x for sync-to-claude.sh and other referenced scripts in install-hooks.sh.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
