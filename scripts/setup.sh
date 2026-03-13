#!/usr/bin/env bash
# setup.sh — Install ant-farm plugin files to ~/.claude/ and PATH.
#
# Replaces sync-to-claude.sh. Copies:
#   agents/*.md         → ~/.claude/agents/
#   orchestration/      → ~/.claude/orchestration/  (non-_archive files)
#   scripts/build-review-prompts.sh → ~/.claude/orchestration/scripts/
#   crumb.py            → ~/.local/bin/crumb
#
# Backs up any existing target file with a timestamped .bak suffix before
# overwriting. Idempotent: re-running updates files; each run generates at
# most one backup per file (using a single TS for the whole run).
#
# Usage:
#   ./scripts/setup.sh
#   ./scripts/setup.sh --dry-run   # print what would change, no writes
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TS="$(date +%Y%m%dT%H%M%S)"
DRY_RUN=false

# ---------------------------------------------------------------------------
# Parse args
# ---------------------------------------------------------------------------
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        *) echo "[ant-farm] ERROR: unknown argument: $arg" >&2; exit 1 ;;
    esac
done

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log() { echo "[ant-farm] $*"; }
warn() { echo "[ant-farm] WARNING: $*" >&2; }

# backup_and_copy SRC DST
#   If DST exists and differs from SRC, back it up then copy.
#   If DST does not exist, just copy.
backup_and_copy() {
    local src="$1"
    local dst="$2"
    local dst_dir
    dst_dir="$(dirname "$dst")"

    if [ "$DRY_RUN" = true ]; then
        if [ -f "$dst" ]; then
            if cmp -s "$src" "$dst"; then
                log "[dry-run] unchanged: $dst"
            else
                log "[dry-run] would backup + update: $dst -> ${dst}.bak.${TS}"
            fi
        else
            log "[dry-run] would install: $dst"
        fi
        return
    fi

    mkdir -p "$dst_dir"

    if [ -f "$dst" ]; then
        if ! cmp -s "$src" "$dst"; then
            local bak="${dst}.bak.${TS}"
            cp "$dst" "$bak" || { echo "[ant-farm] ERROR: backup failed for $dst" >&2; exit 1; }
            log "Backed up: $dst -> $bak"
        else
            log "Unchanged: $dst"
            return
        fi
    fi

    cp "$src" "$dst"
    log "Installed: $dst"
}

# ---------------------------------------------------------------------------
# Validate prerequisites
# ---------------------------------------------------------------------------
if [ ! -d "$REPO_ROOT/agents" ]; then
    warn "agents/ directory not found: $REPO_ROOT/agents — skipping agent install"
fi
if [ ! -d "$REPO_ROOT/orchestration" ]; then
    warn "orchestration/ directory not found: $REPO_ROOT/orchestration — skipping orchestration install"
fi

# ---------------------------------------------------------------------------
# Step 1: Install agent definitions → ~/.claude/agents/
# ---------------------------------------------------------------------------
log "Installing agent definitions → ~/.claude/agents/ ..."
AGENTS_CHANGED=false
agents_installed=0

if [ -d "$REPO_ROOT/agents" ]; then
    if [ "$DRY_RUN" = false ]; then
        mkdir -p "${HOME}/.claude/agents/"
    fi
    for agent_file in "$REPO_ROOT/agents/"*.md; do
        [ -f "$agent_file" ] || continue
        name="$(basename "$agent_file")"
        dst="${HOME}/.claude/agents/${name}"

        # Track whether any agent file actually changed (for restart warning)
        if [ -f "$dst" ] && ! cmp -s "$agent_file" "$dst"; then
            AGENTS_CHANGED=true
        elif [ ! -f "$dst" ]; then
            AGENTS_CHANGED=true
        fi

        backup_and_copy "$agent_file" "$dst"
        agents_installed=$((agents_installed + 1))
    done

    if [ "$agents_installed" -eq 0 ]; then
        warn "agents/ directory exists but contains no .md files — no agents installed."
    else
        log "Agents installed: $agents_installed"
    fi
