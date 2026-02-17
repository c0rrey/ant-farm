# Session Plan Template

Use this template for planning multi-agent orchestration sessions.

## Session Overview

**Date:** YYYY-MM-DD
**Boss-Bot:** Claude Sonnet 4.5
**User Request:** [Paste original request here]
**Task IDs:** [List all task IDs]
**Epic:** [If applicable]

---

## Pre-Flight Analysis

### Task Metadata Summary

| Task ID | Title | Files Modified | Priority | Depends On | Blocks |
|---------|-------|----------------|----------|------------|--------|
| xxx-001 | Description | file.py | P1 | - | xxx-002 |
| xxx-002 | Description | file.py, test.py | P2 | xxx-001 | - |
| ... | ... | ... | ... | ... | ... |

### File Conflict Matrix

```
build.py: [xxx-001, xxx-002, xxx-005]       → 3 tasks (CONFLICT RISK)
site.yaml: [xxx-003, xxx-004]               → 2 tasks (manageable)
templates/index.html: [xxx-006]             → 1 task (no conflict)
```

### Dependency Graph

```mermaid
graph TD
    A[xxx-001: Task A] --> B[xxx-002: Task B]
    A --> C[xxx-003: Task C]
    B --> D[xxx-004: Task D]
    C --> D
```

### Conflict Risk Assessment

- 🔴 **HIGH RISK:** build.py (3 tasks, overlapping sections)
- 🟡 **MEDIUM RISK:** site.yaml (2 tasks, schema change + usage)
- 🟢 **LOW RISK:** templates (independent files)

---

## Execution Strategy

### Option A: Maximum Safety (Serial)

**Approach:** Sequential execution, batched by file

**Agent Groups:**
1. **build.py group** (3 tasks: xxx-001, xxx-002, xxx-005)
   - Agent: python-pro
   - Execution: Sequential within agent
   - Estimated time: 45 min

2. **site.yaml group** (2 tasks: xxx-003, xxx-004)
   - Agent: refactoring-specialist
   - Execution: Sequential within agent
   - Estimated time: 20 min

3. **templates group** (1 task: xxx-006)
   - Agent: refactoring-specialist
   - Execution: Immediate
   - Estimated time: 15 min

**Total estimated time:** 80 minutes
**Conflict risk:** 🟢 Very Low
**Parallelization:** Minimal (only independent files)

### Option B: Balanced (Recommended)

**Approach:** Parallel where safe, serial where risky

**Wave 1 (Parallel):**
- Agent 1: xxx-001 (build.py - foundational change)
- Agent 2: xxx-003 (site.yaml - schema change)
- Agent 3: xxx-006 (templates - independent)

**Wave 2 (After Wave 1 completes):**
- Agent 4: xxx-002, xxx-005 (build.py - depends on xxx-001)
- Agent 5: xxx-004 (site.yaml - depends on xxx-003)

**Total estimated time:** 35-45 minutes
**Conflict risk:** 🟡 Low-Medium (managed via dependencies)
**Parallelization:** High (3 agents → 2 agents)

### Option C: Maximum Speed (Parallel + Rebase)

**Approach:** All parallel, let git rebase handle conflicts

**All at once:**
- Agent 1: xxx-001 (build.py validation)
- Agent 2: xxx-002 (build.py error handling)
- Agent 3: xxx-005 (build.py idempotency)
- Agent 4: xxx-003, xxx-004 (site.yaml batched)
- Agent 5: xxx-006 (templates)

**Total estimated time:** 20-30 minutes
**Conflict risk:** 🟡 Medium (multiple agents → build.py)
**Parallelization:** Maximum (5 concurrent agents)
**Requires:** Experienced with git rebase conflict resolution

---

## User Approval Checkpoint

**Present to user:**

> I analyzed the 6 tasks you requested. Here's what I found:
>
> **Conflict Analysis:**
> - 3 tasks modify build.py (potential conflicts)
> - 2 tasks modify site.yaml (manageable)
> - 1 task modifies templates (no conflicts)
>
> **I recommend Option B (Balanced):**
> - Wave 1: 3 agents in parallel (foundational changes)
> - Wave 2: 2 agents after Wave 1 (dependent changes)
> - Estimated time: 35-45 minutes
> - Conflict risk: Low-Medium (managed via dependencies)
>
> Alternative options:
> - Option A: Serial execution (safer, 80 min)
> - Option C: Full parallel (faster, 20-30 min, higher conflict risk)
>
> Which strategy would you prefer?

**Wait for user response before spawning agents.**

---

## Execution Plan (Selected Strategy)

**Strategy chosen:** [Option A / B / C]

### Agent Spawn Sequence

#### Wave 1: [Name]

```python
spawn(
    subagent_type='python-pro',
    description='xxx-001: Task description',
    tasks=['xxx-001'],
    files=['build.py'],
    background=True,
)

spawn(
    subagent_type='refactoring-specialist',
    description='xxx-003: Task description',
    tasks=['xxx-003'],
    files=['site.yaml'],
    background=True,
)

# ... more agents
```

