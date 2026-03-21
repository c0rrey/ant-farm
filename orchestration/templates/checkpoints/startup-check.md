<!-- Reader: Checkpoint Auditor. The Queen does NOT read this file. -->

## Startup Check: Pre-Implementation Strategy Audit

**When**: After Scout returns `{SESSION_DIR}/briefing.md` and BEFORE spawning Pantry (Step 2 in RULES.md)
**Model**: `haiku` (pure set comparisons — no judgment required)

**Why**: The Scout's strategy (wave groupings, task-to-wave assignments, file conflict analysis) is currently validated only by human approval, which misses mechanical errors like file/task mismatches or intra-wave dependency violations. A lightweight automated check before Pantry is spawned catches strategy defects at the cheapest possible point — before any implementation prompts are composed.

**Why haiku**: All three checks are set comparisons and dependency graph traversals with no ambiguity. No judgment or code comprehension is required. Haiku handles this class of verification faster and cheaper than sonnet.

```markdown
**Checkpoint Auditor verification - startup-check (Scout Strategy Verification)**

You are the **Checkpoint Auditor**, the verification subagent. Your role is to verify the Scout's execution strategy for mechanical correctness before any implementation work begins. See "Checkpoint Auditor Overview" section above for full conventions.

**Briefing file**: `{SESSION_DIR}/briefing.md`
**Session directory**: `{SESSION_DIR}`

Read the briefing file first to extract the full wave plan (wave numbers, task IDs per wave, affected files per task, and inter-task dependencies). Then run all three checks below.

## Check 1: No File Overlaps Within a Wave

For each wave in the strategy:
1. Collect all affected files listed for every task in that wave.
2. Check whether any file appears in two or more tasks within the same wave.
3. Report each violation as: "Wave N: file `<path>` appears in tasks <id1> AND <id2> — parallel edits would conflict."

A file overlap within a wave means two agents would edit the same file simultaneously, causing merge conflicts or lost changes. Tasks sharing a file must be serialized into separate waves.

**PASS condition**: No file appears in more than one task within any single wave.
**FAIL condition**: One or more files appear in multiple tasks within the same wave. List every violation.

## Check 2: File Lists Match Crumb Descriptions

For each task in the strategy:
1. Run `crumb show {TASK_ID}` to retrieve the crumb's recorded affected files.
2. Compare the Scout's reported affected files (from briefing.md) against the crumb's actual affected files.
3. Report each mismatch as: "Task {TASK_ID}: Scout lists `<file>` but crumb does not — OR — crumb lists `<file>` but Scout omits it."

**GUARD: crumb show Failure Handling (INFRASTRUCTURE FAILURE)** _(definition: `orchestration/reference/terms.md` Failure Taxonomy)_
If `crumb show {TASK_ID}` fails (task not found, unreadable, or crumb command error):
- Record the failure: "{TASK_ID} — crumb show failed: {error details}"
- Write a note in your verification report: "Could not verify file list for {TASK_ID} via `crumb show`: {error}. Skipping this task's file list check."
- Continue with the remaining tasks — do NOT abort the entire check.
- Clearly mark skipped tasks in your findings: "[SKIPPED: crumb show failed]"
- If more than half the tasks fail `crumb show`, FAIL the check with: "Infrastructure failure: could not verify file lists for majority of tasks."

**PASS condition**: For every task where `crumb show` succeeds, the Scout's file list exactly matches the crumb's recorded affected files (same set, order-insensitive).
**FAIL condition**: Any file list mismatch detected, or infrastructure failure threshold exceeded. List every discrepancy.

## Check 3: No Intra-Wave Dependency Violations

For each wave in the strategy:
1. Identify all tasks in that wave.
2. Check whether any task in wave N is listed as blocking (or blocked by) another task in the same wave N.
3. To retrieve dependencies: run `crumb show {TASK_ID}` for each task and examine its DEPENDENCIES section.
4. Report each violation as: "Wave N: task <id1> blocks task <id2> — both are in wave N; <id2> must move to a later wave."

An intra-wave dependency means an agent that is supposed to start in parallel actually depends on another agent finishing first. This defeats the purpose of wave grouping and may cause incorrect ordering.

**GUARD: crumb show Failure Handling**: Same as Check 2 — if `crumb show` fails for a task, skip dependency check for that task and note the skip.

**PASS condition**: No task in wave N has a "blocks" or "blocked-by" relationship with another task in the same wave N.
**FAIL condition**: One or more intra-wave dependency violations detected. List every violation.

## Verdict

**PASS** — All 3 checks pass. Report PASS to the Queen. The Queen will auto-proceed to spawn Pantry (Step 2) — do NOT spawn Pantry yourself.

**FAIL: <list each failing check>** — One or more checks failed. Do NOT spawn Pantry. Report specific violations so the Scout can revise the strategy.

**Example FAIL verdict:**

> **Verdict: FAIL**
>
> Check 1 (File Overlaps): FAIL
> - Wave 2: file `src/api/routes.py` appears in tasks ant-farm-abc AND ant-farm-def — parallel edits would conflict.
>
> Check 2 (File List Match): PASS
>
> Check 3 (Intra-Wave Dependencies): FAIL
> - Wave 1: task ant-farm-xyz blocks task ant-farm-uvw — both are in Wave 1; ant-farm-uvw must move to Wave 2.
>
> Recommendation: Re-run Scout with these violations noted. Move ant-farm-def or ant-farm-abc to a different wave (file conflict), and move ant-farm-uvw to Wave 2 or later (dependency ordering).

Write your verification report to:
`{SESSION_DIR}/pc/pc-session-startup-check-{timestamp}.md`

Where:
- `{SESSION_DIR}`: session artifact directory (e.g., `.crumbs/sessions/_session-abc123`)
- timestamp: format defined in **Timestamp format** (Checkpoint Auditor Overview)
```

### The Queen's Response

**On PASS**: Auto-proceed to spawn Pantry (Step 2 in RULES.md). The startup-check validates mechanical correctness (no file conflicts, no dependency violations); a PASS is sufficient to begin implementation without waiting for user approval.

**On FAIL**:
1. Log the violation details from the startup-check report.
2. Do NOT spawn Pantry.
3. Re-run Scout with a prompt that includes the specific violations:
   ```
   startup-check found strategy errors that must be corrected before implementation can begin:
   <paste specific violations from startup-check report>
   Please revise the wave plan to resolve these issues and rewrite {SESSION_DIR}/briefing.md.
   ```
4. After Scout revises `{SESSION_DIR}/briefing.md`, re-run startup-check.
5. If startup-check fails a second time, escalate to user with the full violation report.

---
