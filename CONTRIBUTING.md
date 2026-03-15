# Contributing to ant-farm

This guide covers the mechanics of modifying the orchestration framework: adding agents, adding checkpoints, editing templates, testing changes, and keeping cross-file references in sync.

For project setup and wiring orchestration into a new project, see `orchestration/SETUP.md`.

## Adding a New Agent

Agent files live in `agents/` and are installed to `~/.claude/agents/` by `scripts/setup.sh`.

### File format

Create `agents/<agent-name>.md` with YAML frontmatter:

```markdown
---
name: <agent-name>
description: One-line description of what this agent does and when it's used.
tools: <comma-separated list of tools>
---

Body text: the agent's system prompt. Instructions, principles, workflow steps.
```

**Required frontmatter fields:**
- `name` -- must match the filename (without `.md`)
- `description` -- used by Claude Code to decide when to suggest this agent type
- `tools` -- subset of: `Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep`

**Optional frontmatter fields:**
- `model` -- e.g. `sonnet`, `haiku`. If omitted, the model is set by the Queen at spawn time via the `model` parameter on the Task tool call. See the Model Assignments table in `orchestration/RULES.md`.

### Restart requirement

Claude Code loads agent files once at startup. Adding or editing an agent file requires a full quit and reopen of Claude Code. Restarting mid-session (or running `/clear`) is not sufficient.

### Cross-file updates after adding an agent

1. **`README.md`** -- add the agent to the "Custom agents" table
2. **`orchestration/RULES.md`** -- add the agent to the "Agent Types" table and "Model Assignments" table
3. **`orchestration/templates/scout.md`** -- the Scout discovers agents dynamically by scanning `~/.claude/agents/`, so no template change is needed unless you want to add heuristic rules for when to recommend the new agent
4. **`orchestration/GLOSSARY.md`** -- add the agent to the "Ant Metaphor Roles" table (lines 77-85)

### One-TeamCreate-per-session constraint

Claude Code supports only one `TeamCreate` call per session. The Nitpicker review team (Step 3b-iv) uses this slot for the entire session.

**Implication for new agents**: If your new agent needs to receive messages from another agent via `SendMessage` (as Pest Control does from Big Head), it MUST be added as a member of the Nitpicker team — it cannot be spawned as a separate Task agent and reached via `SendMessage` from inside the team. Adding a second `TeamCreate` call will fail at runtime.

If the agent does not require intra-team messaging, it can be spawned as a regular Task agent and is not subject to this constraint.

## Adding a New Checkpoint

Checkpoints are verification gates run by Pest Control. All checkpoint definitions live in a single file: `orchestration/templates/checkpoints.md`.

### Where checkpoints are defined

`orchestration/templates/checkpoints.md` contains the full prompt template for each checkpoint type (CCO, WWD, DMVDC, CCB). Pest Control reads this file at spawn time.

### How to add a new checkpoint

1. **Define the checkpoint** in `orchestration/templates/checkpoints.md`:
   - Add a new H2 section (e.g., `## New Checkpoint Name (NCP): Description`)
   - Include: when it runs, what model to use, the verification prompt template, verdict thresholds (PASS/WARN/FAIL), and artifact naming convention
   - Follow the existing pattern: each checkpoint has a `When`, `Model`, `Agent type`, `Why` preamble followed by a fenced markdown block containing the actual Pest Control prompt

2. **Add verdict thresholds** to the "Verdict Thresholds Summary" section at the top of `checkpoints.md`:
   - Add a row to the "Checkpoint-Specific Thresholds" table
   - Add a subsection under "Details by Checkpoint"

3. **Update cross-references** (see "Cross-File Dependencies" below):
   - `orchestration/RULES.md` -- add the checkpoint to the Hard Gates table, specify where in the workflow it runs, and add the model to the Model Assignments table
   - `README.md` -- add the checkpoint to the Hard Gates table and the architecture diagram if it introduces a new flow

### Artifact naming

All checkpoint artifacts are written to `{SESSION_DIR}/pc/` with this naming convention:
- Task-specific: `pc-{TASK_SUFFIX}-{checkpoint}-{timestamp}.md`
- Session-wide: `pc-session-{checkpoint}-{timestamp}.md`

