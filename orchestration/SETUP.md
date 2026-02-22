# Orchestration Setup

## Prerequisites

The orchestration system uses custom Claude Code agent types defined in `agents/`. These are synced to `~/.claude/agents/` automatically on `git push` via the pre-push hook.

**First-time setup:** See the Quick Setup and Full Setup sections below for installation, sync behavior, backup, and uninstall documentation.

Quick reference:
```bash
./scripts/install-hooks.sh          # Install the hook
./scripts/sync-to-claude.sh         # Initial sync to ~/.claude/
# Then restart Claude Code
```

For details on what gets synced, how to back up `~/.claude/`, and how to uninstall, see the Full Setup section below.

## Quick Setup (5 minutes)

**Step 1: Install the hook and sync**

For complete details, see `docs/installation-guide.md`. Quick reference:

```bash
./scripts/install-hooks.sh          # Install pre-push hook
./scripts/sync-to-claude.sh         # Sync to ~/.claude/
# Then restart Claude Code
```

**Step 2: Add orchestration reference to project CLAUDE.md**

```bash
cd /path/to/your/project
```

Add this section:

````markdown
## Orchestration

Global workflows: `~/.claude/orchestration/` (RULES.md, templates/, reference/)
Project: SESSION_PLAN_TEMPLATE.md

### Kickoff Statement

```
Let's get to work on: <task-ids>
Follow orchestration docs for pre-flight planning.
```

### Quality Gates
- [ ] Tests pass: [your test command]
- [ ] Linter clean: [your lint command]
- [ ] Build succeeds: [your build command]
````

**Step 3: Copy session template (optional)**

```bash
# Copy from reference project:
cp orchestration/templates/SESSION_PLAN_TEMPLATE.md .

# Customize:
# - Line 30-35: List your high-conflict files
# - Line 95-110: Update quality gate commands
# - Line 200: Map file types to agent types
```

**Step 4: Test it**

```bash
bd create --title="Test orchestration" --type=task --priority=3

# Start session:
# "Let's get to work on: <task-id>"

# Verify Claude (the Queen):
# 1. Delegates to the Scout subagent (Scout runs bd show — Queen does NOT run bd show directly)
# 2. Analyzes conflicts
# 3. Presents strategy
# 4. Waits for approval
# 5. Spawns agent
```

## Recipe Card

Copy-paste this into new project CLAUDE.md:

```markdown
## Orchestration

Global: `~/.claude/orchestration/` (RULES.md, templates/, reference/)
Project: SESSION_PLAN_TEMPLATE.md

Kickoff: "Let's get to work on: <task-ids>. Follow orchestration docs for pre-flight planning."

Quality Gates:
- [ ] [test command]
- [ ] [lint command]
- [ ] [build command]
```

## Language-Specific Quality Gates

| Language | Commands | Agent Type |
|----------|----------|------------|
| Python | `pytest --cov`, `ruff check`, `mypy --strict` | python-pro |
| Node/TS | `npm test`, `npm run lint`, `npm run build` | typescript-pro |
| Go | `go test ./...`, `golangci-lint run`, `go build` | general-purpose |
| Rust | `cargo test`, `cargo clippy`, `cargo fmt --check` | general-purpose |

## Full Setup (15 minutes)

For projects needing customization:

**Step 1: Create custom SESSION_PLAN_TEMPLATE.md**

Copy reference template and customize for your project:

```bash
cp orchestration/templates/SESSION_PLAN_TEMPLATE.md .
```

Edit to match your project:
- File structure (replace build.py examples with your files)
- Quality gates (replace pytest with your test command)
- Agent types (python-pro, typescript-pro, general-purpose)

**Step 2: Create project-specific QUALITY_PROCESS.md (if needed)**

For unique requirements beyond standard reviews:

```markdown
# Quality Process for [Project Name]

## Overview

Uses standard session-scoped reviews from orchestration/templates/reviews.md
(reviews run once per session across all epics) with these additions:

## Additional Quality Gates

### Security Review
- [ ] No hardcoded secrets (gitleaks)
- [ ] Dependencies scanned: npm audit / pip-audit / cargo audit
- [ ] OWASP Top 10 addressed

### Performance Review (Critical Path)
- [ ] Load testing: k6 run load-test.js
- [ ] Profiling complete
- [ ] Benchmarks: <5% regression

## Test Coverage Requirements

- Core business logic: 90%
- API endpoints: 85%
- Utilities: 70%
- UI components: 60%
```

**Step 3: Document agent type mapping**

Add to project CLAUDE.md:

```markdown
### Agent Type Mapping

| File Pattern | Agent |
|--------------|-------|
| **/*.py | python-pro |
| **/*.ts, **/*.js | typescript-pro |
| **/*.go | general-purpose |
| **/*.rs | general-purpose |
| templates/** | refactoring-specialist |
| docs/** | technical-writer |
| .github/workflows/** | devops-engineer |
```

**Step 4: Identify file conflict zones**

Add to project CLAUDE.md or SESSION_PLAN_TEMPLATE.md:

```markdown
### High-Risk Files (Batch Carefully)

- Entry points: main.py, index.ts (frequently modified)
- Dependencies: package.json, requirements.txt (sequential execution)
- Config: config.yaml, .env.example (sequential)
- Schema: migrations/, schema.sql (sequential)

Strategy: Group tasks touching these files to same agent or sequential execution.
```

**Step 5: Commit**

```bash
git add CLAUDE.md SESSION_PLAN_TEMPLATE.md QUALITY_PROCESS.md
git commit -m "docs: add orchestration workflow support"
git push
```

## Troubleshooting

**Problem: Claude starts working without pre-flight analysis**

Fix: Be explicit in kickoff:
```
Let's get to work on: <task-ids>

IMPORTANT: Before spawning any agents:
1. Spawn the Scout subagent to gather all task metadata (do NOT run bd show directly as Queen)
2. Analyze file conflicts (create file modification matrix)
3. Present 2-3 execution strategies (Serial/Balanced/Parallel)
4. Wait for my approval
5. Then spawn agents per approved strategy

Do NOT spawn agents until I approve the strategy.
```

**Problem: Claude reads too many implementation files**

Fix: Remind about information diet:
```
Orchestration discipline: Only read task metadata in this window.
See RULES.md Information Diet section.
Delegate all implementation file reading to subagents.
```

**Problem: File conflicts keep occurring**

Fix: Improve pre-flight analysis:
```
Follow reference/dependency-analysis.md more carefully:
- Create explicit file modification matrix
- Choose Serial execution for 3+ tasks on same file
- Use dependency chaining for related files
- Ask me to approve strategy before spawning
```

**Problem: Reviews find too few issues**

Fix: Check review comprehensiveness:
```
Use exact prompts from templates/reviews.md.
Reviews are session-scoped (run once per session, covering all epics).
Each review type should find 3-10 root-cause issues for a typical session.
If finding <3 issues, review may be too superficial.
```

## Common High-Conflict Files

Always identify these in your conflict analysis:

**High risk (batch to same agent):**
- Entry: main.py, index.ts, main.go, main.rs
- Deps: package.json, requirements.txt, go.mod, Cargo.toml
- Config: config.yaml, .env.example, settings.py
- Schema: migrations/*.sql, schema.sql

**Medium risk (parallelize carefully):**
- Utilities: utils.py, helpers.ts
- Models: models.py, types.ts
- Routes: routes.py, api/*.ts

**Low risk (safe to parallelize):**
- Tests: test_*.py, *.spec.ts
- Docs: *.md
- Independent modules
