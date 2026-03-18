# ant-farm

You spawned 7 agents in parallel. Three of them edited the same file. Now your main branch looks like a merge conflict art installation and the only audit trail is "Agent completed successfully."

ant-farm is a bounded multi-agent orchestration framework for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). It separates planning from execution, drives implementation through specialist subagents, and uses mechanical verification gates to keep agent work auditable, recoverable, and hard to fake.

It is not an open-ended autonomous coding agent. It is a constrained orchestration layer that sits on top of Claude Code, with checkpoints at every phase transition. The agents do the work. The system makes sure they did it right.

> **TL;DR**
>
> - Decomposes specs into dependency-aware tasks, then executes them in parallel waves
> - Six verification checkpoints block progression if agents cut corners or drift out of scope
> - The orchestrator (the Queen) never reads source code. It reads briefings, verdicts, and commit messages. Everything else is delegated.
> - Four parallel code reviewers (with automatic split-instancing for large file sets) consolidate findings by root cause, file fix tasks, and re-review until convergence
> - Every session produces a full artifact trail: metadata, prompts, summaries, review reports, checkpoint audits, exec summary, and CHANGELOG entry
> - If something goes wrong, the system escalates to you with context instead of retrying forever

## How It Works

ant-farm defines two workflows:

- **Planning** (`/ant-farm-plan`): turns a freeform request or structured spec into dependency-aware tasks (trails and crumbs) via requirements gathering, parallel research, and decomposition.
- **Execution** (`/ant-farm-work` or "let's get to work"): runs an implementation session with recon, prompt composition, parallel agent spawning, post-commit verification, code review, and documentation.

The core idea is **constrained delegation**. Work is split across specialist agents, but progression is controlled by artifacts on disk, verification checkpoints, retry limits, and explicit escalation to you when things go wrong.

```
Planning Workflow                    Execution Workflow

  Surveyor                             Scout (recon)
     |                                    |
  Foragers (4x parallel research)      SSV gate
     |                                    |
  Architect (decomposition)            Pantry (prompt composition)
     |                                    |
  TDV gate                             CCO gate (prompt audit)
     |                                    |
  User approval gate                   Dirt Pushers (implementation, up to 7 parallel)
     |                                    |
  .crumbs/tasks.jsonl  ────────►       WWD + DMVDC gates (scope + substance verification)
                                          |
                                       Nitpickers (4+ parallel review) + Big Head (consolidation)
                                          |
                                       CCB gate (consolidation audit)
                                          |
                                       Scribe (exec summary + CHANGELOG)
                                          |
                                       ESV gate → git push
```

## Architecture

Four layers, each with a clear job.

**1. Task and artifact layer.** `crumb.py` stores tasks and trails in `.crumbs/tasks.jsonl`. Sessions write durable artifacts (metadata, prompts, summaries, review reports, checkpoint audits) under `.crumbs/sessions/`.

**2. Two orchestrators.** The Planner handles decomposition (Surveyor, Foragers, Architect). The Queen handles execution (Scout, Pantry, Dirt Pushers, Nitpickers, Big Head, Scribe). They have different permissions, different state models, and different agent teams.

**3. Specialist agents.** Claude Code agent definitions in `agents/` cover recon, prompt composition, implementation, review, consolidation, verification, and documentation.

**4. Verification layer.** Pest Control runs six checkpoint types (SSV, CCO, WWD, DMVDC, CCB, ESV) that mechanically block progression. It operates both as a standalone checkpoint runner and as a member of the Nitpicker review team.

### The Queen's Information Diet

The Queen never reads source code, tests, configs, or implementation templates. It reads the Scout's briefing, agent notifications, commit messages, and verdict tables. That's it.

Every other agent absorbs its own context cost so the Queen's window stays clean. The target: finish a 40+ task session with >75% of a 1M context window remaining.

If your orchestrator is spending tokens reading `utils.py`, it is not orchestrating.

### Hard Gates

Nothing progresses until these pass.

