# Orchestration Rules

## Queen Prohibitions (read FIRST)

- **NEVER** run `bd show`, `bd ready`, `bd list`, `bd blocked`, or any `bd` query command — the Scout does this
- **NEVER** read source code, tests, data files, or config files — agents do this
- **NEVER** read agent template files (scout.md, pantry.md, etc.) — pass the path to the agent, let it read its own instructions

Your first instinct will be to "gather context" by running `bd show` on the task list.
**Do not do this.** Spawn the Scout and let it gather context for you.

## Workflow: "Let's Get to Work"

**Step 0:** Session setup — generate session ID, create session directory +
            task-metadata subdirectory. Then immediately proceed to Step 1.
            Do NOT examine, read, or query any task/issue details.

**Step 1:** Recon — spawn the Scout (`scout-organizer` subagent). Pass it:
            (1) session dir path, (2) input mode + task list,
            (3) the path `~/.claude/orchestration/templates/scout.md` as its
            instruction file. Do NOT read the scout template yourself.
            Do NOT run `bd show`, `bd ready`, `bd blocked`, or any other `bd`
            commands — the Scout handles all task discovery and metadata
            gathering. WAIT for the Scout to return its briefing verdict,
            then present the recommended strategy to the user for approval.

**Step 2:** Spawn — create epic artifact dirs (from briefing Epics line).
            Spawn the Pantry for data files + combined previews
            (→ templates/pantry.md). Spawn Pest Control (`code-reviewer`) for Colony Cartography Office (CCO)
            (pass preview file paths, Pest Control reads checkpoints.md itself).
            Only after all CCO PASS: spawn agents using skeleton
            (→ templates/dirt-pusher-skeleton.md, using Agent Type from Pantry verdict table).
            Prepare next wave (Pantry + Pest Control) WHILE current wave runs.

**Step 3:** Verify — after each agent commits, spawn Pest Control for Wandering Worker Detection (WWD)
            (scope check before next agent in the wave can proceed).
            After the full wave completes, spawn Pest Control for Dirt Moved vs Dirt Claimed (DMVDC)
            (pass task IDs, commit hashes, summary doc paths; Pest Control reads
            checkpoints.md + task-metadata/ + git diffs itself).
            Failed DMVDC → resume agent (max 2 retries).

**Step 3b:** Review — spawn the Pantry (review mode) for review prompts + previews.
             Spawn Pest Control for CCO on review previews.
             Create Nitpicker team with 5 members: 4 reviewers
             (→ templates/nitpicker-skeleton.md) + Big Head
             (→ templates/big-head-skeleton.md). Big Head MUST be a team
             member, NOT a separate Task agent.
             After team completes, spawn Pest Control for DMVDC + Colony Census Bureau (CCB)
             (pass report paths; Pest Control reads checkpoints.md itself).

**Step 4:** Documentation — update CHANGELOG, README, CLAUDE.md in single commit

**Step 5:** Verify — cross-references valid, all tasks have CHANGELOG entries

**Step 6:** Land the plane — git pull --rebase, bd sync, git push, cleanup artifacts

## Hard Gates

