#!/usr/bin/env bash
# setup.sh — Install ant-farm plugin files to ~/.claude/ and PATH.
#
# Copies:
#   agents/*.md         → ~/.claude/agents/
#   orchestration/      → ~/.claude/orchestration/  (non-_archive files)
#   scripts/build-review-prompts.sh → ~/.claude/orchestration/scripts/
#   skills/*.md         → ~/.claude/skills/ant-farm-<name>/SKILL.md
#   crumb.py            → ~/.local/bin/crumb
#
# CLAUDE.md handling:
#   Step 6a: Remove any existing ant-farm block from ~/.claude/CLAUDE.md
#            (migration cleanup — the block now lives in the repo's CLAUDE.md).
#   Step 6b: Remove stale ant-farm block from prompt-dir CLAUDE.md
#            (migration cleanup — the block previously lived there).
#   Step 6c: Write block to the repo's own CLAUDE.md (loaded by Claude Code
#            at session start).
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
FORCE=false

# ---------------------------------------------------------------------------
# Parse args
# ---------------------------------------------------------------------------
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --force)   FORCE=true ;;
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
            cp "$dst" "$bak" || { echo "[ant-farm] ERROR: backup failed for $dst" >&2; return 1; }
            log "Backed up: $dst -> $bak"
        else
            log "Unchanged: $dst"
            return
        fi
    fi

    cp "$src" "$dst" || { echo "[ant-farm] ERROR: install failed for $dst" >&2; return 1; }
    log "Installed: $dst"
}

ANTFARM_START="<!-- ant-farm:start -->"
ANTFARM_END="<!-- ant-farm:end -->"

# extract_block FILE
#   Extracts the ant-farm block (inclusive of sentinels) using exact string
#   matching. Returns empty string if no block found.
extract_block() {
    awk -v start="$ANTFARM_START" -v end="$ANTFARM_END" '
        $0 == start { found=1 }
        found { print }
        $0 == end && found { exit }
    ' "$1"
}

# sync_claude_block SRC DST
#   Inserts or replaces the ant-farm block in DST using content from SRC.
#   The block is delimited by sentinel comments so user content is preserved.
#   Always backs up DST before modifying (unless unchanged).
sync_claude_block() {
    local src="$1"
    local dst="$2"
    local dst_dir
    dst_dir="$(dirname "$dst")"

    # Build the block we want to insert
    local block
    block="$(printf '%s\n' "$ANTFARM_START"; cat "$src"; printf '%s\n' "$ANTFARM_END")"

    if [ "$DRY_RUN" = true ]; then
        if [ ! -f "$dst" ]; then
            log "[dry-run] would create: $dst (with ant-farm block)"
        elif ! grep -qF "$ANTFARM_START" "$dst"; then
            log "[dry-run] would append ant-farm block to: $dst"
        else
            local existing
            existing="$(extract_block "$dst")"
            if [ "$existing" = "$block" ]; then
                log "[dry-run] unchanged: $dst (ant-farm block)"
            else
                log "[dry-run] would update ant-farm block in: $dst -> ${dst}.bak.${TS}"
            fi
        fi
        return
    fi

    mkdir -p "$dst_dir"

    if [ ! -f "$dst" ]; then
        # No file yet — create with just the block
        printf '%s\n' "$block" > "$dst"
        log "Created: $dst (with ant-farm block)"
        return
    fi

    if ! grep -qF "$ANTFARM_START" "$dst"; then
        # File exists but no ant-farm block — back up then append
        local bak="${dst}.bak.${TS}"
        cp "$dst" "$bak" || { echo "[ant-farm] ERROR: backup failed for $dst" >&2; return 1; }
        log "Backed up: $dst -> $bak"
        # Ensure trailing newline before appending
        if [ -s "$dst" ] && [ "$(tail -c 1 "$dst" | wc -l)" -eq 0 ]; then
            printf '\n' >> "$dst"
        fi
        printf '\n%s\n' "$block" >> "$dst"
        log "Appended ant-farm block to: $dst"
        return
    fi

    # Guard: both markers must be present
    if ! grep -qF "$ANTFARM_END" "$dst"; then
        echo "[ant-farm] ERROR: Found start marker but not end marker in $dst — refusing to replace. Fix the file manually." >&2
        return 1
    fi

    # Block exists — check if it needs updating
    local existing
    existing="$(extract_block "$dst")"
    if [ "$existing" = "$block" ]; then
        log "Unchanged: $dst (ant-farm block)"
        return
    fi

    # Block differs — back up then replace
    local bak="${dst}.bak.${TS}"
    cp "$dst" "$bak" || { echo "[ant-farm] ERROR: backup failed for $dst" >&2; return 1; }
    log "Backed up: $dst -> $bak"

    # Replace block using awk with exact string matching.
    # New block content is read from a temp file (not -v) to avoid BSD awk
    # silently dropping multi-line strings passed via -v assignment.
    local blockfile tmpfile
    blockfile="$(mktemp)"
    tmpfile="$(mktemp)"
    printf '%s\n' "$block" > "$blockfile"

    if awk -v start="$ANTFARM_START" -v end="$ANTFARM_END" -v blockfile="$blockfile" '
        $0 == start {
            while ((getline line < blockfile) > 0) print line
            close(blockfile)
            skip=1; next
        }
        skip && $0 == end { skip=0; next }
        !skip { print }
    ' "$dst" > "$tmpfile"; then
        mv "$tmpfile" "$dst"
        log "Updated ant-farm block in: $dst"
    else
        rm -f "$tmpfile" "$blockfile"
        echo "[ant-farm] ERROR: awk replacement failed for $dst — backup at $bak" >&2
        return 1
    fi
    rm -f "$blockfile"
}

