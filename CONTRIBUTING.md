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
- `model` -- e.g. `sonnet`, `haiku`. If omitted, the model is set by the Orchestrator at spawn time via the `model` parameter on the Task tool call. See `orchestration/reference/model-assignments.md`.

### Restart requirement

Claude Code loads agent files once at startup. Adding or editing an agent file requires a full quit and reopen of Claude Code. Restarting mid-session (or running `/clear`) is not sufficient.

### Cross-file updates after adding an agent

1. **`README.md`** -- add the agent to the "Custom agents" table
2. **`orchestration/reference/agent-types.md`** and **`orchestration/reference/model-assignments.md`** -- add the agent to the Agent Types table and Model Assignments table
3. **`orchestration/templates/recon-planner.md`** -- the Recon Planner discovers agents dynamically by scanning `~/.claude/agents/`, so no template change is needed unless you want to add heuristic rules for when to recommend the new agent
4. **`orchestration/GLOSSARY.md`** -- add the agent to the "Agent Roles" table (the `## Agent Roles` section)

### One-TeamCreate-per-session constraint

Claude Code supports only one `TeamCreate` call per session. The Reviewer team (Step 3b-iv) uses this slot for the entire session.

**Implication for new agents**: If your new agent needs to receive messages from another agent via `SendMessage` (as Checkpoint Auditor does from Review Consolidator), it MUST be added as a member of the Reviewer team — it cannot be spawned as a separate Task agent and reached via `SendMessage` from inside the team. Adding a second `TeamCreate` call will fail at runtime.

If the agent does not require intra-team messaging, it can be spawned as a regular Task agent and is not subject to this constraint.

## Adding a New Checkpoint

Checkpoints are verification gates run by the Checkpoint Auditor. Checkpoint definitions live in `orchestration/templates/checkpoints/` — one file per checkpoint type, plus a shared `common.md` preamble.

### Where checkpoints are defined

`orchestration/templates/checkpoints/` contains a shared preamble (`common.md`) and one file per checkpoint type (e.g., `pre-spawn-check.md`, `scope-verify.md`). The Checkpoint Auditor reads `common.md` plus the specific checkpoint file at spawn time.

### How to add a new checkpoint

1. **Create a new checkpoint file** in `orchestration/templates/checkpoints/` (e.g., `ncp.md`):
   - Add a new H2 section (e.g., `## New Checkpoint Name (NCP): Description`)
   - Include: when it runs, what model to use, the verification prompt template, verdict thresholds (PASS/WARN/FAIL), and artifact naming convention
   - Follow the existing pattern: each checkpoint has a `When`, `Model`, `Agent type`, `Why` preamble followed by a fenced markdown block containing the actual Checkpoint Auditor prompt

2. **Add verdict thresholds** to `orchestration/templates/checkpoints/common.md`:
   - Add a row to the "Checkpoint-Specific Thresholds" table
   - Add a subsection under "Details by Checkpoint"

3. **Update cross-references** (see "Cross-File Dependencies" below):
   - `orchestration/RULES.md` -- add the checkpoint to the Hard Gates table and specify where in the workflow it runs
   - `orchestration/reference/model-assignments.md` -- add the model to the Model Assignments table
   - `README.md` -- add the checkpoint to the Hard Gates table and the architecture diagram if it introduces a new flow

### Artifact naming

All checkpoint artifacts are written to `{SESSION_DIR}/pc/` with this naming convention:
- Task-specific: `pc-{TASK_SUFFIX}-{checkpoint}-{timestamp}.md`
- Session-wide: `pc-session-{checkpoint}-{timestamp}.md`

Timestamp format: `YYYYMMDD-HHmmss` (UTC).

## Modifying Agent Templates

Templates live in `orchestration/templates/`. Each template has a specific reader (see inventory below). The Orchestrator reads five templates directly (`implementer-skeleton.md`, `reviewer-skeleton.md`, `review-consolidator-skeleton.md`, `scribe-skeleton.md`, `orchestrator-state.md`); all others are read by subagents or scripts.

### Template inventory

