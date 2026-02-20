# Meta-Orchestration: Multi-Queen Parallel Workflow

## Problem

Running parallel Queens today is manual. The user:
1. Manually scouts epics to ensure no file overlaps
2. Opens 2 terminal tabs and starts Queens independently
3. Monitors both sessions by switching tabs
4. Manually sequences follow-up work after Queens finish

This limits throughput to what the user can manually coordinate. With a structured orchestration layer, multiple Queens can run safely in parallel with automated conflict detection, rolling task scheduling, and crash recovery.

## Architecture Overview

```
Meta-Orchestrator (tmux pane 0 — interactive Claude Code session)
  ├── Meta-Scout: analyzes all work, builds dependency DAG, scores complexity
  ├── SSV Checkpoint: haiku PC agent verifies strategy before execution
  ├── Pool Manager: maintains N concurrent Queens, schedules on task completion
  ├── Worktree Manager: creates/tears down git worktrees per Queen
  └── Progress Monitor: tails Queen progress logs, detects completion/crash/stuck

Queen A (tmux pane 1)          Queen B (tmux pane 2)          Queen C (tmux pane 3)
  └── Standard workflow            └── Standard workflow            └── Standard workflow
      (Scout → Pantry →                (Scout → Pantry →                (Scout → Pantry →
       Dirt Pushers →                   Dirt Pushers →                   Dirt Pushers →
       Reviews → Close)                 Reviews → Close)                 Reviews → Close)
```

Queens are standard Claude Code sessions running the normal workflow. They do not need to know they were spawned by a meta-orchestrator.

## Key Design Decisions

### tmux-Based Spawning (Not `claude -p`)

Queens run as full interactive Claude Code sessions in tmux panes. This eliminates:
- File-based approval protocol (Queens use normal interactive approval)
- Permission pre-configuration (interactive sessions handle permissions normally)
- Non-interactive mode limitations (Queens support full multi-turn workflows)

The user can switch to any pane at any time to interact with a Queen or the meta-orchestrator directly.

Spawning a Queen:

iTerm2 compatibility: `tmux -CC` is how iTerm2 attaches as a tmux client, rendering each tmux
window as a native iTerm2 tab. External scripts send commands to the tmux server via its socket —
not through the control-mode client — so standard `tmux new-window` and `tmux send-keys` commands
work identically whether a `-CC` client is attached or not.

```bash
# Create a named window for the Queen
tmux new-window -t session-name -n "queen-ant-farm-w7p"

# Start Claude Code in the worktree
tmux send-keys -t session-name:queen-ant-farm-w7p 'cd /path/to/worktree && claude' Enter

# Wait for Claude Code to reach its input prompt (node process takes 3-8s to initialize)
sleep 5

# Send the initial prompt
tmux send-keys -t session-name:queen-ant-farm-w7p "Let's get to work on ant-farm-w7p" Enter
```

Checking Queen status:
```bash
# What command is running in a window (Claude Code appears as 'node')
tmux display-message -t session-name:queen-ant-farm-w7p -p '#{pane_current_command}'

# List all windows with running commands (for pool status monitoring)
tmux list-windows -t session-name -F '#{window_name}: #{pane_current_command}'

# Kill a Queen window when done
tmux kill-window -t session-name:queen-ant-farm-w7p
```

### Rolling Pool Model (Not Strict Waves)

Instead of serialized waves where all Queens must finish before the next wave starts, the meta-orchestrator maintains a pool of N concurrent Queens and fills slots as they free up.

When a Queen finishes:
1. Merge her branch to main
2. Check if any queued tasks are now unblocked (beads deps + file-conflict deps)
3. Pick highest-priority eligible task
4. Set up worktree from current main, spawn new Queen

This eliminates idle time from strict wave boundaries. The only serialization is between tasks that share files or have beads dependency edges.

### Dependency DAG (Not Wave Groupings)

The meta-scout outputs a dependency-augmented task queue, not wave groupings:

```
Task A: ready (no deps, no file conflicts)
Task B: ready (no deps, no file conflicts with A)
Task C: blocked by A (beads dep)
Task D: ready (no file conflicts with A or B)
Task E: file conflict with B → synthetic dep on B
```

Beads already has the dependency DAG. The meta-scout overlays file-conflict constraints as synthetic dependency edges. Tasks sharing files get a synthetic edge forcing sequential execution. Everything else can run in parallel up to the pool limit.

Scheduling algorithm: **longest-job-first** — start the highest-complexity eligible tasks first so they finish earlier relative to the session, avoiding the long-tail problem where one big task holds up the final stretch.

### Worktrees for Source Code, Shared Dolt for Beads

