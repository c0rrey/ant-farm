# Task: ant-farm-wg2i
**Status**: success
**Title**: fix: installed pre-push hook is fatal on sync failure, contradicting install-hooks.sh non-fatal design
**Type**: bug
**Priority**: P1
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- .git/hooks/pre-push -- regenerate via install-hooks.sh to get non-fatal sync wrapper
- CONTRIBUTING.md:161 -- fix rsync --delete claim, add _archive/ exclusion note
- CONTRIBUTING.md -- add reminder about re-running install-hooks.sh after changes
- scripts/install-hooks.sh -- source of truth (read-only reference, not modified)

## Root Cause
The installed .git/hooks/pre-push is an older version that runs sync-to-claude.sh under set -euo pipefail with no error handling. The current install-hooks.sh wraps sync in a non-fatal if block. The hook was never regenerated after install-hooks.sh was updated.

## Expected Behavior
Push should succeed even when sync-to-claude.sh fails. The installed hook should match the current install-hooks.sh output (non-fatal sync).

## Acceptance Criteria
1. Installed .git/hooks/pre-push matches output of install-hooks.sh (non-fatal sync)
2. CONTRIBUTING.md rsync description matches actual sync-to-claude.sh behavior (no --delete, excludes _archive/)
3. CONTRIBUTING.md includes guidance on re-running install-hooks.sh after pulling changes
4. Push succeeds even when sync-to-claude.sh fails (manual test)