Timestamp format: `YYYYMMDD-HHmmss` (UTC).

## Modifying Agent Templates

Templates live in `orchestration/templates/`. Each template has a specific reader -- the Queen never reads most of them directly.

### Template inventory

| Template | Read by | Purpose |
|----------|---------|---------|
| `scout.md` | Scout (self-read) | Pre-flight recon instructions |
| `pantry.md` | Pantry (self-read) | Prompt composition instructions |
| `implementation.md` | Pantry | Agent prompt template with 6 mandatory steps |
| `checkpoints.md` | Pest Control | All checkpoint definitions |
| `reviews.md` | `build-review-prompts.sh` | Review protocol, report format |
| `dirt-pusher-skeleton.md` | Queen | Minimal agent spawn template |
| `nitpicker-skeleton.md` | Queen, `build-review-prompts.sh` | Review agent spawn template |
| `big-head-skeleton.md` | Queen, `build-review-prompts.sh` | Consolidation agent spawn template |
| `queen-state.md` | Queen | Session state file schema |
| `scribe-skeleton.md` | Queen | Scribe spawn template |
| `review-focus-areas.md` | `build-review-prompts.sh` | Per-type focus blocks for Nitpicker prompts |
| `surveyor.md` | Surveyor (self-read) | Requirements gathering instructions |
| `surveyor-skeleton.md` | Planner | Surveyor spawn template |
| `forager.md` | Forager (self-read) | Parallel research instructions |
| `forager-skeleton.md` | Planner | Forager spawn template |
| `decomposition.md` | Architect | Decomposition workflow instructions |
| `architect-skeleton.md` | Planner | Architect spawn template |
| `SESSION_PLAN_TEMPLATE.md` | User (optional) | Session planning template for new projects |

### Placeholder conventions

Templates use `{PLACEHOLDER}` (single braces) for values filled by the Queen or Pantry at spawn time. Review skeletons use `{{SLOT_NAME}}` (double braces) for values filled by `build-review-prompts.sh`.

Common placeholders:
- `{TASK_ID}`, `{TASK_SUFFIX}` -- crumb identifiers
- `{SESSION_DIR}` -- session artifact directory path
- `{REVIEW_ROUND}`, `{TIMESTAMP}` -- review cycle metadata
- `{{COMMIT_RANGE}}`, `{{CHANGED_FILES}}`, `{{TASK_IDS}}` -- review slot markers

### What to watch when editing templates

- **`implementation.md`** defines the 6 mandatory steps that every Dirt Pusher must follow. If you change a step, update the corresponding CCO check in `checkpoints.md` (Check 4 verifies all 6 steps are present).
- **`reviews.md`** defines review types and report format. Changes here must stay in sync with `build-review-prompts.sh` (which reads `reviews.md` to build review prompts) and the CCB checks in `checkpoints.md` (which verify report structure).
- **`nitpicker-skeleton.md`** and **`big-head-skeleton.md`** are read by `build-review-prompts.sh` to produce filled prompt files. If you change their structure, verify the script still parses them correctly.
- **`dirt-pusher-skeleton.md`** is what the Queen uses to spawn agents. If you add fields, the Pantry's task briefs must include the corresponding data.

## Testing Changes

### Manual validation

1. **Run the setup script** to deploy changes to `~/.claude/`:
   ```bash
   ./scripts/setup.sh
   ```

2. **Restart Claude Code** if you changed any agent files in `agents/`.

3. **Run a test orchestration** with a single low-priority task:
   ```bash
   crumb create --title="Test orchestration change" --type=task --priority=3
   # Then in Claude Code: "Let's get to work on: <task-id>"
   ```

4. **Verify the workflow reaches the gate you modified.** For example:
   - Changed `checkpoints.md` CCO checks? Verify the CCO report in `{SESSION_DIR}/pc/` reflects the new check.
   - Changed `implementation.md`? Verify the Dirt Pusher's summary doc follows the updated steps.
   - Changed `reviews.md`? Verify the review previews in `{SESSION_DIR}/previews/` contain the expected content.

### Script validation

For changes to the review pipeline script:

