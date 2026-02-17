# Orchestration Rules

## Workflow: "Let's Get to Work"

**Step 0:** Pre-flight — gather task metadata (bd show), analyze file conflicts (→ reference/dependency-analysis.md), present strategy, WAIT for user approval

**Step 1:** Discover — run bd ready, filter epics, group by priority tier, select highest tier

**Step 2:** Spawn — Prompt Factory composes data files + runs Checkpoint A (→ templates/prompt-factory.md),
then boss-bot spawns agents using skeleton (→ templates/agent-skeleton.md)

**Step 3:** Monitor — track agent status, Checkpoint Coordinator runs A.5 + B after wave completes
(→ templates/checkpoint-coordinator.md)

**Step 3b:** Review — Prompt Factory (review mode) composes prompts + Checkpoint A,
boss-bot launches team with review skeletons (→ templates/review-skeleton.md),
Checkpoint Coordinator (review mode) runs B + C after team completes

**Step 4:** Documentation — update CHANGELOG, README, CLAUDE.md in single commit

**Step 5:** Verify — cross-references valid, all tasks have CHANGELOG entries

**Step 6:** Land the plane — git pull --rebase, bd sync, git push, cleanup artifacts

## Hard Gates

| Gate | Blocks | Artifact |
|------|--------|----------|
| Checkpoint A PASS | Agent/team spawn | .beads/agent-summaries/<epic>/verification/snitch-bot/*-checkpoint-a-*.md |
| Checkpoint B PASS | Task closure (bd close) | .beads/agent-summaries/<epic>/verification/snitch-bot/*-checkpoint-b-*.md |
| Checkpoint C PASS | Presenting results to user | .beads/agent-summaries/<epic>/verification/snitch-bot/*-consolidation-checkpoint-c-*.md |
| Reviews | Mandatory after ALL implementation completes — do NOT ask user, do NOT skip |

## Information Diet (Boss-Bot Window)

**READ:** bd show (once per task, in Step 0), git status/log/diff --stat, agent notifications,
commit messages, agent-skeleton.md (once per wave), review-skeleton.md (once per review cycle),
lead-skeleton.md (once per review cycle), verdict tables from factory/coordinator

**DO NOT READ:** source code, tests, data files, configs, implementation.md, checkpoints.md, reviews.md
(these are read by Prompt Factory and Checkpoint Coordinator, not boss-bot)

## Concurrency Rules

- Max 7 background agents at any time
- No two agents edit the same file — queue conflicting tasks sequentially
- Each agent runs `git pull --rebase` before committing
- Only boss-bot pushes to remote
- Only boss-bot updates documentation files (CHANGELOG, README, CLAUDE.md)
- Prepare next wave prompts WHILE current wave runs (eliminates spawn latency)

## Session Directory

At session start (Step 0), generate a session ID and create the session artifact directory:

    SESSION_ID=$(date +%s | shasum | head -c 6)
    mkdir -p .beads/agent-summaries/_session-${SESSION_ID}

All session-scoped artifacts go here:
- `boss-bot-state.md` — session state for context recovery
- `orchestrator-state*.md` — orchestrator snapshots
- `step3b-transition-gate.md` — review transition gate
- `HANDOFF-*.md` — handoff documents

The `_session-` prefix distinguishes session directories from epic directories (e.g., `78k/`, `goose-6dh/`).
This prevents collisions when multiple boss-bots run in the same repo.

## Epic Artifact Directories

At Step 2, after selecting epics but before spawning any agents or running Checkpoint A, create all artifact directories for each epic:

    mkdir -p .beads/agent-summaries/<epic-id>/verification/snitch-bot/

This creates the full path (`<epic-id>/` and `verification/snitch-bot/`) in one command. Agents and snitch-bot can then write artifacts immediately without each independently creating directories.

The `review-reports/` subdirectory is created separately at Step 3b (see templates/reviews.md Pre-Spawn Directory Setup).

## Anti-Patterns

- Reading every agent's output files — trust summaries and commit messages
- Spawning agents one at a time — batch by file/priority
- Doing implementation work in boss-bot window — delegate everything
- Re-reading the same metadata — read once, take notes in session state file
- Pushing mid-session — only push at end (atomic deployment)
- Updating docs per-agent — batch all doc updates in Step 4
- Verbose agent prompts — be concise, agents read their own task details via bd show
- Reading implementation.md or checkpoints.md directly — spawn Prompt Factory instead
- Running individual checkpoints per agent — spawn Checkpoint Coordinator as batch
- Composing full agent prompts in boss-bot context — use agent-skeleton.md with data file redirect

## Template Lookup

| Workflow Phase | Read This File |
|----------------|----------------|
| Composing agent prompts (Step 2) | templates/prompt-factory.md |
| Agent skeleton for spawning (Step 2) | templates/agent-skeleton.md |
| Review skeleton for team (Step 3b) | templates/review-skeleton.md |
| Lead skeleton for consolidation (Step 3b) | templates/lead-skeleton.md |
| Post-wave verification (Step 3) | templates/checkpoint-coordinator.md |
| Implementation details (read by Prompt Factory) | templates/implementation.md |
| Checkpoint details (read by Factory/Coordinator) | templates/checkpoints.md |
| Review details (read by Prompt Factory) | templates/reviews.md |
| Analyzing file conflicts (Step 0) | reference/dependency-analysis.md |
| Diagnosing a failure or post-mortem | reference/known-failures.md |
| Creating/recovering boss-bot state file | templates/boss-bot-state.md |
| Setting up orchestration in new project | SETUP.md |

## Retry Limits

| Situation | Max Retries | After Limit |
|-----------|-------------|-------------|
| Agent fails Checkpoint B | 2 | Escalate to user with full context |
| Checkpoint C fails | 1 | Present to user with verification report attached |
| Agent stuck (no commit within 15 turns) | 0 | Check status; escalate to user |
| Total retries per session | 5 | Pause all new spawns; triage with user |

Track retry count in boss-bot state file (→ templates/boss-bot-state.md).

## Priority Calibration

**P1** = build failure, broken links, data loss, security vulnerability

**P2** = visual regression, accessibility issue, functional degradation

**P3** = style, naming, cleanup, polish

Project-specific overrides belong in the project's CLAUDE.md or QUALITY_PROCESS.md.

## Context Preservation Targets

- Token budget: finish with >50% remaining
- File reads in boss-bot: <10 for 40+ task sessions
- Concurrent agents: typical 5-6, max 7
- Commits per session: <20 (batch related work)
