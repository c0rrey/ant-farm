# Handoff: Eliminate Colony TSA, File-Based Pest Control Handoff

## Context

Claude Code does not support nested subagent spawning (Queen → Subagent → Sub-subagent). Two templates currently instruct subagents to spawn their own subagents:

- **Pantry** (Step 3/5): spawns haiku `code-reviewer` for Checkpoint A
- **Colony TSA** (Steps 2-3): spawns haiku/sonnet `code-reviewer` for Checkpoints A.5, B, C

Both fail at runtime with "nested session restriction" errors. The Pantry currently falls back to inline validation, but Colony TSA hasn't been tested yet and will hit the same wall.

## Decision

**Eliminate Colony TSA entirely. Have the Queen spawn Pest Control directly using file-based handoff.**

Colony TSA's only value was:
1. Absorbing `checkpoints.md` read cost (~450 lines)
2. Orchestrating per-task Pest Control spawns
3. Collecting verdicts into a table

But Pest Control can read `checkpoints.md` itself (absorbing the cost), and the Queen can pass file paths directly. The middleman adds no value.

The user feels strongly that Pest Control must remain an independent agent — checkpoint quality is higher when done by a separate agent that doesn't share context with the prompt composer or implementation agents.

## Design: File-Based Handoff

All handoffs between agents use files on disk. No agent passes large content through the Queen's window — only file paths and verdict tables.

### Step 2: Implementation (per wave)

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

### Step 3: Post-wave verification

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

### Step 3b: Reviews

```
Queen                          Pantry                    Pest Control
  │                              │                           │
  ├──spawn (review mode)──────►  │                           │
  │  "compose review prompts"    ├─read reviews.md           │
  │                              ├─read checkpoints.md       │
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

### Context budget comparison

| Phase | Old (with Colony TSA) | New (direct Pest Control) |
|-------|----------------------|--------------------------|
| Step 2 (2 waves) | ~80 lines | ~90 lines |
| Step 3 (2 waves) | ~80 lines | ~70 lines |
| Step 3b | ~80 lines | ~95 lines |
| **Total** | **~240 lines** | **~255 lines** |

~15 extra lines on the Queen. Negligible.

## Concurrency

The user approved increasing the max to 10 total agents while keeping 7 max Dirt Pushers:

- **Dirt Pushers**: max 7 concurrent
- **Support agents** (Pantry, Pest Control, Scout): additional slots up to 10 total
- In practice: 7 dirt pushers + 1 Pantry (prepping next wave) + 1 Pest Control = 9 max

## Files to Change

### 1. Archive `orchestration/templates/colony-tsa.md`

Move to `orchestration/_archive/colony-tsa.md`.

### 2. Rewrite `orchestration/templates/pantry.md`

**Section 1 (Implementation Mode):**
- Step 1: Read `implementation.md` only (drop `checkpoints.md` — Pest Control reads that now)
- Step 2: Compose data files (unchanged)
- Step 3: NEW — Write combined prompt previews to `{session-dir}/previews/`:
  - Read `dirt-pusher-skeleton.md`
  - For each task: fill skeleton placeholders + append data file → write to `{session-dir}/previews/task-{task-id-suffix}-preview.md`
- Step 4: Return file paths (no Checkpoint A, no verdict table):
  ```
  | Task ID | Data File | Preview File |
  |---------|-----------|--------------|
  | {id}    | {path}    | {path}       |
  ```

**Section 2 (Review Mode):**
- Step 1: Read `reviews.md` only (drop `checkpoints.md`)
- Steps 2-4: Compose review data files + Big Head data file (unchanged)
- Step 5: NEW — Write combined review previews to `{session-dir}/previews/`:
  - Read `nitpicker-skeleton.md`
  - For each review: fill skeleton placeholders + append data file → write preview
- Step 6: Return file paths (no Checkpoint A):
  ```
  | Review Type | Data File | Preview File | Report Output Path |
  |-------------|-----------|--------------|-------------------|
  | clarity     | {path}    | {path}       | {path}            |
  | ...         |           |              |                   |

  Big Head consolidation data: {path}
  Big Head consolidated output: {path}
  ```

**Section 3 (Error Handling):**
- Remove `bd show` failure handling (Scout handles that now)
- Remove Checkpoint A failure handling (Pest Control handles that now)
- Keep: write-immediately, partial-failure return

### 3. Update `orchestration/RULES.md`

**Queen Prohibitions:** Remove `colony-tsa.md` from the template files list.

**Steps 2, 3, 3b:** Rewrite to reflect new flow:

```
**Step 2:** Spawn — create epic artifact dirs (from briefing Epics line).
            Spawn the Pantry for data files + combined previews
            (→ templates/pantry.md). Spawn Pest Control for Checkpoint A
            (pass preview file paths, Pest Control reads checkpoints.md itself).
            Only after all Checkpoint A PASS: spawn agents using skeleton
            (→ templates/dirt-pusher-skeleton.md).
            Prepare next wave (Pantry + Pest Control) WHILE current wave runs.

**Step 3:** Verify — after each wave completes, spawn Pest Control for A.5 + B
            (pass task IDs, commit hashes, summary doc paths; Pest Control reads
            checkpoints.md + task-metadata/ + git diffs itself).
            Failed B → resume agent (max 2 retries).

**Step 3b:** Review — spawn the Pantry (review mode) for review prompts + previews.
             Spawn Pest Control for Checkpoint A on review previews.
             Create Nitpicker team (→ templates/nitpicker-skeleton.md).
             After team completes, spawn Pest Control for B + C
             (pass report paths; Pest Control reads checkpoints.md itself).
