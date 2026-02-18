# Installation Guide: Hook/Sync Workflow

This guide covers installing and managing the ant-farm orchestration system's pre-push hook and sync mechanism. The hook automatically syncs your agent definitions, templates, and configuration to `~/.claude/` on every `git push`.

## Table of Contents

1. [Installation](#installation)
2. [Understanding Sync Behavior](#understanding-sync-behavior)
3. [Backup Strategy](#backup-strategy)
4. [Uninstalling the Hook](#uninstalling-the-hook)

## Installation

### Prerequisites

- Git repository initialized in your project (`.git/` directory exists)
- Bash shell or compatible shell environment
- Read/write permissions to `.git/hooks/` and `~/.claude/`

### Step 1: Install the Pre-Push Hook

The pre-push hook automates syncing on every `git push`. Run this command from your project root:

```bash
./scripts/install-hooks.sh
```

This script:
- Creates `.git/hooks/pre-push` with the hook code
- Backs up any existing hook to `.git/hooks/pre-push.bak` (safe to re-run)
- Makes the hook executable

### Step 2: Perform Initial Sync

After installing the hook, manually run the sync script to update `~/.claude/` immediately:

```bash
./scripts/sync-to-claude.sh
```

This script:
- Creates `~/.claude/orchestration/` and `~/.claude/agents/` if they don't exist
- Backs up your existing `~/.claude/CLAUDE.md` to `~/.claude/CLAUDE.md.bak.[timestamp]`
- Copies your project's `CLAUDE.md` to `~/.claude/CLAUDE.md`
- Syncs all files from `orchestration/` to `~/.claude/orchestration/` (using rsync --delete)
- Copies all agent definitions from `agents/` to `~/.claude/agents/`
- Reports if any agent files were updated (see Step 3 below)

### Step 3: Restart Claude Code

If the sync script reports that agent files were updated:

```
[ant-farm] Agent files were updated. Reload Claude Code for changes to take effect.
```

Then **fully quit and reopen Claude Code**. Agent types are loaded at startup and won't appear in the available agents list until Claude Code is restarted.

### Verification

To verify the installation works:

```bash
# Make a small change to a file
echo "# Test" >> docs/test.md

# Commit and push
git add docs/test.md
git commit -m "test: verify hook installation"
git push

# Check that ~/.claude/ was updated
ls -la ~/.claude/orchestration/
ls -la ~/.claude/agents/
```

You should see the current date/time in the file modification times.

## Understanding Sync Behavior

The sync process performs these operations:

### CLAUDE.md Synchronization

- **Source**: `{repo-root}/CLAUDE.md`
- **Target**: `~/.claude/CLAUDE.md`
- **Behavior**: Unconditional copy with timestamped backup
- **Why**: Project-specific instructions (like Parallel Work Mode) must be available in `~/.claude/` for the Queen to load at startup

**Backup Location**: `~/.claude/CLAUDE.md.bak.[YYYYMMDDTHHMMSS]`

If you edit `~/.claude/CLAUDE.md` directly, those changes will be overwritten on the next `git push`. Backup files are created but never automatically deleted.

### Orchestration Directory Synchronization

- **Source**: `{repo-root}/orchestration/`
- **Target**: `~/.claude/orchestration/`
- **Behavior**: One-way sync with `--delete` flag (removes files from target that no longer exist in source)
- **Contents**: RULES.md, templates/, reference/, SETUP.md, etc.

Files deleted from the repo's `orchestration/` directory will be deleted from `~/.claude/orchestration/` on the next sync. This ensures stale templates and outdated rules don't interfere with active sessions.

### Agent Definitions Synchronization

- **Source**: `{repo-root}/agents/`
- **Target**: `~/.claude/agents/`
- **Behavior**: File-by-file copy with change detection
- **Contents**: Custom agent type definitions (.md files)

New agent files require a Claude Code restart to load. Existing agents are updated but don't require a restart unless they define new capabilities.

### File Permissions

The hook preserves file permissions:
- `~/.claude/CLAUDE.md` — readable by user (600)
- `~/.claude/orchestration/` files — readable by user (644)
- `~/.claude/agents/` files — readable by user (644)

## Backup Strategy

The sync process automatically creates timestamped backups of critical files. Understand what is backed up and why.

### Automatic Backups

**CLAUDE.md Backup**

Every sync backs up the existing `~/.claude/CLAUDE.md` before overwriting:

```
~/.claude/CLAUDE.md.bak.20260217T214523
~/.claude/CLAUDE.md.bak.20260217T215015
~/.claude/CLAUDE.md.bak.20260217T220133
```

Format: `CLAUDE.md.bak.[YYYYMMDDTHHMMSS]`

**When**: Every time `git push` runs the hook
**Why**: If the repo's CLAUDE.md becomes corrupted or accidentally breaks your Claude Code behavior, you can restore a previous version

**How to Restore**:

```bash
# List available backups
ls -la ~/.claude/CLAUDE.md.bak.*

# Restore a specific backup
cp ~/.claude/CLAUDE.md.bak.20260217T214523 ~/.claude/CLAUDE.md
```

**Hook Backup** (if you had a previous hook)

If you re-run `install-hooks.sh` and a `.git/hooks/pre-push` already exists, it's backed up to `.git/hooks/pre-push.bak`.

This is stored in your local git directory (not synced to remote):

```
.git/hooks/pre-push.bak
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
- **Individual session artifacts** — `.beads/agent-summaries/` and other session state are working files, not meant for backup

If you need to recover orchestration files, use git:

```bash
git show HEAD:orchestration/RULES.md > /tmp/recovered-RULES.md
```

## Uninstalling the Hook

If you want to remove the orchestration hook and stop syncing to `~/.claude/`, follow these steps.

### Step 1: Remove the Hook

```bash
# Delete the hook (the backup is preserved if you re-run install-hooks.sh later)
rm ~/.git/hooks/pre-push

# Alternatively, restore your previous hook if one existed
cp .git/hooks/pre-push.bak .git/hooks/pre-push
```

### Step 2: Clean Up `~/.claude/` (Optional)

The sync files remain in `~/.claude/` even after removing the hook. To clean up:

```bash
# Full removal (WARNING: This deletes all ~/.claude/ content)
rm -rf ~/.claude/

# Or selective removal (keep only CLAUDE.md)
rm -rf ~/.claude/orchestration/ ~/.claude/agents/
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
# Hook should not exist
ls -la .git/hooks/pre-push

# This should show error or be empty (depending on your cleanup choice)
ls -la ~/.claude/orchestration/
```

### Reinstalling After Removal

You can safely reinstall the hook later by re-running the installation steps:

```bash
./scripts/install-hooks.sh
./scripts/sync-to-claude.sh
# Restart Claude Code
```

The scripts back up existing files, so re-running is safe.

## Troubleshooting

### Hook Not Running on `git push`

**Symptom**: Agents are not updated in `~/.claude/` after pushing.

**Solutions**:

1. Verify the hook is executable:
   ```bash
   ls -la .git/hooks/pre-push
   ```
   Should show `-rwxr-xr-x` (executable). If not:
   ```bash
   chmod +x .git/hooks/pre-push
   ```

2. Verify the hook file exists and is correct:
   ```bash
   cat .git/hooks/pre-push
   ```
   Should show the sync script path. If corrupted, reinstall:
   ```bash
   ./scripts/install-hooks.sh
   ```

3. Check if `sync-to-claude.sh` is executable:
   ```bash
   ls -la scripts/sync-to-claude.sh
   chmod +x scripts/sync-to-claude.sh
   ```

### Agents Not Appearing in Claude Code

**Symptom**: New agents are listed in `~/.claude/agents/` but don't appear in Claude Code's agent selection.

**Solution**: Fully quit and reopen Claude Code. Agent types are loaded at startup only.

```bash
# Quit Claude Code (⌘Q on macOS, Ctrl+Q on Linux, etc.)
# Then reopen Claude Code application
```

### `~/.claude/CLAUDE.md` Overwritten Too Frequently

**Symptom**: Personal edits to `~/.claude/CLAUDE.md` keep getting overwritten.

**Why**: The hook overwrites `~/.claude/CLAUDE.md` on every `git push` to keep project instructions in sync.

**Solutions**:

1. **Edit the repo's CLAUDE.md instead**: Changes made to the repo's `CLAUDE.md` will sync to `~/.claude/CLAUDE.md`.

2. **Create a personal global instructions file**: If you have personal Claude Code preferences, store them in a separate file and source them from the synced CLAUDE.md:
   ```markdown
   # In ~/.claude/CLAUDE.md (synced from repo)
   # Include personal settings from home directory
   ```
   Then create `~/.claude-personal.md` for your personal rules.

3. **Use git hooks to preserve local changes**: Advanced users can modify `.git/hooks/pre-push` to preserve local CLAUDE.md edits, but this breaks the intended sync behavior.

### Sync Script Errors

**Symptom**: Running `sync-to-claude.sh` produces errors.

**Common issues**:

1. **rsync not installed** (rare on macOS/Linux):
   ```bash
   # Install rsync
   brew install rsync  # macOS
   sudo apt-get install rsync  # Linux
   ```

2. **Permission denied on `~/.claude/`**:
   ```bash
   # Check permissions
   ls -ld ~/.claude/

   # Fix permissions
   chmod 755 ~/.claude/
   chmod 755 ~/.claude/orchestration/
   chmod 755 ~/.claude/agents/
   ```

3. **Disk space issues**:
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
4. **Monitor syncs**: Check `~/.claude/` after pushes to confirm agents and rules are current

## See Also

- `orchestration/SETUP.md` — Orchestration system overview and quick setup
- `orchestration/RULES.md` — Queen and subagent workflow rules
- `scripts/install-hooks.sh` — Installation script source
- `scripts/sync-to-claude.sh` — Sync script source
