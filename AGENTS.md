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

See the **Landing the Plane** section in `CLAUDE.md` for the full mandatory workflow.
`CLAUDE.md` is the single source of truth for session-completion steps. Do not duplicate
that content here — edit `CLAUDE.md` if the procedure needs to change.

