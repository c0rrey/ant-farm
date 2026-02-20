#!/usr/bin/env bash
# install-hooks.sh — Install ant-farm git hooks into .git/hooks/
#
# Usage: ./scripts/install-hooks.sh
#
# This script installs:
#   - pre-push hook: triggers sync-to-claude.sh on every `git push`
#   - pre-commit hook: runs scrub-pii.sh to strip email addresses from
#     issues.jsonl before any commit, preventing PII from entering git history
#
# Safe to re-run: backs up any existing hook before overwriting.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

if [[ ! -d "$HOOKS_DIR" ]]; then
    echo "ERROR: .git/hooks directory not found. Are you in a git repo?" >&2
    exit 1
fi

# ── pre-push hook ──────────────────────────────────────────────────────────────

HOOK_TARGET="$HOOKS_DIR/pre-push"

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

if ! "$SYNC_SCRIPT"; then
    echo "[ant-farm] WARNING: sync-to-claude.sh failed — push continuing without sync." >&2
fi
HOOK

chmod +x "$HOOK_TARGET"
echo "Installed pre-push hook -> $HOOK_TARGET"
echo "The hook will run scripts/sync-to-claude.sh on every git push."

# ── pre-commit hook (PII scrub) ────────────────────────────────────────────────

PRECOMMIT_TARGET="$HOOKS_DIR/pre-commit"

if [[ -f "$PRECOMMIT_TARGET" ]]; then
    BACKUP="$PRECOMMIT_TARGET.bak"
    echo "Existing pre-commit hook found — backing up to $BACKUP"
    cp "$PRECOMMIT_TARGET" "$BACKUP"
fi

cat > "$PRECOMMIT_TARGET" <<'HOOK'
#!/usr/bin/env bash
# pre-commit: scrub PII from issues.jsonl before each commit.
# bd sync exports raw email addresses from the database; this hook
# ensures they are stripped before the file enters git history.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRUB_SCRIPT="$REPO_ROOT/scripts/scrub-pii.sh"
ISSUES_FILE="$REPO_ROOT/.beads/issues.jsonl"

if [[ ! -x "$SCRUB_SCRIPT" ]]; then
    echo "[ant-farm] ERROR: scrub-pii.sh not found or not executable — cannot scrub PII. Commit blocked." >&2
    exit 1
fi

# Only run the scrub if issues.jsonl is staged for this commit.
if git diff --cached --name-only | grep -q "^\.beads/issues\.jsonl$"; then
    "$SCRUB_SCRIPT"
    # Re-stage the scrubbed file so the clean version is what gets committed.
    git add "$ISSUES_FILE"
    echo "[ant-farm] PII scrub applied and re-staged: .beads/issues.jsonl"
fi
HOOK

chmod +x "$PRECOMMIT_TARGET"
echo "Installed pre-commit hook -> $PRECOMMIT_TARGET"
echo "The hook will run scripts/scrub-pii.sh before committing .beads/issues.jsonl."

# Ensure the scrub script is executable so the pre-commit hook can run it.
SCRUB_SCRIPT_PATH="$REPO_ROOT/scripts/scrub-pii.sh"
if [[ -f "$SCRUB_SCRIPT_PATH" ]]; then
    chmod +x "$SCRUB_SCRIPT_PATH"
    echo "Ensured scripts/scrub-pii.sh is executable."
else
    echo "WARNING: scripts/scrub-pii.sh not found — pre-commit hook will block commits until it is present." >&2
fi
