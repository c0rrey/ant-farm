---
description: This skill should be used when the user invokes "/ant-farm-init", says "initialize crumbs", "set up .crumbs", "init ant-farm", or asks to scaffold the crumbs task system in a new project. Bootstraps .crumbs/ directory structure, installs crumb.py, and configures the project for crumb-based task management.
---

# /ant-farm-init — Project Initialization Skill

This skill governs the `/ant-farm-init` slash command. It scaffolds the `.crumbs/` directory structure in the current project, installs `crumb.py`, configures `.gitignore`, and **installs the orchestration block into the project's CLAUDE.md**. It is safe to re-run on an already-initialized project (idempotent).

**HARD REQUIREMENT**: Init is NOT complete until the orchestration block is installed in `CLAUDE.md` (Step 8b). If you skip Step 8b, the orchestration framework will not work in this project. You MUST execute every step through Step 9.

## Trigger Conditions

Activate this skill when the user:
- Invokes `/ant-farm-init` (with or without arguments)
- Asks to initialize, set up, or scaffold `.crumbs/` in a project
- Asks to install or set up the crumb task system in a new project

## Step 0 — Already Initialized Check

Before doing anything else, check if `.crumbs/` is already fully initialized.

```bash
[ -f .crumbs/tasks.jsonl ] && [ -f .crumbs/config.json ] && echo "INITIALIZED" || echo "NOT_INITIALIZED"
```

If `INITIALIZED`:

> `.crumbs/` is already initialized in this project. Re-running init is safe — existing data files will not be overwritten. Proceeding to verify and repair any missing components.

Continue to Step 1 anyway (idempotent repair mode). Do not abort.

## Step 1 — Detect Project Language / Stack

Run the following checks to identify the project's primary language and stack. Store the results for use in Step 5 (agent type suggestion).

```bash
# Check for language indicators in order of specificity
[ -f package.json ] && echo "nodejs"
[ -f tsconfig.json ] && echo "typescript"
[ -f pyproject.toml ] || [ -f setup.py ] || [ -f requirements.txt ] && echo "python"
[ -f go.mod ] && echo "go"
[ -f Cargo.toml ] && echo "rust"
[ -f pom.xml ] || [ -f build.gradle ] && echo "java"
```

Use the first match as the primary language. If none match, record as `unknown`.

Also attempt to derive a project prefix from the directory name:

```bash
basename "$(pwd)" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | cut -c1-8
```

Store this as `DERIVED_PREFIX`. It will be offered as a default in Step 3.

## Step 2 — Create Directory Structure

Create the required directories. These commands are safe to re-run — `mkdir -p` is idempotent.

```bash
mkdir -p .crumbs/sessions
mkdir -p .crumbs/history
```

## Step 3 — Prompt for Config Prefix

Ask the user for a short prefix that will be prepended to all task IDs in this project (e.g., `myapp-`, `api-`, `web-`).

> What prefix should be used for task IDs in this project?
> Suggested: `[DERIVED_PREFIX]` (derived from directory name)
> Press Enter to accept, or type a custom prefix (letters, digits, hyphens; max 16 chars):

Accept the user's input or use `DERIVED_PREFIX` if the user accepts the default.

Validate the prefix:
- Minimum 1 character (empty input must re-prompt, not silently pass)
- Contains only lowercase letters, digits, and hyphens
- Does not end with a hyphen
- Maximum 16 characters

If invalid, prompt again with a correction message.

Store as `PREFIX`.

## Step 4 — Create .crumbs/tasks.jsonl

Only create this file if it does not already exist.

```bash
[ -f .crumbs/tasks.jsonl ] || touch .crumbs/tasks.jsonl
```

If the file already exists, leave it untouched. Surface a note:

> `.crumbs/tasks.jsonl` already exists — preserving existing task data.

## Step 5 — Create .crumbs/config.json

Only create this file if it does not already exist.

```bash
[ -f .crumbs/config.json ] && echo "EXISTS" || echo "MISSING"
```

If `MISSING`, write `.crumbs/config.json` with this structure:

```json
{
  "prefix": "<PREFIX>",
  "default_priority": "P2",
  "next_crumb_id": 1,
  "next_trail_id": 1,
  "language": "<DETECTED_LANGUAGE>",
  "created_at": "<ISO8601_TIMESTAMP>"
}
```

Substitute:
- `<PREFIX>` — the prefix collected in Step 3
- `<DETECTED_LANGUAGE>` — the language detected in Step 1 (or `"unknown"`)
- `<ISO8601_TIMESTAMP>` — current UTC time in ISO 8601 format (e.g., `2026-03-13T02:17:48Z`)

