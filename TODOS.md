# TODO

## Explore tmux-based agent spawning for real-time observability

Explore running orchestrated subagents in tmux windows instead of background Task agents, so you can observe agent work in real-time. The current limitation is that shift+up in Claude Code only shows abbreviated subagent output.

**Key research questions:**
1. Can the boss-bot launch claude CLI sessions in tmux windows via Bash?
2. How to pipe prompts into those sessions?
3. How to collect results back?
4. Hook-based automation options?

**Goal:** Each spawned agent gets its own tmux window you can switch to with ctrl+b n/p. May influence orchestration templates if feasible.

## Come up with a better name for the Pantry's "data files"

The Pantry template references "data files" — find a more descriptive/thematic name that fits the ant-farm metaphor.

