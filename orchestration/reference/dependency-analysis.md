# Dependency Analysis Reference

Pre-flight conflict analysis and agent spawn patterns for parallel orchestration.

## Term Definitions (Canonical)

These definitions apply across all orchestration templates and reference files.

### {TASK_ID}

Full bead ID including project prefix.

**Format**: `<project>-<suffix>` or `<project>-<suffix>.<sub-id>`

**Examples**:
- `ant-farm-9oa` — full ID, no sub-ID
- `hs_website-74g.1` — full ID with sub-ID

### {TASK_SUFFIX}

Suffix portion only, extracted from {TASK_ID} by splitting on the LAST hyphen and removing any leading dots.

**Extraction rule**: Split on the LAST hyphen (`-`), take the right side, then remove any leading dots from the result.

**Regex**: `^.*-(.+)$` → capture group 1, with dots normalized to the numeric suffix pattern

**Algorithm (step-by-step)**:
1. Locate the LAST hyphen (`-`) in {TASK_ID}
2. Extract everything after the last hyphen: `ant-farm-9oa` → `9oa`, `ant-farm-74g.1` → `74g.1`
3. If the result contains a dot followed by digits, convert to alphanumeric suffix: `74g.1` → `74g1`
4. Return the suffix

**Examples**:
- `ant-farm-9oa` → `9oa` (no hyphens in project name; remove project prefix)
- `ant-farm-b61` → `b61` (no hyphens in project name; remove project prefix)
- `ant-farm-74g.1` → `74g1` (with dotted sub-ID; remove project prefix, normalize dot)
- `hs_website-74g.1` → `74g1` (no hyphens in project; remove prefix, normalize dot)
- `my-project-abc.10` → `abc10` (hyphen in project name; split on last hyphen, normalize dot)

**Usage context**:
- File paths: `{SESSION_DIR}/task-metadata/{TASK_SUFFIX}.md`
- Directories: `{SESSION_DIR}/summaries/{TASK_SUFFIX}.md`
- Artifact naming: `pc-{TASK_SUFFIX}-cco-{timestamp}.md`

### {SESSION_DIR}

Session artifact directory path containing task metadata, prompts, summaries, and verification checkpoints.

**Format**: `.beads/agent-summaries/_session-<id>`

**Example**: `.beads/agent-summaries/_session-abc123` or `.beads/agent-summaries/_session-3be37d`

---

## Pre-Flight Checklist

Before spawning any agents:

1. **Gather task metadata** (parallel `bd show` calls) — extract title, files modified, dependencies (blocks/blockedBy), priority
2. **Check explicit dependencies** — run `bd blocked`, create dependency chains (A → B → C)
3. **Build file modification matrix** — map which tasks touch which files
4. **Assess conflict risk** — use Decision Matrix below
5. **Estimate agent load** — target balanced workload (±50%), max 7 tasks/agent
6. **Return briefing to the Queen** — the Queen presents strategy to user and waits for approval

## Decision Matrix

| Scenario | Same File? | Same Section? | Strategy | Risk |
|----------|------------|---------------|----------|------|
| 2 tasks, same file, same section | ✅ | ✅ | Serial or batch | 🔴 High |
| 3+ tasks, same file | ✅ | Mixed | Batch to 1 agent | 🟡 Medium |
| 2 tasks, same file, different sections | ✅ | ❌ | Parallel + rebase | 🟡 Medium |
| Tasks A→B→C dependency chain | ✅ | ✅ | Sequential spawn | 🟢 Low |
| Independent files | ❌ | N/A | Full parallel | 🟢 Low |
| Related files (schema change) | ❌ | N/A | Dependency chain | 🟡 Medium |

## Conflict Patterns

### Pattern 1: Same File, Same Section
**Risk:** 🔴 HIGH — Direct conflict almost guaranteed. Use serial execution or batch both tasks to same agent.

### Pattern 2: Same File, Different Sections
**Risk:** 🟡 MEDIUM — May conflict if both touch imports/globals. Can go parallel IF functions are far apart, no shared globals, and both agents use `git pull --rebase` before commit.

### Pattern 3: Related Files (Cross-File Consistency)
**Risk:** 🟡 MEDIUM — Semantic conflict (Task B expects old schema). Create explicit dependency: Task A (schema) must complete before Task B (usage).

### Pattern 4: Independent Files
**Risk:** 🟢 LOW — No conflict. Full parallel execution safe.

## Example Session Analysis

**User Request:** "Let's get to work on: task-1, task-2, task-3, task-4, task-5"

