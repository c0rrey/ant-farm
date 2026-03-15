# ant-farm

A bounded multi-agent orchestration framework for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). It separates **planning** from **execution**, drives implementation through specialized subagents, and uses mechanical verification gates to keep agent work auditable, recoverable, and hard to fake.

ant-farm is not an open-ended autonomous coding agent. It is a constrained orchestration layer that sits on top of Claude Code, enforcing a governed software-delivery workflow with checkpoints at every phase transition.

## How It Works

ant-farm defines two workflows:

- **Planning** (`/ant-farm:plan`) — turns a freeform request or structured spec into dependency-aware tasks (trails and crumbs) via requirements gathering, parallel research, and decomposition.
- **Execution** (`/ant-farm:work` or "let's get to work") — runs an implementation session: recon, prompt composition, parallel agent spawning, post-commit verification, code review, and documentation.

The key idea is **constrained delegation**: work is split across specialist agents, but progression is controlled by artifacts on disk, verification checkpoints, retry limits, and explicit escalation to the user when things go wrong.

```
Planning Workflow                    Execution Workflow

  Surveyor                             Scout (recon)
     |                                    |
  Foragers (4x parallel research)      SSV gate
     |                                    |
  Architect (decomposition)            Pantry (prompt composition)
     |                                    |
  .crumbs/tasks.jsonl  ──────────►     CCO gate (prompt audit)
                                          |
                                       Dirt Pushers (implementation, up to 7 parallel)
                                          |
                                       WWD + DMVDC gates (scope + substance verification)
                                          |
                                       Nitpickers (4x parallel review) + Big Head (consolidation)
                                          |
                                       CCB gate (consolidation audit)
                                          |
                                       Scribe (exec summary + CHANGELOG)
                                          |
                                       ESV gate → git push
```

## Architecture

The system has four layers:

1. **Task and artifact layer** — `crumb.py` stores tasks and trails in `.crumbs/tasks.jsonl`. Sessions write durable artifacts (metadata, prompts, summaries, review reports, checkpoint audits) under `.crumbs/sessions/`.

2. **Two orchestrators** — the **Planner** handles decomposition (Surveyor, Foragers, Architect); the **Queen** handles execution (Scout, Pantry, Dirt Pushers, Nitpickers, Big Head, Scribe). They have different permissions, state models, and agent teams.

3. **Specialist agents** — Claude Code agent definitions in `agents/` cover recon, prompt composition, implementation, review, consolidation, verification, and documentation.

4. **Verification layer** — **Pest Control** runs six checkpoint types (SSV, CCO, WWD, DMVDC, CCB, ESV) that mechanically block progression. It operates both as a standalone checkpoint runner spawned by the Queen and as a member of the Nitpicker review team.

### Information Diet

The Queen **never reads source code, tests, configs, or implementation templates**. It reads only the Scout's briefing, agent notifications, commit messages, and verdict tables. Every other agent absorbs its own context cost so the Queen's window stays clean.

Target: finish a 40+ task session with >75% context window remaining (1M window).

### Hard Gates

| Gate | Full Name | What it blocks | Model |
|------|-----------|---------------|-------|
| **SSV** | Scout Strategy Verification | Pantry spawn | haiku |
| **CCO** | Colony Cartography Office | Agent spawn | haiku |
| **WWD** | Wandering Worker Detection | Next agent in wave | haiku |
| **DMVDC** | Dirt Moved vs Dirt Claimed | Task closure | sonnet |
| **CCB** | Colony Census Bureau | Presenting results to user | haiku |
| **ESV** | Exec Summary Verification | Git push (Step 6) | haiku |

All checkpoint artifacts are written to `<session-dir>/pc/` with timestamped filenames for full audit history.

## Getting Started

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- Git repository initialized in your project
- Bash shell
- Read/write permissions to `~/.claude/` and `~/.local/bin/`

### Installation

```bash
git clone <repo-url> && cd ant-farm
./scripts/setup.sh           # installs agents, orchestration, skills, crumb CLI
```

The setup script installs:
- Agent definitions (`agents/*.md`) to `~/.claude/agents/`
- Orchestration files to `~/.claude/orchestration/`
- Skills to `~/.claude/plugins/ant-farm/commands/`
- `crumb.py` to `~/.local/bin/crumb`

Then **restart Claude Code** — agent types are loaded at startup only.

For detailed installation, backup, and uninstall instructions, see `docs/installation-guide.md`.

### Wire Up a Target Project

Run `/ant-farm:init` inside the target project to install orchestration triggers into the project's prompt-dir `CLAUDE.md`. This creates a per-project installation scoped to that project's Claude Code prompt directory.

