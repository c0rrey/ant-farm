# Task Brief: ant-farm-z69
**Task**: Pre-push hook blocks all git pushes when sync-to-claude.sh fails
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/z69.md

## Context
- **Affected files**: scripts/install-hooks.sh:L34-45 (generated pre-push hook uses `set -euo pipefail` which causes any sync-to-claude.sh failure to exit non-zero, blocking git push)
- **Root cause**: install-hooks.sh:L34-45 generates a pre-push hook with `set -euo pipefail` (L35) that runs sync-to-claude.sh (L44). If sync-to-claude.sh fails for any reason (rsync error, permissions, disk space), `set -e` causes the hook to exit non-zero, which blocks the `git push` entirely. The sync operation is non-critical -- a failed sync should warn the user but not prevent pushing code. The sync script not being found/executable (L39-41) should still block, since that indicates a broken installation.
- **Expected behavior**: Sync failure produces a warning but the push proceeds. Sync success still works normally. Missing/non-executable sync script still blocks (as it does now).
- **Acceptance criteria**:
  1. Sync failure (sync-to-claude.sh exits non-zero) produces a warning message but push proceeds (hook exits 0)
  2. Sync success still works normally (no behavioral change on happy path)

## Scope Boundaries
Read ONLY: scripts/install-hooks.sh:L23-49
Do NOT edit: scripts/sync-to-claude.sh, scripts/scrub-pii.sh, docs/installation-guide.md, orchestration/ files

## Focus
Your task is ONLY to make the pre-push hook resilient to sync-to-claude.sh failures while preserving the script-missing guard.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
