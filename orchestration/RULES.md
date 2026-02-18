# Orchestration Rules

## Path Reference Convention

All file paths in this document use **repo-root relative** format: `orchestration/templates/scout.md`.

When code runs at runtime, agent files are synced to `~/.claude/agents/` and orchestration files are
accessible at `~/.claude/orchestration/templates/scout.md`. To translate repo paths to runtime paths:
- Replace `orchestration/` with `~/.claude/orchestration/`
- Replace `agents/` with `~/.claude/agents/`

**In-document shorthand** (e.g., "templates/scout.md") is informal and always refers to the repo-root path with the `orchestration/` prefix implied.

## Queen Prohibitions (read FIRST)

- **NEVER** run `bd show`, `bd ready`, `bd list`, `bd blocked`, or any `bd` query command — the Scout does this
- **NEVER** read source code, tests, project data files, or config files — agents do this
- **NEVER** read agent **instruction files** (scout.md, pantry.md, implementation.md, checkpoints.md, reviews.md, etc.) — pass the path to the agent, let it read its own instructions

Your first instinct will be to "gather context" by running `bd show` on the task list.
**Do not do this.** Spawn the Scout and let it gather context for you.

## Queen Read Permissions

The Queen's window is restricted to prevent context bloat, but certain files are explicitly PERMITTED.

**PERMITTED (Queen must read these):**
- `{SESSION_DIR}/briefing.md` — Scout-generated strategy summary, required for Step 1 approval decision
- `{SESSION_DIR}/task-metadata/*.md` — Per-task scope, acceptance criteria (pre-digested by Scout)
- `{SESSION_DIR}/previews/*.md` — Combined prompt previews (pre-digested by Pantry)
- `{SESSION_DIR}/review-reports/*.md` — Individual reviewer reports and Big Head consolidated summary
- Verdict tables from Pantry and Pest Control — CCO, WWD, DMVDC, CCB verdicts
- Commit messages and git status/log/diff --stat output
- Agent notifications (as they complete)

**PERMITTED (Queen reads once per phase, for context only):**
- `orchestration/templates/dirt-pusher-skeleton.md` — Once per implementation wave (skeleton structure)
- `orchestration/templates/nitpicker-skeleton.md` — Once per review cycle (skeleton structure)
- `orchestration/templates/big-head-skeleton.md` — Once per review cycle (skeleton structure)
- Project's `CLAUDE.md` — Global project rules

**FORBIDDEN (agents read; Queen never reads):**
- `orchestration/templates/scout.md` — Scout's instruction file
- `orchestration/templates/pantry.md` — Pantry's instruction file
- `orchestration/templates/implementation.md` — Implementation details (read by Pantry)
- `orchestration/templates/checkpoints.md` — Checkpoint definitions (read by Pest Control)
- `orchestration/templates/reviews.md` — Review protocol (read by Pantry in review mode)
- `orchestration/reference/dependency-analysis.md` — Used by Scout for conflict analysis
- `orchestration/reference/known-failures.md` — Reference material; for post-mortem only
- Source code files, tests, project configs, application data files
- Raw `bd show`, `bd ready`, `bd blocked`, `bd list` output (let the Scout digest this)

## Workflow: "Let's Get to Work"

**Step 0:** Session setup — run the commands in the Session Directory section below to
            generate SESSION_ID and SESSION_DIR. Store both as variables in your context.
            Then immediately proceed to Step 1.
            Do NOT examine, read, or query any task/issue details.

**Step 1:** Recon — Read `{SESSION_DIR}/briefing.md` written by the Scout's previous run, or spawn the Scout
            (`scout-organizer` subagent) if this is the first session. Include in Scout's prompt:
            (1) `Session directory: <value of SESSION_DIR>`,
            (2) `Mode: <mode>` — derive from the user's message:
                - User specifies an epic → `epic <epic-id>`
                - User lists specific tasks → `tasks <id1>, <id2>, ...`
                - User describes a filter → `filter <description>`
                - User gives no specific scope (e.g., just "let's get to work") → `ready`
            (3) the path `orchestration/templates/scout.md` as its instruction file.
            Do NOT read the scout template yourself. Do NOT run `bd show`, `bd ready`, `bd blocked`,
            or any other `bd` commands — the Scout handles all task discovery and metadata gathering.
            WAIT for the Scout to return its briefing verdict (written to `{SESSION_DIR}/briefing.md`),
            then present the recommended strategy to the user for approval.

