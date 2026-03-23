# Decomposition Workflow Rules

> This is the Planner's workflow document for `/ant-farm-plan`. The Planner reads THIS file alone
> and follows it exactly. Do NOT read `orchestration/RULES.md` — it governs the Orchestrator's
> implementation session workflow, which is separate from decomposition.

## Path Reference Convention

All file paths in this document use **repo-root relative** format: `orchestration/templates/spec-writer.md`.

When code runs at runtime, agent files are synced to `~/.claude/agents/` and orchestration files are
accessible at `~/.claude/orchestration/`. To translate repo paths to runtime paths:
- Replace `orchestration/` with `~/.claude/orchestration/`
- Replace `agents/` with `~/.claude/agents/`

---

## Planner Prohibitions (read FIRST)

- **NEVER** run `crumb show`, `crumb ready`, `crumb list`, `crumb blocked`, or any `crumb` query command
- **NEVER** read source code, test files, or application data files directly — agents do this
- **NEVER** read agent instruction files (`ant-farm-spec-writer.md`, `ant-farm-researcher.md`, `decomposition.md`) —
  pass the path to the agent and let it read its own instructions
- **NEVER** set `run_in_background` on Task agents — multiple Task calls in one message already
  run concurrently; background mode leaks JSONL transcripts into the Planner's context
- **NEVER** spawn the Task Decomposer until ALL four Researcher outputs exist and the spec quality gate passes
- **NEVER** create trails or crumbs yourself — only the Task Decomposer does this via `crumb` CLI

---

## Planner Orchestrator Profile

The Planner is a distinct orchestrator from the Orchestrator. Understanding this distinction prevents
misapplying Orchestrator patterns to decomposition sessions.

### Distinction from Orchestrator

| Dimension | Planner | Orchestrator |
|-----------|---------|-------|
| Trigger | `/ant-farm-plan` command | "let's get to work" message |
| Purpose | Decompose a feature into trails and crumbs | Execute a prepared work session |
| Workflow file | `orchestration/RULES-decompose.md` (this file) | `orchestration/RULES.md` |
| Read permissions | `spec.md` and `decomposition-brief.md` only | `orchestrator-state.md`, task files, git diffs |
| State tracking | Step number + per-agent retry count (in context only) | `orchestrator-state.md` written to disk |
| Primary agents | Spec Writer, Researcher x4, Task Decomposer | Recon Planner, Prompt Composer, Checkpoint Auditor, Reviewer |
| Context budget target | 15–20% of context window | Not separately specified |
| `crumb` CLI usage | Prohibited — only the Task Decomposer calls `crumb` | Orchestrator calls `crumb` directly |

The Planner MUST NOT read `orchestration/RULES.md`. The Orchestrator MUST NOT read this file. They are
separate orchestrators with non-overlapping roles.

### State Tracking

The Planner tracks state **in context only** — no state file is written to disk during a
decomposition session.

State tracked:
- **Current step** (0–6): derived from progress log and agent return values
- **Retry count per agent**: incremented each time an agent is re-spawned for a gate failure
  - PRD Importer retry count (max 1, PRD path only)
  - Spec Writer retry count (max 1, freeform path only)
  - Per-Researcher retry count (max 1 each)
  - Task Decomposer retry count (max 2)

The Planner does NOT use `orchestrator-state.md`. That file belongs to the Orchestrator's implementation
workflow. Writing a state file during decomposition would be a scope violation.

**Recovery**: If the Planner's context is lost mid-session, the `progress.log` serves as a
recoverable audit trail. The Planner can re-read the progress log (via bash) to determine
which steps completed without re-reading any agent instruction files or research briefs.

### Context Budget

**Target: 15–20% of the context window.**

Reasoning: A decomposition session involves multiple round-trips with interactive agents. The
Spec Writer may ask the user several questions and return a multi-section spec. Four Researchers each
return summaries. The Task Decomposer returns a structured brief. If the Planner's context fills up
during Step 3 or Step 4 returns, it cannot process gate checks or spawn the next agent.

