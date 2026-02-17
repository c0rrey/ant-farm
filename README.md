# ant-farm

A multi-agent orchestration and quality review system for Claude Code. Coordinates parallel agent work across projects with structured verification gates that prevent the failure modes inherent to AI-generated code: skipped design steps, scope creep, fabricated review claims, and unverified acceptance criteria.

## Architecture

The system has three layers: **the Queen** (the orchestrator that never touches source code), **Dirt Pushers** (implementation and review subagents), and **Pest Control** (an independent verification agent that audits both).

```
┌─────────────────────────────────────────────────────────┐
│  The Queen (orchestrator)                               │
│  - Reads briefing + verdict tables only                 │
│  - Spawns Scout, Pantry, Pest Control directly          │
│  - Only agent that pushes to remote                     │
├───────────┬─────────────┬───────────────────────────────┤
│  Scout    │  Pantry     │  Pest Control                 │
│  - Recon  │  - Composes │  - Checkpoint A (prompt audit)│
│  - Writes │    data files│  - Checkpoint A.5 (scope)    │
│    briefing│  - Writes   │  - Checkpoint B (substance)  │
│  - Writes │    previews │  - Checkpoint C (consolidation│
│    metadata│            │    audit)                     │
├───────────┴─────────────┴───────────────────────────────┤
│  Dirt Pushers (up to 7 concurrent)                      │
├─────────────────────────────────────────────────────────┤
│  The Nitpickers (4 reviewers + Big Head)                │
└─────────────────────────────────────────────────────────┘
```

## Workflow

Triggered by saying **"let's get to work"** in any project wired up per `SETUP.md`.

### Step 0: Session setup

Generate a session ID, create the session directory and `task-metadata/` subdirectory. No agents spawn yet.

### Step 1: Recon

The Queen spawns **the Scout** (`templates/scout.md`), a sonnet subagent that performs all pre-flight reconnaissance:

1. Discovers tasks (from epic, explicit list, or natural-language filter)
2. Runs `bd ready` and `bd blocked` to separate ready vs. blocked tasks
3. Runs `bd show` per task and writes per-task metadata files to `{session-dir}/task-metadata/`
4. Builds a file modification matrix and assesses conflict risk using `reference/dependency-analysis.md`
5. Proposes 2-3 execution strategies with wave groupings, agent counts, and risk assessments
6. Writes `{session-dir}/briefing.md` — a ~40-line summary the Queen presents to the user

The Queen reads the briefing, presents the strategy options, and **waits for user approval** before proceeding.

### Step 2: Spawn implementation agents