**Step 2:** Spawn — Spawn the Pantry (`pantry-impl`) for task briefs + combined previews
            (→ orchestration/templates/pantry.md). Include `Session directory: <value of SESSION_DIR>`
            in Pantry's prompt. Pass preview file paths and SESSION_DIR to Pest Control
            (`pest-control`) for Colony Cartography Office (CCO); Pest Control reads orchestration/templates/checkpoints.md itself.
            Only after all CCO PASS: spawn agents using skeleton
            (→ orchestration/templates/dirt-pusher-skeleton.md, using Agent Type from Pantry verdict table).
            Prepare next wave (Pantry + Pest Control) WHILE current wave runs.

**Step 3:** Verify — after each agent commits, spawn Pest Control for Wandering Worker Detection (WWD)
            (scope check before next agent in the wave can proceed).
            After the full wave completes, spawn Pest Control for Dirt Moved vs Dirt Claimed (DMVDC)
            (pass task IDs, commit hashes, summary doc paths; Pest Control reads
            checkpoints.md + task-metadata/ + git diffs itself).
            Failed DMVDC → resume agent (max 2 retries).

**Step 3b:** Review — pre-spawn directory setup:
              `mkdir -p ${SESSION_DIR}/review-reports`
            Gather review inputs from the Queen's state file:
            - Commit range: first commit of the session through HEAD
            - File list: `git diff --name-only <first-session-commit>..HEAD` (deduplicated)
            - Task IDs: all task IDs worked on this session (from Queen's state file)
            - Epic IDs: all epics worked on this session (for context only)
            Then: spawn the Pantry (`pantry-review`) for review prompts + previews.
            Spawn Pest Control for CCO on review previews.
            Create Nitpicker team with 5 members: 4 reviewers
            (→ orchestration/templates/nitpicker-skeleton.md) + Big Head
            (→ orchestration/templates/big-head-skeleton.md). Big Head MUST be a team
            member, NOT a separate Task agent.
            After team completes, spawn Pest Control for DMVDC + Colony Census Bureau (CCB)
            (pass report paths; Pest Control reads orchestration/templates/checkpoints.md itself).

**Step 3c:** User triage on P1/P2 findings — **MANDATORY if P1 or P2 issues found; SKIP if none**.
            After CCB PASS (and reviews.md Big Head consolidation completes):
            1. Read the consolidated review summary (written to {session-dir}/review-reports/)
            2. Present findings to user with priority breakdown (P1 count, P2 count, P3 count)
            3. Ask user: "Reviews found X P1 and Y P2 issues. Should we fix them now, or push and address later?"
            - **If "fix now"**: Follow orchestration/templates/reviews.md L485-514 (test-writing + fix workflow)
            - **If "push and address later"**: P1/P2 beads stay open; document in CHANGELOG; proceed to Step 4
            - **If no P1/P2 issues**: Skip to Step 4 directly

**Step 4:** Documentation — update CHANGELOG, README, CLAUDE.md in single commit

**Step 5:** Verify — cross-references valid, all tasks have CHANGELOG entries

**Step 6:** Land the plane — git pull --rebase, bd sync, git push, clean up stashes and remote branches

## Hard Gates

| Gate | Blocks | Artifact |
|------|--------|----------|
| CCO PASS (impl) | Agent spawn | ${SESSION_DIR}/pc/*-cco-*.md |
| CCO PASS (review) | Nitpicker team spawn | ${SESSION_DIR}/pc/pc-session-cco-review-{timestamp}.md |
| WWD PASS | Next agent in wave | ${SESSION_DIR}/pc/*-wwd-*.md |
| DMVDC PASS | Task closure (bd close) | ${SESSION_DIR}/pc/*-dmvdc-*.md |
| CCB PASS | Presenting results | ${SESSION_DIR}/pc/pc-session-ccb-{timestamp}.md |
| Reviews | Mandatory after ALL implementation completes — do NOT ask user, do NOT skip |

## Information Diet (The Queen's Window)

The Queen's read permissions are defined explicitly in the "Queen Read Permissions" section above.

**Quick summary**:
- **READ**: Briefing, verdict tables, skeleton files, orchestration artifacts from session dir, git log
- **DO NOT READ**: Agent instruction files, source code, tests, configs, implementation details
- **Permitted**: Pre-digested artifacts written by Pantry/Scout to session directories

For the complete detailed list and rationale, see "Queen Read Permissions" above.

## Agent Types

| Agent | subagent_type | Rationale |
|-------|---------------|-----------|
| Scout | `scout-organizer` | Custom agent: agent-organizer + Bash for bd CLI |
| Pantry (impl) | `pantry-impl` | Custom agent: CCO-aligned implementation prompt composer |
| Pantry (review) | `pantry-review` | Custom agent: CCO-aligned review prompt composer |
| Pest Control | `pest-control` | Custom agent: verification auditor, catches fabrication + scope creep |
| Dirt Pushers | from Pantry verdict table | Specialist per task — Scout recommends via dynamic agent discovery, Pantry passes through |
| Nitpickers | `nitpicker` | Custom agent: file:line specificity, calibrated severity, complete coverage |
| Big Head | `big-head` | Custom agent: deduplication, root-cause grouping, issue filing |

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
    SESSION_DIR=".beads/agent-summaries/_session-${SESSION_ID}"
    mkdir -p ${SESSION_DIR}/{task-metadata,previews,prompts,pc,summaries}

Store SESSION_DIR in your context. Pass it explicitly to every agent that needs to write artifacts:
Scout receives it as "Session directory: <SESSION_DIR>".
Pantry receives it as "Session directory: <SESSION_DIR>".
Pest Control receives it as "Session directory: <SESSION_DIR>" (when writing checkpoint artifacts).

All session-scoped artifacts go here:
- `queen-state.md` — session state for context recovery
- `orchestrator-state*.md` — orchestrator snapshots
- `step3b-transition-gate.md` — review transition gate
- `HANDOFF-*.md` — handoff documents

The `_session-` prefix distinguishes session directories from other entries in `agent-summaries/`.
This prevents collisions when multiple Queens run in the same repo.

## Anti-Patterns

- Reading every agent's output files — trust summaries and commit messages
- Spawning agents one at a time — batch by file/priority
- Doing implementation work in the Queen's window — delegate everything
- Re-reading the same metadata — read once, take notes in session state file
- Pushing mid-session — only push at end (atomic deployment)
- Updating docs per-agent — batch all doc updates in Step 4
- Verbose agent prompts — be concise, agents read their own task details from their task brief
- Reading implementation.md or checkpoints.md directly — the Pantry and Pest Control read these
- Running bd show, bd ready, or bd list before spawning the Scout — all task discovery belongs to Step 1, which the Scout owns
- Reading agent template files (scout.md, dirt-pusher-skeleton.md, etc.) in the Queen's window — pass the path to the agent, let it read its own instructions
- Running individual checkpoints per agent — spawn one Pest Control with the full batch
- Composing full agent prompts in the Queen's context — use dirt-pusher-skeleton.md with task brief redirect

## Template Lookup

| Workflow Phase | Read This File |
|----------------|----------------|
| Composing agent prompts (Step 2) | orchestration/templates/pantry.md |
| Agent skeleton for spawning (Step 2) | orchestration/templates/dirt-pusher-skeleton.md |
| Review skeleton for team (Step 3b) | orchestration/templates/nitpicker-skeleton.md |
| Big Head skeleton for consolidation (Step 3b) | orchestration/templates/big-head-skeleton.md |
| Implementation details (read by the Pantry) | orchestration/templates/implementation.md |
| Checkpoint details (read by Pest Control) | orchestration/templates/checkpoints.md |
| Review details (read by the Pantry) | orchestration/templates/reviews.md |
| Pre-flight recon (Step 1) | orchestration/templates/scout.md |
| Conflict patterns (read by the Scout) | orchestration/reference/dependency-analysis.md |
| Diagnosing a failure or post-mortem | orchestration/reference/known-failures.md |
| Creating/recovering the Queen's state file | orchestration/templates/queen-state.md |
| Setting up orchestration in new project | orchestration/SETUP.md |

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
