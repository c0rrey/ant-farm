# Task Brief: ant-farm-rja
**Task**: sync-to-claude.sh agent glob fails silently when agents/ directory missing
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/rja.md

## Context
- **Affected files**: scripts/sync-to-claude.sh:L38-39 -- agent file glob pattern ('for agent in "$REPO_ROOT/agents/"*.md')
- **Root cause**: When agents/ directory does not exist, the glob pattern fails silently. No warning that agent files could not be synced.
- **Expected behavior**: Missing agents/ directory should produce a warning or be handled gracefully.
- **Acceptance criteria**:
  1. Missing agents/ directory produces a warning
  2. Script continues normally when agents/ is absent

## Scope Boundaries
Read ONLY: scripts/sync-to-claude.sh:L1-53 (full file, focus on L36-45 agent sync section)
Do NOT edit: scripts/install-hooks.sh, scripts/scrub-pii.sh, any other scripts

## Focus
Your task is ONLY to add a warning when the agents/ directory is missing during sync.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
