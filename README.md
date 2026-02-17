# ant-farm

A multi-agent orchestration and quality review system for Claude Code. Coordinates parallel agent work across projects with structured verification gates that prevent the failure modes inherent to AI-generated code: skipped design steps, scope creep, fabricated review claims, and unverified acceptance criteria.

## Architecture

The system has three layers: a **boss-bot** (the orchestrator that never touches source code), **worker agents** (implementation and review subagents), and **snitch-bot** (an independent verification agent that audits both).

```
┌─────────────────────────────────────────────────────────┐
│  Boss-Bot (orchestrator)                                │
│  - Reads task metadata only (never source code)         │
│  - Spawns Prompt Factory & Checkpoint Coordinator       │
│  - Tracks state in session state file                   │
│  - Only agent that pushes to remote                     │
├─────────────────────┬───────────────────────────────────┤
│  Prompt Factory     │  Checkpoint Coordinator           │
│  - Reads templates  │  - Reads checkpoint templates     │
│  - Composes agent   │  - Spawns snitch-bot in batch     │
│    data files       │  - Returns verdict tables         │
│  - Runs Checkpoint A│                                   │
├─────────────────────┴───────────────────────────────────┤
│  Worker Agents (up to 7 concurrent)                     │
│  - Implementation agents: 6-step process per task       │
│  - Review team: 4 parallel reviewers + lead             │
├─────────────────────────────────────────────────────────┤
│  Snitch-Bot (verification)                              │
│  - Audits prompts before spawn (Checkpoint A)           │
│  - Verifies commit scope after each agent (A.5)         │
│  - Cross-checks claims against code (Checkpoint B)      │
│  - Audits consolidated review (Checkpoint C)            │
└─────────────────────────────────────────────────────────┘
```

## Workflow

Triggered by saying **"let's get to work"** in any project wired up per `SETUP.md`.

### Step 0: Pre-flight

Boss-bot gathers task metadata (`bd show`), builds a **file modification matrix** to identify conflict risk, and presents 2-3 execution strategies (serial, balanced, full parallel) to the user. No agents spawn until the user approves a strategy.

Conflict risk tiers:
- **HIGH** (3+ tasks on same file) — serialize or batch to one agent
- **MEDIUM** (2 tasks on same file, different sections) — parallel with rebase
- **LOW** (independent files) — full parallel

See `reference/dependency-analysis.md` for the full decision matrix.

### Step 1: Discover

Run `bd ready`, filter by epic, group by priority tier. P1 tasks (build failures, security, data loss) go first.

### Step 2: Spawn implementation agents