```bash
# Test build-review-prompts.sh:
# Requires a session dir to write output into
./scripts/build-review-prompts.sh <SESSION_DIR> \
  "abc1234..HEAD" "file1.py\nfile2.py" "task-1 task-2" \
  "$(date +%Y%m%d-%H%M%S)" 1 \
  ~/.claude/orchestration/templates/nitpicker-skeleton.md \
  ~/.claude/orchestration/templates/big-head-skeleton.md
```

The script exits 0 on success and prints error messages to stderr on failure.

## Syncing to ~/.claude/

The orchestration framework runs from `~/.claude/`, not from the repo. Changes in the repo must be synced before they take effect.

### What gets synced

`scripts/setup.sh` installs:
- `agents/*.md` to `~/.claude/agents/`
- `orchestration/` to `~/.claude/orchestration/` (excluding `_archive/` — existing files in the target that are not in the source are preserved)
- `scripts/build-review-prompts.sh` to `~/.claude/orchestration/scripts/`
- `skills/*.md` to `~/.claude/plugins/ant-farm/commands/<name>.md`
- `crumb.py` to `~/.local/bin/crumb`
- `CLAUDE.md` to `~/.claude/CLAUDE.md` (backs up existing file first)

### When syncing happens

- **Manually** by running `./scripts/setup.sh` after pulling changes or editing local files
- The setup script is idempotent: re-running it updates files and backs up any changed targets with a timestamped `.bak` suffix

### Running setup

```bash
./scripts/setup.sh
```

Use `--dry-run` to preview changes without writing:

```bash
./scripts/setup.sh --dry-run
```

### After syncing

If agent files changed, restart Claude Code. The setup script prints a warning when agent files differ.

## Cross-File Dependencies

Changes to one file often require updates to others. This table lists the critical dependencies.

### implementation.md dependencies

| If you change... | Also update... |
|------------------|----------------|
| The 6 mandatory steps | `checkpoints.md` CCO Check 4 (verifies all 6 steps present) |
| Summary doc format | `checkpoints.md` DMVDC Check 1-4 (reads summary docs) |
| Scope boundary format | `checkpoints.md` CCO Check 5, WWD (compares scope to diff) |

### checkpoints.md dependencies

| If you change... | Also update... |
|------------------|----------------|
| A checkpoint's verdict thresholds | `RULES.md` Hard Gates table (describes blocking behavior) |
| A checkpoint's model assignment | `RULES.md` Model Assignments table |
| Artifact naming convention | Any template or script that references `{SESSION_DIR}/pc/` paths |
| CCB report-count check | `reviews.md` (must match expected report count per round) |

### reviews.md dependencies

| If you change... | Also update... |
|------------------|----------------|
| Review types or report format | `build-review-prompts.sh` (reads reviews.md to build review prompts) |
| Report output paths | `build-review-prompts.sh` `{{REPORT_OUTPUT_PATH}}` slot logic |
| Number of review types per round | `checkpoints.md` CCB Check 0 (verifies expected report count) |
| Review types per round | `RULES.md` Step 3b (specifies round 1: 4 types, round 2+: 2 types) |

### Skeleton template dependencies

| If you change... | Also update... |
|------------------|----------------|
| `nitpicker-skeleton.md` structure | `build-review-prompts.sh` (parses this file) |
| `big-head-skeleton.md` structure | `build-review-prompts.sh` (parses this file) |
| `dirt-pusher-skeleton.md` fields | `pantry.md` (Pantry must produce matching task brief data) |
| Slot marker names (`{{...}}`) | `build-review-prompts.sh` (fills the markers) |

### Agent file dependencies

| If you change... | Also update... |
|------------------|----------------|
| Agent name or tools | `README.md` Custom agents table |
| Agent name or role | `RULES.md` Agent Types table, Model Assignments table |
| Agent tools list | Verify the agent can still perform its workflow steps |

### RULES.md dependencies

| If you change... | Also update... |
|------------------|----------------|
| Workflow step sequence | `CLAUDE.md` (if it references step numbers) |
| Template lookup table | Verify all referenced file paths exist |
| Concurrency limits | No cross-file deps, but document in CHANGELOG |

### Quick checklist for any change

1. Identify which file you changed and check the tables above
2. Update all listed dependent files
3. Run `./scripts/setup.sh`
4. Restart Claude Code if agent files changed
5. Test with a single-task orchestration run
