# ant-farm Project Instructions

This is the **ant-farm** repository — the orchestration system for Claude Code parallel work sessions.

## Orchestration Triggers

The "let's get to work" trigger and session-completion ("landing the plane") orchestration blocks are installed via `/ant-farm:init`. That command writes the canonical block from `orchestration/templates/claude-block.md` into the prompt-dir CLAUDE.md (`~/.claude/projects/-<escaped-project-path>/CLAUDE.md`), not into this repo-root file.

Do not add orchestration trigger sections here. Edit `orchestration/templates/claude-block.md` as the single source of truth for those blocks.

## Project Structure

- `orchestration/RULES.md` — Queen's workflow rules
- `orchestration/templates/` — Agent prompts, checkpoints, reviews, and the canonical claude-block
- `orchestration/templates/claude-block.md` — Canonical orchestration block (trigger + session-completion sections)
- `.crumbs/` — Issue tracker and session artifacts
