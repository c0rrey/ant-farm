#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "[ant-farm] Syncing to ~/.claude/ ..."

# Ensure target directories exist before writing into them
mkdir -p ~/.claude/orchestration/
mkdir -p ~/.claude/agents/

# Back up existing CLAUDE.md before overwrite
if [ -f ~/.claude/CLAUDE.md ]; then
    BACKUP_PATH="${HOME}/.claude/CLAUDE.md.bak.$(date +%Y%m%dT%H%M%S).$$"
    cp ~/.claude/CLAUDE.md "$BACKUP_PATH"
    echo "[ant-farm] Backed up ~/.claude/CLAUDE.md -> $BACKUP_PATH"
fi

# Sync CLAUDE.md (single file copy)
cp "$REPO_ROOT/CLAUDE.md" ~/.claude/CLAUDE.md

# Sync orchestration/ — adds/updates files from source without deleting user-created files in target.
# --delete is intentionally omitted: removing it preserves any custom files adopters have placed
# under ~/.claude/orchestration/. If you need to remove a stale source file from the target,
# delete it manually from ~/.claude/orchestration/.
# Exclude scripts/ — these live under $REPO_ROOT/scripts/ and are synced separately below.
rsync -av --exclude='scripts/' "$REPO_ROOT/orchestration/" ~/.claude/orchestration/

# Sync orchestration scripts (review slot-filling pipeline).
# Only compose-review-skeletons.sh and fill-review-slots.sh are synced here because they are
# the two user-facing pipeline tools that Claude Code subagents invoke at runtime from
# ~/.claude/orchestration/scripts/. Other scripts in scripts/ (e.g. sync-to-claude.sh itself,
# install-hooks.sh, scrub-pii.sh) are developer/maintainer tools that run from the repo
# checkout and are not needed inside the ~/.claude/ tree.
mkdir -p ~/.claude/orchestration/scripts/
for script in "$REPO_ROOT/scripts/compose-review-skeletons.sh" "$REPO_ROOT/scripts/fill-review-slots.sh"; do
    if [ ! -f "$script" ]; then
        echo "[ant-farm] WARNING: expected script not found, skipping: $script" >&2
        continue
    fi
    dest=~/.claude/orchestration/scripts/"$(basename "$script")"
    cp "$script" "$dest"
    chmod +x "$dest"
    echo "[ant-farm] Synced script: $dest"
done

# Sync custom agents to ~/.claude/agents/
AGENTS_CHANGED=false
for agent in "$REPO_ROOT/agents/"*.md; do
    [ -f "$agent" ] || continue
    name="$(basename "$agent")"
    if ! cmp -s "$agent" ~/.claude/agents/"$name"; then
        AGENTS_CHANGED=true
    fi
    cp "$agent" ~/.claude/agents/"$name"
done

echo "[ant-farm] Sync complete."

if [ "$AGENTS_CHANGED" = true ]; then
    echo ""
    echo "[ant-farm] Agent files were updated. Reload Claude Code for changes to take effect."
fi
