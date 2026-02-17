# Migration Guide: Adding Orchestration to Existing Projects

This guide shows how to add world-class orchestration to your existing projects.

## Quick Migration (5 minutes)

For projects that already use beads and Claude Code:

### Step 1: Add Orchestration Reference to Project CLAUDE.md

```bash
cd /path/to/your/project
```

Add this section to your project's `CLAUDE.md`:

```markdown
## Orchestration Workflows

This project uses standardized multi-agent orchestration patterns.

**Process documentation:** `~/.claude/orchestration/`
- **ORCHESTRATOR_DISCIPLINE.md** - Information diet, agent spawn patterns
- **QUALITY_REVIEW_TEMPLATES.md** - Standard 4-phase review process
- **DEPENDENCY_ANALYSIS_GUIDE.md** - Conflict detection and resolution

**Project-specific:**
- Session planning: `SESSION_PLAN_TEMPLATE.md` (in this repo)
- Quality gates: See "Quality Process" section below

### Recommended Kickoff

When starting multi-task sessions:

```
Let's get to work on these beads: <task-ids>

Follow ORCHESTRATOR_DISCIPLINE.md and DEPENDENCY_ANALYSIS_GUIDE.md
for pre-flight planning. Present strategy options before spawning.
```
```

### Step 2: Copy Session Template (Optional)

```bash
# If you don't have one yet:
curl -O https://raw.githubusercontent.com/c0rrey/hs_website/main/SESSION_PLAN_TEMPLATE.md

# Or copy from hs_website locally:
cp ~/projects/hs_website/SESSION_PLAN_TEMPLATE.md .
```

### Step 3: Define Quality Gates (Optional)

Add project-specific quality requirements to your CLAUDE.md:

```markdown
## Quality Process

### Pre-Push Quality Gates
- [ ] All tests passing: `pytest tests/` (or your test command)
- [ ] Linter clean: `ruff check` (or your linter)
- [ ] Type checking: `mypy src/` (if applicable)
- [ ] Build succeeds: `python build.py --dry-run` (if applicable)

### Review Process
Reviews use agent teams for parallel execution. See QUALITY_REVIEW_TEMPLATES.md.
Four specialized reviewers run concurrently, lead consolidates findings.
Minimum bar: No P1 bugs before push.
```

### Step 4: Test It

```bash
# Create a test session
bd create --title="Test orchestration workflow" --type=task --priority=2

# Start a session with the new kickoff statement
# Claude will follow the orchestration patterns automatically
```

---

## Full Migration (15 minutes)

For projects that need more customization:

### Step 1: Analyze Current Project

```bash
cd /path/to/your/project

# Check structure
ls -la

# Identify:
# - Build system (make, npm, cargo, etc.)
# - Test framework (pytest, jest, go test, etc.)
# - Linter (ruff, eslint, golangci-lint, etc.)
# - File structure (monorepo? microservices? single app?)
```

### Step 2: Create Custom SESSION_PLAN_TEMPLATE.md

Copy the reference template and customize:

```bash
cp ~/projects/hs_website/SESSION_PLAN_TEMPLATE.md .

# Edit to match your project:
# - File structure (replace build.py examples with your files)
# - Quality gates (replace pytest with your test command)
# - Agent types (python-pro, javascript-pro, etc.)
```

Example customizations:

**For Node.js projects:**
```markdown
### Quality Review Plan

After all Dirt Pushers complete:

1. **Clarity Review**
   - Files: src/**/*.ts, tests/**/*.spec.ts
   - ...

### Pre-Push Quality Gates

- [ ] `npm test` - All tests passing
- [ ] `npm run lint` - ESLint clean
- [ ] `npm run type-check` - TypeScript clean
- [ ] `npm run build` - Production build succeeds
```

**For Go projects:**
```markdown
### Quality Review Plan

After all Dirt Pushers complete:

1. **Clarity Review**
   - Files: **/*.go, **/*_test.go
   - ...

### Pre-Push Quality Gates

- [ ] `go test ./...` - All tests passing
- [ ] `golangci-lint run` - Linter clean
- [ ] `go build` - Build succeeds
- [ ] `go vet ./...` - No vet warnings
```