# remove_claude_block DST
#   Removes the ant-farm sentinel block (inclusive of markers) from DST.
#   User content outside the markers is preserved verbatim.
#   If the block is not present, does nothing.
#   If the file ends up empty (or whitespace-only) after removal, it is left
#   in place (not deleted) — per AC-4.
#   Always backs up DST before modifying using ${dst}.bak.${TS} convention.
#   Respects DRY_RUN.
remove_claude_block() {
    local dst="$1"

    if [ ! -f "$dst" ]; then
        # Nothing to remove — file does not exist
        return
    fi

    if ! grep -qF "$ANTFARM_START" "$dst"; then
        # No block present — global CLAUDE.md is clean
        if [ "$DRY_RUN" = true ]; then
            log "[dry-run] no ant-farm block found in $dst — nothing to remove"
        fi
        return
    fi

    # Guard: both markers must be present
    if ! grep -qF "$ANTFARM_END" "$dst"; then
        echo "[ant-farm] ERROR: Found start marker but not end marker in $dst — refusing to remove. Fix the file manually." >&2
        return 1
    fi

    if [ "$DRY_RUN" = true ]; then
        log "[dry-run] would remove ant-farm block from: $dst (backup: ${dst}.bak.${TS})"
        return
    fi

    # Backup before modifying
    local bak="${dst}.bak.${TS}"
    cp "$dst" "$bak" || { echo "[ant-farm] ERROR: backup failed for $dst" >&2; return 1; }
    log "Backed up: $dst -> $bak"

    # Strip the block: print all lines EXCEPT those between (inclusive) the sentinels.
    # Write stripped result to a temp file, then atomically replace DST.
    local tmpfile
    tmpfile="$(mktemp)"

    if awk -v start="$ANTFARM_START" -v end="$ANTFARM_END" '
        $0 == start { skip=1; next }
        skip && $0 == end { skip=0; next }
        !skip { print }
    ' "$dst" > "$tmpfile"; then
        mv "$tmpfile" "$dst"
        log "Removed ant-farm block from: $dst"
    else
        rm -f "$tmpfile"
        echo "[ant-farm] ERROR: awk removal failed for $dst — backup at $bak" >&2
        return 1
    fi
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
#   Before installing, migrate old unprefixed agent files left over from
#   before AF-47 renamed them to ant-farm-<name>.md.  A file is confirmed
#   as an ant-farm agent if its YAML front matter contains a "name:" line
#   whose value matches the expected old basename (without .md extension).
#   Confirmed files are removed; unrecognised files are left with a warning.
# ---------------------------------------------------------------------------

# Old unprefixed basenames (pre-AF-47) mapped to their new prefixed names.
# Format: "old-basename new-prefixed-basename" (space-separated pairs)
AGENT_MIGRATIONS=(
    "scout-organizer.md ant-farm-scout-organizer.md"
    "pantry-impl.md ant-farm-pantry-impl.md"
    "pest-control.md ant-farm-pest-control.md"
    "nitpicker.md ant-farm-nitpicker.md"
    "big-head.md ant-farm-big-head.md"
    "architect.md ant-farm-architect.md"
    "forager.md ant-farm-forager.md"
    "surveyor.md ant-farm-surveyor.md"
)

# migrate_old_agents
#   Check each known old unprefixed agent path. If found and confirmed as an
#   ant-farm file (via "name:" sentinel in YAML front matter), remove it.
#   Unrecognised files are left in place with a warning.
migrate_old_agents() {
    local agents_dir="${HOME}/.claude/agents"
    local found_any=false

    for pair in "${AGENT_MIGRATIONS[@]}"; do
        local old_name new_name old_path expected_name_value
        old_name="${pair%% *}"                       # e.g. scout-organizer.md
        new_name="${pair##* }"                       # e.g. ant-farm-scout-organizer.md
        old_path="${agents_dir}/${old_name}"
        expected_name_value="${old_name%.md}"        # e.g. scout-organizer

        if [ ! -f "$old_path" ]; then
            continue
        fi

        found_any=true

        # Identity check: YAML front matter must contain "name: <old-basename>"
        if grep -qxF "name: ${expected_name_value}" "$old_path" 2>/dev/null; then
            if [ "$DRY_RUN" = true ]; then
                log "[dry-run] would remove stale ant-farm agent: $old_path (replacing with $new_name)"
            else
                rm "$old_path" || { warn "Failed to remove stale agent -- check permissions. Continuing."; continue; }
                log "Removed stale ant-farm agent: $old_path (replaced by $new_name)"
            fi
        else
            warn "Found $old_path but it does not look like an ant-farm agent — leaving in place."
        fi
    done

    if [ "$found_any" = false ] && [ "$DRY_RUN" = true ]; then
        log "[dry-run] no old unprefixed agent files found — nothing to migrate."
    fi
}

log "Checking for old unprefixed agent files to migrate ..."
migrate_old_agents

log "Installing agent definitions → ~/.claude/agents/ ..."
AGENTS_CHANGED=false
agents_installed=0

if [ -d "$REPO_ROOT/agents" ]; then
    if [ "$DRY_RUN" = false ]; then
        mkdir -p "${HOME}/.claude/agents/"
    fi
    shopt -s nullglob
    for agent_file in "$REPO_ROOT/agents/"*.md; do
        name="$(basename "$agent_file")"
        dst="${HOME}/.claude/agents/${name}"

        # Track whether any agent file actually changed (for restart warning)
        if [ -f "$dst" ] && ! cmp -s "$agent_file" "$dst"; then
            AGENTS_CHANGED=true
        elif [ ! -f "$dst" ]; then
            AGENTS_CHANGED=true
        fi

        backup_and_copy "$agent_file" "$dst" || { warn "Failed to install agent: $agent_file"; continue; }
        agents_installed=$((agents_installed + 1))
    done
    shopt -u nullglob

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
    find_output=$(mktemp)
    if ! find "$REPO_ROOT/orchestration" -type f -print0 > "$find_output" 2>&1; then
        warn "find failed while walking orchestration/: $(cat "$find_output")"
        rm -f "$find_output"
    else
        while IFS= read -r -d '' src_file; do
            # Compute path relative to orchestration/
            rel="${src_file#"$REPO_ROOT/orchestration/"}"

            # Skip anything under _archive/
            case "$rel" in
                _archive/*) continue ;;
            esac

            dst="${HOME}/.claude/orchestration/${rel}"
            backup_and_copy "$src_file" "$dst" || { warn "Failed to install orchestration file: $src_file"; continue; }
            orchestration_installed=$((orchestration_installed + 1))

            # Detect .local override: if a .local variant exists at the destination,
            # print a notice. setup.sh never creates, modifies, or deletes .local files.
            local_dst="${dst%.*}.local.${dst##*.}"
            if [ -f "$local_dst" ]; then
                log "Notice: .local override active: $local_dst (overrides $dst)"
            fi
        done < "$find_output"
        rm -f "$find_output"

        if [ "$orchestration_installed" -eq 0 ]; then
            warn "orchestration/ directory exists but no files were installed — directory may be empty."
        else
            log "Orchestration files installed: $orchestration_installed"
        fi
    fi
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
# Step 4: Install skills → ~/.claude/skills/ant-farm-<name>/SKILL.md
#   Claude Code personal skills format: ~/.claude/skills/<skill-name>/SKILL.md
#   Commands are invocable as /ant-farm-<name> (hyphenated).
# ---------------------------------------------------------------------------
log "Installing skills → ~/.claude/skills/ ..."
skills_installed=0

if [ -d "$REPO_ROOT/skills" ]; then
    shopt -s nullglob
    for skill_file in "$REPO_ROOT/skills/"*.md; do
        name="$(basename "$skill_file" .md)"
        skill_dir="${HOME}/.claude/skills/ant-farm-${name}"
        dst="${skill_dir}/SKILL.md"
        if [ "$DRY_RUN" = false ]; then
            mkdir -p "$skill_dir"
        fi
        backup_and_copy "$skill_file" "$dst" || { warn "Failed to install skill: $skill_file"; continue; }
        skills_installed=$((skills_installed + 1))
    done
    shopt -u nullglob

    if [ "$skills_installed" -eq 0 ]; then
        warn "skills/ directory exists but contains no .md files — no skills installed."
    else
        log "Skills installed: $skills_installed"
    fi
else
    warn "skills/ directory not found: $REPO_ROOT/skills — skipping skills install"
fi

# ---------------------------------------------------------------------------
# Step 5: Install crumb.py → ~/.local/bin/crumb
# ---------------------------------------------------------------------------
CRUMB_SRC="$REPO_ROOT/crumb.py"
CRUMB_DST="${HOME}/.local/bin/crumb"

if [ ! -f "$CRUMB_SRC" ]; then
    warn "crumb.py not found: $CRUMB_SRC — skipping crumb install"
elif [ -f "$CRUMB_DST" ] && ! head -n 3 "$CRUMB_DST" | grep -qF '# ant-farm crumb CLI' && [ "$FORCE" = false ]; then
    warn "~/.local/bin/crumb exists but was not installed by ant-farm (sentinel missing)."
    warn "To overwrite it, re-run with --force."
    warn "Skipping crumb install to avoid clobbering an unrelated tool."
else
    log "Installing crumb → ${HOME}/.local/bin/crumb ..."
    backup_and_copy "$CRUMB_SRC" "$CRUMB_DST"
    if [ "$DRY_RUN" = false ]; then
        chmod +x "$CRUMB_DST"
        log "crumb installed and marked executable: $CRUMB_DST"
    fi
fi

# ---------------------------------------------------------------------------
# Step 6a: Remove any existing ant-farm block from ~/.claude/CLAUDE.md
#   Migration cleanup: the block now lives in the per-project prompt-dir.
#   User content outside sentinel markers is preserved verbatim.
#   If no block is present, the file is left unchanged.
# ---------------------------------------------------------------------------
GLOBAL_CLAUDE_DST="${HOME}/.claude/CLAUDE.md"
log "Checking for ant-farm block to remove from ${GLOBAL_CLAUDE_DST} ..."
remove_claude_block "$GLOBAL_CLAUDE_DST"

# ---------------------------------------------------------------------------
# Step 6b: Remove stale ant-farm block from prompt-dir CLAUDE.md (migration)
#   The block previously lived in the per-project prompt-dir. It now lives in
#   the repo's own CLAUDE.md (Step 6c). Clean up the old location.
# ---------------------------------------------------------------------------
PROMPTDIR_COMPONENT="$(printf '%s' "$REPO_ROOT" | tr '/' '-')"
PROMPTDIR_CLAUDE="${HOME}/.claude/projects/${PROMPTDIR_COMPONENT}/CLAUDE.md"
log "Checking for stale ant-farm block in prompt-dir ${PROMPTDIR_CLAUDE} ..."
remove_claude_block "$PROMPTDIR_CLAUDE"

# ---------------------------------------------------------------------------
# Step 6c: Write ant-farm block to the repo's CLAUDE.md
#   Claude Code loads the repo's CLAUDE.md into the system prompt at session
#   start. The prompt-dir CLAUDE.md is NOT loaded, so the block must live here.
#   Block content is sourced from orchestration/templates/claude-block.md.
# ---------------------------------------------------------------------------
BLOCK_SRC="$REPO_ROOT/orchestration/templates/claude-block.md"
REPO_CLAUDE_DST="$REPO_ROOT/CLAUDE.md"

if [ ! -f "$BLOCK_SRC" ]; then
    warn "claude-block.md not found: $BLOCK_SRC — skipping repo CLAUDE.md install"
else
    log "Installing ant-farm block → ${REPO_CLAUDE_DST} ..."
    sync_claude_block "$BLOCK_SRC" "$REPO_CLAUDE_DST"
fi

# ---------------------------------------------------------------------------
# Step 7: Validate PATH includes ~/.local/bin
# ---------------------------------------------------------------------------
if [[ ":${PATH}:" != *":${HOME}/.local/bin:"* ]]; then
    warn "~/.local/bin is not in your PATH."
    warn "Add this to your shell profile (~/.zshrc, ~/.bashrc, etc.):"
    warn "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    warn "Then restart your shell or run: source ~/.zshrc"
fi

# ---------------------------------------------------------------------------
# Step 8: Preflight checks
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
