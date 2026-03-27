# Installation Guide

This guide covers installing and managing the ant-farm orchestration system. The setup script (`scripts/setup.sh`) installs agent definitions, orchestration files, skills, and the `crumb` CLI to their runtime locations, and writes the orchestration block to the project's `CLAUDE.md`.

## Table of Contents

1. [Installation](#installation)
2. [Understanding Setup Behavior](#understanding-setup-behavior)
3. [Backup Strategy](#backup-strategy)
4. [Uninstalling](#uninstalling)

## Installation

### Prerequisites

- Git repository initialized in your project (`.git/` directory exists)
- Bash shell or compatible shell environment
- Read/write permissions to `~/.claude/` and `~/.local/bin/`

### Step 1: Run the Setup Script

`setup.sh` installs all ant-farm components to their runtime locations. Run this command from the project root:

```bash
./scripts/setup.sh
```

To preview what would change without writing anything:

```bash
./scripts/setup.sh --dry-run
```

The script performs these steps:

1. **Agent definitions** -- copies `agents/*.md` to `~/.claude/agents/`
2. **Orchestration files** -- copies `orchestration/` to `~/.claude/orchestration/`
3. **Review script** -- copies `scripts/build-review-prompts.sh` to `~/.claude/orchestration/scripts/` and marks it executable
4. **Skills** -- copies `skills/*.md` to `~/.claude/skills/ant-farm-<name>/SKILL.md`
5. **Crumb CLI** -- copies `crumb.py` to `~/.local/bin/crumb` and marks it executable
6. **Hooks** -- copies `hooks/*.js` and `hooks/lib/` to `~/.claude/hooks/`
7. **MCP server** -- copies `mcp_server.py` to `~/.claude/mcp_server.py`
8. **Hook registration** -- registers hooks in `~/.claude/settings.json` (statusLine, PreToolUse, PostToolUse events)
9. **MCP registration** -- registers the MCP server in `~/.claude.json`
10. **CLAUDE.md** -- removes any existing ant-farm sentinel block from `~/.claude/CLAUDE.md` (migration cleanup), removes any stale block from the per-project prompt-dir file (migration cleanup), then writes the ant-farm prompt block to the repo's own `CLAUDE.md`
11. **PATH check** -- warns if `~/.local/bin` is not in your PATH
12. **Preflight check** -- warns if `~/.claude/agents/code-reviewer.md` is missing (required by the Reviewer team)

### Step 2: Verify PATH

If the setup script warns that `~/.local/bin` is not in your PATH, add it to your shell profile:

```bash
# Add to ~/.zshrc or ~/.bashrc:
export PATH="$HOME/.local/bin:$PATH"
```

Then restart your shell or run `source ~/.zshrc`.

Verify the `crumb` CLI is available:

```bash
crumb --help
```

### Step 3: Restart Claude Code

If the setup script reports that agent files were installed or updated:

```
[ant-farm] Agent files were installed or updated.
[ant-farm] You MUST restart Claude Code for new/changed agent
[ant-farm] definitions to take effect.
```

Then **fully quit and reopen Claude Code**. Agent types are loaded at startup and won't appear in the available agents list until Claude Code is restarted.

### Verification

To verify the installation:

```bash
# Confirm agent files are installed
ls ~/.claude/agents/ant-farm-*.md

# Confirm orchestration files are installed
ls ~/.claude/orchestration/

# Confirm hooks are installed
ls ~/.claude/hooks/ant-farm-*.js

# Confirm MCP server is installed
ls ~/.claude/mcp_server.py

# Confirm crumb CLI is available
crumb --help

# Confirm skills are installed
ls ~/.claude/skills/ant-farm-*/SKILL.md
```

## Understanding Setup Behavior

The setup process copies files from the repo to runtime locations. It is idempotent: re-running updates changed files and leaves unchanged files alone.

### CLAUDE.md: Global Migration Cleanup

- **Action**: Removes any existing ant-farm sentinel block (`<!-- ant-farm:start -->` / `<!-- ant-farm:end -->` and everything between them) from `~/.claude/CLAUDE.md`. Content outside the block is left untouched.
- **Why**: Earlier versions of ant-farm injected a sentinel block into the global `~/.claude/CLAUDE.md`. The current model stores instructions in the repo's own `CLAUDE.md` (loaded by Claude Code at session start). Step 6a removes the old global block so the global file is not polluted.

If `~/.claude/CLAUDE.md` contains no ant-farm sentinel block, this step is a no-op.

### Prompt-Dir Migration Cleanup

After global cleanup, `setup.sh` removes any stale ant-farm block from the per-project prompt-dir file:

- **Target**: `~/.claude/projects/-<escaped-project-path>/CLAUDE.md`
- **Action**: Removes the ant-farm sentinel block if present. Content outside the block is preserved.
- **Why**: An intermediate version of ant-farm stored the block in the prompt-dir file. The current model stores it in the repo's own `CLAUDE.md` instead (see below). Step 6b removes the stale copy.

### Repo CLAUDE.md Installation

After migration cleanup, `setup.sh` writes the ant-farm prompt block to the repo's own `CLAUDE.md`:

- **Source**: `{repo-root}/orchestration/templates/claude-block.md`
- **Target**: `{repo-root}/CLAUDE.md`
- **Behavior**: Inserts or replaces the ant-farm sentinel block in the repo's CLAUDE.md. Content outside the block is preserved.
- **Why**: Claude Code loads the repo's `CLAUDE.md` into the system prompt at session start. Storing the block here means the instructions are active for this project without modifying the global `~/.claude/CLAUDE.md` or relying on prompt-dir files.

### Orchestration Directory Installation

- **Source**: `{repo-root}/orchestration/`
- **Target**: `~/.claude/orchestration/`
- **Behavior**: File-by-file copy (adds/updates files from source, preserves user-created files in target).
- **Contents**: RULES.md, templates/, reference/, SETUP.md, etc.

Files deleted from the repo's `orchestration/` directory will **not** be automatically removed from `~/.claude/orchestration/`. This preserves any custom files adopters have placed in the target. If you need to remove a stale file from the target, delete it manually from `~/.claude/orchestration/`.

### Agent Definitions Installation

- **Source**: `{repo-root}/agents/`
- **Target**: `~/.claude/agents/`
- **Behavior**: File-by-file copy with change detection
- **Contents**: Custom agent type definitions (.md files)

New or changed agent files require a Claude Code restart to load.

### Hooks Installation

- **Source**: `{repo-root}/hooks/*.js` and `{repo-root}/hooks/lib/`
- **Target**: `~/.claude/hooks/`
- **Behavior**: File-by-file copy with change detection
- **Contents**: Claude Code event hooks (PreToolUse, PostToolUse, statusLine) and shared libraries

After copying, setup.sh registers hooks in `~/.claude/settings.json` via `npm/lib/hooks-registration.js`. This adds entries for each hook's event type and tool matcher (e.g., scope advisor triggers on Write|Edit, gate enforcer on Task|TeamCreate|SendMessage).

### MCP Server Installation

- **Source**: `{repo-root}/mcp_server.py`
- **Target**: `~/.claude/mcp_server.py`
- **Behavior**: Copy with change detection
- **Contents**: MCP server exposing crumb.py operations as MCP tools

After copying, setup.sh registers the server in `~/.claude.json` via `npm/lib/mcp-registration.js`. This tells Claude Code to start the MCP server at session launch.

### Skills Installation

- **Source**: `{repo-root}/skills/*.md`
- **Target**: `~/.claude/skills/ant-farm-<name>/SKILL.md`
- **Behavior**: Each skill file is placed in its own directory under `~/.claude/skills/`
- **Contents**: Slash command definitions (`/ant-farm-work`, `/ant-farm-plan`, `/ant-farm-quick`, `/ant-farm-pause`, `/ant-farm-status`, `/ant-farm-init`)

### Crumb CLI Installation

- **Source**: `{repo-root}/crumb.py`
- **Target**: `~/.local/bin/crumb`
- **Behavior**: Copy with backup, marked executable
- **Contents**: The task-tracking CLI used by all agents

### File Backups

The setup script backs up any existing target file that differs from the source before overwriting. Backups use a timestamped `.af-bak` suffix (e.g., `CLAUDE.md.af-bak.20260313T142500`). Each run uses a single timestamp for all backups. Unchanged files are not backed up or rewritten.

## Backup Strategy

The setup process automatically creates timestamped backups of changed files. Understand what is backed up and why.

### Automatic Backups

**CLAUDE.md Backup**

When setup.sh detects an ant-farm block in `~/.claude/CLAUDE.md`, it backs up the file before removing the block. If no block is present, no backup is created.

```
~/.claude/CLAUDE.md.af-bak.20260217T214523
~/.claude/CLAUDE.md.af-bak.20260217T215015
```

Format: `<filename>.af-bak.<YYYYMMDDTHHMMSS>`

**When**: Only when setup.sh removes an ant-farm block from `~/.claude/CLAUDE.md`.
**Why**: If the block removal has an unintended side effect, you can restore the pre-removal state from the backup.

**How to Restore**:

```bash
# List available backups
ls -la ~/.claude/CLAUDE.md.af-bak.*

# Restore a specific backup
cp ~/.claude/CLAUDE.md.af-bak.20260217T214523 ~/.claude/CLAUDE.md
```

### Manual Backups

For extra safety, back up `~/.claude/` before major changes:

```bash
# Full backup
cp -r ~/.claude ~/.claude.backup.$(date +%Y%m%d_%H%M%S)

# Later restore if needed
rm -rf ~/.claude/*
cp -r ~/.claude.backup.20260217_214523/* ~/.claude/
```

### What Is NOT Automatically Backed Up

- **orchestration/** directory — The source is in version control (.git), so restoring from there is safer than relying on backups
- **agents/** directory — Same rationale as orchestration/
- **hooks/** directory — Same rationale as orchestration/
- **MCP server** — Same rationale as orchestration/
- **settings.json / .claude.json registrations** — Hook and MCP registrations are additive; re-running setup.sh restores them
- **Session artifacts** — `.crumbs/sessions/` contains working files, not meant for backup

If you need to recover orchestration files, use git:

```bash
git show HEAD:orchestration/RULES.md > /tmp/recovered-RULES.md
```

## Uninstalling

If you want to remove ant-farm from your system, follow these steps.

### Step 1: Remove Installed Files

```bash
# Remove agents installed by ant-farm
rm ~/.claude/agents/ant-farm-recon-planner.md
rm ~/.claude/agents/ant-farm-prompt-composer.md
rm ~/.claude/agents/ant-farm-checkpoint-auditor.md
rm ~/.claude/agents/ant-farm-reviewer-clarity.md
rm ~/.claude/agents/ant-farm-reviewer-edge-cases.md
rm ~/.claude/agents/ant-farm-reviewer-correctness.md
rm ~/.claude/agents/ant-farm-reviewer-drift.md
rm ~/.claude/agents/ant-farm-review-consolidator.md
rm ~/.claude/agents/ant-farm-task-decomposer.md
rm ~/.claude/agents/ant-farm-researcher.md
rm ~/.claude/agents/ant-farm-spec-writer.md
rm ~/.claude/agents/ant-farm-session-scribe.md

# Remove hooks and hook libraries
rm -rf ~/.claude/hooks/ant-farm-*.js
rm -rf ~/.claude/hooks/lib/

# Remove MCP server
rm ~/.claude/mcp_server.py

# Remove orchestration directory
rm -rf ~/.claude/orchestration/

# Remove skills
rm -rf ~/.claude/skills/ant-farm-init/
rm -rf ~/.claude/skills/ant-farm-plan/
rm -rf ~/.claude/skills/ant-farm-quick/
rm -rf ~/.claude/skills/ant-farm-pause/
rm -rf ~/.claude/skills/ant-farm-status/
rm -rf ~/.claude/skills/ant-farm-work/

# Remove crumb CLI
rm ~/.local/bin/crumb
```

**Note**: Hook registrations in `~/.claude/settings.json` and MCP registrations in `~/.claude.json` are not automatically removed. Edit those files manually to remove ant-farm entries, or delete them if ant-farm was the only consumer.

### Step 2: Clean Up `~/.claude/` (Optional)

```bash
# Full removal (WARNING: This deletes all ~/.claude/ content)
rm -rf ~/.claude/

# Or selective removal (keep only CLAUDE.md)
rm -rf ~/.claude/orchestration/ ~/.claude/agents/ ~/.claude/skills/
```

### Step 3: Remove Repo CLAUDE.md Block

The setup script writes an ant-farm block to the repo's `CLAUDE.md`. Remove the block (between the sentinel markers) or delete the file:

```bash
# Open CLAUDE.md and delete content between these markers (inclusive):
# <!-- ant-farm:start -->
# <!-- ant-farm:end -->
```

If an older install left a stale prompt-dir file, remove it too:

```bash
# Determine the escaped path for your project
# Replace each '/' in the absolute project path with '-'
# Example: /Users/alice/projects/ant-farm → -Users-alice-projects-ant-farm
rm ~/.claude/projects/-<escaped-project-path>/CLAUDE.md

# If that leaves the project directory empty, remove it too
rmdir ~/.claude/projects/-<escaped-project-path>/
```

### Step 4: Restore Global CLAUDE.md (If Desired)

If you had a personal `~/.claude/CLAUDE.md` before installing ant-farm (older installs may have left a backup), you can restore it:

```bash
# Find any backup
ls -la ~/.claude/CLAUDE.md.af-bak.*

# Restore an old backup
cp ~/.claude/CLAUDE.md.af-bak.XXXXXXX ~/.claude/CLAUDE.md
```

If you never had a personal `~/.claude/CLAUDE.md`, no action is needed — the migration cleanup in Step 6a of setup.sh already removed the ant-farm sentinel block from the global file.

### Verification

Verify removal:

```bash
# Check that orchestration is removed
ls -la ~/.claude/orchestration/

# Check that crumb is removed
which crumb
```

### Reinstalling After Removal

You can safely reinstall later by re-running the setup script:

```bash
./scripts/setup.sh
# Restart Claude Code
```

The script backs up existing files, so re-running is safe.

## Troubleshooting

### Agents Not Appearing in Claude Code

**Symptom**: New agents are listed in `~/.claude/agents/` but don't appear in Claude Code's agent selection.

**Solution**: Fully quit and reopen Claude Code. Agent types are loaded at startup only.

```bash
# Quit Claude Code (Cmd+Q on macOS, Ctrl+Q on Linux, etc.)
# Then reopen Claude Code application
```

### `crumb` Command Not Found

**Symptom**: Running `crumb` returns "command not found".

**Solutions**:

1. Verify `~/.local/bin` is in your PATH:
   ```bash
   echo $PATH | tr ':' '\n' | grep local
   ```
   If missing, add to your shell profile:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

2. Verify the file exists and is executable:
   ```bash
   ls -la ~/.local/bin/crumb
   ```

### Ant-Farm Instructions Not Loading

**Symptom**: ant-farm instructions are not active when working in the project — the Orchestrator does not follow Parallel Work Mode or other project-specific rules.

**Why**: Claude Code loads the repo's `CLAUDE.md` into the system prompt at session start. The ant-farm block must be present in `CLAUDE.md` at the repo root.

**Solutions**:

1. **Re-run setup.sh** to write (or refresh) the ant-farm block in the repo's `CLAUDE.md`:
   ```bash
   ./scripts/setup.sh
   ```

2. **Verify the block is present**:
   ```bash
   grep 'ant-farm:start' CLAUDE.md
   ```

3. **Restart Claude Code** after modifying `CLAUDE.md`, to ensure the file is loaded fresh.

### Personal `~/.claude/CLAUDE.md` Edits Not Overwritten

The current version of ant-farm does **not** write to `~/.claude/CLAUDE.md`. If you see unexpected changes to that file, check whether an older version of `setup.sh` left a sentinel block. You can remove it manually:

```bash
# Open the file and delete any content between these markers (inclusive):
# <!-- ant-farm:start -->
# <!-- ant-farm:end -->
```

Running the current `setup.sh` also removes this block automatically (Step 6a).

### Permission Denied on `~/.claude/`

**Symptom**: Running `setup.sh` produces permission errors.

**Solution**:
```bash
# Check permissions
ls -ld ~/.claude/

# Fix permissions
chmod 755 ~/.claude/
chmod 755 ~/.claude/orchestration/
chmod 755 ~/.claude/agents/
```

### Disk Space Issues

```bash
# Check available disk space
df -h ~

# Clear old CLAUDE.md backups if needed
rm ~/.claude/CLAUDE.md.af-bak.*
```

## Next Steps

After installation:

1. **Read orchestration/RULES.md**: Understand the Orchestrator's workflow rules
2. **Read orchestration/templates/**: Review available agent templates for your use case
3. **Start a session**: Use "Let's get to work on: <task-ids>" to begin collaborative work

## See Also

- `orchestration/SETUP.md` -- Orchestration system overview and quick setup
- `orchestration/RULES.md` -- Orchestrator and subagent workflow rules
- `scripts/setup.sh` -- Setup script source