### Step 3: Create Project-Specific QUALITY_PROCESS.md

If you have unique requirements:

```markdown
# Quality Process for [Project Name]

## Overview

This project uses standard reviews from ~/.claude/orchestration/QUALITY_REVIEW_TEMPLATES.md
with these project-specific additions:

## Additional Quality Gates

### Security Review (After Excellence Review)
- [ ] No hardcoded secrets (check with `gitleaks`)
- [ ] Dependencies scanned: `npm audit` / `pip-audit` / `cargo audit`
- [ ] OWASP Top 10 concerns addressed

### Performance Review (For Critical Path Changes)
- [ ] Load testing: `k6 run load-test.js`
- [ ] Profiling: `py-spy` / Node.js profiler / pprof
- [ ] Benchmarks: Regression <5%

### Compliance Review (For Regulated Industries)
- [ ] HIPAA compliance checklist
- [ ] Audit logging verified
- [ ] Data retention policies followed

## Test Coverage Requirements

Minimum coverage by module:
- Core business logic: 90%
- API endpoints: 85%
- Utilities: 70%
- UI components: 60%

## Code Review Checklist

Beyond standard reviews, check:
- [ ] API versioning maintained
- [ ] Database migrations backward compatible
- [ ] Feature flags used for risky changes
- [ ] Rollback plan documented
```

### Step 4: Update Project CLAUDE.md

Add comprehensive orchestration section:

```markdown
## Orchestration Workflows

### Global Process Docs

This project follows standardized patterns from `~/.claude/orchestration/`:
- **ORCHESTRATOR_DISCIPLINE.md** - Context preservation, agent patterns
- **QUALITY_REVIEW_TEMPLATES.md** - 4-phase review process
- **DEPENDENCY_ANALYSIS_GUIDE.md** - Pre-flight conflict analysis

### Project-Specific Docs

- **SESSION_PLAN_TEMPLATE.md** - Customized for this project's structure
- **QUALITY_PROCESS.md** - Additional quality gates beyond standard reviews

### Recommended Kickoff

For multi-task sessions:

```
Let's get to work on these beads: <task-ids>

Project: [Your Project Name]
Structure: [monorepo/app/library/etc]

Follow orchestration docs for pre-flight planning:
- Analyze file conflicts (DEPENDENCY_ANALYSIS_GUIDE.md)
- Present execution strategies
- Wait for approval before spawning

Quality: See QUALITY_PROCESS.md for project-specific gates.
```
```

### Agent Type Mapping

