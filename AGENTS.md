# Agent Instructions

This project uses two CLI tools for task management:

- **crumb** (`crumb.py`) — the primary JSONL task tracker for all issue operations (list, show, update, close, link, trail). Run `crumb doctor` to get started.

Use `crumb` for all task management — individual operations, orchestration workflows, and decomposition. When in doubt, use `crumb`.

## Quick Reference

```bash
crumb ready              # Find available work
crumb show <id>          # View issue details
crumb update <id> --status in_progress  # Claim work
crumb close <id>         # Complete work
```

## Landing the Plane (Session Completion)

See the **Landing the Plane** section in `orchestration/templates/claude-block.md` for the full mandatory workflow.
That file is the single source of truth for session-completion steps — it is installed into
each project's prompt-dir CLAUDE.md by `setup.sh` and `/ant-farm:init`.