fi

# ---------------------------------------------------------------------------
# Step 2: Install orchestration/ → ~/.claude/orchestration/
#   Copies all files under orchestration/ excluding _archive/.
#   Preserves any user-created files already in ~/.claude/orchestration/.
# ---------------------------------------------------------------------------
log "Installing orchestration files → ~/.claude/orchestration/ ..."
orchestration_installed=0

if [ -d "$REPO_ROOT/orchestration" ]; then
    if [ "$DRY_RUN" = false ]; then
        mkdir -p "${HOME}/.claude/orchestration/"
    fi

    # Walk the orchestration tree, skip _archive/
    while IFS= read -r -d '' src_file; do
        # Compute path relative to orchestration/
        rel="${src_file#"$REPO_ROOT/orchestration/"}"

        # Skip anything under _archive/
        case "$rel" in
            _archive/*) continue ;;
        esac

        dst="${HOME}/.claude/orchestration/${rel}"
        backup_and_copy "$src_file" "$dst"
        orchestration_installed=$((orchestration_installed + 1))
    done < <(find "$REPO_ROOT/orchestration" -type f -print0)

    log "Orchestration files installed: $orchestration_installed"
fi

# ---------------------------------------------------------------------------
# Step 3: Install build-review-prompts.sh → ~/.claude/orchestration/scripts/
# ---------------------------------------------------------------------------
BRP_SRC="$REPO_ROOT/scripts/build-review-prompts.sh"
BRP_DST="${HOME}/.claude/orchestration/scripts/build-review-prompts.sh"

if [ ! -f "$BRP_SRC" ]; then
    warn "Expected script not found, skipping: $BRP_SRC"
else
    log "Installing build-review-prompts.sh → ${HOME}/.claude/orchestration/scripts/ ..."
    backup_and_copy "$BRP_SRC" "$BRP_DST"
    if [ "$DRY_RUN" = false ]; then
        chmod +x "$BRP_DST"
    fi
fi

# ---------------------------------------------------------------------------
# Step 4: Install crumb.py → ~/.local/bin/crumb
# ---------------------------------------------------------------------------
CRUMB_SRC="$REPO_ROOT/crumb.py"
CRUMB_DST="${HOME}/.local/bin/crumb"

if [ ! -f "$CRUMB_SRC" ]; then
    warn "crumb.py not found: $CRUMB_SRC — skipping crumb install"
else
    log "Installing crumb → ${HOME}/.local/bin/crumb ..."
    backup_and_copy "$CRUMB_SRC" "$CRUMB_DST"
    if [ "$DRY_RUN" = false ]; then
        chmod +x "$CRUMB_DST"
        log "crumb installed and marked executable: $CRUMB_DST"
    fi
fi

# ---------------------------------------------------------------------------
# Step 5: Validate PATH includes ~/.local/bin
# ---------------------------------------------------------------------------
if [[ ":${PATH}:" != *":${HOME}/.local/bin:"* ]]; then
    warn "~/.local/bin is not in your PATH."
    warn "Add this to your shell profile (~/.zshrc, ~/.bashrc, etc.):"
    warn "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    warn "Then restart your shell or run: source ~/.zshrc"
fi

# ---------------------------------------------------------------------------
# Step 6: Preflight checks
# ---------------------------------------------------------------------------
if [ ! -f "${HOME}/.claude/agents/code-reviewer.md" ]; then
    warn "~/.claude/agents/code-reviewer.md is missing."
    warn "Nitpicker team members will fail to spawn without it."
    warn "Copy it manually to ~/.claude/agents/code-reviewer.md before starting a review session."
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
log ""
log "Setup complete."

if [ "$AGENTS_CHANGED" = true ]; then
    log ""
    log "============================================================"
    log "  IMPORTANT: Agent files were installed or updated."
    log "  You MUST restart Claude Code for new/changed agent"
    log "  definitions to take effect."
    log "============================================================"
fi
