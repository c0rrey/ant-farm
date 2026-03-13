# Installation Guide

This guide covers installing and managing the ant-farm orchestration system. The setup script (`scripts/setup.sh`) installs agent definitions, orchestration files, skills, the `crumb` CLI, and `CLAUDE.md` to their runtime locations.

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
2. **Orchestration files** -- copies `orchestration/` to `~/.claude/orchestration/` (excluding `_archive/`)
3. **Review script** -- copies `scripts/build-review-prompts.sh` to `~/.claude/orchestration/scripts/` and marks it executable
4. **Skills** -- copies `skills/*.md` to `~/.claude/skills/ant-farm-<name>/SKILL.md`
5. **Crumb CLI** -- copies `crumb.py` to `~/.local/bin/crumb` and marks it executable
6. **CLAUDE.md** -- copies `CLAUDE.md` to `~/.claude/CLAUDE.md`
7. **PATH check** -- warns if `~/.local/bin` is not in your PATH
8. **Preflight check** -- warns if `~/.claude/agents/code-reviewer.md` is missing (required by the Nitpicker review team)

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
ls ~/.claude/agents/

# Confirm orchestration files are installed
ls ~/.claude/orchestration/

# Confirm crumb CLI is available
crumb --help

# Confirm skills are installed
ls ~/.claude/skills/ant-farm-*/
```

**Verify the pre-commit PII scrubbing** (if `.crumbs/tasks.jsonl` contains email addresses):

```bash
# Stage tasks.jsonl and commit -- the hook should run automatically
git add .crumbs/tasks.jsonl
git commit -m "test: verify pre-commit scrub hook"
```

You should see the message: `[ant-farm] PII scrub applied and re-staged: .crumbs/tasks.jsonl`

## Understanding Setup Behavior

The setup process copies files from the repo to runtime locations. It is idempotent: re-running updates changed files and leaves unchanged files alone.

### CLAUDE.md Installation

- **Source**: `{repo-root}/CLAUDE.md`
- **Target**: `~/.claude/CLAUDE.md`
- **Behavior**: Copies with timestamped backup of existing file
- **Why**: Project-specific instructions (like Parallel Work Mode) must be available in `~/.claude/` for the Queen to load at startup

**Backup Location**: `~/.claude/CLAUDE.md.bak.[YYYYMMDDTHHMMSS]`

If you edit `~/.claude/CLAUDE.md` directly, those changes will be overwritten next time you run `setup.sh`. Backup files are created but never automatically deleted.

### Orchestration Directory Installation

- **Source**: `{repo-root}/orchestration/`
- **Target**: `~/.claude/orchestration/`
- **Behavior**: File-by-file copy (adds/updates files from source, preserves user-created files in target). Files under `_archive/` are excluded.
- **Contents**: RULES.md, templates/, reference/, SETUP.md, etc.

Files deleted from the repo's `orchestration/` directory will **not** be automatically removed from `~/.claude/orchestration/`. This preserves any custom files adopters have placed in the target. If you need to remove a stale file from the target, delete it manually from `~/.claude/orchestration/`.

### Agent Definitions Installation

- **Source**: `{repo-root}/agents/`
- **Target**: `~/.claude/agents/`
- **Behavior**: File-by-file copy with change detection
- **Contents**: Custom agent type definitions (.md files)

New or changed agent files require a Claude Code restart to load.

### Skills Installation

- **Source**: `{repo-root}/skills/*.md`
- **Target**: `~/.claude/skills/ant-farm-<name>/SKILL.md`
- **Behavior**: Each skill file gets its own directory named `ant-farm-<basename>`
- **Contents**: Slash command definitions (e.g., `/ant-farm:work`, `/ant-farm:plan`)

### Crumb CLI Installation

- **Source**: `{repo-root}/crumb.py`
- **Target**: `~/.local/bin/crumb`
- **Behavior**: Copy with backup, marked executable
- **Contents**: The task-tracking CLI used by all agents

### File Backups

The setup script backs up any existing target file that differs from the source before overwriting. Backups use a timestamped `.bak` suffix (e.g., `CLAUDE.md.bak.20260313T142500`). Each run uses a single timestamp for all backups. Unchanged files are not backed up or rewritten.

## Backup Strategy

The setup process automatically creates timestamped backups of changed files. Understand what is backed up and why.

### Automatic Backups

**CLAUDE.md Backup**

Every setup run backs up the existing `~/.claude/CLAUDE.md` before overwriting (if the content differs):

```
~/.claude/CLAUDE.md.bak.20260217T214523
~/.claude/CLAUDE.md.bak.20260217T215015
```

Format: `<filename>.bak.<YYYYMMDDTHHMMSS>`

**When**: Every time `setup.sh` runs and the file has changed
**Why**: If the repo's CLAUDE.md becomes corrupted or accidentally breaks your Claude Code behavior, you can restore a previous version

**How to Restore**:

```bash
# List available backups
ls -la ~/.claude/CLAUDE.md.bak.*

# Restore a specific backup
cp ~/.claude/CLAUDE.md.bak.20260217T214523 ~/.claude/CLAUDE.md
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
rm ~/.claude/agents/scout-organizer.md
rm ~/.claude/agents/pantry-impl.md
rm ~/.claude/agents/pest-control.md
rm ~/.claude/agents/nitpicker.md
rm ~/.claude/agents/big-head.md

# Remove orchestration directory
rm -rf ~/.claude/orchestration/

# Remove skills
rm -rf ~/.claude/skills/ant-farm-*/

# Remove crumb CLI
rm ~/.local/bin/crumb
```

### Step 2: Clean Up `~/.claude/` (Optional)

```bash
# Full removal (WARNING: This deletes all ~/.claude/ content)
rm -rf ~/.claude/

# Or selective removal (keep only CLAUDE.md)
rm -rf ~/.claude/orchestration/ ~/.claude/agents/ ~/.claude/skills/
```

### Step 3: Restore Manual CLAUDE.md (If Desired)

If you backed up a personal `~/.claude/CLAUDE.md` before installing ant-farm, you can restore it:

```bash
# Find your backup
ls -la ~/.claude/CLAUDE.md.bak.*

# Restore an old backup
cp ~/.claude/CLAUDE.md.bak.XXXXXXX ~/.claude/CLAUDE.md
```

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

### `~/.claude/CLAUDE.md` Overwritten Too Frequently

**Symptom**: Personal edits to `~/.claude/CLAUDE.md` keep getting overwritten.

**Why**: The setup script overwrites `~/.claude/CLAUDE.md` to keep project instructions in sync.

**Solutions**:

1. **Edit the repo's CLAUDE.md instead**: Changes made to the repo's `CLAUDE.md` will be installed to `~/.claude/CLAUDE.md` on the next setup run.

2. **Create a personal global instructions file**: If you have personal Claude Code preferences, store them in a separate file and source them from the synced CLAUDE.md:
   ```markdown
   # In ~/.claude/CLAUDE.md (synced from repo)
   # Include personal settings from home directory
   ```
   Then create `~/.claude-personal.md` for your personal rules.

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
rm ~/.claude/CLAUDE.md.bak.*
```

## Next Steps

After installation:

1. **Read orchestration/RULES.md**: Understand the Queen's workflow rules
2. **Read orchestration/templates/**: Review available agent templates for your use case
3. **Start a session**: Use "Let's get to work on: <task-ids>" to begin collaborative work

## See Also

- `orchestration/SETUP.md` -- Orchestration system overview and quick setup
- `orchestration/RULES.md` -- Queen and subagent workflow rules
- `scripts/setup.sh` -- Setup script source