The 15–20% budget preserves capacity for:
- Up to 4 Researcher return summaries
- The Spec Writer spec (read at Step 2 gate)
- The Task Decomposer's decomposition brief (read at Step 4 gate)
- Gate check outputs and progress log appends

If the feature request is very large (> 500 words), summarize it internally before spawning any
agent. Do NOT pass the raw user input verbatim to every agent prompt — use the structured
`{SPEC_PATH}` reference instead once spec.md exists.

---

## Planner Read Permissions

The Planner's context window is restricted to prevent bloat. The following are explicitly permitted.

**PERMITTED (Planner reads these directly):**
- `{DECOMPOSE_DIR}/spec.md` — Spec Writer output; Planner reads after spec quality gate to confirm
  requirement count before spawning Researchers
- `{DECOMPOSE_DIR}/decomposition-brief.md` — Task Decomposer output; Planner reads to confirm trail and
  crumb counts before closing the decomposition session

**FORBIDDEN (agents read; Planner never reads):**
- `orchestration/templates/spec-writer.md` — Spec Writer's instruction file
- `orchestration/templates/researcher.md` — Researcher's instruction file
- `orchestration/templates/decomposition.md` — Task Decomposer's instruction file
- `{DECOMPOSE_DIR}/research/*.md` — Researcher research briefs (Task Decomposer reads these)
- Source code files, test files, application configs, project data files
- Raw `crumb show`, `crumb list`, `crumb trail status` output (let the Task Decomposer handle CLI calls)

---

## Workflow: `/ant-farm-plan`

**Step 0:** Session setup — generate a DECOMPOSE_ID and DECOMPOSE_DIR. Store both as variables.

```bash
DECOMPOSE_ID=$(date +%Y%m%d-%H%M%S)
DECOMPOSE_DIR=".crumbs/sessions/_decompose-${DECOMPOSE_ID}"
mkdir -p "${DECOMPOSE_DIR}/research"
```

Store DECOMPOSE_DIR in your context. Pass it explicitly to every agent.

If `INPUT_CLASS=PRD`, also record the PRD path in the manifest. Write a manifest file to capture session metadata:

```bash
# For PRD input:
jq -n \
  --arg decompose_id "${DECOMPOSE_ID}" \
  --arg input_source "prd:<PRD_PATH>" \
  --arg input_class "PRD" \
  --arg prd_path "<PRD_PATH>" \
  --arg created_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{decompose_id: $decompose_id, input_source: $input_source, input_class: $input_class, prd_path: $prd_path, created_at: $created_at}' \
  > "${DECOMPOSE_DIR}/manifest.json"

# For STRUCTURED or FREEFORM input (existing behavior):
jq -n \
  --arg decompose_id "${DECOMPOSE_ID}" \
  --arg input_source "<INPUT_SOURCE>" \
  --arg input_class "<INPUT_CLASS>" \
  --arg created_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{decompose_id: $decompose_id, input_source: $input_source, input_class: $input_class, created_at: $created_at}' \
  > "${DECOMPOSE_DIR}/manifest.json"
```

**Brownfield vs. greenfield detection**: Before spawning any agent, run:

> **Before running**: substitute `{CODEBASE_ROOT}` with the absolute repo root path (e.g., `/Users/user/projects/myapp`). Do NOT run this block with the literal string `{CODEBASE_ROOT}`.

```bash
[ -d "${CODEBASE_ROOT}" ] || { echo "ERROR: CODEBASE_ROOT is not set or does not exist"; exit 1; }
find "${CODEBASE_ROOT}" -maxdepth 2 \
  -not -path "*/.git/*" \
  -not -name "*.md" \
  -not -name "*.yaml" \
  -not -name "*.yml" \
  -not -name "*.toml" \
  -not -name "*.cfg" \
  -not -name "*.ini" \
  -not -name ".gitignore" \
  -not -name ".env*" \
  -not -name "LICENSE" \
  -type f | wc -l
```