Each Queen gets its own git worktree (isolated working tree, own branch, no git index conflicts). All Queens share the same Dolt database via the `BEADS_DB` environment variable, pointed at the main repo's `.beads/dolt/beads`. Dolt's flock-based locking handles concurrent `bd create`, `bd close`, `bd update` safely.

```bash
# Create worktree for a Queen
git worktree add /tmp/ant-farm-queen-a -b queen/ant-farm-w7p

# Set shared beads DB
export BEADS_DB=/Users/correy/projects/ant-farm/.beads/dolt/beads
```

### SSV Checkpoint Replaces Human Strategy Approval

A haiku-model Pest Control agent runs automatically after the meta-scout produces its strategy. Three mechanical checks:

1. **No file overlaps among concurrent tasks**: For all tasks eligible to run simultaneously, no file appears in two or more tasks.
2. **File lists match bead descriptions**: The meta-scout's reported affected files match the bead's actual affected files.
3. **No dependency violations among concurrent tasks**: No concurrent task depends on another concurrent task.

PASS: meta-orchestrator proceeds. FAIL: re-run meta-scout or escalate to user.

See: ant-farm-s0ak

### Progress Log for Crash Recovery

Each Queen appends milestone entries to `{session-dir}/progress.log`. The meta-orchestrator monitors these to detect completion, crashes, and stuck Queens.

```
2026-02-19T14:01:23 | SCOUT_COMPLETE | metadata=.beads/agent-summaries/_session-abc/task-metadata/
2026-02-19T14:02:45 | PANTRY_IMPL_COMPLETE | prompts=3 skeletons=4
2026-02-19T14:08:12 | DIRT_PUSHER_COMPLETE | task=ant-farm-w7p status=success
2026-02-19T14:15:44 | BIG_HEAD_CONSOLIDATED | report=...
2026-02-19T14:16:30 | BEADS_FILED | count=7
```

Lifecycle detection:
- **Finished**: progress log has `SESSION_CLOSE_STARTED`, process exited
- **Crashed**: process exited but progress log has no close entry
- **Stuck**: process alive but progress log stale for N minutes

On crash: meta-orchestrator reads the progress log, determines resume point, spawns a recovery Queen in a new tmux pane pointed at the same session dir.

See: ant-farm-0b4k (progress log), ant-farm-b219 (automated recovery)

### Meta-Orchestrator Durability

The meta-orchestrator writes its own state file:

```json
{
  "wave_plan": [{"task": "ant-farm-w7p", "queen_pid": 12345, "worktree": "/tmp/ant-farm-queen-a", "branch": "queen/ant-farm-w7p", "session_dir": "..."}],
  "pool_size": 3,
  "active_queens": 2,
  "completed_tasks": ["ant-farm-cifp"],
  "status": "running"
}
```

If the meta-orchestrator crashes, Queens keep running (separate processes). A new meta-orchestrator session reads the state file + Queens' progress logs to resume coordination.

## Task Complexity Scoring

The meta-scout scores each task to drive longest-job-first scheduling. The formula uses only data already in the bead:

```
Files are classified as:
  source = everything except test and docs files
  test   = test_*, *_test.*, *.spec.*, files in test(s)/ or __tests__/
  docs   = .md, .txt, .rst, .adoc

score = (source_files * 3) + (test_files * 2) + (docs_files * 0.5)
        * type_multiplier (feature=1.5, task=1.0, bug=0.7)
        + new_file_bonus (2 per new source file, 1 per new test)
        + min(description_words / 50, 3)
```

This is implemented as a standalone script callable by the meta-scout. No project-specific configuration needed — the "everything else is source" rule means project-specific file types (templates, configs, schemas) automatically get the highest weight.

## Meta-Scout Behavior

The meta-scout behaves like the current Scout but scoped wider. Three input modes:

- **Explicit**: "Meta-orchestrate epics ant-farm-21d and ant-farm-6k0 with 3 queens"
- **Filtered**: "Meta-orchestrate all P1 bugs with 2 queens"
- **Open-ended**: "Let's get to work" — meta-scout runs `bd ready`, analyzes everything, proposes a plan scoped to pool size and estimated session length

In all modes, the meta-scout:
1. Reads affected files from all in-scope beads
2. Builds the file-conflict graph (set intersection on affected file lists)
3. Overlays beads dependency edges
4. Scores complexity for each task
5. Produces the dependency DAG with complexity ordering
6. Presents the plan to the user for approval

## Branch Merge Strategy