If `EXISTS`, leave the file untouched. Surface a note:

> `.crumbs/config.json` already exists — preserving existing configuration.

## Step 6 — Update .gitignore

Add `.crumbs/sessions/` to `.gitignore` so session artifacts are not committed. Data files (tasks.jsonl, config.json, history/) remain tracked.

```bash
# Check if entry already present
grep -qF '.crumbs/sessions/' .gitignore 2>/dev/null && echo "PRESENT" || echo "MISSING"
```

If `MISSING`:

```bash
# Create .gitignore if it doesn't exist, then append
[ -f .gitignore ] || touch .gitignore
echo '' >> .gitignore
echo '# crumb session artifacts (ephemeral — not committed)' >> .gitignore
echo '.crumbs/sessions/' >> .gitignore
```

If `PRESENT`, skip. Surface a note:

> `.crumbs/sessions/` already in `.gitignore` — no change needed.

## Step 7 — Install crumb.py

Check whether `crumb` is already available on PATH.

```bash
command -v crumb 2>/dev/null && echo "INSTALLED" || echo "NOT_INSTALLED"
```

If `INSTALLED`:

> `crumb` is already installed at `$(command -v crumb)` — skipping installation.

If `NOT_INSTALLED`, attempt to install crumb.py to `~/.local/bin/crumb`:

```bash
# Ensure install directory exists
mkdir -p ~/.local/bin

# Look for crumb.py in the repository
CRUMB_SRC="$(find . -maxdepth 3 -name 'crumb.py' | head -1)"
```

If `CRUMB_SRC` is found:

```bash
cp "$CRUMB_SRC" ~/.local/bin/crumb
chmod +x ~/.local/bin/crumb
```

If `CRUMB_SRC` is not found, surface an error:

> **Warning**: `crumb.py` not found in this repository. Cannot auto-install `crumb`. You will need to manually place `crumb.py` at `~/.local/bin/crumb` (or another directory on your PATH) and run `chmod +x` on it.

After installation, verify:

```bash
command -v crumb 2>/dev/null && echo "OK" || echo "NOT_ON_PATH"
```

If `NOT_ON_PATH`:

> **Note**: `crumb` was installed to `~/.local/bin/crumb` but is not on your PATH. Add the following to your shell profile (`.bashrc`, `.zshrc`, etc.) and restart your shell or source the file:
>
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```

## Step 8a — Agent Type Suggestion

Based on the language detected in Step 1, suggest appropriate agent types for task execution:

| Language | Suggested Agent Type |
|---|---|
| python | python-pro |
| typescript | typescript-pro |
| nodejs | typescript-pro |
| go | general-purpose |
| rust | general-purpose |
| java | general-purpose |
| unknown | general-purpose |

Surface this as a recommendation:

> For a `[LANGUAGE]` project, recommended agent type is `[AGENT_TYPE]`. You can set this per-task with `crumb create --agent [AGENT_TYPE]` or add it to your project CLAUDE.md.

## Step 8b — Install Orchestration Triggers to Repo CLAUDE.md

This step writes the ant-farm orchestration block into the project's `CLAUDE.md` file. Claude Code loads this file into the system prompt at session start, so the orchestration triggers are available from the first message.

### 8b.1 — Locate Block Source

The block content is sourced from the ant-farm repository's canonical file:

```bash
BLOCK_SRC=""
# Try common locations
for candidate in \
    "orchestration/templates/claude-block.md" \
    "$HOME/.claude/orchestration/templates/claude-block.md"; do
    [ -f "$candidate" ] && { BLOCK_SRC="$candidate"; break; }
done

[ -n "$BLOCK_SRC" ] && echo "FOUND: $BLOCK_SRC" || echo "NOT_FOUND"
```

If `NOT_FOUND`, surface a warning and skip 8b.2–8b.3:

> **Warning**: `claude-block.md` not found. Cannot install orchestration triggers automatically. Run `./scripts/setup.sh` from the ant-farm repo first, then re-run `/ant-farm-init`.

Store the block content (wrapped in sentinel markers) in a temp variable:

```bash
ANTFARM_START="<!-- ant-farm:start -->"
ANTFARM_END="<!-- ant-farm:end -->"
BLOCK_CONTENT="$(printf '%s\n' "$ANTFARM_START"; cat "$BLOCK_SRC"; printf '%s\n' "$ANTFARM_END")"
```

### 8b.2 — Detect Existing State

```bash
REPO_CLAUDE="CLAUDE.md"
if [ ! -f "$REPO_CLAUDE" ]; then
    echo "STATE=create"
