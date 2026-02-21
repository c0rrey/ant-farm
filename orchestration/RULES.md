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
- `orchestration/templates/dirt-pusher-skeleton.md` — Once per implementation wave (skeleton structure; see [Glossary: wave](GLOSSARY.md#workflow-concepts))
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
- `orchestration/_archive/*` — Deprecated documents; stale instructions that contradict current workflows. **No agent should read these.**
- Source code files, tests, project configs, application data files
- Raw `bd show`, `bd ready`, `bd blocked`, `bd list` output (let the Scout digest this)

## Workflow: "Let's Get to Work"

**Step 0:** Session setup — run the commands in the Session Directory section below to
            generate SESSION_ID and SESSION_DIR. Store both as variables in your context.
            Then immediately proceed to Step 1.
            Do NOT examine, read, or query any task/issue details.
            **Progress log:** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SESSION_INIT|complete|session_dir=${SESSION_DIR}" >> ${SESSION_DIR}/progress.log`

            **Crash recovery detection (run BEFORE generating a new SESSION_ID):**
            Check whether the user's message contains a session directory path
            (e.g. `.beads/agent-summaries/_session-<id>`). If a prior SESSION_DIR is
            supplied or you can identify an incomplete session from context:
            1. Run `bash scripts/parse-progress-log.sh <prior_SESSION_DIR>`
            2. On exit 0: read `<prior_SESSION_DIR>/resume-plan.md` and present it verbatim to the user.
               Wait for the user to reply `resume` or `fresh start` before taking any further action.
               - `resume`: restore SESSION_DIR to the prior value and continue from the indicated step.
               - `fresh start`: generate a new SESSION_ID and proceed normally.
            3. On exit 2: the prior session completed — proceed normally with a new SESSION_ID.
            4. On exit 1: surface the error to the user and await instruction.
            If no prior session is indicated, skip crash recovery and proceed normally.

**Step 1:** Recon — Read `{SESSION_DIR}/briefing.md` written by the Scout's previous run, or spawn the Scout
            (`scout-organizer` subagent, `model: "opus"`) if this is the first session. Include in Scout's prompt:
            (1) `Session directory: <value of SESSION_DIR>`,
            (2) `Mode: <mode>` — derive from the user's message:
                - User specifies an epic → `epic <epic-id>`
                - User lists specific tasks → `tasks <id1>, <id2>, ...`
                - User describes a filter → `filter <description>`
                - User gives no specific scope (e.g., just "let's get to work") → `ready`
            (3) the path `orchestration/templates/scout.md` as its instruction file.
            Do NOT read the scout template yourself. Do NOT run `bd show`, `bd ready`, `bd blocked`,
            or any other `bd` commands — the Scout handles all task discovery and metadata gathering.
            WAIT for the Scout to return its briefing verdict (written to `{SESSION_DIR}/briefing.md`).

**Step 1b:** SSV gate — After Scout writes `{SESSION_DIR}/briefing.md`, spawn Pest Control
            (`pest-control`, `model: "haiku"`) for Scout Strategy Verification (SSV) before presenting to user.
            Pass `Session directory: <value of SESSION_DIR>` and the path `orchestration/templates/checkpoints.md`
            as its instruction file. Pest Control reads `{SESSION_DIR}/briefing.md` itself and runs all three
            mechanical checks (file overlap within waves, file list match against beads, intra-wave dependency
            ordering). **SSV must PASS before proceeding.**

            **On SSV PASS**: Present the recommended strategy to the user for approval.
            **On SSV FAIL**: Re-run Scout with the specific violations from the SSV report (do NOT present
            a failed strategy to the user). After Scout revises briefing.md, re-run SSV.

            **Progress log (after SSV PASS and user approves strategy):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SCOUT_COMPLETE|briefing=${SESSION_DIR}/briefing.md|ssv=pass|tasks_approved=<N>" >> ${SESSION_DIR}/progress.log`

**Step 2:** Spawn — Spawn the Pantry (`pantry-impl`, `model: "opus"`) for task briefs + combined previews
            (→ orchestration/templates/pantry.md, Section 1). Include `Session directory: <value of SESSION_DIR>`
            in Pantry's prompt. Pass preview file paths and SESSION_DIR to Pest Control
            (`pest-control`, `model: "haiku"`) for Colony Cartography Office (CCO); Pest Control reads orchestration/templates/checkpoints.md itself.
            Only after all CCO PASS: spawn agents using skeleton
            (→ orchestration/templates/dirt-pusher-skeleton.md, using Agent Type from Pantry verdict table, `model: "sonnet"` for all Dirt Pushers regardless of subagent_type).
            **Wave pipelining**: When spawning wave N Dirt Pushers, include the wave N+1 Pantry
            (`pantry-impl`, `model: "opus"`) in the SAME message so they launch concurrently.
            The Pantry reads from task-metadata (written by Scout) and has no dependency on wave N's output.
            This eliminates the idle gap between waves. The flow per wave boundary:
            1. Wave N CCO PASS → spawn wave N Dirt Pushers + wave N+1 Pantry (single message)
            2. Wave N+1 Pantry returns → spawn wave N+1 CCO
            3. Wave N Dirt Pushers finish → run WWD/DMVDC (Step 3)
            4. Wave N+1 CCO PASS + wave N verification done → spawn wave N+1 Dirt Pushers + wave N+2 Pantry
            For the final wave (no wave N+1), skip the Pantry — just spawn Dirt Pushers alone.
            **Progress log (after each wave's Dirt Pushers are spawned):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|WAVE_SPAWNED|wave=<N>|spawned=<agent-ids>|previews_dir=${SESSION_DIR}/previews" >> ${SESSION_DIR}/progress.log`

**Step 3:** Verify — after each agent commits, spawn Pest Control (`model: "haiku"`) for Wandering Worker Detection (WWD)
            (scope check before next agent in the wave can proceed).
            After the full wave completes, spawn Pest Control (`model: "sonnet"`) for Dirt Moved vs Dirt Claimed (DMVDC)
            (pass task IDs, commit hashes, summary doc paths; Pest Control reads
            checkpoints.md + task-metadata/ + git diffs itself).
            Failed DMVDC → resume agent (max 2 retries).
            **Progress log (after DMVDC PASS for each wave):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|WAVE_VERIFIED|wave=<N>|dmvdc=pass|tasks_verified=<ids>|commits=<hashes>" >> ${SESSION_DIR}/progress.log`

**Step 3b:** Review — fill review slots and spawn Nitpickers.

            **3b-i. Gather inputs** from the Queen's state file:
            - Review round: read from session state (default: 1)
            - Commit range: round 1 = first session commit..HEAD; round 2+ = first fix commit..HEAD
            - File list: `git diff --name-only <commit-range>` (deduplicated)
            - Task IDs: round 1 = all task IDs; round 2+ = fix task IDs only
            - Timestamp: The Queen generates ONE timestamp at the start of Step 3b using `date +%Y%m%d-%H%M%S` format (YYYYMMDD-HHMMSS).
              This shell variable corresponds to the canonical `{REVIEW_TIMESTAMP}` placeholder defined in
              `orchestration/PLACEHOLDER_CONVENTIONS.md` (Tier 1 uppercase). Use `${TIMESTAMP}` in bash
              code blocks; use `{REVIEW_TIMESTAMP}` when referencing the placeholder in prose or templates.
              ```bash
              TIMESTAMP=$(date +%Y%m%d-%H%M%S)
              ```

            **3b-i.5. Validate review inputs** before proceeding:
            ```bash
            # REVIEW_ROUND: must be a positive integer
            if ! echo "${REVIEW_ROUND}" | grep -qE '^[1-9][0-9]*$'; then
              echo "ERROR: REVIEW_ROUND is missing or non-numeric (got: '${REVIEW_ROUND}'). Expected: integer >= 1." >&2
              exit 1
            fi

            # CHANGED_FILES: must be non-empty (at least one changed file)
            if [ -z "$(echo "${CHANGED_FILES}" | tr -s ' \n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')" ]; then
              echo "ERROR: CHANGED_FILES is empty. git diff returned no files for the commit range. Verify the commit range contains actual changes." >&2
              exit 1
            fi

            # TASK_IDS: must be non-empty (at least one task ID)
            if [ -z "$(echo "${TASK_IDS}" | tr -s ' \n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')" ]; then
              echo "ERROR: TASK_IDS is empty. Round 1 requires all task IDs; round 2+ requires fix task IDs. Verify session state is populated." >&2
              exit 1
            fi
            ```
            On any validation failure: surface the error to the user and do NOT proceed to 3b-ii.

            **3b-ii. Fill review slots** (NO Pantry spawn — skeletons were assembled in Step 2):
            ```bash
            bash ~/.claude/orchestration/scripts/fill-review-slots.sh \
              "${SESSION_DIR}" "<commit-range>" "<changed-files>" \
              "<task-IDs>" "<timestamp>" "<round>"
            ```
            On exit 0: prompts/previews written to `${SESSION_DIR}/prompts/` and `${SESSION_DIR}/previews/`.
            On non-zero: surface stderr to user — do NOT proceed.

            **3b-iii. CCO gate**: `mkdir -p "${SESSION_DIR}"/review-reports`, then spawn
            Pest Control (`model: "haiku"`) for CCO on review previews. Must PASS before spawning team.

            **3b-iv. Spawn Nitpicker team**:
            - Round 1: 6 members — 4 reviewers + Big Head + Pest Control
            - Round 2+: 4 members — 2 reviewers (Correctness + Edge Cases) + Big Head + Pest Control
            - Big Head MUST be a team member, NOT a separate Task agent
            - Pest Control MUST be a team member so Big Head can SendMessage to it
            - Templates: `nitpicker-skeleton.md`, `big-head-skeleton.md`
            - After team completes, DMVDC and CCB have already run inside the team

            **3b-v. Spawn dummy reviewer** (context usage instrumentation — sunset after ~30 sessions):
            The dummy reviewer mirrors the correctness reviewer to produce empirical context-usage data.
            Its report is discarded — Big Head does NOT read or consolidate it.

            Step 1: Copy the correctness prompt as the dummy data file:
            ```bash
            cp "${SESSION_DIR}/prompts/review-correctness.md" \
               "${SESSION_DIR}/prompts/review-dummy.md"
            ```

            Step 2: Launch a new tmux window for the dummy reviewer:
            ```bash
            # TIMESTAMP was assigned at the start of Step 3b-i: TIMESTAMP=$(date +%Y%m%d-%H%M%S)
            # TMUX_SESSION is the name of the tmux session the Queen is running in.
            # Resolve it at runtime: TMUX_SESSION=$(tmux display-message -p '#S')
            if [ -n "$TMUX" ]; then
              TMUX_SESSION=$(tmux display-message -p '#S')
              DUMMY_WINDOW="dummy-reviewer-round-<N>"

              tmux new-window -t "${TMUX_SESSION}" -n "${DUMMY_WINDOW}"
              tmux send-keys -t "${TMUX_SESSION}:${DUMMY_WINDOW}" \
                "cd $(pwd) && claude" Enter
              sleep 5
              tmux send-keys -t "${TMUX_SESSION}:${DUMMY_WINDOW}" \
                "Perform a correctness review of the completed work. Step 0: Read your full review brief from ${SESSION_DIR}/prompts/review-dummy.md (Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions.) Follow the instructions in the brief exactly, including the report format and output path. Write your report to ${SESSION_DIR}/review-reports/dummy-review-${TIMESTAMP}.md" Enter
            fi
            ```

            Notes:
            - Replace `<N>` in `DUMMY_WINDOW` with the actual round number.
            - The dummy reviewer runs in its own tmux pane; the user observes context usage via the Claude Code UI.
            - The dummy reviewer's report path (`dummy-review-${TIMESTAMP}.md`) is intentionally excluded from the Big Head consolidation brief and from all CCB/DMVDC checks — it is measurement-only.
            - Do NOT wait for the dummy reviewer to finish before proceeding with Step 3c. It runs concurrently.
            - Sunset clause: remove Step 3b-v after ~30 sessions of data collection or when a reliable file-budget threshold is established. Removal has no effect on the rest of the review workflow.

            **Progress log (after Nitpicker team completes):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_COMPLETE|round=<N>|team=complete|report=${SESSION_DIR}/review-reports/review-consolidated-${TIMESTAMP}.md" >> ${SESSION_DIR}/progress.log`

**Step 3c:** User triage — **after CCB PASS and Big Head consolidation completes**:
            1. Read the consolidated review summary
            2. Check finding counts: P1, P2, P3
            **Termination check**: If zero P1 and zero P2 findings:
            - Round 2+: P3s already auto-filed by Big Head to "Future Work" epic
            - Round 1: P3s filed via "Handle P3 Issues" flow in reviews.md
            - Update session state: `Termination: terminated (round N: 0 P1/P2)`
            - Proceed directly to Step 4 (documentation)
            **If P1 or P2 issues found**:
            **Round cap — escalate after round 4** (check this FIRST before any fix decision):
            - If current round >= 4 and P1/P2 findings are still present, do NOT start another round
            - Present full round history to user (round numbers, finding counts, bead IDs)
            - Ask user: "Review loop has not converged after 4 rounds. Continue or abort?"
            - Await user decision before taking any further action
            **Only if current round < 4**: proceed with fix-now/defer decision:
            - Present findings to user: "Reviews found X P1 and Y P2 issues. Fix now or defer?"
            - **If "fix now"**: Spawn fix tasks (see reviews.md), then re-run Step 3b with round N+1
              - Update session state: increment review round, record fix commit range
            - **If "defer"**: P1/P2 beads stay open; document in CHANGELOG; proceed to Step 4
            **Progress log (after triage decision):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_TRIAGED|round=<N>|p1=<count>|p2=<count>|decision=<fix_now|defer|terminated>" >> ${SESSION_DIR}/progress.log`

**Step 4:** Documentation — update CHANGELOG, README, CLAUDE.md in single commit
            **Progress log (after doc commit):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|DOCS_COMMITTED|complete|commit=<hash>" >> ${SESSION_DIR}/progress.log`

**Step 5:** Verify — cross-references valid, all tasks have CHANGELOG entries
            **Progress log (after cross-reference check):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|XREF_VERIFIED|complete|tasks_with_changelog=<ids>" >> ${SESSION_DIR}/progress.log`

**Step 6:** Land the plane — git pull --rebase, bd sync, git push, clean up stashes and remote branches
            **Progress log (after git push succeeds):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SESSION_COMPLETE|pushed=true" >> ${SESSION_DIR}/progress.log`

## Hard Gates

| Gate | Blocks | Artifact |
|------|--------|----------|
| SSV PASS | Pantry spawn (and all downstream steps) | ${SESSION_DIR}/pc/pc-session-ssv-{timestamp}.md |
| CCO PASS (impl) | Agent spawn | ${SESSION_DIR}/pc/*-cco-*.md |
| CCO PASS (review) | Nitpicker team spawn | ${SESSION_DIR}/pc/pc-session-cco-review-{timestamp}.md |
| WWD PASS | Next agent in wave | ${SESSION_DIR}/pc/*-wwd-*.md |
| DMVDC PASS | Task closure (bd close) | ${SESSION_DIR}/pc/*-dmvdc-*.md |
| CCB PASS | Presenting results | ${SESSION_DIR}/pc/pc-session-ccb-{timestamp}.md |
| Reviews | Mandatory after ALL implementation completes; re-runs after fix cycles with reduced scope (round 2+) |

## Information Diet (The Queen's Window)

The Queen's read permissions are defined explicitly in the "Queen Read Permissions" section above.

**Quick summary**:
- **READ**: Briefing, verdict tables, skeleton files, orchestration artifacts from session dir, git log
- **DO NOT READ**: Agent instruction files, source code, tests, configs, implementation details
- **NEVER READ**: `orchestration/_archive/` — contains deprecated documents that contradict current workflows. A glob like `orchestration/**/*.md` will match these stale files. Exclude `_archive/` from all searches and reads.
- **Permitted**: Pre-digested artifacts written by Pantry/Scout to session directories

For the complete detailed list and rationale, see "Queen Read Permissions" above.

## Agent Types

| Agent | subagent_type | Rationale |
|-------|---------------|-----------|
| Scout | `scout-organizer` | Custom agent: agent-organizer + Bash for bd CLI |
| Pantry (impl) | `pantry-impl` | Custom agent: CCO-aligned implementation prompt composer (also assembles review skeletons via compose-review-skeletons.sh) |
| Pest Control | `pest-control` | Custom agent: verification auditor, catches fabrication + scope creep |
| Dirt Pushers | from Pantry verdict table | Specialist per task — Scout recommends via dynamic agent discovery, Pantry passes through |
| Nitpickers | `nitpicker` | Custom agent: file:line specificity, calibrated severity, complete coverage |
| Big Head | `big-head` | Custom agent: deduplication, root-cause grouping, issue filing |

## Model Assignments

Every `Task` tool call the Queen makes MUST include the `model` parameter from this table. Omitting `model` causes the agent to inherit the Queen's opus model, wasting tokens on agents that don't need it.

| Agent | Spawn Method | Model | Notes |
|-------|-------------|-------|-------|
| Scout | Task (`scout-organizer`) | opus | Orchestration role |
| Pantry (impl) | Task (`pantry-impl`) | opus | Prompt composition + review skeleton assembly (Script 1) |
| Dirt Pushers | Task (dynamic type) | sonnet | All dirt pushers regardless of subagent_type |
| PC — CCO | Task (`pest-control`) | haiku | Mechanical checklist |
| PC — WWD | Task (`pest-control`) | haiku | Mechanical file comparison |
| PC — DMVDC | Task (`pest-control`) | sonnet | Judgment: claims vs actual code |
| PC — CCB | Task (`pest-control`) | haiku | Mechanical counting |
| Nitpickers (all 4) | TeamCreate member | sonnet | Set in big-head-skeleton.md |
| Big Head | TeamCreate member | opus | Set in big-head-skeleton.md (`{MODEL}`) |
| PC (team member) | TeamCreate member | sonnet | Runs DMVDC inside team; needs sonnet |
| Fix Dirt Pushers | Task (dynamic type) | sonnet | Same rule as regular Dirt Pushers |

## Concurrency Rules

- Max 7 Dirt Pushers concurrent
- Max 12 total agents (Dirt Pushers + support agents: Pantry, Pest Control, Scout)
- No two agents edit the same file — queue conflicting tasks sequentially
- Each agent runs `git pull --rebase` before committing
- Only the Queen pushes to remote
- Only the Queen updates documentation files (CHANGELOG, README, CLAUDE.md)
- Pipeline wave N Dirt Pushers with wave N+1 Pantry in a single message (see Step 2 wave pipelining)

### Wave Management

**7-agent limit rationale**: Claude Code's Task tool runs concurrent calls from a single message. 7 Dirt Pushers is the practical ceiling for context-window pressure from interleaved agent outputs and API rate limits in a single orchestration session.

**Retry counting**: Retry spawns count against the concurrent agent limit. A failed-and-respawned Dirt Pusher occupies a slot.

**Mid-wave decision tree**:

| Scenario | Action |
|----------|--------|
| Agent failure | Log failure, file a beads issue for the failed task, continue with remaining agents. Re-attempt in next wave if slots available. |
| Early completion | Do NOT backfill mid-wave. Wait for the full wave to complete before starting the next. Rationale: backfilling creates interleaved commits that complicate review scope tracking. |
| All agents fail | Stop. Surface failures to user. Do not auto-retry the entire wave. |

## Session Directory

At session start (Step 0), generate a session ID and create the session artifact directory:

    SESSION_ID=$(echo "$$-$(date +%s%N)-$RANDOM" | shasum | head -c 8)
    SESSION_DIR=".beads/agent-summaries/_session-${SESSION_ID}"
    mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts,pc,summaries}

Store SESSION_DIR in your context. Pass it explicitly to every agent that needs to write artifacts:
Scout receives it as "Session directory: <SESSION_DIR>".
Pantry receives it as "Session directory: <SESSION_DIR>".
Pest Control receives it as "Session directory: <SESSION_DIR>" (when writing checkpoint artifacts).

All session-scoped artifacts go here:
- `queen-state.md` — session state for context recovery
- `orchestrator-state*.md` — orchestrator snapshots
- `step3b-transition-gate.md` — review transition gate
- `HANDOFF-*.md` — handoff documents
- `progress.log` — append-only milestone log; one pipe-delimited line per completed step; written by the Queen at each workflow milestone; never read or overwritten during normal operation; recovery sessions read this once to determine the resume point
- `resume-plan.md` — written by `scripts/parse-progress-log.sh` on crash recovery; structured markdown resume plan presented to the user for approval before any action is taken

**Crash recovery script**: `scripts/parse-progress-log.sh <SESSION_DIR>`
- Exit 0: resume-plan.md written; present to user and await `resume` or `fresh start`
- Exit 1: error (missing log, unreadable); surface to user and await instruction
- Exit 2: session already completed (SESSION_COMPLETE logged); no resume-plan written; proceed with fresh start

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
| Agent stuck (no commit within 15 turns) | 0 | Run stuck-agent diagnostic (see below); escalate to user |
| Pantry CCO fails | 1 | Escalate to user; do not spawn Dirt Pushers without verified prompts |
| Scout fails or returns no tasks | 1 | Escalate to user; do not proceed to Step 2 without task list |
| Total retries per session | 5 | Pause all new spawns; triage with user |

Counter interaction: each CCB re-run counts as 1 toward both the per-checkpoint limit (1) and the session total (5). A CCB re-run that hits the per-checkpoint limit also consumes one slot of the session total.

Track retry count in the Queen's state file (→ templates/queen-state.md).

### Stuck-Agent Diagnostic Procedure

When an agent has not produced a commit within 15 turns, follow these steps before escalating:

1. Read the agent's task brief to confirm the scope and acceptance criteria were unambiguous.
2. Check `.beads/agent-summaries/_session-*/` for any partial summary the agent may have written, which can reveal how far it progressed before stalling.
3. Check `git log --oneline -10` to determine whether a commit was made but not reported back correctly.
4. If the agent is still running, check its most recent output for a blocking question, permission error, or tool failure message.
5. If the agent exited without a commit and no diagnostic information is available, escalate to the user with: the task ID, the agent type, the turn count, and any last-known output.

Do not re-spawn the agent or attempt a fix without user approval after the stuck-agent limit (0 retries) is reached.

### Wave Failure Threshold

If more than 50% of agents in a single wave fail (DMVDC failure, stuck, or unrecoverable error), the Queen must:

1. Stop spawning new agents for the remainder of the current wave.
2. Collect failure summaries from all failed agents in the wave.
3. Notify the user immediately: list each failed task ID, the failure type, and retry count consumed.
4. Await explicit user instruction before continuing — options include: re-run the failed subset, abort the session, or manually resolve blockers and resume.

A wave is defined as a set of agents spawned concurrently in a single Step 2 batch. Failures from earlier waves do not carry over into the threshold calculation for a new wave.

## Priority Calibration

**P1** = build failure, broken links, data loss, security vulnerability

**P2** = visual regression, accessibility issue, functional degradation

**P3** = style, naming, cleanup, polish

Project-specific overrides belong in the project's CLAUDE.md or QUALITY_PROCESS.md.

## Context Preservation Targets

- Token budget: finish with >50% remaining
- File reads in the Queen: <10 for 40+ task sessions
- Concurrent agents: typical 5-6 Dirt Pushers, max 12 total
- Commits per session: <20 (batch related work)