When a Queen finishes:
1. Meta-orchestrator merges the Queen's branch to main
2. Since SSV verified no file overlaps among concurrent tasks, merges should be clean
3. If merge fails unexpectedly (new files not in bead file list, adjacency conflicts): spawn a merge-conflict agent to attempt resolution
4. If the merge-conflict agent can't resolve: escalate to user
5. Next Queen spawns from updated main (includes all merged work)

## User Interaction

The meta-orchestrator runs in tmux pane 0. The user can:
- Ask status questions ("how are the Queens doing?")
- Adjust mid-session ("pause, don't start any new Queens")
- Kill a Queen or add tasks
- Tab to any Queen pane and interact directly
- Talk to the meta-orchestrator to request merges, reruns, or early termination

The meta-orchestrator periodically aggregates progress:
```
Pool status (3 slots):
  Queen A (ant-farm-w7p): DIRT_PUSHER_COMPLETE  [2m ago]
  Queen B (ant-farm-cifp): PANTRY_IMPL_COMPLETE  [5m ago]
  Queen C (ant-farm-0cf): SCOUT_COMPLETE  [1m ago]
Queue: 4 tasks remaining, next eligible: ant-farm-7k1 (score: 6.5)
```

## Resource Constraints

Target hardware: MacBook Air 16GB RAM, Anthropic Max plan ($200/month).

- 2-3 concurrent Queens is the practical limit
- Each Queen: ~500MB RAM (Claude Code + subagents during peak phases)
- API rate limits are more likely to throttle than local resources, especially during review phases when Queens spawn Nitpicker teams simultaneously
- Staggering Queen starts by a few minutes helps avoid rate limit spikes

## Incremental Delivery Phases

Each phase delivers standalone value and is a prerequisite for subsequent phases.

### Phase 1: Progress Log
**Bead**: ant-farm-0b4k (P1)
**Value**: Crash recovery for single-Queen workflow. Foundation for all monitoring.
**Work**: Add append-only progress log to RULES.md workflow. One `echo >>` per milestone.

### Phase 2: SSV Checkpoint
**Bead**: ant-farm-s0ak (P2)
**Value**: Automated strategy verification for single-Queen workflow. Catches Scout errors before implementation. Prerequisite for removing human approval gate.
**Work**: New haiku PC checkpoint after Scout returns, before Pantry spawns.

### Phase 3: Complexity Scoring Script
**Value**: Standalone utility for meta-scout and manual prioritization.
**Work**: Small script that reads bead JSON and outputs complexity score. Universal formula, no project-specific config.

### Phase 4: Meta-Orchestrator MVP
**Value**: Proves the core architecture — tmux spawning, worktree management, shared beads DB, single wave of parallel Queens.
**Work**: Meta-orchestrator that can spawn N Queens in tmux panes with worktrees, monitor progress logs, merge branches when Queens finish. Fixed pool, no rolling replacement.

### Phase 5: Rolling Pool with Dependency-Aware Scheduling
**Value**: Full vision — rolling task assignment, longest-job-first scheduling, crash recovery, automated wave transitions.
**Work**: Dependency DAG scheduling, slot replacement on Queen completion, meta-orchestrator state file for its own durability, merge-conflict agent for edge cases.

## Open Questions

- **Trigger phrase**: Starting point is "meta-orchestrate epics X and Y with N queens". Final phrasing TBD.
- **`claude` CLI invocation via tmux**: Confirmed working. `tmux send-keys` reliably starts Claude Code and sends the initial prompt. Use `sleep 5` between starting `claude` and sending the initial prompt — the node process takes 3-8s to reach the input state. Claude Code shows as `node` in `#{pane_current_command}`.
- **Dolt lock contention under load**: With 3 Queens sharing a Dolt DB, brief lock contention is expected. Needs testing to confirm 15s timeout is sufficient or if Queens need retry logic.
- **iTerm2 alternative**: Not needed. Standard `tmux new-window` and `tmux send-keys` commands are fully compatible with iTerm2 control mode. External scripts communicate with the tmux server via its socket — independent of whether a `-CC` client is attached. iTerm2 renders the resulting windows as native tabs automatically.

## Related Beads

| ID | Priority | Title | Phase |
|----|----------|-------|-------|
| ant-farm-0b4k | P1 | Add append-only progress log for Queen crash recovery | 1 |
| ant-farm-b219 | P3 | Automated Queen crash recovery from progress log | 5 |
| ant-farm-s0ak | P2 | Add pre-flight Scout strategy verification checkpoint | 2 |
| ant-farm-0cf | P1 | Parallelize review prompt composition via bash scripts | Related |
| ant-farm-7hgn | P2 | Delay Big Head bead filing until after PC checkpoint | Related |
