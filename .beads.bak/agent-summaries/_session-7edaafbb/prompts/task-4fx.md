# Task Brief: ant-farm-4fx
**Task**: install-hooks.sh backup uses fixed filename, losing backup history on re-run
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/4fx.md

## Context
- **Affected files**: scripts/install-hooks.sh:L28-30 -- pre-push hook backup uses fixed '.bak' suffix; scripts/install-hooks.sh:L57-60 -- pre-commit hook backup uses fixed '.bak' suffix
- **Root cause**: Backup uses a fixed filename (e.g., pre-push.bak, pre-commit.bak). Re-running install-hooks.sh overwrites the previous backup, losing backup history.
- **Expected behavior**: Backup filenames should include a timestamp or sequence number to preserve history.
- **Acceptance criteria**:
  1. Each backup has a unique filename
  2. Previous backups are not overwritten

## Scope Boundaries
Read ONLY: scripts/install-hooks.sh:L1-99 (full file, focus on L28-30 and L57-60 backup logic)
Do NOT edit: scripts/sync-to-claude.sh, scripts/scrub-pii.sh, any other scripts

## Focus
Your task is ONLY to add timestamps to backup filenames in install-hooks.sh.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
