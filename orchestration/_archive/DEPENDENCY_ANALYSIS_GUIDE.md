# Dependency Analysis Guide

How to analyze task dependencies and file conflicts before spawning agents.

## Pre-Flight Analysis Checklist

Before spawning any agents, complete this analysis:

### 1. Gather Task Metadata (Parallel)

```bash
# For each task ID provided by user
for task_id in $TASK_IDS; do
    bd show $task_id  # Run in parallel, don't read sequentially
done
```

**What to extract:**
- Task title and description
- Acceptance criteria
- File(s) the task will modify (from description or your analysis)
- Dependencies (blocks/blockedBy fields)
- Priority level
- Task type (bug vs feature)

### 2. Check Explicit Dependencies

```bash
# Find tasks that are explicitly blocked
bd blocked

# For each task in your list, check what it blocks/is blocked by
bd show $task_id | grep -E "blocks:|blockedBy:"
```

**Dependency Rules:**
- If Task B is blocked by Task A → A must complete before B starts
- Create dependency chains: A → B → C
- Don't spawn B until A completes

### 3. Analyze File Conflicts (Critical!)

**Create a file modification matrix:**

```python
file_matrix = {
    'build.py': ['task-1', 'task-2', 'task-3', 'task-5'],
    'site.yaml': ['task-4', 'task-6'],
    'templates/index.html': ['task-7', 'task-8'],
    'templates/canvas-work.html': ['task-9'],
    '.htaccess': ['task-10'],
}
```

**Conflict Resolution Strategies:**

#### Strategy 1: Serial Execution (Safest)
```python
# When 3+ tasks touch the same file
if len(tasks_for_file) >= 3:
    execute_serially(tasks_for_file)  # One agent, batched tasks
```

#### Strategy 2: Parallel with Rebase (Risky but Fast)
```python
# When 2 tasks touch different sections of same file
if tasks_modify_different_sections and team_is_experienced:
    execute_parallel_with_rebase(tasks)  # Multiple agents, git rebase
```

#### Strategy 3: Dependency Chaining (Hybrid)
```python
# When tasks have natural ordering
# Example: refactor function, then use new function, then add tests
chain = [
    ('refactor-task', 'agent-1'),
    ('usage-task', 'agent-2', depends_on='refactor-task'),
    ('test-task', 'agent-3', depends_on='usage-task'),
]
```

### 4. Priority Tier Analysis

**Group tasks by priority:**

```python
priority_tiers = {
    'P0': [<critical-incidents>],  # Drop everything
    'P1': [<high-priority>],       # Do first
    'P2': [<medium-priority>],     # Do second
    'P3': [<low-priority-polish>], # Do last
}
```

**Execution Rules:**
1. Always complete P0 before P1
2. P1 before P2
3. P2 before P3
4. **Exception:** P3 clarity fixes that don't conflict can run parallel with P2

### 5. Estimate Agent Load

**Calculate work distribution:**

```python
agent_workload = {
    'agent-1 (build.py validation)': 4 tasks,      # ~30 min
    'agent-2 (build.py error handling)': 4 tasks,  # ~30 min
    'agent-3 (build.py file ops)': 4 tasks,        # ~30 min
    'agent-4 (templates/index.html)': 3 tasks,     # ~20 min
    'agent-5 (templates/canvas-work.html)': 2 tasks, # ~15 min
}

# Target: Roughly balanced (±50%)
# Max: 7 tasks per agent (more = harder to track)
```

## Conflict Detection Patterns

### Pattern 1: Same File, Same Section

**Example:** Two tasks both modify `build.py` line 50-60

**Risk:** 🔴 **HIGH** - Direct conflict almost guaranteed

**Solution:**
```python
# Option A: Serial execution
spawn_agent_1(task_a)
await completion
spawn_agent_2(task_b)

# Option B: Batch to same agent
spawn_agent([task_a, task_b], sequential=True)
```

### Pattern 2: Same File, Different Sections

**Example:** Task A modifies `build.py` load_data(), Task B modifies write_output()

**Risk:** 🟡 **MEDIUM** - May conflict if both touch imports/globals

**Solution:**
```python
# Can go parallel IF:
# - Functions are far apart (different sections)
# - No shared imports/globals
# - Both agents use git pull --rebase before commit

spawn_parallel([task_a, task_b], rebase_before_commit=True)
```

### Pattern 3: Related Files (Cross-File Consistency)