| Template | Read by | Purpose |
|----------|---------|---------|
| `recon-planner.md` | Recon Planner (self-read) | Pre-flight recon instructions |
| `prompt-composer.md` | Prompt Composer (self-read) | Prompt composition instructions |
| `implementation.md` | Implementer (via Prompt Composer composition) | Agent prompt template with 6 mandatory steps |
| `implementation-summary.md` | Prompt Composer | Condensed extract of implementation.md read by Prompt Composer during prompt composition |
| `checkpoints/` | Checkpoint Auditor | Per-checkpoint definitions (common.md + one per type) |
| `reviews.md` | `build-review-prompts.sh` | Review protocol, report format |
| `implementer-skeleton.md` | Orchestrator | Minimal agent spawn template |
| `reviewer-skeleton.md` | Orchestrator, `build-review-prompts.sh` | Review agent spawn template |
| `reviewer-skeleton.md` | Orchestrator, `build-review-prompts.sh` | Reviewer spawn template (alternative skeleton) |
| `review-consolidator-skeleton.md` | Orchestrator, `build-review-prompts.sh` | Review Consolidator spawn template |
| `orchestrator-state.md` | Orchestrator | Session state file schema |
| `scribe-skeleton.md` | Orchestrator | Session Scribe spawn template |
| `review-focus-areas.md` | `build-review-prompts.sh` | Per-type focus blocks for Reviewer prompts |
| `prd-import.md` | Planner | PRD import and requirements extraction instructions |
| `spec-writer.md` | Spec Writer (self-read) | Requirements gathering instructions |
| `spec-writer-skeleton.md` | Planner | Spec Writer spawn template |
| `researcher.md` | Researcher (self-read) | Parallel research instructions |
| `researcher-skeleton.md` | Planner | Researcher spawn template |
| `decomposition.md` | Task Decomposer | Decomposition workflow instructions |
| `task-decomposer-skeleton.md` | Planner | Task Decomposer spawn template |
| `SESSION_PLAN_TEMPLATE.md` | User (optional) | Session planning template for new projects |

### Placeholder conventions

Templates use `{PLACEHOLDER}` (single braces) for values filled by the Orchestrator or Prompt Composer at spawn time. Review skeletons use `{{SLOT_NAME}}` (double braces) for values filled by `build-review-prompts.sh`.

Common placeholders:
- `{TASK_ID}`, `{TASK_SUFFIX}` -- crumb identifiers
- `{SESSION_DIR}` -- session artifact directory path
- `{REVIEW_ROUND}`, `{TIMESTAMP}` -- review cycle metadata
- `{{COMMIT_RANGE}}`, `{{CHANGED_FILES}}`, `{{TASK_IDS}}` -- review slot markers

### What to watch when editing templates

- **`implementation.md`** defines the 6 mandatory steps that every Implementer must follow. If you change a step, update the corresponding pre-spawn-check rule in `checkpoints/pre-spawn-check.md` (pre-spawn-check Check 4 verifies all 6 steps are present).
- **`reviews.md`** defines review types and report format. Changes here must stay in sync with `build-review-prompts.sh` (which reads `reviews.md` to build review prompts) and the review-integrity checks in `checkpoints/review-integrity.md` (which verify report structure).
- **`reviewer-skeleton.md`** and **`review-consolidator-skeleton.md`** are read by `build-review-prompts.sh` to produce filled prompt files. If you change their structure, verify the script still parses them correctly.
- **`implementer-skeleton.md`** is what the Orchestrator uses to spawn agents. If you add fields, the Prompt Composer's task briefs must include the corresponding data.

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
   - Changed `checkpoints/pre-spawn-check.md` pre-spawn-check rules? Verify the pre-spawn-check report in `{SESSION_DIR}/pc/` reflects the new check.
   - Changed `implementation.md`? Verify the Implementer's summary doc follows the updated steps.
   - Changed `reviews.md`? Verify the review previews in `{SESSION_DIR}/previews/` contain the expected content.

### Script validation

For changes to the review pipeline script:

```bash
# Test build-review-prompts.sh:
# Requires a session dir to write output into
./scripts/build-review-prompts.sh <SESSION_DIR> \
  "abc1234..HEAD" $'file1.py\nfile2.py' "task-1 task-2" \
  "$(date +%Y%m%d-%H%M%S)" 1 \
  ~/.claude/orchestration/templates/reviewer-skeleton.md \
  ~/.claude/orchestration/templates/review-consolidator-skeleton.md
```

The script exits 0 on success and prints error messages to stderr on failure.

## Syncing to ~/.claude/

The orchestration framework runs from `~/.claude/`, not from the repo. Changes in the repo must be synced before they take effect.

### What gets synced

`scripts/setup.sh` installs:
- `agents/*.md` to `~/.claude/agents/`
- `orchestration/` to `~/.claude/orchestration/` (existing files in the target that are not in the source are preserved; this means stale files accumulate in `~/.claude/orchestration/` when source files are renamed or deleted -- remove orphaned target files manually)
- `scripts/build-review-prompts.sh` to `~/.claude/orchestration/scripts/`
- `skills/*.md` to `~/.claude/skills/ant-farm-<name>/SKILL.md`
- `crumb.py` to `~/.local/bin/crumb`
- Orchestration block from `orchestration/templates/claude-block.md` to the repo's `CLAUDE.md` (also removes any stale block from global `~/.claude/CLAUDE.md` and from the prompt-dir)

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
| The 6 mandatory steps | `checkpoints/pre-spawn-check.md` pre-spawn-check Check 4 (verifies all 6 steps present) |
| Summary doc format | `checkpoints/claims-vs-code.md` claims-vs-code Check 1-4 (reads summary docs) |
| Scope boundary format | `checkpoints/pre-spawn-check.md` Check 5, `checkpoints/scope-verify.md` (compares scope to diff) |

