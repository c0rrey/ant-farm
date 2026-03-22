#!/usr/bin/env bash
# setup.sh — Install ant-farm plugin files to ~/.claude/ and PATH.
#
# Copies:
#   agents/*.md         → ~/.claude/agents/
#   orchestration/      → ~/.claude/orchestration/
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
# Backs up any existing target file with a timestamped .af-bak suffix before
# overwriting. Idempotent: re-running updates files; each run generates at
# most one backup per file (using a single TS for the whole run).
#
# Usage:
#   ./scripts/setup.sh
#   ./scripts/setup.sh --dry-run   # print what would change, no writes
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Temp file registry — all mktemp results are appended here so the EXIT trap
# can clean them up even if the script exits early due to set -e.
TEMP_FILES=()
trap 'rm -f "${TEMP_FILES[@]+"${TEMP_FILES[@]}"}" 2>/dev/null' EXIT
TS="$(date +%Y%m%dT%H%M%S)"
DRY_RUN=false
FORCE=false

# ---------------------------------------------------------------------------
# Manifest tracking: collects every destination path installed this run.
# Written to MANIFEST_PATH after all install steps complete.
# ---------------------------------------------------------------------------
MANIFEST_PATH="${HOME}/.claude/.ant-farm-manifest"
INSTALLED_FILES=()

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
                log "[dry-run] would backup + update: $dst -> ${dst}.af-bak.${TS}"
            fi
        else
            log "[dry-run] would install: $dst"
        fi
        INSTALLED_FILES+=("$dst")
        return
    fi

    mkdir -p "$dst_dir"

    if [ -f "$dst" ]; then
        if ! cmp -s "$src" "$dst"; then
            local bak="${dst}.af-bak.${TS}"
            cp "$dst" "$bak" || { echo "[ant-farm] ERROR: backup failed for $dst" >&2; return 1; }
            log "Backed up: $dst -> $bak"
        else
            log "Unchanged: $dst"
            INSTALLED_FILES+=("$dst")
            return
        fi
    fi

    cp "$src" "$dst" || { echo "[ant-farm] ERROR: install failed for $dst" >&2; return 1; }
    log "Installed: $dst"
    INSTALLED_FILES+=("$dst")
}

ANTFARM_START="<!-- ant-farm:start -->"
ANTFARM_END="<!-- ant-farm:end -->"

# extract_block FILE
#   Extracts the ant-farm block (inclusive of sentinels) using exact string
#   matching. Returns empty string if no block found.
extract_block() {
    awk -v start="$ANTFARM_START" -v end="$ANTFARM_END" '
        index($0, start) > 0 { found=1 }
        found { print }
        index($0, end) > 0 && found { exit }
    ' "$1"
}

