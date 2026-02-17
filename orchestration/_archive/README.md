# Claude Code Orchestration Toolkit

**Global workflow documentation for multi-agent orchestration across all projects.**

## Purpose

This directory contains reusable orchestration patterns that work across any project using beads task management and Claude Code. These workflows ensure consistent operational excellence regardless of project size or tech stack.

## Documents in This Directory

### Core Process Guides (Read-Only Reference)

1. **ORCHESTRATOR_DISCIPLINE.md** - Information diet and context preservation
   - What to read vs delegate in orchestrator window
   - Agent spawn patterns (file-based, dependency-aware, priority-tier)
   - Monitoring protocols
   - Session closure checklist
   - Success metrics

2. **QUALITY_REVIEW_TEMPLATES.md** - Agent teams review protocol
   - Clarity Review (P3 bugs)
   - Edge Cases Review (P2 bugs)
   - Correctness Redux Review (P1 bugs)
   - Excellence Review (P3 features)
   - Parallel execution via agent teams with lead consolidation
   - Review quality calibration

3. **DEPENDENCY_ANALYSIS_GUIDE.md** - Conflict detection and resolution
   - Pre-flight analysis checklist
   - File conflict matrix creation
   - 4 conflict resolution strategies (Serial, Parallel+Rebase, Dependency Chain, Independent)
   - Decision matrix and risk assessment
   - Real-world examples

## How to Use

### Initial Setup (One Time)

1. **Update global CLAUDE.md** to reference these docs:
   ```bash
   code ~/.claude/CLAUDE.md
   ```

   Add to "Let's get to work" section:
   ```markdown
   **Process Documentation:** See ~/.claude/orchestration/ for:
   - ORCHESTRATOR_DISCIPLINE.md (information diet, patterns)
   - QUALITY_REVIEW_TEMPLATES.md (standard reviews)
   - DEPENDENCY_ANALYSIS_GUIDE.md (conflict resolution)
   ```

2. **Add kickoff statement template** to global CLAUDE.md:
   ```markdown
   ## Recommended Kickoff Statement

   For multi-agent orchestration sessions:

   ```
   Let's get to work on these beads: <task-ids>

   Follow ~/.claude/orchestration/ORCHESTRATOR_DISCIPLINE.md and
   DEPENDENCY_ANALYSIS_GUIDE.md for pre-flight planning.
   Present strategy options before spawning agents.
   ```
   ```

### Per-Project Setup

Each project should have:

1. **SESSION_PLAN_TEMPLATE.md** (copy from hs_website or create custom)
   - This gets filled out per-session
   - Customize for project structure
   - Archive completed plans in `session-notes/`

2. **QUALITY_PROCESS.md** (optional, project-specific)
   - Override standard review patterns if needed
   - Add project-specific quality gates
   - Define test requirements

3. **Reference in project CLAUDE.md**:
   ```markdown
   ## Orchestration

   This project uses standard orchestration workflows from ~/.claude/orchestration/

   - Pre-flight planning: DEPENDENCY_ANALYSIS_GUIDE.md
   - Information diet: ORCHESTRATOR_DISCIPLINE.md
   - Quality reviews: QUALITY_REVIEW_TEMPLATES.md
   - Session planning: SESSION_PLAN_TEMPLATE.md (in this repo)
   ```

## When to Update These Docs

**Global docs (~/.claude/orchestration/):**
- ✅ Update when you discover better patterns that work across projects
- ✅ Update when Claude Code adds new features (new agent types, tools)
- ✅ Update after major version changes (Python 3.12+, new best practices)
- ❌ Don't add project-specific details here

**Project docs:**
- ✅ Customize SESSION_PLAN_TEMPLATE.md for project structure
- ✅ Create project-specific QUALITY_PROCESS.md for unique requirements
- ✅ Document project conventions in project CLAUDE.md
- ❌ Don't duplicate global process docs

## Benefits of This Approach

✅ **Single source of truth** - Update once, all projects benefit
✅ **Consistency** - Same high-quality patterns everywhere
✅ **Discoverability** - New projects instantly get best practices
✅ **Maintainability** - No drift between project copies
✅ **Flexibility** - Projects can override/extend as needed
✅ **Learning** - Improvements from one project benefit all

## Version Control

**Global docs (this directory):**
- Not in git (personal workflow, evolves with your usage)
- Consider backing up to Dropbox/iCloud: `ln -s ~/.claude ~/Dropbox/claude-backup`
- Or create git repo: `cd ~/.claude && git init`

**Project docs:**
- SESSION_PLAN_TEMPLATE.md should be in project git
- Filled-in session plans archived in `session-notes/` (optional, .gitignore if desired)

## Quick Reference

**Starting a new project:**
```bash
# 1. Create project directory
mkdir my-new-project && cd my-new-project

# 2. Initialize beads
bd init --prefix myproj

# 3. Copy session template
cp /path/to/reference-project/SESSION_PLAN_TEMPLATE.md .

# 4. Create project CLAUDE.md with orchestration reference:
cat > CLAUDE.md << 'EOF'
# Project Name

## Orchestration

This project uses standard orchestration workflows from ~/.claude/orchestration/

See global docs for:
- ORCHESTRATOR_DISCIPLINE.md (information diet, agent patterns)
- QUALITY_REVIEW_TEMPLATES.md (standard quality reviews)
- DEPENDENCY_ANALYSIS_GUIDE.md (conflict detection & resolution)
- SESSION_PLAN_TEMPLATE.md (planning template, in this repo)

## Project-Specific Notes
[Add your project details here]
EOF

# 5. Ready to work!
```

**Starting a work session:**
```bash
# Use this kickoff statement:
# "Let's get to work on these beads: <task-ids>
#  Follow orchestration docs for pre-flight planning."
```

## Customization Examples

### For Python Projects
Add to project CLAUDE.md:
```markdown
## Quality Gates
- pytest --cov (require 80% coverage)
- mypy --strict (no type errors)
- ruff check (no linting errors)
- See QUALITY_REVIEW_TEMPLATES.md for review process
```

### For Web Projects
Add to project CLAUDE.md:
```markdown
## Quality Gates
- npm test (all tests pass)
- npm run lint (ESLint clean)
- npm run build (production build succeeds)
- Lighthouse score >90 (performance, accessibility)
- See QUALITY_REVIEW_TEMPLATES.md for review process
```

### For Multi-Language Monorepos
Create custom QUALITY_PROCESS.md:
```markdown
# Monorepo Quality Process

## Language-Specific Reviews

- Python: Follow QUALITY_REVIEW_TEMPLATES.md + pytest
- JavaScript: Follow QUALITY_REVIEW_TEMPLATES.md + Jest + ESLint
- Go: Follow QUALITY_REVIEW_TEMPLATES.md + go test + golangci-lint

## Cross-Language Concerns
- API contracts validated
- Shared types synced
- Integration tests passing
```

## Migration Guide

See MIGRATION_GUIDE.md for step-by-step instructions to migrate existing projects.
