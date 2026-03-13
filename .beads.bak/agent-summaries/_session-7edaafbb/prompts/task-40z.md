# Task Brief: ant-farm-40z
**Task**: rsync --delete silently removes custom user files from ~/.claude/orchestration/
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/40z.md

## Context
- **Affected files**: scripts/sync-to-claude.sh:L22-24 -- rsync --delete flag removes files not in source
- **Root cause**: sync-to-claude.sh uses rsync --delete to sync orchestration files (L24). This flag removes any custom user files in the target directory that are not present in the source. Adopters who add their own files under ~/.claude/orchestration/ will have them silently deleted on every sync.
- **Expected behavior**: Sync should add/update files from source without deleting user-created files in the target.
- **Acceptance criteria**:
  1. rsync no longer uses --delete (or equivalent protection is added)
  2. Custom user files in ~/.claude/orchestration/ survive sync operations
  3. Stale files from removed source are documented or handled explicitly

## Scope Boundaries
Read ONLY: scripts/sync-to-claude.sh:L1-53 (full file, focus on L22-24 rsync invocation)
Do NOT edit: scripts/install-hooks.sh, scripts/scrub-pii.sh, any other scripts

## Focus
Your task is ONLY to fix the rsync --delete behavior that silently removes custom user files.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