| Gate | Full Name | What it blocks | Model |
|------|-----------|---------------|-------|
| **SSV** | Scout Strategy Verification | Pantry spawn | haiku |
| **CCO** | Colony Cartography Office | Agent spawn | haiku |
| **WWD** | Wandering Worker Detection | Next agent in wave | haiku |
| **DMVDC** | Dirt Moved vs Dirt Claimed | Task closure | sonnet |
| **CCB** | Colony Census Bureau | Presenting results to user | haiku |
| **ESV** | Exec Summary Verification | Git push | haiku |

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
- Skills to `~/.claude/skills/ant-farm-*/SKILL.md`
- `crumb.py` to `~/.local/bin/crumb`
- Orchestration triggers to your project's `CLAUDE.md`

Then **restart Claude Code**. Agent types are loaded at startup only.

For detailed installation, backup, and uninstall instructions, see `docs/installation-guide.md`.

### Wire Up a Target Project

Run `/ant-farm-init` inside the target project to install orchestration triggers. This writes the canonical orchestration block into the project's `CLAUDE.md`, which Claude Code loads into the system prompt at session start.

See `orchestration/SETUP.md` for the full recipe and manual setup option.

### Run Your First Session

```bash
crumb create --title="My first task" --type=task --priority=3
```

Then tell Claude Code:

```
Let's get to work on: ant-farm-XXXX
```

The Queen spawns the Scout for recon, verifies the strategy via SSV, and auto-proceeds to spawn implementation agents. You don't approve the strategy. The checkpoint does.

## Project Structure

```
ant-farm/
├── agents/                  # Custom Claude Code agent definitions (.md files)
│   ├── ant-farm-scout-organizer.md
│   ├── ant-farm-pantry-impl.md
│   ├── ant-farm-pest-control.md
│   ├── ant-farm-nitpicker-{clarity,edge-cases,correctness,drift}.md
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
│   ├── templates/           # Agent prompt templates and skeletons
│   │   ├── claude-block.md  # Canonical orchestration block (triggers + session completion)
│   │   ├── scout.md, pantry.md, implementation.md, reviews.md
│   │   ├── checkpoints/     # Per-checkpoint definitions (common.md + one file per checkpoint)
│   │   │   ├── common.md   # Shared preamble (term definitions, verdict thresholds)
│   │   │   ├── cco.md, wwd.md, dmvdc.md, ccb.md, ssv.md, esv.md, tdv.md
│   │   ├── dirt-pusher-skeleton.md, nitpicker-skeleton.md, big-head-skeleton.md
│   │   ├── scribe-skeleton.md, surveyor-skeleton.md, forager-skeleton.md
│   │   ├── decomposition.md, architect-skeleton.md
│   │   └── review-focus-areas.md, queen-state.md, SESSION_PLAN_TEMPLATE.md
│   └── reference/
│       ├── dependency-analysis.md   # Pre-flight conflict analysis
│       └── known-failures.md        # Past failures and fixes applied
├── scripts/
│   ├── setup.sh                     # Installs everything to ~/.claude/ and PATH
│   ├── build-review-prompts.sh      # Builds review prompts from templates
│   └── parse-progress-log.sh        # Session recovery from progress log
├── skills/                  # Slash commands (/ant-farm-work, /ant-farm-plan, etc.)
├── crumb.py                 # Task-tracking CLI (installed to ~/.local/bin/crumb)
├── tests/                   # Tests for crumb.py
├── CONTRIBUTING.md          # How to add agents, checkpoints, and templates
├── CHANGELOG.md             # Session-by-session development history
└── .crumbs/                 # Task database and session artifacts
    ├── tasks.jsonl           # Task/trail database (this project's issue tracker)
    └── sessions/             # Per-session artifact directories
```

## Execution Workflow, Step by Step

Triggered by saying **"let's get to work"** in any project wired up per `orchestration/SETUP.md`.

### Step 0: Session Setup

Generate a session ID, create the session directory, and initialize the artifact layout. If a prior session directory is supplied, the Queen can recover from `progress.log` via `scripts/parse-progress-log.sh`.

### Step 1: Recon

The Queen spawns the Scout, an opus subagent that:

1. Discovers tasks (from epic, explicit list, or natural-language filter)
2. Separates ready vs. blocked tasks
3. Writes per-task metadata to `{session-dir}/task-metadata/`
4. Builds a file modification matrix and assesses conflict risk
5. Recommends the best specialist agent type per task
6. Proposes 2-3 execution strategies with wave groupings
7. Writes `{session-dir}/briefing.md`

