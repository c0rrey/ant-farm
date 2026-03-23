<!-- Reader: Checkpoint Auditor. The Orchestrator does NOT read this file. -->

## Startup Check: Pre-Implementation Strategy Audit

**When**: After Recon Planner returns `{SESSION_DIR}/briefing.md` and BEFORE spawning Prompt Composer (Step 2 in RULES.md)
**Model**: `haiku` (pure set comparisons — no judgment required)

**Why**: The Recon Planner's strategy (wave groupings, task-to-wave assignments, agent batching, file conflict analysis) is currently validated only by human approval, which misses mechanical errors like file/task mismatches, agent overloading, or intra-wave dependency violations. A lightweight automated check before Prompt Composer is spawned catches strategy defects at the cheapest possible point — before any implementation prompts are composed.

**Why haiku**: All four checks are set comparisons, count validations, and dependency graph traversals with no ambiguity. No judgment or code comprehension is required. Haiku handles this class of verification faster and cheaper than sonnet.

```markdown
**Checkpoint Auditor verification - startup-check (Recon Planner Strategy Verification)**

You are the **Checkpoint Auditor**, the verification subagent. Your role is to verify the Recon Planner's execution strategy for mechanical correctness before any implementation work begins. See "Checkpoint Auditor Overview" section above for full conventions.

**Briefing file**: `{SESSION_DIR}/briefing.md`
**Session directory**: `{SESSION_DIR}`

Read the briefing file first to extract the full wave plan (wave numbers, task IDs per wave, agent assignments per task, affected files per task, and inter-task dependencies). Then run all four checks below (1, 1b, 2, 3).

## Check 1: No Unresolved File Overlaps Within a Wave

For each wave in the strategy:
1. Collect all affected files listed for every task in that wave.
2. Check whether any file appears in two or more tasks within the same wave.
3. For each overlap, check whether the overlapping tasks are assigned to the **same agent** in the briefing.
   - **Same agent**: The overlap is resolved — not a violation. Record it as: "Wave N: file `<path>` shared by tasks <id1>, <id2> — RESOLVED (same agent: Agent M)."
   - **Different agents**: The overlap is a conflict. Report as: "Wave N: file `<path>` appears in tasks <id1> (Agent M) AND <id2> (Agent P) — parallel edits would conflict."

File overlaps between tasks assigned to the same agent are safe because a single agent executes its tasks sequentially — no concurrent edits occur. Overlaps between tasks assigned to different agents remain dangerous and must be resolved by moving tasks to separate waves or consolidating them under one agent.

**PASS condition**: Every file overlap within a wave is resolved (all overlapping tasks assigned to the same agent), AND no agent exceeds 3 tasks per wave (see Check 1b).
**FAIL condition**: One or more file overlaps exist between tasks assigned to different agents. List every unresolved violation.

## Check 1b: Agent Task Cap (Max 3 Tasks Per Agent Per Wave)

For each wave in the strategy:
1. Count the number of tasks assigned to each agent.
2. Report any agent with more than 3 tasks as: "Wave N: Agent M has <count> tasks (<id1>, <id2>, ...) — exceeds the 3-task cap."

An agent with too many tasks risks scope creep, context bloat, and reduced quality. The cap ensures each agent's workload stays focused.

**PASS condition**: No agent has more than 3 tasks in any single wave.
**FAIL condition**: One or more agents exceed 3 tasks in a wave. List every violation.

## Check 2: File Lists Match Crumb Descriptions

For each task in the strategy:
1. Use the `crumb_show` MCP tool with `crumb_id: "{TASK_ID}"` to retrieve the crumb's recorded affected files (CLI fallback: `crumb show {TASK_ID}`).
2. Compare the Recon Planner's reported affected files (from briefing.md) against the crumb's actual affected files.
3. Report each mismatch as: "Task {TASK_ID}: Recon Planner lists `<file>` but crumb does not — OR — crumb lists `<file>` but Recon Planner omits it."

**GUARD: Zero-task boundary**
If the strategy contains zero tasks, PASS Check 2 immediately with a note: "No tasks in strategy — file list verification not applicable (vacuous PASS)." Skip the per-task loop below.

**GUARD: crumb_show Failure Handling (INFRASTRUCTURE FAILURE)** _(definition: `orchestration/reference/terms.md` Failure Taxonomy)_
If the `crumb_show` MCP tool (or `crumb show {TASK_ID}` CLI) fails (task not found, unreadable, or crumb command error):
- Record the failure: "{TASK_ID} — crumb_show failed: {error details}"
- Write a note in your verification report: "Could not verify file list for {TASK_ID} via `crumb_show`: {error}. Skipping this task's file list check."
- Continue with the remaining tasks — do NOT abort the entire check.
- Clearly mark skipped tasks in your findings: "[SKIPPED: crumb_show failed]"
- If more than half the tasks fail `crumb_show` (and total tasks > 0), FAIL the check with: "Infrastructure failure: could not verify file lists for majority of tasks."

**PASS condition**: For every task where `crumb_show` succeeds, the Recon Planner's file list exactly matches the crumb's recorded affected files (same set, order-insensitive).
**FAIL condition**: Any file list mismatch detected, or infrastructure failure threshold exceeded. List every discrepancy.

## Check 3: No Intra-Wave Dependency Violations

For each wave in the strategy:
1. Identify all tasks in that wave.
2. Check whether any task in wave N is listed as blocking (or blocked by) another task in the same wave N.
3. To retrieve dependencies: use the `crumb_show` MCP tool with `crumb_id: "{TASK_ID}"` for each task and examine its DEPENDENCIES section (CLI fallback: `crumb show {TASK_ID}`).
4. Report each violation as: "Wave N: task <id1> blocks task <id2> — both are in wave N; <id2> must move to a later wave."

An intra-wave dependency means an agent that is supposed to start in parallel actually depends on another agent finishing first. This defeats the purpose of wave grouping and may cause incorrect ordering.

**GUARD: crumb_show Failure Handling**: Same as Check 2 — if the `crumb_show` MCP tool (or `crumb show` CLI) fails for a task, skip dependency check for that task and note the skip.

**PASS condition**: No task in wave N has a "blocks" or "blocked-by" relationship with another task in the same wave N.
**FAIL condition**: One or more intra-wave dependency violations detected. List every violation.

## Verdict

**PASS** — All 4 checks pass (1, 1b, 2, 3). Report PASS to the Orchestrator. The Orchestrator will auto-proceed to spawn Prompt Composer (Step 2) — do NOT spawn Prompt Composer yourself.

**FAIL: <list each failing check>** — One or more checks failed. Do NOT spawn Prompt Composer. Report specific violations so the Recon Planner can revise the strategy.

**Example FAIL verdict:**

> **Verdict: FAIL**
>
> Check 1 (File Overlaps): FAIL
> - Wave 2: file `src/api/routes.py` appears in tasks ant-farm-abc (Agent 3) AND ant-farm-def (Agent 5) — parallel edits would conflict.
> - Wave 2: file `src/api/models.py` shared by tasks ant-farm-ghi, ant-farm-jkl — RESOLVED (same agent: Agent 3).
>
> Check 1b (Agent Task Cap): PASS
>
> Check 2 (File List Match): PASS
>
> Check 3 (Intra-Wave Dependencies): FAIL
> - Wave 1: task ant-farm-xyz blocks task ant-farm-uvw — both are in Wave 1; ant-farm-uvw must move to Wave 2.
>
> Recommendation: Re-run Recon Planner with these violations noted. Move ant-farm-def to the same agent as ant-farm-abc, or move one to a different wave (file conflict). Move ant-farm-uvw to Wave 2 or later (dependency ordering).

Write your verification report to:
`{SESSION_DIR}/pc/pc-session-startup-check-{timestamp}.md`

Where:
- `{SESSION_DIR}`: session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Checkpoint Auditor Overview)
```

### The Orchestrator's Response

**On PASS**: Auto-proceed to spawn Prompt Composer (Step 2 in RULES.md). The startup-check validates mechanical correctness (no file conflicts, no dependency violations); a PASS is sufficient to begin implementation without waiting for user approval.

**On FAIL**:
1. Log the violation details from the startup-check report.
2. Do NOT spawn Prompt Composer.
3. Re-run Recon Planner with a prompt that includes the specific violations:
   ```
   startup-check found strategy errors that must be corrected before implementation can begin:
   <paste specific violations from startup-check report>
   Please revise the wave plan to resolve these issues and rewrite {SESSION_DIR}/briefing.md.
   ```
4. After Recon Planner revises `{SESSION_DIR}/briefing.md`, re-run startup-check.
5. If startup-check fails a second time, escalate to user with the full violation report.

---
