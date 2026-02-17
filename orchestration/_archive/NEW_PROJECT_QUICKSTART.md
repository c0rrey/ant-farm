# New Project Orchestration Setup

## 5-Minute Setup

```bash
cd /path/to/new-project

# 1. Copy session template
curl -O https://raw.githubusercontent.com/c0rrey/hs_website/main/SESSION_PLAN_TEMPLATE.md
# OR: cp ~/projects/hs_website/SESSION_PLAN_TEMPLATE.md .

# 2. Add to project CLAUDE.md
cat >> CLAUDE.md << 'EOF'

## Orchestration

Global workflows: `~/.claude/orchestration/`
- ORCHESTRATOR_DISCIPLINE.md (agent patterns)
- QUALITY_REVIEW_TEMPLATES.md (reviews)
- DEPENDENCY_ANALYSIS_GUIDE.md (conflicts)

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
EOF

# 3. Customize SESSION_PLAN_TEMPLATE.md
# - Replace "build.py" examples with your main files
# - Update "pytest" references to your test framework
# - Update agent types (python-pro, typescript-pro, etc.)

# 4. Done! Start a session:
# "Let's get to work on: <task-ids>"
```

## What to Customize

### In SESSION_PLAN_TEMPLATE.md

**Line 13-20:** Task metadata table
- Change example file names to your project's files

**Line 30-35:** Common file conflicts
- List your frequently-modified files (entry points, config, deps)

**Line 95-110:** Quality gates
- Replace `pytest` → your test command
- Replace `ruff` → your linter
- Add your build command

**Line 200:** Agent type mapping
- Map your file extensions to agent types

### In project CLAUDE.md

**Quality Gates section:**
```markdown
### Quality Gates
- [ ] npm test (or pytest, go test, cargo test)
- [ ] npm run lint (or ruff, eslint, clippy)
- [ ] npm run build (or python build.py, cargo build)
```

## File Checklist

**Required:**
- [x] Project CLAUDE.md has orchestration section
- [x] Kickoff statement added to CLAUDE.md

**Recommended:**
- [ ] SESSION_PLAN_TEMPLATE.md copied and customized
- [ ] Quality gates defined in CLAUDE.md

**Optional:**
- [ ] QUALITY_PROCESS.md for project-specific requirements

## Project Types

### Python
```markdown
Quality Gates:
- [ ] pytest --cov (>80%)
- [ ] ruff check
- [ ] mypy --strict

Agent types: python-pro
```

### Node.js/TypeScript
```markdown
Quality Gates:
- [ ] npm test
- [ ] npm run lint
- [ ] npm run type-check
- [ ] npm run build

Agent types: typescript-pro, javascript-pro
```

### Go
```markdown
Quality Gates:
- [ ] go test ./...
- [ ] golangci-lint run
- [ ] go build

Agent types: general-purpose
```

### Rust
```markdown
Quality Gates:
- [ ] cargo test
- [ ] cargo clippy
- [ ] cargo fmt --check

Agent types: general-purpose
```

## Common Files to Watch

Always identify these in SESSION_PLAN_TEMPLATE.md:

**High conflict risk (batch to same agent):**
- Entry points: `main.py`, `index.ts`, `main.go`, `main.rs`
- Dependencies: `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`
- Config: `config.yaml`, `.env.example`, `settings.py`
- Migrations: `schema.sql`, `migrations/*.sql`

**Medium risk (can parallelize carefully):**
- Utilities: `utils.py`, `helpers.ts`
- Models: `models.py`, `types.ts`
- Routes: `routes.py`, `api/*.ts`

**Low risk (safe to parallelize):**
- Tests: `test_*.py`, `*.spec.ts`
- Docs: `*.md`
- Independent modules

## Test Your Setup

```bash
# Create a test task
bd create --title="Test orchestration" --type=task --priority=3

# Start session
# Say: "Let's get to work on: <that-task-id>"

# Verify Claude:
# 1. Runs bd show
# 2. Analyzes conflicts (even for 1 task)
# 3. Presents strategy
# 4. Waits for approval
# 5. Spawns agent
```

## Troubleshooting

**Claude doesn't do pre-flight analysis:**
```
Add to kickoff: "Follow orchestration docs for pre-flight planning."
```

**Claude reads too many files:**
```
Remind: "Orchestrator discipline - only read task metadata."
```

**Need project-specific reviews:**
```
Create QUALITY_PROCESS.md with additional requirements.
```