| File Pattern | Recommended Agent |
|--------------|-------------------|
| **/*.py | python-pro |
| **/*.ts, **/*.js | typescript-pro / javascript-pro |
| **/*.go | general-purpose |
| **/*.rs | general-purpose |
| templates/** | refactoring-specialist |
| docs/** | technical-writer |
| tests/** | python-pro / typescript-pro |
| .github/workflows/** | devops-engineer |

### File Conflict Zones

High-risk files (often modified, batch carefully):
- `src/main.py` / `src/index.ts` - Entry points
- `package.json` / `requirements.txt` - Dependencies
- `config.yaml` / `.env.example` - Configuration
- `schema.sql` / `migrations/` - Database

Strategy: Group tasks touching these files to same agent or sequential execution.
```

### Step 5: Commit Changes

```bash
git add CLAUDE.md SESSION_PLAN_TEMPLATE.md QUALITY_PROCESS.md
git commit -m "docs: add orchestration workflow support

- Add references to global orchestration docs
- Customize session planning template for project
- Define project-specific quality gates

See ~/.claude/orchestration/ for global process documentation."

git push
```

---

## Migration Checklist

Use this checklist when adding orchestration to a new project:

### Minimum (5 min)
- [ ] Add orchestration reference section to project CLAUDE.md
- [ ] Test with sample kickoff statement
- [ ] Verify Claude follows pre-flight planning workflow

### Recommended (10 min)
- [ ] Copy SESSION_PLAN_TEMPLATE.md to project
- [ ] Customize template for project file structure
- [ ] Add quality gates section to CLAUDE.md
- [ ] Test with real multi-task session

### Complete (15 min)
- [ ] Create custom QUALITY_PROCESS.md
- [ ] Document agent type mapping for project
- [ ] Identify file conflict zones
- [ ] Add pre-push checklist
- [ ] Archive first session plan as example

### Advanced (Optional)
- [ ] Create project-specific agent spawn templates
- [ ] Document common task grouping patterns
- [ ] Set up automated quality gates (CI/CD)
- [ ] Create session metrics dashboard
- [ ] Build project-specific review checklists

---

## Troubleshooting

### Claude doesn't follow orchestration patterns

**Symptom:** Claude starts working immediately without pre-flight analysis

**Fix:** Be more explicit in kickoff:
```
Let's get to work on: <task-ids>

IMPORTANT: Before spawning any agents, follow these steps from
ORCHESTRATOR_DISCIPLINE.md and DEPENDENCY_ANALYSIS_GUIDE.md:

1. Gather all task metadata (bd show <id> for each)
2. Analyze file conflicts (create file modification matrix)
3. Present 2-3 execution strategies (Serial/Balanced/Parallel)
4. Wait for my approval
5. Then spawn agents per approved strategy

Do NOT spawn agents until I approve the strategy.
```

### Claude reads too many implementation files

**Symptom:** Context window fills up, token usage >60%

**Fix:** Remind about information diet:
```
Orchestration discipline: Only read task metadata in this window.
See ORCHESTRATOR_DISCIPLINE.md "What NOT to Read" section.
Delegate all implementation file reading to subagents.
```

### Reviews find too few issues

**Symptom:** Quality reviews report 0-2 issues for 20+ task sessions

**Fix:** Check review prompts are comprehensive:
```
Use exact prompts from QUALITY_REVIEW_TEMPLATES.md.
Each review should find 10-20 issues for 40+ task sessions.
If finding <5 issues, review may be too superficial.
```

### File conflicts keep occurring

**Symptom:** Agents report merge conflicts frequently

**Fix:** Improve pre-flight analysis:
```
Follow DEPENDENCY_ANALYSIS_GUIDE.md more carefully:
- Create explicit file modification matrix
- Choose Serial execution for 3+ tasks on same file
- Use dependency chaining for related files
- Ask me to approve strategy before spawning
```

---

## Examples by Project Type

### Python CLI Tool

```markdown
## Orchestration

Global docs: ~/.claude/orchestration/
Project: SESSION_PLAN_TEMPLATE.md

Quality gates:
- pytest --cov --cov-report=term-missing (>80% coverage)
- ruff check
- mypy --strict
- python -m build (package builds)

Common file conflicts:
- src/cli.py (entry point - batch tasks)
- pyproject.toml (deps - sequential execution)
```

### Next.js Web App

```markdown
## Orchestration

Global docs: ~/.claude/orchestration/
Project: SESSION_PLAN_TEMPLATE.md

Quality gates:
- npm test (Jest)
- npm run lint (ESLint + Prettier)
- npm run type-check (TypeScript)
- npm run build (production)
- Lighthouse CI >90

Common file conflicts:
- app/layout.tsx (root layout - batch)
- package.json (deps - sequential)
- next.config.js (config - sequential)
```

### Rust Library

```markdown
## Orchestration

Global docs: ~/.claude/orchestration/
Project: SESSION_PLAN_TEMPLATE.md

Quality gates:
- cargo test --all-features
- cargo clippy -- -D warnings
- cargo fmt --check
- cargo doc --no-deps

Common file conflicts:
- src/lib.rs (module root - batch)
- Cargo.toml (deps - sequential)
```

---

## Next Steps

After migration:

1. **Run a test session** with 3-5 tasks
2. **Fill out SESSION_PLAN_TEMPLATE.md** during session
3. **Archive completed plan** in `session-notes/YYYY-MM-DD-session.md`
4. **Iterate:** Update templates based on what worked/didn't
5. **Share learnings:** Update global docs if you discover better patterns

Happy orchestrating! 🎯