Boss-bot delegates prompt composition to the **Prompt Factory**, a subagent that:
1. Reads `templates/implementation.md` and `templates/checkpoints.md` (keeping these out of boss-bot's context)
2. Extracts pre-digested context from each task (affected files, root cause, acceptance criteria)
3. Writes a data file per task with scope boundaries and explicit off-limits areas
4. Runs **Checkpoint A** (pre-spawn prompt audit) on each composed prompt
5. Returns a verdict table — boss-bot only spawns agents with PASS verdicts

Boss-bot then spawns agents using `templates/agent-skeleton.md`, a minimal template that points the agent to its data file. Each agent executes 6 mandatory steps:

1. **Claim** — `bd show` + `bd update --status=in_progress`
2. **Design** — 4+ genuinely distinct approaches with tradeoffs (not cosmetic variations)
3. **Implement** — clean, minimal code satisfying acceptance criteria
4. **Correctness review** — re-read every changed file, verify acceptance criteria, assumptions audit
5. **Commit** — `git pull --rebase` then commit with task ID in message
6. **Summary doc** — structured artifact with approaches, rationale, review evidence, and test results

Agents are constrained by **scope boundaries**: they may only edit the files and line ranges listed in their data file. If they notice adjacent issues, they document them in an "Adjacent Issues Found" section but do not fix them.

### Step 3: Monitor and verify

After each agent commits, the **Checkpoint Coordinator** runs verification in batch:

- **Checkpoint A.5** (haiku, mechanical) — compares files changed in the commit against expected scope from the task. Catches scope creep between agents before it cascades.
- **Checkpoint B** (sonnet, judgment-based) — reads the agent's summary doc and cross-checks claims against the actual git diff: Do the claimed file changes exist? Are acceptance criteria genuinely met? Are the 4 design approaches substantively distinct? Is the correctness review specific or boilerplate?

Failed Checkpoint B → agent is resumed with specific gaps listed → re-verified → escalated to user after 2 retries.

Boss-bot prepares next-wave prompts while the current wave runs, eliminating spawn latency between waves.

### Step 3b: Quality review

After **all** implementation completes and all Checkpoint Bs pass, boss-bot enters the review phase. This is mandatory — it cannot be skipped or deferred.

#### Transition gate

Before launching reviews, verify: all agents completed, all Checkpoint Bs passed, git log shows expected commits.

#### Review team

Boss-bot creates an **agent team** (TeamCreate, not Task) with 4 parallel reviewers that can message each other about overlapping findings:

| Review | Priority | Focus |
|--------|----------|-------|
| **Clarity** | P3 | Readability, naming, documentation, consistency |
| **Edge Cases** | P2 | Input validation, error handling, boundary conditions, concurrency |
| **Correctness Redux** | P1-P2 | Acceptance criteria verification, logic errors, regressions, cross-file consistency |
| **Excellence** | P3 | Best practices, performance, security, maintainability, architecture |

Each reviewer reads all changed files, catalogs findings with file:line references and severity, groups them into preliminary root causes, and writes a structured report. Reviewers **do not file issues** — only the lead does.

Every report includes a **coverage log** — every in-scope file must appear, even those with no findings. This prevents silently skipping files.

#### Lead consolidation

An opus-model lead reads all 4 reports and:
1. Merges duplicate findings across reviewers
2. Groups by root cause (one group per underlying problem, not per occurrence)
3. Documents merge rationale for every grouping
4. Files one issue per root cause with all affected surfaces
5. Writes a consolidated summary with deduplication log and priority breakdown

#### Checkpoint C (consolidation audit)

Before presenting results to the user, snitch-bot audits the consolidation:
- Finding count reconciliation (raw findings → consolidated, all accounted for)
- Every filed issue exists and has required fields (root cause, file:line refs, acceptance criteria, suggested fix)
- Priority calibration (P1s are genuinely blocking, not mislabeled style issues)
- Traceability matrix (every finding traces to either an issue or an explicit dedup entry)
- Deduplication correctness (merged findings actually share a code path, not just vague similarity)
- Provenance audit (no unauthorized issues filed during review phase)

### Step 4-5: Document and verify

Update CHANGELOG, README, and project CLAUDE.md in a single commit. Cross-reference all entries.

### Step 6: Land

```bash
git pull --rebase
bd sync
git push
git status  # must show "up to date with origin"
rm -rf .beads/agent-summaries/_session-*/
```

Work is not complete until `git push` succeeds.

## Information diet

A core design principle: boss-bot **never reads source code, tests, configs, or implementation templates**. It reads only task metadata, agent notifications, commit messages, and verdict tables.

Templates like `implementation.md`, `checkpoints.md`, and `reviews.md` are read by the Prompt Factory and Checkpoint Coordinator — specialized subagents that absorb the context cost so boss-bot's window stays clean.

Target: finish a 40+ task session with >50% context window remaining, <10 file reads in boss-bot, <20 commits.

## Hard gates

| Gate | What it blocks | Model |
|------|---------------|-------|
| **Checkpoint A** — prompt audit | Agent spawn | haiku |
| **Checkpoint A.5** — scope verification | Next agent in wave | haiku |
| **Checkpoint B** — substance verification | Task closure | sonnet |
| **Checkpoint C** — consolidation audit | Presenting results to user | haiku |

All checkpoint artifacts are written to `.beads/agent-summaries/<epic>/verification/snitch-bot/` with timestamped filenames for full audit history.

## Priority calibration

| Level | Meaning | Examples |
|-------|---------|---------|
| **P1** | Blocking | Build failure, broken links, data loss, security vulnerability |
| **P2** | Important | Visual regression, accessibility issue, functional degradation |
| **P3** | Polish | Style, naming, cleanup, code quality improvements |

## Retry limits

| Situation | Max retries | After limit |
|-----------|-------------|-------------|
| Agent fails Checkpoint B | 2 | Escalate to user |
| Checkpoint C fails | 1 | Present to user with verification report |
| Agent stuck (no commit in 15 turns) | 0 | Check status, escalate |
| Total retries per session | 5 | Pause all spawns, triage with user |

## Known failure modes

Documented in `reference/known-failures.md`. Key incidents that shaped the system:

**Skipped design and review steps** (Epic 3) — Agents bypassed the mandatory design (4 approaches) and correctness review steps. Fix: Checkpoint B now verifies substance, not just completion claims.

**Work scrambling** (Epic 74g) — Three agents on the same file without line-level boundaries. Each "helpfully" fixed adjacent issues, scrambling work attribution. Fixes: Checkpoint A.5 for real-time scope verification, enhanced Checkpoint A requiring line-number specificity, anti-scope-creep template with explicit boundary language, and pre-flight conflict risk assessment.

## File reference

| File | Read by | Purpose |
|------|---------|---------|
| `CLAUDE.md` | Claude Code (all projects) | Global instructions: triggers, session completion rules |
| `orchestration/RULES.md` | Boss-bot | Workflow steps, hard gates, concurrency rules, template lookup |
| `orchestration/SETUP.md` | User | How to wire orchestration into a new project |
| `orchestration/templates/implementation.md` | Prompt Factory | Agent prompt template with 6 mandatory steps |
| `orchestration/templates/checkpoints.md` | Prompt Factory, Checkpoint Coordinator | All checkpoint definitions (A, A.5, B, C) |
| `orchestration/templates/reviews.md` | Prompt Factory (review mode) | Review protocol, 4 review types, report format, lead consolidation |
| `orchestration/templates/prompt-factory.md` | Boss-bot (to spawn Prompt Factory) | Prompt Factory's own instructions |
| `orchestration/templates/checkpoint-coordinator.md` | Boss-bot (to spawn Coordinator) | Checkpoint Coordinator's own instructions |
| `orchestration/templates/agent-skeleton.md` | Boss-bot | Minimal agent spawn template |
| `orchestration/templates/review-skeleton.md` | Boss-bot | Minimal review agent spawn template |
| `orchestration/templates/lead-skeleton.md` | Boss-bot | Minimal lead consolidation spawn template |
| `orchestration/templates/boss-bot-state.md` | Boss-bot | Session state file schema |
| `orchestration/reference/dependency-analysis.md` | Boss-bot (Step 0) | Pre-flight conflict analysis, spawn patterns |
| `orchestration/reference/known-failures.md` | Post-mortem reference | Past failures and fixes applied |