**Monitor:** TaskCreate for each agent

#### Wave 2: [Name]

**Trigger:** After Wave 1 completes
**Dependencies:** xxx-001, xxx-003 must be committed

```python
# Wait for Wave 1 completion
await_all_complete(wave_1_agents)

# Check for conflicts
verify_no_conflicts()

# Spawn Wave 2
spawn(
    subagent_type='python-pro',
    description='xxx-002, xxx-005: Batched build.py tasks',
    tasks=['xxx-002', 'xxx-005'],
    files=['build.py'],
    background=True,
)
```

---

## Quality Review Plan

After all implementation agents complete:

### Review Wave (Sequential)

1. **Clarity Review**
   - Agent: refactoring-specialist (sonnet)
   - Files: All changed files
   - Output: P3 clarity bugs
   - Estimated: 15 min

2. **Edge Cases Review**
   - Agent: code-reviewer (sonnet)
   - Files: All changed files
   - Output: P2 edge case bugs
   - Estimated: 20 min

3. **Correctness Redux Review**
   - Agent: code-reviewer (sonnet)
   - Files: All changed files + acceptance criteria
   - Output: P1-P2 correctness bugs
   - Estimated: 25 min

4. **Excellence Review**
   - Agent: code-reviewer (sonnet)
   - Files: All changed files
   - Output: P3 excellence features
   - Estimated: 30 min

**Total review time:** ~90 minutes
**Expected output:** 30-50 new beads filed

### Review Follow-Up Decision

**If <5 P1/P2 issues found:**
- Document in CHANGELOG
- Proceed to push
- Address in future session

**If 5-15 P1/P2 issues found:**
- Ask user: Fix now or later?
- If now: Group by file and spawn fix agents
- If later: Document and push

**If >15 P1/P2 issues found:**
- Quality gate failure
- Must address before push
- Group and spawn fix agents
- May need to re-run reviews after fixes

---

## Documentation Plan

Files to update after all work completes:

- [ ] **CHANGELOG.md** - Add entries under [Unreleased]
  - Original task descriptions
  - P2 bug fix summaries
  - P3 improvement summaries
  - New features added
  - Breaking changes (if any)

- [ ] **README.md** - Update if needed
  - New scripts or tools
  - New directory structure
  - New dependencies
  - Usage examples changed

- [ ] **CLAUDE.md** - Update if needed
  - Architecture changes
  - New file locations
  - Process changes
  - Important decisions

- [ ] **Other docs** - Project-specific
  - API docs
  - User guides
  - Configuration examples

**Single commit:** `docs: update documentation for [session summary]`

---

## Landing the Plane Checklist

Before declaring session complete:

### Pre-Push Verification

- [ ] All spawned agents completed (none stuck/errored)
- [ ] All TaskCreate entries marked completed
- [ ] All beads tasks closed (bd close <ids>)
- [ ] Git working tree clean (git status)
- [ ] Build/test quality gates passed
  - [ ] `python build.py --dry-run` succeeds
  - [ ] `pytest tests/` passes (if tests exist)
  - [ ] Linter passes (if configured)

### Documentation Complete

- [ ] CHANGELOG.md updated
- [ ] README.md updated (if needed)
- [ ] CLAUDE.md updated (if needed)
- [ ] All cross-references verified (no broken links)

### Git Operations

- [ ] `git pull --rebase` (check for remote changes)
- [ ] `bd sync` (sync beads with remote)
- [ ] `git push` (**MANDATORY** - not done until pushed!)
- [ ] `git status` shows "up to date with origin/main"
- [ ] Beads sync status clean (bd sync --status)

### Handoff

- [ ] Session summary created
- [ ] Commit list documented
- [ ] New beads filed (if any remain open)
- [ ] Context for next session provided

---

## Session Metrics (Track These)

**Efficiency Metrics:**
- Tasks completed: ___ / ___
- Agents spawned: ___
- Commits created: ___
- Time elapsed: ___ minutes
- Token budget used: ___K / 200K (___%)

**Quality Metrics:**
- P1 bugs filed: ___
- P2 bugs filed: ___
- P3 improvements filed: ___
- Test coverage: ___% (if applicable)
- Build success: ✅ / ❌

**Conflict Metrics:**
- Merge conflicts encountered: ___
- Conflicts resolved: ___
- Commits rebased: ___
- Strategy changes mid-session: ___

**Context Preservation:**
- Implementation files read in boss-bot window: ___ (target: <10)
- Token budget remaining: ___K (target: >100K)
- Boss-bot stayed focused: ✅ / ❌

---

## Lessons Learned

**What worked well:**
- [Document successful patterns]

**What could improve:**
- [Document pain points and ideas]

**For next session:**
- [Action items and improvements]

---

## Template Usage Instructions

1. **Copy this template** at start of session
2. **Fill out Pre-Flight Analysis** after gathering task metadata
3. **Present Execution Strategy options** to user
4. **Wait for approval** before spawning agents
5. **Update in real-time** as session progresses
6. **Complete metrics** at end of session
7. **Archive** in session-notes/ directory for future reference