After running `/ant-farm:init`, the project's `CLAUDE.md` will contain an orchestration section (see `orchestration/SETUP.md` for the full recipe and manual setup option):

```markdown
## Orchestration
Global: `~/.claude/orchestration/` (RULES.md, templates/, reference/)
Kickoff: "Let's get to work on: <task-ids>."
Quality Gates:
- [ ] Tests pass
- [ ] Linter clean
- [ ] Build succeeds
```

### Run Your First Session

```bash
crumb create --title="My first task" --type=task --priority=3
```

Then tell Claude Code:

```
Let's get to work on: ant-farm-XXXX
```

The Queen will spawn the Scout for recon, verify the strategy via SSV, and auto-proceed to spawn implementation agents.

## Project Structure

```
ant-farm/
├── agents/                  # Custom Claude Code agent definitions (.md files)
│   ├── ant-farm-scout-organizer.md
│   ├── ant-farm-pantry-impl.md
│   ├── ant-farm-pest-control.md
│   ├── ant-farm-nitpicker.md
│   ├── ant-farm-big-head.md
│   ├── ant-farm-architect.md
│   ├── ant-farm-forager.md
│   ├── ant-farm-surveyor.md
│   └── ant-farm-technical-writer.md
├── orchestration/
│   ├── RULES.md             # Queen's execution workflow steps and gates
│   ├── RULES-decompose.md   # Planner's decomposition workflow
│   ├── RULES-review.md      # Review-phase-specific rules
│   ├── SETUP.md             # How to wire orchestration into a new project
│   ├── GLOSSARY.md          # Term definitions used across docs
│   ├── PLACEHOLDER_CONVENTIONS.md
│   ├── templates/           # Agent prompt templates and skeletons
│   │   ├── scout.md, pantry.md, implementation.md, reviews.md
│   │   ├── checkpoints.md   # All checkpoint definitions (CCO, WWD, DMVDC, CCB, ESV)
│   │   ├── dirt-pusher-skeleton.md, nitpicker-skeleton.md, big-head-skeleton.md
│   │   ├── scribe-skeleton.md
│   │   ├── surveyor.md, surveyor-skeleton.md
│   │   ├── forager.md, forager-skeleton.md
│   │   ├── decomposition.md, architect-skeleton.md
│   │   └── review-focus-areas.md, queen-state.md, SESSION_PLAN_TEMPLATE.md
│   └── reference/
│       ├── dependency-analysis.md   # Pre-flight conflict analysis
│       └── known-failures.md        # Past failures and fixes applied
├── scripts/
│   ├── setup.sh                     # Installs everything to ~/.claude/ and PATH
│   ├── build-review-prompts.sh      # Builds review prompts from templates
│   └── parse-progress-log.sh        # Session recovery from progress log
├── skills/                  # Slash commands (/ant-farm:work, /ant-farm:plan, etc.)
├── crumb.py                 # Task-tracking CLI (installed to ~/.local/bin/crumb)
├── tests/                   # Tests for crumb.py
├── CONTRIBUTING.md          # How to add agents, checkpoints, and templates
├── CHANGELOG.md             # Session-by-session development history
└── .crumbs/                 # Task database and session artifacts
    ├── tasks.jsonl           # Task/trail database (this project's issue tracker)
    └── sessions/             # Per-session artifact directories
```

## Execution Workflow Detail

Triggered by saying **"let's get to work"** in any project wired up per `orchestration/SETUP.md`.

### Step 0: Session Setup

Generate a session ID, create the session directory, and initialize the artifact layout. Session artifacts include:

- `task-metadata/`, `previews/`, `prompts/`, `summaries/`, `review-reports/`, `pc/`
- `briefing.md`, `queen-state.md`, `progress.log`, `exec-summary.md`, `resume-plan.md`

If a prior session directory is supplied, the Queen can recover from `progress.log` via `scripts/parse-progress-log.sh`.

### Step 1: Recon

The Queen spawns **the Scout** (`orchestration/templates/scout.md`), an opus subagent that:

1. Discovers tasks (from epic, explicit list, or natural-language filter)
2. Runs `crumb ready` and `crumb blocked` to separate ready vs. blocked tasks
3. Runs `crumb show` per task and writes per-task metadata to `{session-dir}/task-metadata/`
4. Builds a file modification matrix and assesses conflict risk
5. Scans `~/.claude/agents/` to discover available agent types and recommends the best specialist per task
6. Proposes 2-3 execution strategies with wave groupings and risk assessments
7. Writes `{session-dir}/briefing.md`