**Heuristic**: 5 or more non-config files → **brownfield**. Fewer than 5 → **greenfield**.
<!-- Threshold rationale: 5 was chosen as the minimum that distinguishes a project with a real
     established code structure (e.g., at least one module, one entry point, one test, one config
     adapter, and one utility) from a near-empty scaffold. Values below 5 are consistent with a
     freshly-initialised repo and receive greenfield treatment. -->
Record the result as `CODEBASE_MODE=brownfield|greenfield` in your context and pass it to the
Spec Writer in its spawn prompt. The Task Decomposer uses this to decide whether to reference existing file
paths or propose new ones.

**Context budget target**: Keep the Planner's total context at 15–20% of the context window.
This leaves room for up to 4 Researcher returns, the Spec Writer spec, and the Task Decomposer's brief.
If the feature request is very large (> 500 words), summarize it internally before spawning agents.

**Progress log:**
```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|DECOMPOSE_INIT|complete|decompose_dir=${DECOMPOSE_DIR}" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

---

**Step 1:** Input classification — determine whether the user's input is a **freeform request**,
            a **structured spec**, or a **PRD import** (`INPUT_CLASS=PRD`).

**PRD import (check FIRST)**: If `INPUT_CLASS=PRD` was set by the skill (because the user
invoked `/ant-farm-plan --prd <file>`), skip all classification logic and go directly to the
PRD import path below. Do NOT re-validate the file here — the skill already confirmed it exists
and is non-empty.

**If PRD import (`INPUT_CLASS=PRD`):**

Spawn the PRD Importer using `orchestration/templates/prd-import.md` as a guide.

```
Task(
  subagent_type="ant-farm-spec-writer",
  model="opus",
  prompt="<filled prd-import.md template — see orchestration/templates/prd-import.md>"
)
```

The PRD Importer reads the file at `PRD_PATH`, extracts requirements into spec.md format,
presents a summary to the user for confirmation (via `AskUserQuestion`), and writes
`{DECOMPOSE_DIR}/spec.md` only after the user confirms. It may return one of three outcomes:

- **success** → spec.md written and user has already confirmed; run the spec quality gate
  (same gate as after Step 2), then proceed directly to Step 3 (Researchers). Do NOT spawn
  the Spec Writer. Step 3.5 (user approval) still applies before the Task Decomposer.
- **fallback_to_surveyor** → PRD had no testable ACs; tell the user why the fallback happened,
  then spawn the Spec Writer in Step 2 passing the PRD path as the `{FEATURE_REQUEST}` context.
- **error** → PRD Importer could not parse or write the spec; surface the error to the user
  and stop.

**IMPORTANT — confirmation ordering**: The PRD Importer handles user confirmation of extracted
requirements *before* writing spec.md. This means confirmation happens before Researcher spawning.
Do NOT spawn Researchers until the PRD Importer returns with **success** outcome.

Record in progress log:
```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|INPUT_CLASS|prd|prd_path=<PRD_PATH>" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

---

**Spec quality gate (PRD path)**: After the PRD Importer returns **success**, run the same
spec quality gate that applies after Step 2 (Spec Writer):
- [ ] `{DECOMPOSE_DIR}/spec.md` exists and is non-empty
- [ ] Contains at least one `REQ-N:` heading
- [ ] Every REQ-N has at least one `AC-N.M:` entry
- [ ] No acceptance criteria contain banned vague phrases
- [ ] `## Scope` section is present
- [ ] `## Non-Requirements` section is present

**On gate PASS**: Proceed to Step 3 (Researchers).

**On gate FAIL**: Re-spawn the PRD Importer with the specific violations. Maximum **1 retry**.
If spec still fails after one retry, present the violations to the user and await instruction.

