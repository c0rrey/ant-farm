# ant-farm

Version-controlled home for `~/.claude/` orchestration files — the global agent instructions and multi-agent workflow system used across all Claude Code projects.

## What's here

| Path | Purpose |
|------|---------|
| `CLAUDE.md` | Global agent instructions (prompt engineering mode, parallel work trigger, session completion rules) |
| `orchestration/RULES.md` | Workflow steps, hard gates, concurrency rules, template lookup table |
| `orchestration/SETUP.md` | How to wire orchestration into a new project |
| `orchestration/templates/` | Agent skeletons, review skeletons, checkpoints, prompt factory, boss-bot state |
| `orchestration/reference/` | Dependency analysis guide, known failure patterns |
| `orchestration/_archive/` | Legacy docs kept for reference |
| `scripts/sync-to-claude.sh` | Syncs repo contents back to `~/.claude/` |

## How it works

Files in this repo are the **source of truth** for `~/.claude/CLAUDE.md` and `~/.claude/orchestration/`.

A `pre-push` git hook runs `scripts/sync-to-claude.sh` on every push, which copies the committed files back to `~/.claude/` so all other projects pick up the latest versions immediately.

```
edit in ant-farm → commit → push → hook syncs to ~/.claude/ → all projects see updates
```

### Sync details

- `CLAUDE.md` is copied with `cp`
- `orchestration/` is synced with `rsync --delete` (propagates removals)
- Repo-only files (`README.md`, `scripts/`, `.gitignore`) are **not** synced
- If the sync script fails, the push is aborted

### One-way sync caveat

This is repo → `~/.claude/` only. Edits made directly to `~/.claude/` files (e.g., from a Claude Code session in another project) will be overwritten on the next push. To pull those edits back in:

```bash
cp ~/.claude/CLAUDE.md ./CLAUDE.md
rsync -av ~/.claude/orchestration/ ./orchestration/
git diff  # review what changed
```

## Orchestration overview

The orchestration system manages multi-agent Claude Code sessions. When you say **"let's get to work"** in any project wired up per `SETUP.md`, Claude reads `RULES.md` and follows a structured workflow:

1. **Pre-flight** — gather task metadata, analyze file conflicts, present execution strategy, wait for approval
2. **Spawn** — Prompt Factory composes agent prompts, boss-bot spawns agents using skeletons
3. **Monitor** — track agents, run checkpoints after each wave
4. **Review** — mandatory code reviews after all implementation completes
5. **Document** — update CHANGELOG, README, CLAUDE.md
6. **Land** — push to remote, clean up session artifacts

Key constraints:
- Max 7 concurrent agents
- No two agents edit the same file
- Three hard gates (Checkpoints A, B, C) block progression
- Boss-bot delegates all implementation — never reads source code directly