After SSV PASS, the Queen auto-proceeds to Step 2. Strategy approval is mechanical, not conversational.

### Step 2: Spawn Implementation Agents

The Queen delegates prompt composition to **the Pantry**, which reads templates, extracts per-task context, and writes combined prompt previews to disk. **Pest Control** then audits the previews against the CCO checkpoint. Only agents with PASS verdicts are spawned.

```
Queen                          Pantry                    Pest Control
  │                              │                           │
  ├──spawn────────────────────►  │                           │
  │  "compose Wave N prompts"    │                           │
  │                              ├─read templates            │
  │                              ├─write task briefs + previews
  │  ◄──return paths + done──────┤                           │
  │                              │(agent dies, context freed)│
  │                                                          │
  ├──spawn─────────────────────────────────────────────────► │
  │  "audit previews against CCO"                            │
  │                                                          ├─read checkpoints.md
  │                                                          ├─audit each preview
  │  ◄──return verdict table─────────────────────────────────┤
  │                                                          │
  ├──spawn Dirt Pushers (up to 7 parallel)──►                │
```

Each Dirt Pusher executes 6 mandatory steps:

1. **Claim** — `crumb show` + `crumb update --status=in_progress`
2. **Design** — 4+ genuinely distinct approaches with tradeoffs
3. **Implement** — clean, minimal code satisfying acceptance criteria
4. **Correctness review** — re-read every changed file, verify acceptance criteria
5. **Commit** — `git pull --rebase` then commit with task ID in message
6. **Summary doc** — structured artifact with approaches, rationale, and review evidence

Agents are constrained by **scope boundaries**: they may only edit the files and line ranges listed in their task brief.

### Step 3: Monitor and Verify

After each wave, Pest Control runs:

- **WWD** (scope verification) — files changed in the commit match expected scope
- **DMVDC** (substance verification) — git diff matches summary claims, acceptance criteria are genuinely met, design approaches are substantively distinct

Failed DMVDC → agent is resumed with specific gaps → re-verified → escalated to user after 2 retries.

### Step 3b: Quality Review

After all implementation and DMVDC checks pass, the Queen enters a mandatory review phase.

The Queen creates a **Nitpicker team** (4 parallel reviewers + Big Head + Pest Control):

| Review | Severity Focus |
|--------|---------------|
| **Clarity** | P3 — readability, naming, documentation |
| **Edge Cases** | P2 — input validation, error handling, boundary conditions |
| **Correctness** | P1-P2 — acceptance criteria, logic errors, regressions |
| **Drift** | P3 — stale cross-file references, broken assumptions |

**Big Head** reads all 4 reports, merges duplicates by root cause, and files one issue per root cause. **Pest Control** runs DMVDC + CCB inside the team before results return to the Queen.

If P1/P2 issues are found, the system enters a review/fix/re-review loop until convergence, deferral, or the round cap.

### Steps 4-6: Document and Land

- **Step 4**: Update README/CLAUDE.md if needed
- **Step 5b**: Scribe writes exec summary and CHANGELOG entry
- **Step 5c**: ESV checkpoint verifies exec summary integrity
- **Step 6**: `git pull --rebase && git push` — work is not complete until push succeeds

## Custom Agents

Agent definitions live in `agents/` and are installed to `~/.claude/agents/` by `scripts/setup.sh`. Changes require restarting Claude Code.

| Agent | Purpose |
|-------|---------|
| `ant-farm-scout-organizer` | Pre-flight recon: task discovery, dependency analysis, execution strategy |
| `ant-farm-pantry-impl` | Implementation prompt composer: builds task briefs and combined previews |
| `ant-farm-pest-control` | Verification auditor: runs all six checkpoints (SSV, CCO, WWD, DMVDC, CCB, ESV) |
| `ant-farm-nitpicker` | Code reviewer: finds issues with file:line specificity and calibrated severity |
| `ant-farm-big-head` | Consolidation reviewer: merges and deduplicates findings across Nitpickers |
| `ant-farm-architect` | Spec decomposition: creates trails, crumbs, and dependencies from specs |
| `ant-farm-forager` | Parallel research: investigates a single focus area against a feature spec |
| `ant-farm-surveyor` | Requirements gathering: writes structured specs with acceptance criteria |
| `ant-farm-technical-writer` | Session Scribe: writes exec summaries and CHANGELOG entries |

## Priority Calibration

| Level | Meaning | Examples |
|-------|---------|---------|
| **P1** | Blocking | Build failure, broken links, data loss, security vulnerability |
| **P2** | Important | Visual regression, accessibility issue, functional degradation |
| **P3** | Polish | Style, naming, cleanup, code quality improvements |