**Example:** Task A modifies `site.yaml`, Task B modifies templates that read site.yaml

**Risk:** 🟡 **MEDIUM** - Semantic conflict (Task B expects old schema)

**Solution:**
```python
# Create explicit dependency
spawn_agent_1(task_a_site_yaml)
await completion
spawn_agent_2(task_b_templates, depends_on=task_a)
```

### Pattern 4: Independent Files

**Example:** Task A modifies `build.py`, Task B modifies `site.yaml`

**Risk:** 🟢 **LOW** - No conflict

**Solution:**
```python
# Full parallel execution
spawn_all_parallel([task_a, task_b, task_c, ...])
```

## Decision Matrix

| Scenario | Same File? | Same Section? | Strategy | Risk |
|----------|------------|---------------|----------|------|
| 2 tasks, same file, same section | ✅ | ✅ | Serial or batch | 🔴 High |
| 3+ tasks, same file | ✅ | Mixed | Batch to 1 agent | 🟡 Medium |
| 2 tasks, same file, different sections | ✅ | ❌ | Parallel + rebase | 🟡 Medium |
| Tasks A→B→C dependency chain | ✅ | ✅ | Sequential spawn | 🟢 Low |
| Independent files | ❌ | N/A | Full parallel | 🟢 Low |
| Related files (schema change) | ❌ | N/A | Dependency chain | 🟡 Medium |

## Example Session Analysis

**User Request:** "Let's get to work on: task-1, task-2, task-3, task-4, task-5"

### Step 1: Metadata Gathered

```
task-1: Fix cache-bust version (files: site.yaml, .htaccess)
task-2: Fix variable mapping (files: build.py)
task-3: Fix directory defaults (files: build.py)
task-4: Add JSON-LD fields (files: site.yaml)
task-5: Fix idempotency (files: build.py)
```

### Step 2: File Conflict Matrix

```python
conflicts = {
    'build.py': [task-2, task-3, task-5],  # 3 tasks! CONFLICT!
    'site.yaml': [task-1, task-4],         # 2 tasks - manageable
    '.htaccess': [task-1],                 # 1 task - no conflict
}
```

### Step 3: Recommendation to User

```markdown
**Analysis Complete:**

I found potential conflicts:
- 3 tasks will modify build.py (task-2, task-3, task-5)
- 2 tasks will modify site.yaml (task-1, task-4)

**Recommended strategy:**

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
```

### Step 4: User Choice Implementation

**User chooses Option B (this session's choice):**

```python
# Spawn all in parallel
agents = [
    spawn('python-pro', [task-2], 'build.py variable mapping'),
    spawn('python-pro', [task-3], 'build.py directory defaults'),
    spawn('python-pro', [task-5], 'build.py idempotency'),
    spawn('refactoring-specialist', [task-1, task-4], 'site.yaml improvements'),
]

# Monitor for conflicts
for agent in agents:
    await_completion(agent)
    if agent.has_conflict:
        alert_user_and_pause()
```

## Red Flags to Watch For

🚩 **More than 3 agents touching same file** - Very high conflict risk
🚩 **Schema/API changes with dependents** - Create explicit dependencies
🚩 **Large refactors + feature additions** - Serial execution required
🚩 **Generated code + manual edits** - Generator must run first
🚩 **Database migrations + code changes** - Migration must complete first

## Conflict Resolution During Session

**If conflict occurs mid-session:**

1. **Detect:**
   ```bash
   # Agent reports: "git push failed - conflicts"
   ```

2. **Pause remaining agents:**
   ```bash
   # Don't spawn more agents until resolved
   ```

3. **Manual resolution:**
   ```bash
   git pull --rebase
   # Resolve conflicts manually
   git rebase --continue
   git commit
   ```

4. **Resume:**
   ```bash
   # Continue with queued agents
   ```

## Best Practices

✅ **Always ask user** when conflict risk is 🟡 Medium or higher
✅ **Prefer batching** over complex dependency chains
✅ **Group by file first**, then by priority
✅ **Test with --dry-run** after agents complete
✅ **Keep conflict groups small** (≤4 tasks per file)
✅ **Document strategy** in session notes

❌ **Don't spawn blind** - Always analyze first
❌ **Don't assume** sections won't overlap - check actual code
❌ **Don't ignore** explicit dependencies in bd show
❌ **Don't over-parallelize** - 7 agents is maximum