| Gate | Blocks | Artifact |
|------|--------|----------|
| CCO PASS | Agent/team spawn | .beads/agent-summaries/<epic>/verification/pc/*-cco-*.md |
| WWD PASS | Next agent in wave | .beads/agent-summaries/<epic>/verification/pc/*-wwd-*.md |
| DMVDC PASS | Task closure (bd close) | .beads/agent-summaries/<epic>/verification/pc/*-dmvdc-*.md |
| CCB PASS | Presenting results to user | .beads/agent-summaries/<epic>/verification/pc/*-ccb-*.md |
| Reviews | Mandatory after ALL implementation completes — do NOT ask user, do NOT skip |

## Information Diet (The Queen's Window)

**READ:** briefing.md (from the Scout, in Step 1), git status/log/diff --stat, agent notifications,
commit messages, dirt-pusher-skeleton.md (once per wave), nitpicker-skeleton.md (once per review cycle),
big-head-skeleton.md (once per review cycle), verdict tables from the Pantry and Pest Control

**DO NOT READ:** source code, tests, data files, configs, implementation.md, checkpoints.md, reviews.md,
bd show/ready/blocked output, agent template files (scout.md, pantry.md, etc.)
— these are agent inputs, not Queen inputs. The Pantry, Pest Control, and Scout read them.

## Agent Types

| Agent | subagent_type | Rationale |
|-------|---------------|-----------|
| Scout | `scout-organizer` | Custom agent: agent-organizer + Bash for bd CLI |
| Pantry | `general-purpose` | Needs file reads + writes |
| Pest Control | `code-reviewer` | Audits diffs, cross-checks claims against code |
| Dirt Pushers | from Pantry verdict table | Specialist per task (see pantry.md selection tables) |
| Nitpickers | `code-reviewer` | Fixed in nitpicker-skeleton.md |
| Big Head | `code-reviewer` | Fixed in big-head-skeleton.md |

## Concurrency Rules

- Max 7 Dirt Pushers concurrent
- Max 10 total agents (Dirt Pushers + support agents: Pantry, Pest Control, Scout)
- No two agents edit the same file — queue conflicting tasks sequentially
- Each agent runs `git pull --rebase` before committing
- Only the Queen pushes to remote
- Only the Queen updates documentation files (CHANGELOG, README, CLAUDE.md)
- Prepare next wave prompts WHILE current wave runs (eliminates spawn latency)

## Session Directory

At session start (Step 0), generate a session ID and create the session artifact directory:

    SESSION_ID=$(date +%s | shasum | head -c 6)
    mkdir -p .beads/agent-summaries/_session-${SESSION_ID}/{task-metadata,previews}

All session-scoped artifacts go here:
- `queen-state.md` — session state for context recovery
- `orchestrator-state*.md` — orchestrator snapshots
- `step3b-transition-gate.md` — review transition gate
- `HANDOFF-*.md` — handoff documents

The `_session-` prefix distinguishes session directories from epic directories (e.g., `78k/`, `goose-6dh/`).
This prevents collisions when multiple Queens run in the same repo.

## Epic Artifact Directories

At Step 2, after the user approves a strategy but before spawning any agents or running CCO, create artifact directories for each epic listed in the Scout's briefing (Metadata → Epics line):

    mkdir -p .beads/agent-summaries/<epic-id>/verification/pc/

Tasks not belonging to any epic use `_standalone` as the epic-id:

    mkdir -p .beads/agent-summaries/_standalone/verification/pc/

The `_standalone` directory persists across sessions (it is NOT cleaned up with `_session-*` artifacts).

This creates the full path (`<epic-id>/` and `verification/pc/`) in one command. Agents and Pest Control can then write artifacts immediately without each independently creating directories.

The `review-reports/` subdirectory is created separately at Step 3b (see templates/reviews.md Pre-Spawn Directory Setup).

## Anti-Patterns

- Reading every agent's output files — trust summaries and commit messages
- Spawning agents one at a time — batch by file/priority
- Doing implementation work in the Queen's window — delegate everything
- Re-reading the same metadata — read once, take notes in session state file
- Pushing mid-session — only push at end (atomic deployment)
- Updating docs per-agent — batch all doc updates in Step 4
- Verbose agent prompts — be concise, agents read their own task details from their data file
- Reading implementation.md or checkpoints.md directly — the Pantry and Pest Control read these
- Running bd show, bd ready, or bd list before spawning the Scout — all task discovery belongs to Step 1, which the Scout owns
- Reading agent template files (scout.md, dirt-pusher-skeleton.md, etc.) in the Queen's window — pass the path to the agent, let it read its own instructions
- Running individual checkpoints per agent — spawn one Pest Control with the full batch
- Composing full agent prompts in the Queen's context — use dirt-pusher-skeleton.md with data file redirect

## Template Lookup

| Workflow Phase | Read This File |
|----------------|----------------|
| Composing agent prompts (Step 2) | templates/pantry.md |
| Agent skeleton for spawning (Step 2) | templates/dirt-pusher-skeleton.md |
| Review skeleton for team (Step 3b) | templates/nitpicker-skeleton.md |
| Big Head skeleton for consolidation (Step 3b) | templates/big-head-skeleton.md |
| Implementation details (read by the Pantry) | templates/implementation.md |
| Checkpoint details (read by Pest Control) | templates/checkpoints.md |
| Review details (read by the Pantry) | templates/reviews.md |
| Pre-flight recon (Step 1) | templates/scout.md |
| Conflict patterns (read by the Scout) | reference/dependency-analysis.md |
| Diagnosing a failure or post-mortem | reference/known-failures.md |
| Creating/recovering the Queen's state file | templates/queen-state.md |
| Setting up orchestration in new project | SETUP.md |

## Retry Limits

| Situation | Max Retries | After Limit |
|-----------|-------------|-------------|
| Agent fails DMVDC | 2 | Escalate to user with full context |
| CCB fails | 1 | Present to user with verification report attached |
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
- Concurrent agents: typical 5-6 Dirt Pushers, max 10 total
- Commits per session: <20 (batch related work)
