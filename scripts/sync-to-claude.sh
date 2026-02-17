#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "[ant-farm] Syncing to ~/.claude/ ..."

# Sync CLAUDE.md (single file copy)
cp "$REPO_ROOT/CLAUDE.md" ~/.claude/CLAUDE.md

# Sync orchestration/ (--delete removes files from target that no longer exist in source)
rsync -av --delete "$REPO_ROOT/orchestration/" ~/.claude/orchestration/

echo "[ant-farm] Sync complete."
