#!/usr/bin/env bash
# install-hooks.sh — Install ant-farm git hooks into .git/hooks/
#
# Usage: ./scripts/install-hooks.sh
#
# This script installs the pre-push hook that triggers sync-to-claude.sh
# on every `git push`. The hook keeps ~/.claude/ in sync with the versioned
# agents/, orchestration/, and CLAUDE.md files in this repo.
#
# Safe to re-run: backs up any existing hook before overwriting.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOK_TARGET="$HOOKS_DIR/pre-push"

if [[ ! -d "$HOOKS_DIR" ]]; then
    echo "ERROR: .git/hooks directory not found. Are you in a git repo?" >&2
    exit 1
fi

# Back up any existing hook so nothing is silently overwritten.
if [[ -f "$HOOK_TARGET" ]]; then
    BACKUP="$HOOK_TARGET.bak"
    echo "Existing pre-push hook found — backing up to $BACKUP"
    cp "$HOOK_TARGET" "$BACKUP"
fi

cat > "$HOOK_TARGET" <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail

SYNC_SCRIPT="$(git rev-parse --show-toplevel)/scripts/sync-to-claude.sh"

if [[ ! -x "$SYNC_SCRIPT" ]]; then
    echo "[ant-farm] ERROR: sync script not found or not executable: $SYNC_SCRIPT" >&2
    exit 1
fi

"$SYNC_SCRIPT"
HOOK

chmod +x "$HOOK_TARGET"

echo "Installed pre-push hook -> $HOOK_TARGET"
echo "The hook will run scripts/sync-to-claude.sh on every git push."
