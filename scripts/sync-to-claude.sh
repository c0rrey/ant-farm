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
    cp ~/.claude/CLAUDE.md "$BACKUP_PATH" || { echo "[ant-farm] ERROR: backup failed" >&2; exit 1; }
    echo "[ant-farm] Backed up ~/.claude/CLAUDE.md -> $BACKUP_PATH"
fi

# Sync CLAUDE.md (single file copy)
cp "$REPO_ROOT/CLAUDE.md" ~/.claude/CLAUDE.md

# Sync orchestration/ — adds/updates files from source without deleting user-created files in target.
# --delete is intentionally omitted: removing it preserves any custom files adopters have placed
# under ~/.claude/orchestration/. If you need to remove a stale source file from the target,
# delete it manually from ~/.claude/orchestration/.
# Exclude scripts/ — these live under $REPO_ROOT/scripts/ and are synced separately below.
rsync -av --exclude='scripts/' --exclude='_archive/' "$REPO_ROOT/orchestration/" ~/.claude/orchestration/

# Sync orchestration scripts (review prompt pipeline).
# Only build-review-prompts.sh is synced here because it is the user-facing pipeline tool
# that Claude Code subagents invoke at runtime from ~/.claude/orchestration/scripts/.
# Other scripts in scripts/ (e.g. sync-to-claude.sh itself, install-hooks.sh, scrub-pii.sh)
# are developer/maintainer tools that run from the repo checkout and are not needed inside
# the ~/.claude/ tree.
mkdir -p ~/.claude/orchestration/scripts/
if [ ! -f "$REPO_ROOT/scripts/build-review-prompts.sh" ]; then
    echo "[ant-farm] WARNING: expected script not found, skipping: $REPO_ROOT/scripts/build-review-prompts.sh" >&2
else
    cp "$REPO_ROOT/scripts/build-review-prompts.sh" ~/.claude/orchestration/scripts/build-review-prompts.sh
    chmod +x ~/.claude/orchestration/scripts/build-review-prompts.sh
    echo "[ant-farm] Synced script: ~/.claude/orchestration/scripts/build-review-prompts.sh"
fi

# Sync custom agents to ~/.claude/agents/
AGENTS_CHANGED=false
if [ ! -d "$REPO_ROOT/agents" ]; then
    echo "[ant-farm] WARNING: agents/ directory not found, skipping agent sync: $REPO_ROOT/agents" >&2
else
    agents_synced=0
    for agent in "$REPO_ROOT/agents/"*.md; do
        [ -f "$agent" ] || continue
        name="$(basename "$agent")"
        if ! cmp -s "$agent" ~/.claude/agents/"$name"; then
            AGENTS_CHANGED=true
        fi
        cp "$agent" ~/.claude/agents/"$name"
        agents_synced=$((agents_synced + 1))
    done
    if [ "$agents_synced" -eq 0 ]; then
        echo "[ant-farm] WARNING: agents/ directory exists but contains no .md files — no agents synced." >&2
    fi
fi

echo "[ant-farm] Sync complete."

# Preflight: code-reviewer.md must be manually installed; warn if missing.
if [ ! -f "${HOME}/.claude/agents/code-reviewer.md" ]; then
    echo "[ant-farm] WARNING: ~/.claude/agents/code-reviewer.md is missing -- Nitpicker team members will fail to spawn. Copy it manually to ~/.claude/agents/code-reviewer.md before starting a review session." >&2
fi

if [ "$AGENTS_CHANGED" = true ]; then
    echo ""
    echo "[ant-farm] Agent files were updated. Reload Claude Code for changes to take effect."
fi