elif grep -qF "<!-- ant-farm:start -->" "$REPO_CLAUDE" && grep -qF "<!-- ant-farm:end -->" "$REPO_CLAUDE"; then
    echo "STATE=update"
elif grep -qF "<!-- ant-farm:start -->" "$REPO_CLAUDE" || grep -qF "<!-- ant-farm:end -->" "$REPO_CLAUDE"; then
    echo "STATE=error_partial"
else
    echo "STATE=append"
fi
```

### 8b.3 — Apply the Appropriate Write Action

**If `STATE=create`** — File does not exist; create it with just the block:

```bash
printf '%s\n' "$BLOCK_CONTENT" > "${REPO_CLAUDE}.tmp" && mv "${REPO_CLAUDE}.tmp" "$REPO_CLAUDE"
PROMPT_STATUS="created"
```

**If `STATE=append`** — File exists with user content but no ant-farm block; append, preserving existing content:

```bash
# Ensure trailing newline before appending
[ -s "$REPO_CLAUDE" ] && [ "$(tail -c 1 "$REPO_CLAUDE" | wc -l)" -eq 0 ] && printf '\n' >> "$REPO_CLAUDE"
printf '\n%s\n' "$BLOCK_CONTENT" >> "$REPO_CLAUDE"
PROMPT_STATUS="updated"
```

**If `STATE=update`** — File exists with an ant-farm block; check if it needs updating first, then replace in-place using awk:

```bash
# Extract the current block for comparison
EXISTING_BLOCK="$(awk '/^<!-- ant-farm:start -->/{found=1} found{print} /^<!-- ant-farm:end -->/{if(found){exit}}' "$REPO_CLAUDE")"
if [ "$EXISTING_BLOCK" = "$BLOCK_CONTENT" ]; then
    PROMPT_STATUS="already up to date"
else
    BLOCKFILE="$(mktemp)"
    TMPFILE="$(mktemp)"
    printf '%s\n' "$BLOCK_CONTENT" > "$BLOCKFILE"
    if awk -v start="<!-- ant-farm:start -->" -v end="<!-- ant-farm:end -->" -v blockfile="$BLOCKFILE" '
        $0 == start {
            while ((getline line < blockfile) > 0) print line
            close(blockfile)
            skip=1; next
        }
        skip && $0 == end { skip=0; next }
        !skip { print }
    ' "$REPO_CLAUDE" > "$TMPFILE" && mv "$TMPFILE" "$REPO_CLAUDE"; then
        PROMPT_STATUS="updated"
    else
        rm -f "$TMPFILE" "$BLOCKFILE"
        echo "ERROR: awk replacement failed — $REPO_CLAUDE unchanged"
    fi
    rm -f "$BLOCKFILE"
fi
```

**If `STATE=error_partial`** — Only one sentinel marker found; do not modify the file:

> **Error**: `CLAUDE.md` contains only one of the two ant-farm sentinel markers (`<!-- ant-farm:start -->` / `<!-- ant-farm:end -->`). The file may be corrupt. Fix it manually, then re-run `/ant-farm-init`.

Set `PROMPT_STATUS="error (partial markers)"`.

Store `PROMPT_STATUS` for use in Step 9.

## Step 9 — Initialization Summary

Print a summary of what was done:

> **ant-farm init complete**
>
> - `.crumbs/tasks.jsonl` — [created / already existed]
> - `.crumbs/config.json` — [created with prefix `<PREFIX>` / already existed]
> - `.crumbs/sessions/` — [created / already existed]
> - `.crumbs/history/` — [created / already existed]
> - `.gitignore` — [updated / already up to date]
> - `crumb` CLI — [installed to `~/.local/bin/crumb` / already installed at `<PATH>` / manual install required]
> - **`CLAUDE.md` (orchestration block)** — [created / updated / already up to date / error (partial markers) / skipped (block source not found)]
>
> **CLAUDE.md verification**: If the CLAUDE.md status above is NOT "created", "updated", or "already up to date", the orchestration framework will not work. Re-run `/ant-farm-init` or manually install the block.
>
> **Next steps:**
> 1. Run `/ant-farm-plan` to decompose a spec or issue into tasks
> 2. Run `/ant-farm-work` to start execution

## Error Reference

| Condition | Behavior |
|---|---|
| Prefix validation fails | Re-prompt user with correction message |
| `.crumbs/` already initialized | Idempotent repair — verify and fill missing components, preserve data |
| `crumb.py` not found in repo | Warn user, provide manual install instructions, continue with other steps |
| `crumb` not on PATH after install | Warn user with PATH export instructions, continue |
| `.gitignore` write fails (permission error) | Warn user, provide manual fix command, continue |