The Queen delegates prompt composition to **the Pantry**, a subagent that:
1. Reads `templates/implementation.md` (keeping it out of the Queen's context)
2. Extracts pre-digested context from each task (affected files, root cause, acceptance criteria)
3. Writes a data file per task with scope boundaries and explicit off-limits areas
4. Writes combined prompt previews (skeleton + data file) to `{session-dir}/previews/`
5. Returns a file path table — data files and preview files for each task

The Queen then spawns **Pest Control** to audit the preview files against **Checkpoint A**. Pest Control reads `templates/checkpoints.md` itself, audits each preview, writes reports, and returns a verdict table. The Queen only spawns agents with PASS verdicts.

```
Queen                          Pantry                    Pest Control
  │                              │                           │
  ├──spawn────────────────────►  │                           │
  │  "compose Wave N prompts"    │                           │
  │                              ├─read templates            │
  │                              ├─read task-metadata/       │
  │                              ├─write data files to disk  │
  │                              ├─write combined previews   │
  │  ◄──return paths + done──────┤                           │
  │  (~10 lines)                 │ (agent dies, context freed)│
  │                                                          │
  ├──spawn─────────────────────────────────────────────────► │
  │  "read previews from {dir},                              │
  │   audit against Checkpoint A                             │
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

The Queen then spawns agents using `templates/dirt-pusher-skeleton.md`, a minimal template that points the agent to its data file. Each agent executes 6 mandatory steps:

1. **Claim** — `bd show` + `bd update --status=in_progress`
2. **Design** — 4+ genuinely distinct approaches with tradeoffs (not cosmetic variations)
3. **Implement** — clean, minimal code satisfying acceptance criteria
4. **Correctness review** — re-read every changed file, verify acceptance criteria, assumptions audit
5. **Commit** — `git pull --rebase` then commit with task ID in message
6. **Summary doc** — structured artifact with approaches, rationale, review evidence, and test results

Agents are constrained by **scope boundaries**: they may only edit the files and line ranges listed in their data file. If they notice adjacent issues, they document them in an "Adjacent Issues Found" section but do not fix them.

### Step 3: Monitor and verify

After each wave completes, the Queen spawns **Pest Control** directly for post-wave verification:

- **Checkpoint A.5** (scope verification) — compares files changed in the commit against expected scope from the task. Catches scope creep between agents before it cascades.
- **Checkpoint B** (substance verification) — reads the agent's summary doc and cross-checks claims against the actual git diff: Do the claimed file changes exist? Are acceptance criteria genuinely met? Are the 4 design approaches substantively distinct? Is the correctness review specific or boilerplate?

Pest Control reads `templates/checkpoints.md`, task metadata, and git diffs itself — the Queen only passes task IDs, commit hashes, and summary doc paths.

```
Queen                                              Pest Control
  │  (agents committed, Queen has commit hashes)        │
  │                                                     │
  ├──spawn──────────────────────────────────────────► │
  │  "read checkpoints.md,                              │
  │   run A.5 for {tasks} against {commits},            │
  │   run B: read summary docs at {paths},              │
  │   cross-check against git diffs,                    │
  │   write reports, return verdicts"                   │
  │                                                     ├─read checkpoints.md
  │                                                     ├─per task: git diff + summary doc
  │                                                     ├─write A.5 + B reports
  │  ◄──return verdict table────────────────────────────┤
  │  (~15 lines)                            (agent dies)│
```

Failed Checkpoint B → agent is resumed with specific gaps listed → re-verified → escalated to user after 2 retries.

The Queen prepares next-wave prompts (Pantry + Pest Control) while the current wave runs, eliminating spawn latency between waves.

### Step 3b: Quality review

After **all** implementation completes and all Checkpoint Bs pass, the Queen enters the review phase. This is mandatory — it cannot be skipped or deferred.

#### Transition gate

Before launching reviews, verify: all agents completed, all Checkpoint Bs passed, git log shows expected commits.

#### The Nitpickers

The Queen creates an **agent team** (TeamCreate, not Task) with 4 parallel reviewers that can message each other about overlapping findings:

| Review | Priority | Focus |
|--------|----------|-------|
| **Clarity** | P3 | Readability, naming, documentation, consistency |
| **Edge Cases** | P2 | Input validation, error handling, boundary conditions, concurrency |
| **Correctness Redux** | P1-P2 | Acceptance criteria verification, logic errors, regressions, cross-file consistency |
| **Excellence** | P3 | Best practices, performance, security, maintainability, architecture |

Each reviewer reads all changed files, catalogs findings with file:line references and severity, groups them into preliminary root causes, and writes a structured report. Reviewers **do not file issues** — only Big Head does.

Every report includes a **coverage log** — every in-scope file must appear, even those with no findings. This prevents silently skipping files.

#### Big Head Consolidation

An opus-model Big Head reads all 4 reports and:
1. Merges duplicate findings across reviewers
2. Groups by root cause (one group per underlying problem, not per occurrence)
3. Documents merge rationale for every grouping
4. Files one issue per root cause with all affected surfaces
5. Writes a consolidated summary with deduplication log and priority breakdown

#### Checkpoint B + C (post-review verification)

After the Nitpicker team completes, the Queen spawns **Pest Control** for Checkpoint B (substance verification on each reviewer's report) and Checkpoint C (consolidation audit on Big Head's output).

```
Queen                          Pantry                    Pest Control
  │                              │                           │
  ├──spawn (review mode)──────►  │                           │
  │  "compose review prompts"    ├─read reviews.md           │
  │                              ├─write 4 review data files │
  │                              ├─write combined previews   │
  │                              ├─write Big Head data file  │
  │  ◄──return paths─────────────┤                           │
  │  (~15 lines)                 │                           │
  │                                                          │
  ├──spawn─────────────────────────────────────────────────► │
  │  "audit review prompts, Checkpoint A"                    │
  │  ◄──return verdicts──────────────────────────────────────┤
  │                                                          │
  ├──create Nitpicker team (4 reviewers + Big Head)──►       │
  │  ...reviewers write reports, Big Head consolidates...    │
  │  ◄──team returns report paths                            │
  │                                                          │
  ├──spawn─────────────────────────────────────────────────► │
  │  "read 4 reports + consolidated report,                  │
  │   run Checkpoint B (Nitpickers) + Checkpoint C,          │
  │   write reports, return verdicts"                        │
  │                                                          ├─read checkpoints.md
  │                                                          ├─read 5 reports
  │                                                          ├─audit each
  │  ◄──return verdict table─────────────────────────────────┤
  │  (~15 lines)                                             │
```

Before presenting results to the user, Checkpoint C audits the consolidation:
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

A core design principle: the Queen **never reads source code, tests, configs, or implementation templates**. It reads only the Scout's briefing, agent notifications, commit messages, and verdict tables.

Task metadata is read by the Scout, which writes per-task files and a briefing. `implementation.md` and `reviews.md` are read by the Pantry. `checkpoints.md` is read by Pest Control. The Pantry reads the Scout's pre-extracted metadata files and writes combined prompt previews to disk. Pest Control reads these previews and checkpoint criteria directly. All agents absorb the context cost so the Queen's window stays clean.

Target: finish a 40+ task session with >50% context window remaining, <10 file reads in the Queen, <20 commits.

## Hard gates

| Gate | What it blocks | Model |
|------|---------------|-------|
| **Checkpoint A** — prompt audit | Agent spawn | haiku |
| **Checkpoint A.5** — scope verification | Next agent in wave | haiku |
| **Checkpoint B** — substance verification | Task closure | sonnet |
| **Checkpoint C** — consolidation audit | Presenting results to user | haiku |

All checkpoint artifacts are written to `.beads/agent-summaries/<epic>/verification/pest-control/` with timestamped filenames for full audit history.

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
| `orchestration/RULES.md` | The Queen | Workflow steps, hard gates, concurrency rules, template lookup |
| `orchestration/SETUP.md` | User | How to wire orchestration into a new project |
| `orchestration/templates/implementation.md` | the Pantry | Agent prompt template with 6 mandatory steps |
| `orchestration/templates/checkpoints.md` | Pest Control | All checkpoint definitions (A, A.5, B, C) |
| `orchestration/templates/reviews.md` | the Pantry (review mode) | Review protocol, 4 review types, report format, Big Head consolidation |
| `orchestration/templates/pantry.md` | The Queen (to spawn the Pantry) | the Pantry's own instructions |
| `orchestration/templates/dirt-pusher-skeleton.md` | The Queen | Minimal agent spawn template |
| `orchestration/templates/nitpicker-skeleton.md` | The Queen | Minimal review agent spawn template |
| `orchestration/templates/big-head-skeleton.md` | The Queen | Minimal Big Head consolidation spawn template |
| `orchestration/templates/queen-state.md` | The Queen | Session state file schema |
| `orchestration/templates/scout.md` | The Queen (to spawn the Scout) | Pre-flight recon instructions |
| `orchestration/reference/dependency-analysis.md` | The Scout | Pre-flight conflict analysis, spawn patterns |
| `orchestration/reference/known-failures.md` | Post-mortem reference | Past failures and fixes applied |