```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SPEC_QUALITY_GATE|pass|source=prd|spec=${DECOMPOSE_DIR}/spec.md" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

---

**Classification for non-PRD input:**

A structured spec has ALL of these:
- Numbered requirements (`REQ-N:` headings or equivalent)
- Acceptance criteria for each requirement
- A stated scope / non-requirements section

A freeform request lacks one or more of these. When in doubt, treat as freeform.

**If structured spec:** Write the input verbatim to `{DECOMPOSE_DIR}/spec.md`. Skip Step 2
(Spec Writer). Then prompt the user:

> "This looks like a structured spec. Want me to run research agents to investigate technical
> decisions before decomposing, or decompose directly?"

- If research requested → proceed to Step 3 (Researchers).
- If direct decomposition → skip to Step 4 (Task Decomposer).

Record in progress log:
```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|INPUT_CLASS|structured|spec=${DECOMPOSE_DIR}/spec.md" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

**If freeform request:** Proceed to Step 2.
```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|INPUT_CLASS|freeform|spec=pending" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

---

**Step 2:** Requirements gathering — spawn the Spec Writer (freeform input only).

Spawn the Spec Writer using `orchestration/templates/spec-writer-skeleton.md` as a guide.
Do NOT read `ant-farm-spec-writer.md` yourself — pass its path to the Spec Writer agent.

```
Task(
  subagent_type="ant-farm-spec-writer",
  model="opus",
  prompt="<filled spec-writer-skeleton.md template — see orchestration/templates/spec-writer-skeleton.md>"
)
```

The Spec Writer interacts with the user via `AskUserQuestion`, then writes `{DECOMPOSE_DIR}/spec.md`.

**Spec quality gate** (HARD GATE — blocks Step 3):

After the Spec Writer returns, verify `{DECOMPOSE_DIR}/spec.md` passes ALL of the following:
- [ ] File exists and is non-empty
- [ ] Contains at least one `REQ-N:` heading
- [ ] Every REQ-N has at least one `AC-N.M:` entry
- [ ] No acceptance criteria contain banned vague phrases: "works correctly", "as expected",
      "handles gracefully", "is well-structured", "user-friendly", "performant" (without a
      number), "reasonable" (without a definition)
- [ ] `## Scope` section is present
- [ ] `## Non-Requirements` section is present

**On gate PASS**: Read `{DECOMPOSE_DIR}/spec.md` (permitted) to confirm requirement count.
Proceed to Step 3.

**On gate FAIL (spec incomplete)**: Re-spawn the Spec Writer with the specific violations listed.
Maximum **1 retry**. If the spec still fails after one retry, present the violations to the user
and await instruction.

