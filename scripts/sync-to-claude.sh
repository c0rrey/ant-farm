#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "[ant-farm] Syncing to ~/.claude/ ..."

# Sync CLAUDE.md (single file copy)
cp "$REPO_ROOT/CLAUDE.md" ~/.claude/CLAUDE.md

# Sync orchestration/ (--delete removes files from target that no longer exist in source)
rsync -av --delete "$REPO_ROOT/orchestration/" ~/.claude/orchestration/

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
    echo "[ant-farm] ⚠ Agent files were updated. Reload Claude Code for changes to take effect."
fi