## Retry Limits

| Situation | Max retries | After limit |
|-----------|-------------|-------------|
| Agent fails DMVDC | 2 | Escalate to user |
| CCB fails | 1 | Present to user with verification report |
| Agent stuck (no commit in 15 turns) | 0 | Check status, escalate |
| Total retries per session | 5 | Pause all spawns, triage with user |

## Known Failure Modes

Documented in `orchestration/reference/known-failures.md`. Key incidents that shaped the system:

**Skipped design and review steps** (Epic 3) — Agents bypassed mandatory design and correctness review steps. Fix: DMVDC now verifies substance, not just completion claims.

**Work scrambling** (Epic 74g) — Three agents on the same file without line-level boundaries, each "helpfully" fixing adjacent issues. Fixes: WWD for scope verification, enhanced CCO requiring line-number specificity, anti-scope-creep template language, and pre-flight conflict risk assessment.

## Forking This Repo

The `.crumbs/tasks.jsonl` file is the issue database for **this** project's development history. If you adopt ant-farm for another project, initialize with `/ant-farm:init` which creates a project-local `.crumbs/` directory.

## Contributing

See `CONTRIBUTING.md` for how to add agents, checkpoints, and templates, including cross-file dependency tables.

## Path Reference Convention

All file paths in this document use **repo-root relative** format. At runtime, agent files are synced to `~/.claude/agents/` and orchestration files to `~/.claude/orchestration/`. To translate:
- `orchestration/` → `~/.claude/orchestration/`
- `agents/` → `~/.claude/agents/`

## File Reference

| File | Read by | Purpose |
|------|---------|---------|
| `CLAUDE.md` | Claude Code (per-project prompt-dir) | Per-project instructions: triggers, session completion rules |
| `agents/*.md` | Claude Code (at startup) | Custom agent type definitions |
| `orchestration/RULES.md` | The Queen | Execution workflow steps, hard gates, concurrency rules |
| `orchestration/RULES-decompose.md` | The Planner | Decomposition workflow steps and gates |
| `orchestration/RULES-review.md` | The Queen (review phase) | Review-specific workflow rules |
| `orchestration/SETUP.md` | User | How to wire orchestration into a new project |
| `orchestration/GLOSSARY.md` | Reference | Term definitions used across orchestration docs |
| `orchestration/PLACEHOLDER_CONVENTIONS.md` | The Pantry, Pest Control | Placeholder syntax rules for templates |
| `orchestration/templates/implementation.md` | The Pantry | Agent prompt template with 6 mandatory steps |
| `orchestration/templates/checkpoints.md` | Pest Control | All checkpoint definitions (SSV, CCO, WWD, DMVDC, CCB, ESV) |
| `orchestration/templates/reviews.md` | `build-review-prompts.sh` | Review protocol, 4 review types, Big Head consolidation |
| `orchestration/templates/review-focus-areas.md` | `build-review-prompts.sh` | Per-type focus blocks for Nitpicker review prompts |
| `orchestration/templates/pantry.md` | The Pantry (self-read) | The Pantry's own instructions |
| `orchestration/templates/scout.md` | The Scout (self-read) | Pre-flight recon instructions |
| `orchestration/templates/surveyor.md` | The Surveyor (self-read) | Requirements gathering instructions |
| `orchestration/templates/forager.md` | The Forager (self-read) | Parallel research instructions |
| `orchestration/templates/decomposition.md` | The Architect | Decomposition workflow instructions |
| `orchestration/templates/dirt-pusher-skeleton.md` | The Queen | Minimal agent spawn template |
| `orchestration/templates/nitpicker-skeleton.md` | The Queen | Minimal review agent spawn template |
| `orchestration/templates/big-head-skeleton.md` | The Queen | Big Head consolidation spawn template |
| `orchestration/templates/scribe-skeleton.md` | The Queen | Scribe spawn template |
| `orchestration/templates/surveyor-skeleton.md` | The Planner | Surveyor spawn template |
| `orchestration/templates/forager-skeleton.md` | The Planner | Forager spawn template |
| `orchestration/templates/architect-skeleton.md` | The Planner | Architect spawn template |
| `orchestration/templates/queen-state.md` | The Queen | Session state template |
| `orchestration/templates/SESSION_PLAN_TEMPLATE.md` | User (copied to target project) | Session planning template |
| `orchestration/reference/dependency-analysis.md` | The Scout | Pre-flight conflict analysis |
| `orchestration/reference/known-failures.md` | Post-mortem reference | Past failures and fixes applied |
