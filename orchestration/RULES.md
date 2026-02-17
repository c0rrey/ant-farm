# Orchestration Rules

## Workflow: "Let's Get to Work"

**Step 0:** Session setup — generate session ID, create session directory,
            create task-metadata subdirectory

**Step 1:** Recon — spawn the Scout with session dir + input mode
            (→ templates/scout.md). Read briefing.md, present strategy to user,
            WAIT for approval

**Step 2:** Spawn — the Pantry composes data files + runs Checkpoint A (→ templates/pantry.md),
then the Queen spawns agents using skeleton (→ templates/dirt-pusher-skeleton.md)

**Step 3:** Monitor — track agent status, Colony TSA runs A.5 + B after wave completes
(→ templates/colony-tsa.md)

**Step 3b:** Review — the Pantry (review mode) composes prompts + Checkpoint A,
the Queen launches team with review skeletons (→ templates/nitpicker-skeleton.md),
Colony TSA (review mode) runs B + C after team completes

**Step 4:** Documentation — update CHANGELOG, README, CLAUDE.md in single commit

**Step 5:** Verify — cross-references valid, all tasks have CHANGELOG entries

**Step 6:** Land the plane — git pull --rebase, bd sync, git push, cleanup artifacts

## Hard Gates

| Gate | Blocks | Artifact |
|------|--------|----------|
| Checkpoint A PASS | Agent/team spawn | .beads/agent-summaries/<epic>/verification/pest-control/*-checkpoint-a-*.md |
| Checkpoint B PASS | Task closure (bd close) | .beads/agent-summaries/<epic>/verification/pest-control/*-checkpoint-b-*.md |
| Checkpoint C PASS | Presenting results to user | .beads/agent-summaries/<epic>/verification/pest-control/*-consolidation-checkpoint-c-*.md |
| Reviews | Mandatory after ALL implementation completes — do NOT ask user, do NOT skip |

## Information Diet (The Queen's Window)

**READ:** briefing.md (from the Scout, in Step 1), git status/log/diff --stat, agent notifications,
commit messages, dirt-pusher-skeleton.md (once per wave), nitpicker-skeleton.md (once per review cycle),
big-head-skeleton.md (once per review cycle), verdict tables from pantry/Colony TSA

**DO NOT READ:** source code, tests, data files, configs, implementation.md, checkpoints.md, reviews.md
(these are read by the Pantry and Colony TSA, not the Queen)

## Concurrency Rules

- Max 7 background agents at any time
- No two agents edit the same file — queue conflicting tasks sequentially
- Each agent runs `git pull --rebase` before committing
- Only the Queen pushes to remote
- Only the Queen updates documentation files (CHANGELOG, README, CLAUDE.md)
- Prepare next wave prompts WHILE current wave runs (eliminates spawn latency)

## Session Directory

At session start (Step 0), generate a session ID and create the session artifact directory:

    SESSION_ID=$(date +%s | shasum | head -c 6)
    mkdir -p .beads/agent-summaries/_session-${SESSION_ID}/task-metadata

All session-scoped artifacts go here:
- `queen-state.md` — session state for context recovery
- `orchestrator-state*.md` — orchestrator snapshots
- `step3b-transition-gate.md` — review transition gate
- `HANDOFF-*.md` — handoff documents

The `_session-` prefix distinguishes session directories from epic directories (e.g., `78k/`, `goose-6dh/`).
This prevents collisions when multiple Queens run in the same repo.

## Epic Artifact Directories

At Step 2, after selecting epics but before spawning any agents or running Checkpoint A, create all artifact directories for each epic:

    mkdir -p .beads/agent-summaries/<epic-id>/verification/pest-control/

This creates the full path (`<epic-id>/` and `verification/pest-control/`) in one command. Agents and Pest Control can then write artifacts immediately without each independently creating directories.

The `review-reports/` subdirectory is created separately at Step 3b (see templates/reviews.md Pre-Spawn Directory Setup).

## Anti-Patterns

- Reading every agent's output files — trust summaries and commit messages
- Spawning agents one at a time — batch by file/priority
- Doing implementation work in the Queen's window — delegate everything
- Re-reading the same metadata — read once, take notes in session state file
- Pushing mid-session — only push at end (atomic deployment)
- Updating docs per-agent — batch all doc updates in Step 4
- Verbose agent prompts — be concise, agents read their own task details from their data file
- Reading implementation.md or checkpoints.md directly — spawn the Pantry instead
- Running bd show in the Queen's window — spawn the Scout instead
- Running individual checkpoints per agent — spawn Colony TSA as batch
- Composing full agent prompts in the Queen's context — use dirt-pusher-skeleton.md with data file redirect

## Template Lookup

| Workflow Phase | Read This File |
|----------------|----------------|
| Composing agent prompts (Step 2) | templates/pantry.md |
| Agent skeleton for spawning (Step 2) | templates/dirt-pusher-skeleton.md |
| Review skeleton for team (Step 3b) | templates/nitpicker-skeleton.md |
| Big Head skeleton for consolidation (Step 3b) | templates/big-head-skeleton.md |
| Post-wave verification (Step 3) | templates/colony-tsa.md |
| Implementation details (read by the Pantry) | templates/implementation.md |
| Checkpoint details (read by Pantry/Colony TSA) | templates/checkpoints.md |
| Review details (read by the Pantry) | templates/reviews.md |
| Pre-flight recon (Step 1) | templates/scout.md |
| Conflict patterns (read by the Scout) | reference/dependency-analysis.md |
| Diagnosing a failure or post-mortem | reference/known-failures.md |
| Creating/recovering the Queen's state file | templates/queen-state.md |
| Setting up orchestration in new project | SETUP.md |

## Retry Limits

| Situation | Max Retries | After Limit |
|-----------|-------------|-------------|
| Agent fails Checkpoint B | 2 | Escalate to user with full context |
| Checkpoint C fails | 1 | Present to user with verification report attached |
| Agent stuck (no commit within 15 turns) | 0 | Check status; escalate to user |
| Total retries per session | 5 | Pause all new spawns; triage with user |

Track retry count in the Queen's state file (→ templates/queen-state.md).

## Priority Calibration

**P1** = build failure, broken links, data loss, security vulnerability

**P2** = visual regression, accessibility issue, functional degradation

**P3** = style, naming, cleanup, polish

Project-specific overrides belong in the project's CLAUDE.md or QUALITY_PROCESS.md.

## Context Preservation Targets

- Token budget: finish with >50% remaining
- File reads in the Queen: <10 for 40+ task sessions
- Concurrent agents: typical 5-6, max 7
- Commits per session: <20 (batch related work)