# sync_claude_block SRC DST
#   Creates, appends, or replaces the ant-farm block in DST using content from SRC.
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
                log "[dry-run] would update ant-farm block in: $dst -> ${dst}.af-bak.${TS}"
            fi
        fi
        INSTALLED_FILES+=("$dst")
        return
    fi

    mkdir -p "$dst_dir"

    if [ ! -f "$dst" ]; then
        # No file yet — create with just the block
        printf '%s\n' "$block" > "$dst"
        log "Created: $dst (with ant-farm block)"
        INSTALLED_FILES+=("$dst")
        return
    fi

    if ! grep -qF "$ANTFARM_START" "$dst"; then
        # File exists but no ant-farm block — back up then append
        local bak="${dst}.af-bak.${TS}"
        cp "$dst" "$bak" || { echo "[ant-farm] ERROR: backup failed for $dst" >&2; return 1; }
        log "Backed up: $dst -> $bak"
        # Ensure trailing newline before appending
        if [ -s "$dst" ] && [ "$(tail -c 1 "$dst" | wc -l)" -eq 0 ]; then
            printf '\n' >> "$dst"
        fi
        printf '\n%s\n' "$block" >> "$dst"
        log "Appended ant-farm block to: $dst"
        INSTALLED_FILES+=("$dst")
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
        INSTALLED_FILES+=("$dst")
        return
    fi

    # Block differs — back up then replace
    local bak="${dst}.af-bak.${TS}"
    cp "$dst" "$bak" || { echo "[ant-farm] ERROR: backup failed for $dst" >&2; return 1; }
    log "Backed up: $dst -> $bak"

    # Replace block using awk with exact string matching.
    # New block content is read from a temp file (not -v) to avoid BSD awk
    # silently dropping multi-line strings passed via -v assignment.
    local blockfile="" tmpfile=""
    # Clean up temp files on any exit path (including set -e failures)
    trap 'rm -f "${blockfile:-}" "${tmpfile:-}" 2>/dev/null' RETURN
    blockfile="$(mktemp "${dst_dir}/.af-tmp.XXXXXX")"; TEMP_FILES+=("$blockfile")
    tmpfile="$(mktemp "${dst_dir}/.af-tmp.XXXXXX")"; TEMP_FILES+=("$tmpfile")
    printf '%s\n' "$block" > "$blockfile"

    if awk -v start="$ANTFARM_START" -v end="$ANTFARM_END" -v blockfile="$blockfile" '
        index($0, start) > 0 {
            while ((getline line < blockfile) > 0) print line
            close(blockfile)
            skip=1; next
        }
        skip && index($0, end) > 0 { skip=0; next }
        !skip { print }
    ' "$dst" > "$tmpfile"; then
        mv "$tmpfile" "$dst"
        tmpfile=""  # Already moved — prevent RETURN trap from removing destination
        log "Updated ant-farm block in: $dst"
        INSTALLED_FILES+=("$dst")
    else
        echo "[ant-farm] ERROR: awk replacement failed for $dst — backup at $bak" >&2
        return 1
    fi
}

# remove_claude_block DST
#   Removes the ant-farm sentinel block (inclusive of markers) from DST.
#   User content outside the markers is preserved verbatim.
#   If the block is not present, does nothing.
#   If the file ends up empty (or whitespace-only) after removal, it is left
#   in place (not deleted) — per AC-4.
#   Always backs up DST before modifying using ${dst}.af-bak.${TS} convention.
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
        log "[dry-run] would remove ant-farm block from: $dst (backup: ${dst}.af-bak.${TS})"
        return
    fi

    # Backup before modifying
    local bak="${dst}.af-bak.${TS}"
    cp "$dst" "$bak" || { echo "[ant-farm] ERROR: backup failed for $dst" >&2; return 1; }
    log "Backed up: $dst -> $bak"

    # Strip the block: print all lines EXCEPT those between (inclusive) the sentinels.
    # Write stripped result to a temp file, then atomically replace DST.
    local dst_dir tmpfile
    dst_dir="$(dirname "$dst")"
    tmpfile="$(mktemp "${dst_dir}/.af-tmp.XXXXXX")"; TEMP_FILES+=("$tmpfile")

    if awk -v start="$ANTFARM_START" -v end="$ANTFARM_END" '
        index($0, start) > 0 { skip=1; next }
        skip && index($0, end) > 0 { skip=0; next }
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