```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SPEC_QUALITY_GATE|pass|spec=${DECOMPOSE_DIR}/spec.md|reqs=<N>" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

---

**Step 3:** Research — spawn four Researchers in parallel (conditional on codebase mode).

**Concurrency rule**: Spawn ALL four Researchers in a SINGLE message with four concurrent Task calls.
Do NOT spawn them sequentially — they are designed for parallel execution.

```
Task(subagent_type="ant-farm-researcher", model="sonnet", prompt="<Stack Researcher prompt>")
Task(subagent_type="ant-farm-researcher", model="sonnet", prompt="<architecture Researcher prompt>")
Task(subagent_type="ant-farm-researcher", model="sonnet", prompt="<Pitfall Researcher prompt>")
Task(subagent_type="ant-farm-researcher", model="sonnet", prompt="<Pattern Researcher prompt>")
```

Fill each prompt from `orchestration/templates/researcher-skeleton.md`. Pass the same `{SPEC_PATH}`
and `{DECOMPOSE_DIR}` to all four; vary only `{FOCUS_AREA}`.

**Pattern Researcher greenfield skip**: If `CODEBASE_MODE=greenfield`, the Pattern Researcher writes
a skip file and returns immediately. This is expected — do not re-spawn it.

**Research complete gate** (HARD GATE — blocks Step 4):

After ALL four Researchers return, verify ALL of the following exist and are non-empty:
- `{DECOMPOSE_DIR}/research/stack.md`
- `{DECOMPOSE_DIR}/research/architecture.md`
- `{DECOMPOSE_DIR}/research/pitfall.md`
- `{DECOMPOSE_DIR}/research/pattern.md` (greenfield exception: file exists but contains skip notice)

**Researcher line cap**: Each Researcher is instructed to cap output at 100 lines. If a Researcher exceeds
100 lines, **truncate at line 100 and proceed** — do NOT re-spawn the Researcher. Record the
truncation in the progress log.

**On gate PASS**: Enforce the line cap before proceeding. Run `wc -l` on each research file and
truncate any file exceeding 100 lines:

```bash
for focus in stack architecture pitfall pattern; do
  f="${DECOMPOSE_DIR}/research/${focus}.md"
  [ -f "${f}" ] || { echo "WARN: ${f} missing, skipping truncation" >> "${DECOMPOSE_DIR}/progress.log"; continue; }
  lines=$(wc -l < "${f}")
  if [ "${lines}" -gt 100 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|FORAGER_TRUNCATED|${focus}|lines=${lines}" \
      >> "${DECOMPOSE_DIR}/progress.log"
    head -100 "${f}" > "${f}.tmp" && mv "${f}.tmp" "${f}"
  fi
done
```

Then proceed to Step 3.5.

**On gate FAIL** (one or more files missing or empty): Re-spawn only the missing/failed Researcher(s).
Maximum **1 retry per Researcher**. If a Researcher still fails after one retry, surface the error to
the user and await instruction.

```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|RESEARCH_COMPLETE|pass|foragers=4|spec=${DECOMPOSE_DIR}/spec.md" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

---

**Step 3.5:** User approval — present the plan and await confirmation (HARD GATE — blocks Step 4).

After research is complete (or immediately after the spec quality gate if research was skipped),
present the plan to the user for review before decomposition into tasks.

Read `{DECOMPOSE_DIR}/spec.md` (permitted) and summarize:
- The feature scope and goals from the spec
- Key requirements and acceptance criteria
- If research ran: high-level findings from each Researcher focus area (stack, architecture, pitfalls, patterns).
  Do NOT read the research files yourself — summarize from the Researcher file names and any
  `FORAGER_TRUNCATED` or `WARN` entries written to `{DECOMPOSE_DIR}/progress.log` during the
  research complete gate check.

Then ask the user for approval using `AskUserQuestion`:

> "The spec is finalized and research is complete. Review the plan above and confirm:
> approve — proceed to decomposition into tasks, or
> revise — describe what to change (I'll update the spec and re-run research if needed)."

**On approve**: Proceed to Step 4 (Task Decomposer).

**On revise**: Apply the user's feedback:
- If the revision affects the spec: update `{DECOMPOSE_DIR}/spec.md` with the changes
  (or re-spawn the Spec Writer if the revision is substantial). Re-run affected Researchers if
  the spec changes invalidate their research. Return to Step 3.5.
- If the revision is minor (scope adjustment, priority change): update the spec directly
  and return to Step 3.5.
- Maximum **2 revision cycles**. If the user is still unsatisfied after two revisions,
  proceed to Step 4 with the current state and note the unresolved concerns in the progress log.

```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|USER_APPROVAL|approved" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

---

**Step 4:** Decomposition — spawn the Task Decomposer.

The Task Decomposer runs alone. Do NOT spawn any other agent concurrently with the Task Decomposer.

Spawn using `orchestration/templates/task-decomposer-skeleton.md` as a guide.
Do NOT read `decomposition.md` yourself — pass its path to the Task Decomposer agent.

```
Task(
  subagent_type="ant-farm-task-decomposer",
  model="opus",
  prompt="<filled task-decomposer-skeleton.md template — see orchestration/templates/task-decomposer-skeleton.md>"
)
```

The Task Decomposer:
1. Reads `{DECOMPOSE_DIR}/spec.md` and all four research briefs
2. Scans `{CODEBASE_ROOT}` to build a brownfield/greenfield map
3. Groups requirements into trails (3–8 crumbs per trail)
4. Decomposes trails into crumbs (5–8 files per crumb)
5. Wires dependencies via `crumb link`
6. Verifies 100% spec coverage (mandatory gate — Task Decomposer does NOT proceed without PASS)
7. Creates trails and crumbs via `crumb` CLI
8. Writes `{DECOMPOSE_DIR}/decomposition-brief.md`

**Task Decomposer output gate** (quick sanity check before decomposition-check):

After the Task Decomposer returns, verify these prerequisites before spawning decomposition-check:
- [ ] `{DECOMPOSE_DIR}/decomposition-brief.md` exists and is non-empty
- [ ] Return summary from the Task Decomposer includes `Coverage: N/N spec requirements — PASS`

If either check fails, re-spawn the Task Decomposer with the specific issue. Do NOT spawn decomposition-check on
a missing or incomplete brief.

```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|ARCHITECT_COMPLETE|brief=${DECOMPOSE_DIR}/decomposition-brief.md" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

---

**Step 5:** Verification — spawn Checkpoint Auditor for decomposition-check (Trail Decomposition Verification).

decomposition-check is a **Checkpoint Auditor spawn**, not an inline check. Spawn Checkpoint Auditor using the decomposition-check checkpoint
from `orchestration/templates/checkpoints/common.md` and `orchestration/templates/checkpoints/decomposition-check.md`.

**Note**: The decomposition-check checkpoint template uses `{SESSION_DIR}` as its output path placeholder. During
decomposition, substitute `{DECOMPOSE_DIR}` for `{SESSION_DIR}` when filling the spawn prompt.

```
Task(
  subagent_type="ant-farm-checkpoint-auditor",
  model="haiku",
  prompt="<decomposition-check checkpoint from checkpoints/decomposition-check.md, with {SESSION_DIR} replaced by {DECOMPOSE_DIR}>"
)
```

**decomposition-check gate** (HARD GATE — blocks Step 6):

**On decomposition-check PASS**: Read `{DECOMPOSE_DIR}/decomposition-brief.md` (permitted) to confirm trail and
crumb counts. Proceed to Step 6.

**On decomposition-check FAIL**: Re-spawn the Task Decomposer with the specific violations from the decomposition-check report
(coverage gaps, circular deps, missing fields, broken trail linkage). Maximum **2 retries**. After
each Task Decomposer retry, re-run decomposition-check. If decomposition-check still fails after two Task Decomposer retries, present the
failure details to the user and await instruction.

```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|DECOMPOSITION_CHECK|pass|trails=<N>|crumbs=<N>|brief=${DECOMPOSE_DIR}/decomposition-brief.md" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

---

**Step 6:** Handoff — copy artifacts, present results, and close the decomposition session.

Report the following to the user:

```
Decomposition complete.

Spec:   {DECOMPOSE_DIR}/spec.md
Brief:  {DECOMPOSE_DIR}/decomposition-brief.md

Trails: <N>
Crumbs: <N>
Coverage: <N>/<N> requirements — PASS

To start implementation: use "let's get to work" (Orchestrator session) targeting
the trails or crumbs created in this decomposition.
```

```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|DECOMPOSE_COMPLETE|handoff=done" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

---

## Hard Gates

| Gate | Step | Blocks | Failure Action |
|------|------|--------|----------------|
| Spec quality gate (PRD path) | After Step 1 PRD Importer success | Step 3 (Researcher spawn) | Re-spawn PRD Importer with violations; max 1 retry; escalate to user |
| Spec quality gate (Spec Writer path) | After Step 2 (Spec Writer) | Step 3 (Researcher spawn) | Re-spawn Spec Writer with violations; max 1 retry; escalate to user |
| Research complete | After Step 3 (all Researchers) | Step 3.5 (User approval) | Re-spawn failed Researcher(s); max 1 retry each; escalate to user |
| User approval | Step 3.5 | Step 4 (Task Decomposer spawn) | User revises spec; max 2 revision cycles; proceed with current state |
| decomposition-check PASS | After Step 5 (Checkpoint Auditor decomposition-check) | Step 6 (Handoff) | Re-spawn Task Decomposer with violations; max 2 retries; escalate to user |

---

## Retry Limits

| Agent | Gate | Max Retries | Escalation Path |
|-------|------|-------------|-----------------|
| PRD Importer | Spec quality gate FAIL (PRD path) | 1 | Present violations to user; await instruction |
| Spec Writer | Spec quality gate FAIL (Spec Writer path) | 1 | Present violations to user; await instruction |
| Researcher (any focus) | Research complete FAIL (missing file) | 1 per Researcher | Surface error per failed Researcher; await instruction |
| Researcher (any focus) | Output exceeds 100 lines | 0 — truncate and proceed | Log truncation; do NOT re-spawn |
| Task Decomposer | decomposition-check FAIL | 2 | Present failure details to user; await instruction |

---

## Concurrency Rules

- **Max 4 Researchers concurrent** — all four spawn in a single message (Step 3)
- **Spec Writer runs alone** — do NOT spawn any other agent concurrently with the Spec Writer
- **Task Decomposer runs alone** — do NOT spawn any other agent concurrently with the Task Decomposer
- **No Researcher cross-reads** — Researchers must NOT read each other's output files
- Researchers and the Task Decomposer each run `git pull --rebase` before writing to disk if they modify
  versioned files

---

## Agent Types and Models

Every `Task` tool call the Planner makes MUST include the `model` parameter from this table.
Omitting `model` causes the agent to inherit the Planner's model, wasting tokens.

| Agent | subagent_type | Model | Rationale |
|-------|--------------|-------|-----------|
| Spec Writer | `ant-farm-spec-writer` | opus | User interaction + requirements synthesis require highest capability |
| Researcher (×4, parallel) | `ant-farm-researcher` | sonnet | Focused single-topic research; sonnet is sufficient |
| Task Decomposer | `ant-farm-task-decomposer` | opus | Multi-source synthesis + design decisions shaping all downstream work |

---

## Decompose Directory Structure

```
.crumbs/sessions/_decompose-{DECOMPOSE_ID}/
├── manifest.json              ← Session metadata (input_class, prd_path if PRD import)
├── spec.md                    ← Spec Writer/PRD Importer output (or user-provided structured spec)
├── decomposition-brief.md     ← Task Decomposer output
├── progress.log               ← Append-only milestone log
└── research/
    ├── stack.md               ← Researcher: Stack output
    ├── architecture.md        ← Researcher: architecture output
    ├── pitfall.md             ← Researcher: Pitfall output
    └── pattern.md             ← Researcher: Pattern output (or skip notice if greenfield)
```

The `_decompose-` prefix distinguishes decomposition directories from other entries.

---

## Anti-Patterns

- Spawning Researchers sequentially — always spawn all four in a single message
- Reading Researcher output files before passing them to the Task Decomposer — trust the Task Decomposer to read them
- Skipping the spec quality gate — a weak spec produces a weak decomposition
- Spawning the Task Decomposer before all four research briefs exist — partial inputs cause incomplete trails
- Re-spawning a Researcher for exceeding the line cap — truncate at 100 lines and proceed
- Skipping the user approval gate (Step 3.5) — after research completes, the user must
  approve the plan before decomposition into tasks. Do not auto-proceed to the Task Decomposer.