```

**Information Diet:** Change `verdict tables from pantry/Colony TSA` → `verdict tables from the Pantry and Pest Control`.

Remove `Colony TSA` from DO NOT READ list.

**Concurrency Rules:** Change:
```
- Max 7 background agents at any time
```
To:
```
- Max 7 Dirt Pushers concurrent
- Max 10 total agents (Dirt Pushers + support agents: Pantry, Pest Control, Scout)
```

**Session Directory:** Add `previews/` to the mkdir:
```
mkdir -p .beads/agent-summaries/_session-${SESSION_ID}/{task-metadata,previews}
```

**Anti-Patterns:** Change:
```
- Running individual checkpoints per agent — spawn Colony TSA as batch
```
To:
```
- Running individual checkpoints per agent — spawn one Pest Control with the full batch
```

Remove:
```
- Reading implementation.md or checkpoints.md directly — spawn the Pantry instead
```
Replace with:
```
- Reading implementation.md or checkpoints.md directly — the Pantry and Pest Control read these
```

**Template Lookup:** Remove Colony TSA row. Change checkpoints.md row:
```
| Checkpoint details (read by Pantry/Colony TSA) | templates/checkpoints.md |
```
To:
```
| Checkpoint details (read by Pest Control) | templates/checkpoints.md |
```

### 4. Update `orchestration/templates/queen-state.md`

Replace Colony TSA section with Pest Control tracking:

```
## Pest Control
| Phase | Checkpoint | Status | Verdict |
|-------|------------|--------|---------|
| Wave 1 prompts | A | pending/completed/failed | All PASS / <details> |
| Wave 1 post | A.5 + B | pending/completed/failed | All PASS / <details> |
| Wave 2 prompts | A | pending/completed/failed | All PASS / <details> |
| Wave 2 post | A.5 + B | pending/completed/failed | All PASS / <details> |
| Reviews | A | pending/completed/failed | All PASS / <details> |
| Reviews | B + C | pending/completed/failed | All PASS / <details> |
```

### 5. Major rewrite of `README.md`

**Architecture diagram:**
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

**Architecture description:** Update the three-layer description. Pest Control is now spawned directly by the Queen (not nested through Colony TSA). Remove Colony TSA references.

**Step 2 section:** Rewrite to describe the Pantry → file handoff → Pest Control → agents flow. Include the Step 2 flow diagram from the Design section above.

**Step 3 section:** Replace Colony TSA description with direct Pest Control spawn. Include the Step 3 flow diagram.

**Step 3b section:** Replace Colony TSA review mode with direct Pest Control spawn for B + C. Include the Step 3b flow diagram.

**Information diet section:** Change:
> Task metadata is read by the Scout, which writes per-task files and a briefing. Templates like `implementation.md`, `checkpoints.md`, and `reviews.md` are read by the Pantry and Colony TSA. The Pantry reads the Scout's pre-extracted metadata files instead of running `bd show`. All these specialized subagents absorb the context cost so the Queen's window stays clean.

To:
> Task metadata is read by the Scout, which writes per-task files and a briefing. `implementation.md` and `reviews.md` are read by the Pantry. `checkpoints.md` is read by Pest Control. The Pantry reads the Scout's pre-extracted metadata files and writes combined prompt previews to disk. Pest Control reads these previews and checkpoint criteria directly. All agents absorb the context cost so the Queen's window stays clean.

**Hard gates table:** Remove model column (Pest Control chooses its own approach):
Keep the table but remove "(haiku, mechanical)" and "(sonnet, judgment-based)" qualifiers since the Queen no longer specifies models — Pest Control is a single agent that handles all checkpoint types.

Actually — keep the table as-is. The model info is useful documentation even if the Queen doesn't configure it per-spawn anymore.

**File reference table:**
- Remove `colony-tsa.md` row
- Change `checkpoints.md` row: `the Pantry, Colony TSA` → `Pest Control`
- Add note that `colony-tsa.md` is archived at `_archive/colony-tsa.md`

## Verification Checklist

After implementation, verify:

1. `colony-tsa.md` moved to `_archive/`, not in `templates/`
2. No remaining references to "Colony TSA" in active templates (grep all non-archive .md files)
3. `pantry.md` no longer mentions Checkpoint A, subagent spawning, or `checkpoints.md`
4. `pantry.md` writes combined previews to `{session-dir}/previews/` and returns file paths
5. `RULES.md` Steps 2/3/3b describe direct Pest Control spawns with file paths
6. `RULES.md` concurrency is "7 Dirt Pushers, 10 total"
7. `RULES.md` template lookup has no Colony TSA row
8. `queen-state.md` has Pest Control section, no Colony TSA section
9. `README.md` architecture diagram shows Pest Control as direct Queen spawn
10. `README.md` includes the three session flow diagrams
11. `README.md` file reference has no `colony-tsa.md` row, `checkpoints.md` says "Pest Control"
12. Session directory mkdir includes `previews/` subdirectory
13. No "nested" or "inline" checkpoint language remains in active templates

## What NOT to Change

- `checkpoints.md` — unchanged, Pest Control reads it as-is
- `dirt-pusher-skeleton.md` — unchanged
- `nitpicker-skeleton.md` — unchanged
- `big-head-skeleton.md` — unchanged
- `scout.md` — unchanged
- `implementation.md` — unchanged
- `reviews.md` — unchanged
- `dependency-analysis.md` — unchanged
- `known-failures.md` — unchanged (but consider adding the nesting failure as a documented incident)
- `CLAUDE.md` — unchanged