# Old unprefixed basenames (pre-AF-47) and middle-generation prefixed names (pre-Wave-1)
# mapped to their new descriptive names.
# Format: "old-basename new-prefixed-basename" (space-separated pairs)
AGENT_MIGRATIONS=(
    "scout-organizer.md ant-farm-recon-planner.md"
    "pantry-impl.md ant-farm-prompt-composer.md"
    "pest-control.md ant-farm-checkpoint-auditor.md"
    "nitpicker.md ant-farm-nitpicker.md"
    "big-head.md ant-farm-review-consolidator.md"
    "architect.md ant-farm-task-decomposer.md"
    "forager.md ant-farm-researcher.md"
    "surveyor.md ant-farm-spec-writer.md"
    "technical-writer.md ant-farm-session-scribe.md"
    "ant-farm-scout-organizer.md ant-farm-recon-planner.md"
    "ant-farm-pantry-impl.md ant-farm-prompt-composer.md"
    "ant-farm-pest-control.md ant-farm-checkpoint-auditor.md"
    "ant-farm-big-head.md ant-farm-review-consolidator.md"
    "ant-farm-architect.md ant-farm-task-decomposer.md"
    "ant-farm-forager.md ant-farm-researcher.md"
    "ant-farm-surveyor.md ant-farm-spec-writer.md"
    "ant-farm-technical-writer.md ant-farm-session-scribe.md"
    "ant-farm-nitpicker-clarity.md ant-farm-reviewer-clarity.md"
    "ant-farm-nitpicker-edge-cases.md ant-farm-reviewer-edge-cases.md"
    "ant-farm-nitpicker-correctness.md ant-farm-reviewer-correctness.md"
    "ant-farm-nitpicker-drift.md ant-farm-reviewer-drift.md"
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

# ---------------------------------------------------------------------------
# Orphan detection: read previous manifest (if any) before installs begin.
# After installs, files in OLD_MANIFEST_FILES but not in INSTALLED_FILES are
# orphans and will be removed.
# ---------------------------------------------------------------------------
OLD_MANIFEST_FILES=()
if [ -f "$MANIFEST_PATH" ]; then
    while IFS= read -r line; do
        # Skip the first line (install date header) and blank lines
        [[ "$line" == "#"* ]] && continue
        [[ -z "$line" ]] && continue
        OLD_MANIFEST_FILES+=("$line")
    done < "$MANIFEST_PATH"
    log "Read previous manifest: ${#OLD_MANIFEST_FILES[@]} entries from $MANIFEST_PATH"
fi

log "Checking for old unprefixed agent files to migrate ..."
migrate_old_agents

log "Installing agent definitions → ~/.claude/agents/ ..."
# AGENTS_CHANGED is consumed at end of script (~L694) to emit a
# "restart Claude Code" warning when agent files are new or modified.
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
#   Copies all files under orchestration/.
#   Preserves any user-created files already in ~/.claude/orchestration/.
# ---------------------------------------------------------------------------
log "Installing orchestration files → ~/.claude/orchestration/ ..."
orchestration_installed=0

if [ -d "$REPO_ROOT/orchestration" ]; then
    if [ "$DRY_RUN" = false ]; then
        mkdir -p "${HOME}/.claude/orchestration/"
    fi

    # Walk the orchestration tree
    find_output=$(mktemp); TEMP_FILES+=("$find_output")
    if ! find "$REPO_ROOT/orchestration" -type f -print0 > "$find_output"; then
        warn "find failed while walking orchestration/: $(cat "$find_output")"
        rm -f "$find_output"
    else
        while IFS= read -r -d '' src_file; do
            # Compute path relative to orchestration/
            rel="${src_file#"$REPO_ROOT/orchestration/"}"

            dst="${HOME}/.claude/orchestration/${rel}"
            backup_and_copy "$src_file" "$dst" || { warn "Failed to install orchestration file: $src_file"; continue; }
            orchestration_installed=$((orchestration_installed + 1))

            # Detect .local override: if a .local variant exists at the destination,
            # print a notice. setup.sh never creates, modifies, or deletes .local files.
            local_dst="${dst%.*}.local.${dst##*.}"  # e.g. RULES.md → RULES.local.md
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
# Transform repo root path to projects subdir name: /Users/x/my-repo → -Users-x-my-repo
REPO_ROOT_ESCAPED="$(printf '%s' "$REPO_ROOT" | tr '/' '-')"
PROMPTDIR_CLAUDE="${HOME}/.claude/projects/${REPO_ROOT_ESCAPED}/CLAUDE.md"
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
# Post-install Step A: Orphan cleanup
#   Files in the previous manifest that are not in this run's INSTALLED_FILES
#   are orphans. Remove them (or report in dry-run).
# ---------------------------------------------------------------------------
if [ "${#OLD_MANIFEST_FILES[@]}" -gt 0 ]; then
    log "Checking for orphaned files from previous install ..."
    orphans_found=0
    for old_path in "${OLD_MANIFEST_FILES[@]}"; do
        # Check if old_path appears in current INSTALLED_FILES
        found_in_current=false
        for current_path in "${INSTALLED_FILES[@]}"; do
            if [ "$current_path" = "$old_path" ]; then
                found_in_current=true
                break
            fi
        done

        if [ "$found_in_current" = false ] && [ -f "$old_path" ]; then
            orphans_found=$((orphans_found + 1))
            if [ "$DRY_RUN" = true ]; then
                log "[dry-run] would remove orphan: $old_path"
            else
                rm "$old_path" || { warn "Failed to remove orphan: $old_path — continuing"; continue; }
                log "Removed orphan: $old_path"
            fi
        fi
    done
    if [ "$orphans_found" -eq 0 ]; then
        log "No orphaned files found."
    fi
fi

# ---------------------------------------------------------------------------
# Post-install Step B: Write manifest
#   Record every destination path installed this run, one per line.
#   The manifest file itself is NOT included in the list.
#   Skipped in dry-run mode.
# ---------------------------------------------------------------------------
if [ "$DRY_RUN" = false ]; then
    {
        printf '# ant-farm install manifest — %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
        for installed_path in "${INSTALLED_FILES[@]}"; do
            printf '%s\n' "$installed_path"
        done
    } > "$MANIFEST_PATH"
    log "Wrote manifest: $MANIFEST_PATH (${#INSTALLED_FILES[@]} entries)"
else
    log "[dry-run] would write manifest: $MANIFEST_PATH (${#INSTALLED_FILES[@]} would-be entries)"
fi

# ---------------------------------------------------------------------------
# Post-install Step C: Backup pruning
#   For each file tracked in INSTALLED_FILES, prune .af-bak.* backups to
#   keep only the 5 most recent. Older backups are deleted (or reported in
#   dry-run). Existing .bak.* files from pre-AF-53 runs are never touched.
# ---------------------------------------------------------------------------
BACKUP_KEEP=5
log "Pruning old backups (keeping ${BACKUP_KEEP} most recent .af-bak.* per file) ..."
pruned_total=0

for base_path in "${INSTALLED_FILES[@]}"; do
    # List all .af-bak.* backups for this base path, sorted newest-first.
    # Pattern: <base_path>.af-bak.<TIMESTAMP>
    # We glob for them, then sort in reverse order.
    backups=()
    shopt -s nullglob
    for bak in "${base_path}".af-bak.*; do
        backups+=("$bak")
    done
    shopt -u nullglob

    # Sort backups newest-first (lexicographic reverse — timestamps are sortable)
    # Use a temp array with process substitution
    if [ "${#backups[@]}" -gt "$BACKUP_KEEP" ]; then
        # Sort descending: newest first (portable — bash 3.2 compatible; no mapfile)
        sorted_backups=()
        while IFS= read -r bak_line; do
            sorted_backups+=("$bak_line")
        done < <(printf '%s\n' "${backups[@]}" | sort -r)
        for (( i=BACKUP_KEEP; i<${#sorted_backups[@]}; i++ )); do
            old_bak="${sorted_backups[$i]}"
            pruned_total=$((pruned_total + 1))
            if [ "$DRY_RUN" = true ]; then
                log "[dry-run] would prune backup: $old_bak"
            else
                rm "$old_bak" || { warn "Failed to prune backup: $old_bak — continuing"; continue; }
                log "Pruned backup: $old_bak"
            fi
        done
    fi
done

if [ "$pruned_total" -eq 0 ]; then
    log "No backups needed pruning."
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
# code-reviewer.md is a Claude Code built-in agent, not installed by this script.
if [ ! -f "${HOME}/.claude/agents/code-reviewer.md" ]; then
    warn "~/.claude/agents/code-reviewer.md is missing."
    warn "Reviewer team members will fail to spawn without it."
    warn "This file is a Claude Code built-in agent — obtain it from ~/.claude/agents/code-reviewer.md"
    warn "on a working Claude Code installation, or check the Claude Code documentation / re-run 'claude init'."
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