**Metadata gathered:**
```
task-1: Fix cache-bust version (files: site.yaml, .htaccess)
task-2: Fix variable mapping (files: build.py)
task-3: Fix directory defaults (files: build.py)
task-4: Add JSON-LD fields (files: site.yaml)
task-5: Fix idempotency (files: build.py)
```

**File conflict matrix:**
```
build.py: [task-2, task-3, task-5]  # 3 tasks! CONFLICT!
site.yaml: [task-1, task-4]         # 2 tasks - manageable
.htaccess: [task-1]                 # 1 task - no conflict
```

**Recommendation to user:**

Option A (Safest - Sequential):
- Agent 1: build.py tasks (task-2, task-3, task-5) in sequence
- Agent 2: site.yaml + .htaccess (task-1, task-4) in sequence
- Estimated time: 45-60 minutes

Option B (Faster - Parallel with rebase):
- Agent 1: task-2 (build.py variable mapping)
- Agent 2: task-3 (build.py directory defaults)
- Agent 3: task-5 (build.py idempotency)
- Agent 4: task-1 + task-4 (site.yaml changes batched)
- All agents use git pull --rebase before commit
- Risk: Possible merge conflicts if build.py sections overlap
- Estimated time: 20-30 minutes

Which strategy do you prefer?

## Agent Spawn Patterns

### Pattern 1: File-Based Grouping (Prevents Conflicts)

Group tasks by primary file modified. Spawn one agent per group to avoid same-file conflicts.

**Conflict risk assessment:**
- **LOW**: Different files, or same file with non-overlapping line ranges >10 lines apart
- **MEDIUM**: Same file, line ranges within 10 lines of each other
- **HIGH**: 3+ tasks on same file, or overlapping line ranges

**Strategy selection:**
- **LOW risk** → Parallel spawn (3-7 agents)
- **MEDIUM risk** → Wave-based (2-3 agents per wave, serialize overlapping ranges)
- **HIGH risk** → Serial execution OR bundle into single agent

**Known failure mode:** Epic 74g spawned 3 agents in parallel on same file without line range analysis. Result: work scrambling (agents did each other's tasks). Prevention: Use wave-based or serial execution for HIGH risk scenarios.

### Pattern 2: Dependency-Aware Sequencing

Multi-file tasks must wait for single-file tasks. Cross-cutting tasks (integration tests, schema migrations) wait for dependencies to complete. Use explicit dependency tracking.

### Pattern 3: Priority Tier Batching

- P1 tasks (critical bugs) → spawn immediately, all parallel if no file conflicts
- P2 tasks (high priority) → spawn after P1 OR in parallel if no file conflicts
- P3 tasks (polish) → spawn only after P1+P2 complete

Typical wave pattern: P1 wave (7 tasks) → P2 wave (6 agents, file-grouped) → P3 wave (6 agents, file-grouped).

## Subagent Type Mapping

Agent type selection is performed dynamically by the Scout (Step 2.5 of
`scout.md`). The Scout scans `~/.claude/agents/*.md` and `.claude/agents/*.md`,
reads frontmatter descriptions, and recommends the best match per task.

Legacy defaults retained for reference:

| Task Category | Subagent Type | Rationale |
|---------------|---------------|-----------|
| Template/Jinja2 work | `python-pro` | Python ecosystem expertise |
| Build system changes | `python-pro` | Build scripts are Python |
| CSS/HTML implementation | `nextjs-developer` or `javascript-pro` | Frontend expertise |
| Build verification | `debugger` | Diagnostic and troubleshooting focus |
| Nitpickers (all 4) | `code-reviewer` / `sonnet` | Code analysis focus |
| Big Head (consolidation) | `opus` | Cross-report judgment, dedup, priority calibration |
| General implementation | Match specialist to primary file type | Best domain expertise |

## Red Flags

🚩 More than 3 agents touching same file — Very high conflict risk
🚩 Schema/API changes with dependents — Create explicit dependencies
🚩 Large refactors + feature additions — Serial execution required
🚩 Generated code + manual edits — Generator must run first
🚩 Database migrations + code changes — Migration must complete first

## Best Practices

✅ Always ask user when conflict risk is 🟡 Medium or higher
✅ Prefer batching over complex dependency chains
✅ Group by file first, then by priority
✅ Keep conflict groups small (≤4 tasks per file)
✅ Document strategy in session notes

❌ Don't spawn blind — Always analyze first
❌ Don't assume sections won't overlap — Check actual code
❌ Don't ignore explicit dependencies in bd show
❌ Don't over-parallelize — 7 agents is maximum
