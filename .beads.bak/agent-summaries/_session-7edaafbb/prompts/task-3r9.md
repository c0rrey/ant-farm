# Task Brief: ant-farm-3r9
**Task**: sync-to-claude.sh backup timestamp has 1-second collision risk
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/3r9.md

## Context
- **Affected files**: scripts/sync-to-claude.sh:L14 -- backup timestamp generation using date +%Y%m%dT%H%M%S
- **Root cause**: Backup timestamp uses second-level granularity. If sync runs twice within the same second, the second backup overwrites the first.
- **Expected behavior**: Backup filenames should be collision-resistant (e.g., include PID or nanoseconds).
- **Acceptance criteria**:
  1. Backup timestamps are collision-resistant
  2. Existing backup behavior preserved for normal use

## Scope Boundaries
Read ONLY: scripts/sync-to-claude.sh:L1-53 (full file, focus on L14 backup path generation)
Do NOT edit: scripts/install-hooks.sh, scripts/scrub-pii.sh, any other scripts

## Focus
Your task is ONLY to make the CLAUDE.md backup filename collision-resistant.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
