# ant-farm

A multi-agent orchestration and quality review system for Claude Code. Coordinates parallel agent work across projects with structured verification gates that prevent the failure modes inherent to AI-generated code: skipped design steps, scope creep, fabricated review claims, and unverified acceptance criteria.

## Quick Start

1. **Clone and install hooks**
   ```bash
   git clone <repo-url> && cd ant-farm
   ./scripts/install-hooks.sh   # installs pre-push (sync) + pre-commit (PII scrub) hooks
   ./scripts/sync-to-claude.sh
   ```

2. **Restart Claude Code** so the custom agent types in `agents/` are loaded.

3. **Wire up a target project** -- add an orchestration section to the project's `CLAUDE.md` (see `orchestration/SETUP.md` for the full recipe):
   ```markdown
   ## Orchestration
   Global: `~/.claude/orchestration/` (RULES.md, templates/, reference/)
   Kickoff: "Let's get to work on: <task-ids>."
   Quality Gates:
   - [ ] Tests pass
   - [ ] Linter clean
   - [ ] Build succeeds
   ```

4. **Create a task and run your first session**
   ```bash
   bd create --title="My first task" --type=task --priority=3
   ```
   Then tell Claude Code:
   ```
   Let's get to work on: ant-farm-XXXX
   ```
   Claude will spawn the Scout for recon, present 2-3 execution strategies, and wait for your approval before spawning any implementation agents.

5. **Approve and watch** -- pick a strategy, and the Queen orchestrates the full workflow: prompt composition, checkpoint audits, implementation, and quality review.

## Architecture

The system has three layers: **the Queen** (the orchestrator that never touches source code), **Dirt Pushers** (implementation and review subagents), and **Pest Control** (an independent verification agent that audits both).

```
┌─────────────────────────────────────────────────────────┐
│  the Queen (orchestrator)                               │
│  - Reads briefing + verdict tables only                 │
│  - Spawns Scout, Pantry, Pest Control directly          │
│  - Only agent that pushes to remote                     │
├───────────┬─────────────┬───────────────────────────────┤
│  Scout    │  Pantry     │  Pest Control                 │
│  - Recon  │  - Composes │  - CCO (prompt audit)         │
│  - Writes │  task briefs│  - WWD (scope)                │
│   briefing│  - Writes   │  - DMVDC (substance)          │
│  - Writes │    previews │  - CCB (consolidation         │
│   metadata│             │    audit)                     │
├───────────┴─────────────┴───────────────────────────────┤
│  Dirt Pushers (up to 7 concurrent)                      │
├─────────────────────────────────────────────────────────┤
│  the Nitpickers (4 reviewers + Big Head + Pest Control) │
└─────────────────────────────────────────────────────────┘
```

**CCO** = Colony Cartography Office | **WWD** = Wandering Worker Detection | **DMVDC** = Dirt Moved vs Dirt Claimed | **CCB** = Colony Census Bureau

## Workflow

Triggered by saying **"let's get to work"** in any project wired up per `orchestration/SETUP.md`.

### Step 0: Session setup

Generate a session ID, create the session directory and `task-metadata/` subdirectory. No agents spawn yet.

### Step 1: Recon

The Queen spawns **the Scout** (`orchestration/templates/scout.md`), an opus subagent that performs all pre-flight reconnaissance:

1. Discovers tasks (from epic, explicit list, or natural-language filter)
2. Runs `bd ready` and `bd blocked` to separate ready vs. blocked tasks
3. Runs `bd show` per task and writes per-task metadata files to `{session-dir}/task-metadata/`
4. Builds a file modification matrix and assesses conflict risk using `orchestration/reference/dependency-analysis.md`
5. Scans `~/.claude/agents/` and `.claude/agents/` to discover available agent types, then recommends the best specialist per task
6. Proposes 2-3 execution strategies with wave groupings, agent counts, and risk assessments
7. Writes `{session-dir}/briefing.md` — a ~40-line summary the Queen presents to the user

The Queen reads the briefing, presents the strategy options, and **waits for user approval** before proceeding.