### checkpoints/ dependencies

| If you change... | Also update... |
|------------------|----------------|
| A checkpoint's verdict thresholds | `RULES.md` Hard Gates table (describes blocking behavior) |
| A checkpoint's model assignment | `orchestration/reference/model-assignments.md` |
| Artifact naming convention | Any template or script that references `{SESSION_DIR}/pc/` paths |
| review-integrity report-count check | `reviews.md` (must match expected report count per round) |

### reviews.md dependencies

| If you change... | Also update... |
|------------------|----------------|
| Review types or report format | `build-review-prompts.sh` (reads reviews.md to build review prompts) |
| Report output paths | `build-review-prompts.sh` `{{REPORT_OUTPUT_PATH}}` slot logic |
| Number of review types per round | `checkpoints/review-integrity.md` review-integrity Check 0 (verifies expected report count) |
| Review types per round | `RULES.md` Step 3b (specifies round 1: 4 types, round 2+: 2 types) |

### Skeleton template dependencies

| If you change... | Also update... |
|------------------|----------------|
| `reviewer-skeleton.md` structure | `build-review-prompts.sh` (parses this file) |
| `review-consolidator-skeleton.md` structure | `build-review-prompts.sh` (parses this file) |
| `implementer-skeleton.md` fields | `prompt-composer.md` (Prompt Composer must produce matching task brief data) |
| Slot marker names (`{{...}}`) | `build-review-prompts.sh` (fills the markers) |

### Agent file dependencies

| If you change... | Also update... |
|------------------|----------------|
| Agent name or tools | `README.md` Custom agents table |
| Agent name or role | `orchestration/reference/agent-types.md`, `orchestration/reference/model-assignments.md` |
| Agent tools list | Verify the agent can still perform its workflow steps |

### RULES.md dependencies

| If you change... | Also update... |
|------------------|----------------|
| Workflow step sequence | `CLAUDE.md` (if it references step numbers) |
| Template lookup table | Verify all referenced file paths exist |
| Concurrency limits | No cross-file deps, but document in CHANGELOG |

### RULES-lite.md dependencies

`orchestration/RULES-lite.md` is the lite mode workflow (single-crumb execution path). It is a standalone document — it does not inherit from RULES.md and should not be treated as a patch on top of it.

| If you change... | Also update... |
|------------------|----------------|
| pre-spawn-check gate rules | Ensure RULES-lite.md Step 2 still references the correct checkpoint files |
| claims-vs-code gate rules | Ensure RULES-lite.md Step 4 still references the correct checkpoint files |
| Progress log step key names | `scripts/parse-progress-log.sh` STEP_KEYS array (lite mode reuses full-mode step keys) |
| When lite mode is appropriate | Update the "Use lite mode when" section in RULES-lite.md and the Lite Mode section in SETUP.md |
| Lite mode glossary terms | `orchestration/GLOSSARY.md` (lite mode and self-review entries) |

### Hook file dependencies

| If you change... | Also update... |
|------------------|----------------|
| `hooks/ant-farm-statusline.js` event parsing | `hooks/lib/progress-reader.js` EVENT_STEP_MAP (must match progress.log event names) |
| `hooks/ant-farm-scope-advisor.js` scope format | `hooks/lib/scope-reader.js`, and any template that writes `.ant-farm-scope.json` |
| Hook file paths or names | `npm/install-manifest.json` (hook entries), `npm/lib/hooks-registration.js` (settings.json paths) |
| `ANT_FARM_DEBUG` logging behavior | `hooks/lib/debug-log.js` |

### MCP server dependencies

| If you change... | Also update... |
|------------------|----------------|
| `mcp_server.py` tool names or signatures | Any orchestration template that references MCP tools (e.g., `recon-planner.md` references `crumb_list`) |
| crumb.py `--json` output schema | `mcp_server.py` (wraps `--json` output), any hook or script that parses JSON output |
| MCP server file path | `npm/install-manifest.json`, `npm/lib/mcp-registration.js` (settings.json config) |

### Skill file dependencies

| If you change... | Also update... |
|------------------|----------------|
| `skills/quick.md` (lite mode skill) | `orchestration/RULES-lite.md` (workflow it triggers), `CLAUDE.md` (trigger documentation) |
| `skills/plan.md` (`--prd` flag) | `orchestration/RULES-decompose.md` (PRD routing logic), `orchestration/templates/prd-import.md` |
| `skills/status.md` | Verify it still reads correct progress.log format and hook status paths |

### Quick checklist for any change

1. Identify which file you changed and check the tables above
2. Update all listed dependent files
3. Run `./scripts/setup.sh`
4. Restart Claude Code if agent files changed
5. Test with a single-task orchestration run