After SSV PASS, the Queen auto-proceeds. Strategy approval is mechanical, not conversational.

### Step 2: Spawn Implementation Agents

The Queen delegates prompt composition to the Pantry, which reads templates, extracts per-task context, and writes combined prompt previews to disk. Pest Control audits the previews against the CCO checkpoint. Only agents with PASS verdicts are spawned.

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
  │                                                          ├─read checkpoints/common.md + cco.md
  │                                                          ├─audit each preview
  │  ◄──return verdict table─────────────────────────────────┤
  │                                                          │
  ├──spawn Dirt Pushers (up to 7 parallel)──►                │
```

Each Dirt Pusher executes 6 mandatory steps:

1. **Claim** the task
2. **Design** 4+ genuinely distinct approaches with tradeoffs
3. **Implement** clean, minimal code satisfying acceptance criteria
4. **Review** every changed file against acceptance criteria
5. **Commit** with `git pull --rebase` first
6. **Write a summary doc** with approaches, rationale, and review evidence

Agents are constrained by scope boundaries: they may only edit the files and line ranges listed in their task brief.

### Step 3: Monitor and Verify

After each wave, Pest Control runs:

- **WWD** (scope verification): files changed in the commit match expected scope. No scope creep.
- **DMVDC** (substance verification): git diff matches summary claims, acceptance criteria are genuinely met, design approaches are substantively distinct.

Failed DMVDC means the agent is resumed with specific gaps, re-verified, and escalated to you after 2 retries.

### Step 3b: Quality Review

After all implementation and DMVDC checks pass, the Queen enters a mandatory review phase with a Nitpicker team (4+ parallel reviewers + Big Head + Pest Control):

| Review | Severity Focus | Model |
|--------|---------------|-------|
| **Clarity** | P3: readability, naming, documentation | sonnet |
| **Edge Cases** | P2: input validation, error handling, boundary conditions | opus |
| **Correctness** | P1-P2: acceptance criteria, logic errors, regressions | opus |
| **Drift** | P3: stale cross-file references, broken assumptions | sonnet |

When the changed-file count exceeds `REVIEW_SPLIT_THRESHOLD` (default 8), Clarity and Drift are split into multiple instances (e.g., `clarity-1`, `clarity-2`) with partitioned file subsets. Correctness and Edge Cases always receive the full file list.

Big Head reads all reports, merges duplicates by root cause, and files one issue per root cause. Pest Control runs DMVDC + CCB inside the team before results return to the Queen.

If P1/P2 issues are found, the system enters a review/fix/re-review loop until convergence, deferral, or the round cap.

### Steps 4-6: Document and Land

- **Step 4**: Update documentation if needed
- **Step 5b**: Scribe writes exec summary and CHANGELOG entry
- **Step 5c**: ESV checkpoint verifies exec summary integrity
- **Step 6**: `git pull --rebase && git push`. Work is not complete until push succeeds.

## Custom Agents

Agent definitions live in `agents/` and are installed to `~/.claude/agents/` by `scripts/setup.sh`. Changes require restarting Claude Code.

| Agent | What it does |
|-------|-------------|
| `ant-farm-scout-organizer` | Pre-flight recon: task discovery, dependency analysis, execution strategy |
| `ant-farm-pantry-impl` | Prompt composer: builds task briefs and combined previews |
| `ant-farm-pest-control` | Verification auditor: runs all six checkpoints |
| `ant-farm-nitpicker-clarity` | Clarity reviewer: readability, naming, documentation |
| `ant-farm-nitpicker-edge-cases` | Edge cases reviewer: input validation, error handling, boundary conditions |
| `ant-farm-nitpicker-correctness` | Correctness reviewer: acceptance criteria, logic errors, regressions |
| `ant-farm-nitpicker-drift` | Drift reviewer: stale cross-file references, broken assumptions |
| `ant-farm-big-head` | Consolidation: merges and deduplicates findings across Nitpickers |
| `ant-farm-architect` | Spec decomposition: creates trails, crumbs, and dependencies |
| `ant-farm-forager` | Parallel research: investigates one focus area against a spec |
| `ant-farm-surveyor` | Requirements gathering: structured specs with acceptance criteria |
| `ant-farm-technical-writer` | Session Scribe: exec summaries and CHANGELOG entries |

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

## How This Has Failed (and What We Built to Stop It)

Documented in `orchestration/reference/known-failures.md`. Two incidents shaped the system more than anything else.

**Agents skipped the hard parts.** During Epic 3, agents bypassed mandatory design and correctness review steps. They claimed "4 approaches considered" without actually considering them. DMVDC now verifies substance, not just completion claims. It reads the git diff and checks whether the summary matches reality.

**Three agents trampled the same file.** During Epic 74g, three agents worked on the same file without line-level boundaries. Each one "helpfully" fixed adjacent issues and introduced conflicts. This produced WWD (scope verification), enhanced CCO (requiring line-number specificity in prompts), anti-scope-creep template language, and pre-flight conflict risk assessment in the Scout.

Most orchestration problems are trust problems wearing a concurrency costume.

## Forking This Repo

The `.crumbs/tasks.jsonl` file is the issue database for **this** project's development history. If you adopt ant-farm for another project, run `/ant-farm-init` which creates a project-local `.crumbs/` directory.

## Contributing

See `CONTRIBUTING.md` for how to add agents, checkpoints, and templates, including cross-file dependency tables.

## Path Reference Convention

All file paths in this document use repo-root relative format. At runtime, agent files are synced to `~/.claude/agents/` and orchestration files to `~/.claude/orchestration/`. To translate:
- `orchestration/` → `~/.claude/orchestration/`
- `agents/` → `~/.claude/agents/`

<details>
<summary><strong>File Reference</strong> (click to expand)</summary>

| File | Read by | Purpose |
|------|---------|---------|
| `orchestration/templates/claude-block.md` | `setup.sh`, `/ant-farm-init` | Canonical orchestration block (triggers + session completion) |
| `agents/*.md` | Claude Code (at startup) | Custom agent type definitions |
| `orchestration/RULES.md` | The Queen | Execution workflow steps, hard gates, concurrency rules |
| `orchestration/RULES-decompose.md` | The Planner | Decomposition workflow steps and gates |
| `orchestration/RULES-review.md` | The Queen (review phase) | Review-specific workflow rules |
| `orchestration/SETUP.md` | User | How to wire orchestration into a new project |
| `orchestration/GLOSSARY.md` | Reference | Term definitions used across orchestration docs |
| `orchestration/templates/implementation.md` | The Pantry | Agent prompt template with 6 mandatory steps |
| `orchestration/templates/checkpoints/` | Pest Control | Per-checkpoint definitions (common.md preamble + one file per checkpoint type) |
| `orchestration/templates/reviews.md` | `build-review-prompts.sh` | Review protocol, 4 review types, Big Head consolidation |
| `orchestration/templates/pantry.md` | The Pantry | Pantry's own instructions |
| `orchestration/templates/scout.md` | The Scout | Pre-flight recon instructions |
| `orchestration/templates/surveyor.md` | The Surveyor | Requirements gathering instructions |
| `orchestration/templates/forager.md` | The Forager | Parallel research instructions |
| `orchestration/templates/decomposition.md` | The Architect | Decomposition workflow instructions |
| `orchestration/templates/dirt-pusher-skeleton.md` | The Queen | Minimal agent spawn template |
| `orchestration/templates/nitpicker-skeleton.md` | The Queen | Minimal review agent spawn template |
| `orchestration/templates/big-head-skeleton.md` | The Queen | Big Head consolidation spawn template |
| `orchestration/templates/scribe-skeleton.md` | The Queen | Scribe spawn template |
| `orchestration/templates/surveyor-skeleton.md` | The Planner | Surveyor spawn template |
| `orchestration/templates/forager-skeleton.md` | The Planner | Forager spawn template |
| `orchestration/templates/architect-skeleton.md` | The Planner | Architect spawn template |
| `orchestration/templates/queen-state.md` | The Queen | Session state template |
| `orchestration/templates/SESSION_PLAN_TEMPLATE.md` | User | Session planning template |
| `orchestration/reference/dependency-analysis.md` | The Scout | Pre-flight conflict analysis |
| `orchestration/reference/known-failures.md` | Post-mortem reference | Past failures and fixes applied |

</details>
