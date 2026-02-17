# Orchestration Setup Recipe Card

## Copy This to New Project CLAUDE.md

```markdown
## Orchestration

Global: `~/.claude/orchestration/` (ORCHESTRATOR_DISCIPLINE.md, QUALITY_REVIEW_TEMPLATES.md, DEPENDENCY_ANALYSIS_GUIDE.md)
Project: SESSION_PLAN_TEMPLATE.md

Kickoff: "Let's get to work on: <task-ids>. Follow orchestration docs for pre-flight planning."

Quality Gates:
- [ ] [test command]
- [ ] [lint command]
- [ ] [build command]
```

## Commands

```bash
# 1. Copy template
cp ~/projects/hs_website/SESSION_PLAN_TEMPLATE.md .

# 2. Edit SESSION_PLAN_TEMPLATE.md
# - Line 30-35: List your high-conflict files
# - Line 95-110: Update quality gate commands
# - Line 200: Map file types to agent types

# 3. Edit project CLAUDE.md
# - Add orchestration section above
# - Update quality gate commands

# 4. Test
# "Let's get to work on: <task-id>"
```

## What to Customize

| File | What | Example |
|------|------|---------|
| SESSION_PLAN_TEMPLATE.md | Conflict files | `build.py` → `main.go` |
| SESSION_PLAN_TEMPLATE.md | Quality gates | `pytest` → `go test` |
| SESSION_PLAN_TEMPLATE.md | Agent types | `python-pro` → `general-purpose` |
| project CLAUDE.md | Test command | `pytest` → `npm test` |
| project CLAUDE.md | Lint command | `ruff` → `eslint` |

## By Language

**Python:** `pytest --cov`, `ruff check`, `mypy --strict` → `python-pro`
**Node/TS:** `npm test`, `npm run lint`, `npm run build` → `typescript-pro`
**Go:** `go test ./...`, `golangci-lint run`, `go build` → `general-purpose`
**Rust:** `cargo test`, `cargo clippy`, `cargo build` → `general-purpose`

## High-Conflict Files (Batch These)

- Entry: `main.py`, `index.ts`, `main.go`
- Deps: `package.json`, `requirements.txt`, `Cargo.toml`
- Config: `config.yaml`, `.env.example`
- Schema: `migrations/`, `schema.sql`