### Step 2: Spawn implementation agents

The Queen delegates prompt composition to **the Pantry**, a subagent that:
1. Reads `orchestration/templates/implementation.md` (keeping it out of the Queen's context)
2. Extracts pre-digested context from each task (affected files, root cause, acceptance criteria)
3. Copies the agent type recommendation from the Scout's task metadata (the Scout selects agent types dynamically based on available agents)
4. Writes a task brief per task with scope boundaries, agent type, and explicit off-limits areas
5. Writes combined prompt previews (skeleton + task brief) to `{session-dir}/previews/`
6. Returns a file path table — task IDs, agent types, task briefs, and preview files

The Queen then spawns **Pest Control** to audit the preview files against the **Colony Cartography Office (CCO)** checkpoint. Pest Control reads `orchestration/templates/checkpoints.md` itself, audits each preview, writes reports, and returns a verdict table. The Queen only spawns agents with PASS verdicts.

```
Queen                          Pantry                    Pest Control
  │                              │                           │
  ├──spawn────────────────────►  │                           │
  │  "compose Wave N prompts"    │                           │
  │                              ├─read templates            │
  │                              ├─read task-metadata/       │
  │                              ├─write task briefs to disk │
  │                              ├─write combined previews   │
  │  ◄──return paths + done──────┤                           │
  │  (~10 lines)                 │(agent dies, context freed)│
  │                                                          │
  ├──spawn─────────────────────────────────────────────────► │
  │  "read previews from {dir},                              │
  │   audit against CCO                                      │
  │   in checkpoints.md,                                     │
  │   write reports, return verdicts"                        │
  │                                                          ├─read checkpoints.md
  │                                                          ├─read preview files
  │                                                          ├─audit each
  │                                                          ├─write reports
  │  ◄──return verdict table─────────────────────────────────┤
  │  (~10 lines)                                (agent dies) │
  │                                                          │
  ├──spawn Dirt Pushers (up to 7)──►                         │
```

The Queen then spawns agents using `orchestration/templates/dirt-pusher-skeleton.md`, a minimal template that points the agent to its task brief. Each agent is spawned with the specialist `subagent_type` recommended by the Pantry (e.g., `python-pro` for `.py` files, `debugger` for investigation bugs). Each agent executes 6 mandatory steps:

1. **Claim** — `bd show` + `bd update --status=in_progress`
2. **Design** — 4+ genuinely distinct approaches with tradeoffs (not cosmetic variations)
3. **Implement** — clean, minimal code satisfying acceptance criteria
4. **Correctness review** — re-read every changed file, verify acceptance criteria, assumptions audit
5. **Commit** — `git pull --rebase` then commit with task ID in message
6. **Summary doc** — structured artifact with approaches, rationale, review evidence, and test results

Agents are constrained by **scope boundaries**: they may only edit the files and line ranges listed in their task brief. If they notice adjacent issues, they document them in an "Adjacent Issues Found" section but do not fix them.

### Step 3: Monitor and verify

After each wave completes, the Queen spawns **Pest Control** directly for post-wave verification:

- **Wandering Worker Detection (WWD)** (scope verification) — compares files changed in the commit against expected scope from the task. Catches scope creep between agents before it cascades.
- **Dirt Moved vs Dirt Claimed (DMVDC)** (substance verification) — reads the agent's summary doc and cross-checks claims against the actual git diff: Do the claimed file changes exist? Are acceptance criteria genuinely met? Are the 4 design approaches substantively distinct? Is the correctness review specific or boilerplate?

Pest Control reads `orchestration/templates/checkpoints.md`, task metadata, and git diffs itself — the Queen only passes task IDs, commit hashes, and summary doc paths.

```
Queen                                              Pest Control
  │  (agents committed, Queen has commit hashes)        │
  │                                                     │
  ├──spawn──────────────────────────────────────────►   │
  │  "read checkpoints.md,                              │
  │   run WWD for {tasks} against {commits},            │
  │   run DMVDC: read summary docs at {paths},          │
  │   cross-check against git diffs,                    │
  │   write reports, return verdicts"                   │
  │                                                     ├─read checkpoints.md
  │                                                     ├─per task: git diff + summary doc
  │                                                     ├─write WWD + DMVDC reports
  │  ◄──return verdict table────────────────────────────┤
  │  (~15 lines)                            (agent dies)│
```

Failed DMVDC → agent is resumed with specific gaps listed → re-verified → escalated to user after 2 retries.

The Queen prepares next-wave prompts (Pantry + Pest Control) while the current wave runs, eliminating spawn latency between waves.

### Step 3b: Quality review

After **all** implementation completes and all DMVDC checks pass, the Queen enters the review phase. This is mandatory — it cannot be skipped or deferred.

#### Transition gate

Before launching reviews, verify: all agents completed, all DMVDC checks passed, git log shows expected commits.

#### The Nitpickers

The Queen creates an **agent team** (TeamCreate, not Task) with 4 parallel reviewers that can message each other about overlapping findings:

| Review | Priority | Focus |
|--------|----------|-------|
| **Clarity** | P3 | Readability, naming, documentation, consistency |
| **Edge Cases** | P2 | Input validation, error handling, boundary conditions, concurrency |
| **Correctness** | P1-P2 | Acceptance criteria verification, logic errors, regressions, cross-file consistency |
| **Drift** | P3 | Stale cross-file references, incomplete propagation, broken assumptions |

Each reviewer reads all changed files, catalogs findings with file:line references and severity, groups them into preliminary root causes, and writes a structured report. Reviewers **do not file issues** — only Big Head does.

Every report includes a **coverage log** — every in-scope file must appear, even those with no findings. This prevents silently skipping files.

#### Big Head Consolidation

An opus-model Big Head reads all 4 reports and:
1. Merges duplicate findings across reviewers
2. Groups by root cause (one group per underlying problem, not per occurrence)
3. Documents merge rationale for every grouping
4. Files one issue per root cause with all affected surfaces
5. Writes a consolidated summary with deduplication log and priority breakdown

#### DMVDC + CCB (post-review verification)

**Pest Control** is a member of the Nitpicker team. It runs DMVDC (substance verification on each reviewer's report) and **Colony Census Bureau (CCB)** (consolidation audit on Big Head's output) inside the team before the team returns to the Queen.

```
Queen                       fill-review-slots.sh
  │                              │
  ├──run script────────────────► │
  │  (replaces pantry-review)    ├─read reviews.md
  │                              ├─write 4 review task briefs
  │                              ├─write combined previews
  │                              ├─write Big Head consolidation brief
  │  ◄──exit (files on disk)─────┤
  │
  ├──spawn Pest Control (CCO, pre-team audit)──────────────► PC
  │  ◄──return verdicts─────────────────────────────────────┤
  │
  ├──create Nitpicker team (4 reviewers + Big Head + PC)
  │  ┌────────────────────────────────────────────────────┐
  │  │  reviewers write reports                           │
  │  │  Big Head consolidates                             │
  │  │  Pest Control runs DMVDC + CCB (inside team)       │
  │  └────────────────────────────────────────────────────┘
  │  ◄──team returns report paths + verdict table
```

Before presenting results to the user, CCB audits the consolidation:
- Finding count reconciliation (raw findings → consolidated, all accounted for)
- Every filed issue exists and has required fields (root cause, file:line refs, acceptance criteria, suggested fix)
- Priority calibration (P1s are genuinely blocking, not mislabeled style issues)
- Traceability matrix (every finding traces to either an issue or an explicit dedup entry)
- Deduplication correctness (merged findings actually share a code path, not just vague similarity)
- Provenance audit (no unauthorized issues filed during review phase)

### Step 4: Document

Update README and CLAUDE.md in a single commit if needed. CHANGELOG is not updated here.

### Step 5b: Scribe

Spawn the Scribe agent to write the session exec summary (`{SESSION_DIR}/exec-summary.md`) and prepend a CHANGELOG entry to `CHANGELOG.md`. The Scribe reads all session artifacts and the commit range to produce both outputs.

### Step 5c: ESV (Exec Summary Verification)

Pest Control runs the ESV checkpoint — a hard gate that must PASS before Step 6. It verifies task coverage, commit coverage, open bead accuracy, CHANGELOG derivation fidelity, section completeness, and metric consistency.

### Step 6: Land

```bash
git pull --rebase
bd sync
git push
git status  # must show "up to date with origin"
```

Work is not complete until `git push` succeeds.

## Information diet

A core design principle: the Queen **never reads source code, tests, configs, or implementation templates**. It reads only the Scout's briefing, agent notifications, commit messages, and verdict tables.

Task metadata is read by the Scout, which writes per-task files and a briefing. `implementation.md` is read by the Pantry. `reviews.md` is read by `build-review-prompts.sh`. `checkpoints.md` is read by Pest Control. The Pantry reads the Scout's pre-extracted metadata files and writes combined prompt previews to disk. Pest Control reads these previews and checkpoint criteria directly. All agents absorb the context cost so the Queen's window stays clean.

Target: finish a 40+ task session with >50% context window remaining, <10 file reads in the Queen, <20 commits.

## Hard gates

| Gate | What it blocks | Model |
|------|---------------|-------|
| **SSV** — strategy verification | Pantry spawn | haiku |
| **CCO** — prompt audit | Agent spawn | haiku |
| **WWD** — scope verification | Next agent in wave | haiku |
| **DMVDC** — substance verification | Task closure | sonnet |
| **CCB** — consolidation audit | Presenting results to user | haiku |
| **ESV** — exec summary verification | Git push (Step 6) | haiku |

All checkpoint artifacts are written to `<session-dir>/pc/` with timestamped filenames for full audit history.

## Priority calibration

| Level | Meaning | Examples |
|-------|---------|---------|
| **P1** | Blocking | Build failure, broken links, data loss, security vulnerability |
| **P2** | Important | Visual regression, accessibility issue, functional degradation |
| **P3** | Polish | Style, naming, cleanup, code quality improvements |

## Retry limits

| Situation | Max retries | After limit |
|-----------|-------------|-------------|
| Agent fails DMVDC | 2 | Escalate to user |
| CCB fails | 1 | Present to user with verification report |
| Agent stuck (no commit in 15 turns) | 0 | Check status, escalate |
| Total retries per session | 5 | Pause all spawns, triage with user |

## Known failure modes

Documented in `orchestration/reference/known-failures.md`. Key incidents that shaped the system:

**Skipped design and review steps** (Epic 3) — Agents bypassed the mandatory design (4 approaches) and correctness review steps. Fix: DMVDC now verifies substance, not just completion claims.

**Work scrambling** (Epic 74g) — Three agents on the same file without line-level boundaries. Each "helpfully" fixed adjacent issues, scrambling work attribution. Fixes: WWD for real-time scope verification, enhanced CCO requiring line-number specificity, anti-scope-creep template with explicit boundary language, and pre-flight conflict risk assessment.

## Custom agents

Custom Claude Code agent types live in `agents/` and are synced to `~/.claude/agents/` on push via the pre-push hook. Changes to agent files require restarting Claude Code (fully quit and reopen) to take effect.

| Agent | Tools | Purpose |
|-------|-------|---------|
| `scout-organizer` | Bash, Read, Write, Glob, Grep | Pre-flight recon: task discovery, dependency analysis, execution strategy |
| `pest-control` | Bash, Read, Write, Glob, Grep | Verification auditor: checkpoint audits (CCO, WWD, DMVDC, CCB) |
| `pantry-impl` | Read, Write, Glob, Grep | Implementation prompt composer: builds task briefs and combined previews |
| `pantry-review` | Read, Write, Glob, Grep | ~~Review prompt composer: builds review briefs and combined previews~~ **DEPRECATED** — replaced by `build-review-prompts.sh` bash script; see RULES.md Step 3b |
| `nitpicker` | Read, Write, Edit, Bash, Glob, Grep | Code reviewer: finds issues with file:line specificity and calibrated severity |
| `big-head` | Read, Write, Edit, Bash, Glob, Grep | Consolidation reviewer: merges and deduplicates findings across Nitpickers |

## Forking this repo

The `.beads/issues.jsonl` file is the issue database for **this** project's development. When you fork ant-farm to use as a template for your own orchestration setup, you should reset the issue database so you start with a clean slate under your own identity.

### Steps for new adopters

1. Fork or clone the repo and navigate into it.
2. Run `bd init` to initialize a fresh issue database:
   ```bash
   bd init --prefix <your-project-name>
   ```
   This creates a new `.beads/issues.jsonl` with no inherited issues and sets your project prefix.
3. If you want to import from the existing JSONL (e.g., you performed manual cleanup first), use the `--from-jsonl` flag:
   ```bash
   bd init --from-jsonl --prefix <your-project-name>
   ```
4. Install the git hooks so agent files sync to `~/.claude/agents/` on push:
   ```bash
   # See orchestration/SETUP.md for full hook installation instructions
   ```

The `.beads/issues.jsonl` in this repo contains sample issues from ant-farm's own development history. They are included as reference material showing how the system has been used but are not required for operation. Running `bd init` replaces them with a fresh database.

## Path reference convention

All file paths in this document and `orchestration/RULES.md` use **repo-root relative** format:
`orchestration/templates/scout.md`, `agents/scout-organizer.md`, etc.

When code runs at runtime, agent files are synced to `~/.claude/agents/` and orchestration files are
accessible at `~/.claude/orchestration/templates/scout.md`. To translate repo paths to runtime paths:
- Replace `orchestration/` with `~/.claude/orchestration/`
- Replace `agents/` with `~/.claude/agents/`

Informal shorthand (e.g., "templates/scout.md") is informal and always refers to repo-root paths with the `orchestration/` prefix implied.

## File reference

| File | Read by | Purpose |
|------|---------|---------|
| `CLAUDE.md` | Claude Code (all projects) | Global instructions: triggers, session completion rules |
| `agents/*.md` | Claude Code (at startup) | Custom agent type definitions, synced to `~/.claude/agents/` on push |
| `orchestration/RULES.md` | The Queen | Workflow steps, hard gates, concurrency rules, template lookup |
| `orchestration/SETUP.md` | User | How to wire orchestration into a new project |
| `orchestration/GLOSSARY.md` | Reference | Term definitions used across orchestration docs |
| `orchestration/PLACEHOLDER_CONVENTIONS.md` | The Pantry, Pest Control | Placeholder syntax rules for templates and checkpoints |
| `orchestration/templates/implementation.md` | The Pantry | Agent prompt template with 6 mandatory steps |
| `orchestration/templates/checkpoints.md` | Pest Control | All checkpoint definitions (CCO, WWD, DMVDC, CCB) |
| `orchestration/templates/reviews.md` | `build-review-prompts.sh` | Review protocol, 4 review types, report format, Big Head consolidation |
| `orchestration/templates/pantry.md` | The Pantry (self-read at spawn) | The Pantry's own instructions |
| `orchestration/templates/dirt-pusher-skeleton.md` | The Queen | Minimal agent spawn template |
| `orchestration/templates/nitpicker-skeleton.md` | The Queen | Minimal review agent spawn template |
| `orchestration/templates/big-head-skeleton.md` | The Queen | Minimal Big Head consolidation spawn template |
| `orchestration/templates/queen-state.md` | The Queen | Session state template with placeholder fields |
| `orchestration/templates/scout.md` | The Scout (self-read at spawn) | Pre-flight recon instructions |
| `orchestration/templates/SESSION_PLAN_TEMPLATE.md` | User (copied to target project) | Session planning template for project customization |
| `orchestration/reference/dependency-analysis.md` | The Scout | Pre-flight conflict analysis, spawn patterns |
| `orchestration/reference/known-failures.md` | Post-mortem reference | Past failures and fixes applied |
