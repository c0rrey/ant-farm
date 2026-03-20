# Decomposition Workflow Rules

> This is the Planner's workflow document for `/ant-farm-plan`. The Planner reads THIS file alone
> and follows it exactly. Do NOT read `orchestration/RULES.md` — it governs the Queen's
> implementation session workflow, which is separate from decomposition.

## Path Reference Convention

All file paths in this document use **repo-root relative** format: `orchestration/templates/surveyor.md`.

When code runs at runtime, agent files are synced to `~/.claude/agents/` and orchestration files are
accessible at `~/.claude/orchestration/`. To translate repo paths to runtime paths:
- Replace `orchestration/` with `~/.claude/orchestration/`
- Replace `agents/` with `~/.claude/agents/`

---

## Planner Prohibitions (read FIRST)

- **NEVER** run `crumb show`, `crumb ready`, `crumb list`, `crumb blocked`, or any `crumb` query command
- **NEVER** read source code, test files, or application data files directly — agents do this
- **NEVER** read agent instruction files (`ant-farm-surveyor.md`, `ant-farm-forager.md`, `decomposition.md`) —
  pass the path to the agent and let it read its own instructions
- **NEVER** set `run_in_background` on Task agents — multiple Task calls in one message already
  run concurrently; background mode leaks JSONL transcripts into the Planner's context
- **NEVER** spawn the Architect until ALL four Forager outputs exist and the spec quality gate passes
- **NEVER** create trails or crumbs yourself — only the Architect does this via `crumb` CLI

---

## Planner Orchestrator Profile

The Planner is a distinct orchestrator from the Queen. Understanding this distinction prevents
misapplying Queen patterns to decomposition sessions.

### Distinction from Queen

| Dimension | Planner | Queen |
|-----------|---------|-------|
| Trigger | `/ant-farm-plan` command | "let's get to work" message |
| Purpose | Decompose a feature into trails and crumbs | Execute a prepared work session |
| Workflow file | `orchestration/RULES-decompose.md` (this file) | `orchestration/RULES.md` |
| Read permissions | `spec.md` and `decomposition-brief.md` only | `queen-state.md`, task files, git diffs |
| State tracking | Step number + per-agent retry count (in context only) | `queen-state.md` written to disk |
| Primary agents | Surveyor, Forager x4, Architect | Scout, Pantry, Pest Control, Nitpicker |
| Context budget target | 15–20% of context window | Not separately specified |
| `crumb` CLI usage | Prohibited — only the Architect calls `crumb` | Queen calls `crumb` directly |

The Planner MUST NOT read `orchestration/RULES.md`. The Queen MUST NOT read this file. They are
separate orchestrators with non-overlapping roles.

### State Tracking

The Planner tracks state **in context only** — no state file is written to disk during a
decomposition session.

State tracked:
- **Current step** (0–6): derived from progress log and agent return values
- **Retry count per agent**: incremented each time an agent is re-spawned for a gate failure
  - Surveyor retry count (max 1)
  - Per-Forager retry count (max 1 each)
  - Architect retry count (max 2)

The Planner does NOT use `queen-state.md`. That file belongs to the Queen's implementation
workflow. Writing a state file during decomposition would be a scope violation.

**Recovery**: If the Planner's context is lost mid-session, the `progress.log` serves as a
recoverable audit trail. The Planner can re-read the progress log (via bash) to determine
which steps completed without re-reading any agent instruction files or research briefs.

### Context Budget

**Target: 15–20% of the context window.**

Reasoning: A decomposition session involves multiple round-trips with interactive agents. The
Surveyor may ask the user several questions and return a multi-section spec. Four Foragers each
return summaries. The Architect returns a structured brief. If the Planner's context fills up
during Step 3 or Step 4 returns, it cannot process gate checks or spawn the next agent.

The 15–20% budget preserves capacity for:
- Up to 4 Forager return summaries
- The Surveyor spec (read at Step 2 gate)
- The Architect's decomposition brief (read at Step 4 gate)
- Gate check outputs and progress log appends

If the feature request is very large (> 500 words), summarize it internally before spawning any
agent. Do NOT pass the raw user input verbatim to every agent prompt — use the structured
`{SPEC_PATH}` reference instead once spec.md exists.

---

## Planner Read Permissions

The Planner's context window is restricted to prevent bloat. The following are explicitly permitted.

**PERMITTED (Planner reads these directly):**
- `{DECOMPOSE_DIR}/spec.md` — Surveyor output; Planner reads after spec quality gate to confirm
  requirement count before spawning Foragers
- `{DECOMPOSE_DIR}/decomposition-brief.md` — Architect output; Planner reads to confirm trail and
  crumb counts before closing the decomposition session

**FORBIDDEN (agents read; Planner never reads):**
- `orchestration/templates/surveyor.md` — Surveyor's instruction file
- `orchestration/templates/forager.md` — Forager's instruction file
- `orchestration/templates/decomposition.md` — Architect's instruction file
- `{DECOMPOSE_DIR}/research/*.md` — Forager research briefs (Architect reads these)
- Source code files, test files, application configs, project data files
- Raw `crumb show`, `crumb list`, `crumb trail status` output (let the Architect handle CLI calls)

---

## Workflow: `/ant-farm-plan`

**Step 0:** Session setup — generate a DECOMPOSE_ID and DECOMPOSE_DIR. Store both as variables.

```bash
DECOMPOSE_ID=$(date +%Y%m%d-%H%M%S)
DECOMPOSE_DIR=".crumbs/sessions/_decompose-${DECOMPOSE_ID}"
mkdir -p "${DECOMPOSE_DIR}/research"
```

Store DECOMPOSE_DIR in your context. Pass it explicitly to every agent.

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
Record the result as `CODEBASE_MODE=brownfield|greenfield` in your context and pass it to the
Surveyor in its spawn prompt. The Architect uses this to decide whether to reference existing file
paths or propose new ones.

**Context budget target**: Keep the Planner's total context at 15–20% of the context window.
This leaves room for up to 4 Forager returns, the Surveyor spec, and the Architect's brief.
If the feature request is very large (> 500 words), summarize it internally before spawning agents.

**Progress log:**
```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|DECOMPOSE_INIT|complete|decompose_dir=${DECOMPOSE_DIR}" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

---

**Step 1:** Input classification — determine whether the user's input is a **freeform request**
            or a **structured spec**.

A structured spec has ALL of these:
- Numbered requirements (`REQ-N:` headings or equivalent)
- Acceptance criteria for each requirement
- A stated scope / non-requirements section

A freeform request lacks one or more of these. When in doubt, treat as freeform.

**If structured spec:** Write the input verbatim to `{DECOMPOSE_DIR}/spec.md`. Skip Step 2
(Surveyor). Then prompt the user:

> "This looks like a structured spec. Want me to run research agents to investigate technical
> decisions before decomposing, or decompose directly?"

- If research requested → proceed to Step 3 (Foragers).
- If direct decomposition → skip to Step 4 (Architect).

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

**Step 2:** Requirements gathering — spawn the Surveyor (freeform input only).

Spawn the Surveyor using `orchestration/templates/surveyor-skeleton.md` as a guide.
Do NOT read `ant-farm-surveyor.md` yourself — pass its path to the Surveyor agent.

```
Task(
  subagent_type="ant-farm-surveyor",
  model="opus",
  prompt="<filled surveyor-skeleton.md template — see orchestration/templates/surveyor-skeleton.md>"
)
```

The Surveyor interacts with the user via `AskUserQuestion`, then writes `{DECOMPOSE_DIR}/spec.md`.

**Spec quality gate** (HARD GATE — blocks Step 3):

After the Surveyor returns, verify `{DECOMPOSE_DIR}/spec.md` passes ALL of the following:
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

**On gate FAIL (spec incomplete)**: Re-spawn the Surveyor with the specific violations listed.
Maximum **1 retry**. If the spec still fails after one retry, present the violations to the user
and await instruction.

```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SPEC_QUALITY_GATE|pass|spec=${DECOMPOSE_DIR}/spec.md|reqs=<N>" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

---

**Step 3:** Research — spawn four Foragers in parallel (conditional on codebase mode).

**Concurrency rule**: Spawn ALL four Foragers in a SINGLE message with four concurrent Task calls.
Do NOT spawn them sequentially — they are designed for parallel execution.

```
Task(subagent_type="ant-farm-forager", model="sonnet", prompt="<Stack forager prompt>")
Task(subagent_type="ant-farm-forager", model="sonnet", prompt="<Architecture forager prompt>")
Task(subagent_type="ant-farm-forager", model="sonnet", prompt="<Pitfall forager prompt>")
Task(subagent_type="ant-farm-forager", model="sonnet", prompt="<Pattern forager prompt>")
```

Fill each prompt from `orchestration/templates/forager-skeleton.md`. Pass the same `{SPEC_PATH}`
and `{DECOMPOSE_DIR}` to all four; vary only `{FOCUS_AREA}`.

**Pattern Forager greenfield skip**: If `CODEBASE_MODE=greenfield`, the Pattern Forager writes
a skip file and returns immediately. This is expected — do not re-spawn it.

**Research complete gate** (HARD GATE — blocks Step 4):

After ALL four Foragers return, verify ALL of the following exist and are non-empty:
- `{DECOMPOSE_DIR}/research/stack.md`
- `{DECOMPOSE_DIR}/research/architecture.md`
- `{DECOMPOSE_DIR}/research/pitfall.md`
- `{DECOMPOSE_DIR}/research/pattern.md` (greenfield exception: file exists but contains skip notice)

**Forager line cap**: Each Forager is instructed to cap output at 100 lines. If a Forager exceeds
100 lines, **truncate at line 100 and proceed** — do NOT re-spawn the Forager. Record the
truncation in the progress log.

**On gate PASS**: Enforce the line cap before proceeding. Run `wc -l` on each research file and
truncate any file exceeding 100 lines:

```bash
for focus in stack architecture pitfall pattern; do
  f="${DECOMPOSE_DIR}/research/${focus}.md"
  lines=$(wc -l < "${f}")
  if [ "${lines}" -gt 100 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|FORAGER_TRUNCATED|${focus}|lines=${lines}" \
      >> "${DECOMPOSE_DIR}/progress.log"
    head -100 "${f}" > "${f}.tmp" && mv "${f}.tmp" "${f}"
  fi
done
```

Then proceed to Step 3.5.

**On gate FAIL** (one or more files missing or empty): Re-spawn only the missing/failed Forager(s).
Maximum **1 retry per Forager**. If a Forager still fails after one retry, surface the error to
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
- If research ran: high-level findings from each Forager focus area (stack, architecture, pitfalls, patterns).
  Do NOT read the research files yourself — summarize from the Forager file names and any notes
  you recorded during the research complete gate check.

Then ask the user for approval using `AskUserQuestion`:

> "The spec is finalized and research is complete. Review the plan above and confirm:
> approve — proceed to decomposition into tasks, or
> revise — describe what to change (I'll update the spec and re-run research if needed)."

**On approve**: Proceed to Step 4 (Architect).

**On revise**: Apply the user's feedback:
- If the revision affects the spec: update `{DECOMPOSE_DIR}/spec.md` with the changes
  (or re-spawn the Surveyor if the revision is substantial). Re-run affected Foragers if
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

**Step 4:** Decomposition — spawn the Architect.

The Architect runs alone. Do NOT spawn any other agent concurrently with the Architect.

Spawn using `orchestration/templates/architect-skeleton.md` as a guide.
Do NOT read `decomposition.md` yourself — pass its path to the Architect agent.

```
Task(
  subagent_type="ant-farm-architect",
  model="opus",
  prompt="<filled architect-skeleton.md template — see orchestration/templates/architect-skeleton.md>"
)
```

The Architect:
1. Reads `{DECOMPOSE_DIR}/spec.md` and all four research briefs
2. Scans `{CODEBASE_ROOT}` to build a brownfield/greenfield map
3. Groups requirements into trails (3–8 crumbs per trail)
4. Decomposes trails into crumbs (5–8 files per crumb)
5. Wires dependencies via `crumb link`
6. Verifies 100% spec coverage (mandatory gate — Architect does NOT proceed without PASS)
7. Creates trails and crumbs via `crumb` CLI
8. Writes `{DECOMPOSE_DIR}/decomposition-brief.md`

**Architect output gate** (quick sanity check before TDV):

After the Architect returns, verify these prerequisites before spawning TDV:
- [ ] `{DECOMPOSE_DIR}/decomposition-brief.md` exists and is non-empty
- [ ] Return summary from the Architect includes `Coverage: N/N spec requirements — PASS`

If either check fails, re-spawn the Architect with the specific issue. Do NOT spawn TDV on
a missing or incomplete brief.

```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|ARCHITECT_COMPLETE|brief=${DECOMPOSE_DIR}/decomposition-brief.md" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

---

**Step 5:** Verification — spawn Pest Control for TDV (Trail Decomposition Verification).

TDV is a **Pest Control spawn**, not an inline check. Spawn Pest Control using the TDV checkpoint
from `orchestration/templates/checkpoints/common.md` and `orchestration/templates/checkpoints/tdv.md`.

**Note**: The TDV checkpoint template uses `{SESSION_DIR}` as its output path placeholder. During
decomposition, substitute `{DECOMPOSE_DIR}` for `{SESSION_DIR}` when filling the spawn prompt.

```
Task(
  subagent_type="ant-farm-pest-control",
  model="haiku",
  prompt="<TDV checkpoint from checkpoints/tdv.md, with {SESSION_DIR} replaced by {DECOMPOSE_DIR}>"
)
```

**TDV gate** (HARD GATE — blocks Step 6):

**On TDV PASS**: Read `{DECOMPOSE_DIR}/decomposition-brief.md` (permitted) to confirm trail and
crumb counts. Proceed to Step 6.

**On TDV FAIL**: Re-spawn the Architect with the specific violations from the TDV report
(coverage gaps, circular deps, missing fields, broken trail linkage). Maximum **2 retries**. After
each Architect retry, re-run TDV. If TDV still fails after two Architect retries, present the
failure details to the user and await instruction.

```bash
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|TDV|pass|trails=<N>|crumbs=<N>|brief=${DECOMPOSE_DIR}/decomposition-brief.md" \
  >> "${DECOMPOSE_DIR}/progress.log"
```

---

**Step 6:** Handoff — copy artifacts, present results, and close the decomposition session.

Copy the decomposition brief to the tracked `.crumbs/` directory and stage it:

```bash
cp "${DECOMPOSE_DIR}/decomposition-brief.md" ".crumbs/decomposition-brief.md"
git add .crumbs/decomposition-brief.md
```

Report the following to the user:

```
Decomposition complete.

Spec:   {DECOMPOSE_DIR}/spec.md
Brief:  {DECOMPOSE_DIR}/decomposition-brief.md

Trails: <N>
Crumbs: <N>
Coverage: <N>/<N> requirements — PASS

To start implementation: use "let's get to work" (Queen session) targeting
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
| Spec quality gate | After Step 2 (Surveyor) | Step 3 (Forager spawn) | Re-spawn Surveyor with violations; max 1 retry; escalate to user |
| Research complete | After Step 3 (all Foragers) | Step 3.5 (User approval) | Re-spawn failed Forager(s); max 1 retry each; escalate to user |
| User approval | Step 3.5 | Step 4 (Architect spawn) | User revises spec; max 2 revision cycles; proceed with current state |
| TDV PASS | After Step 5 (Pest Control TDV) | Step 6 (Handoff) | Re-spawn Architect with violations; max 2 retries; escalate to user |

---

## Retry Limits

| Agent | Gate | Max Retries | Escalation Path |
|-------|------|-------------|-----------------|
| Surveyor | Spec quality gate FAIL | 1 | Present violations to user; await instruction |
| Forager (any focus) | Research complete FAIL (missing file) | 1 per Forager | Surface error per failed Forager; await instruction |
| Forager (any focus) | Output exceeds 100 lines | 0 — truncate and proceed | Log truncation; do NOT re-spawn |
| Architect | TDV FAIL | 2 | Present failure details to user; await instruction |

---

## Concurrency Rules

- **Max 4 Foragers concurrent** — all four spawn in a single message (Step 3)
- **Surveyor runs alone** — do NOT spawn any other agent concurrently with the Surveyor
- **Architect runs alone** — do NOT spawn any other agent concurrently with the Architect
- **No Forager cross-reads** — Foragers must NOT read each other's output files
- Foragers and the Architect each run `git pull --rebase` before writing to disk if they modify
  versioned files

---

## Agent Types and Models

Every `Task` tool call the Planner makes MUST include the `model` parameter from this table.
Omitting `model` causes the agent to inherit the Planner's model, wasting tokens.

| Agent | subagent_type | Model | Rationale |
|-------|--------------|-------|-----------|
| Surveyor | `ant-farm-surveyor` | opus | User interaction + requirements synthesis require highest capability |
| Forager (×4, parallel) | `ant-farm-forager` | sonnet | Focused single-topic research; sonnet is sufficient |
| Architect | `ant-farm-architect` | opus | Multi-source synthesis + design decisions shaping all downstream work |

---

## Decompose Directory Structure

```
.crumbs/sessions/_decompose-{DECOMPOSE_ID}/
├── spec.md                    ← Surveyor output (or user-provided structured spec)
├── decomposition-brief.md     ← Architect output
├── progress.log               ← Append-only milestone log
└── research/
    ├── stack.md               ← Forager: Stack output
    ├── architecture.md        ← Forager: Architecture output
    ├── pitfall.md             ← Forager: Pitfall output
    └── pattern.md             ← Forager: Pattern output (or skip notice if greenfield)
```

The `_decompose-` prefix distinguishes decomposition directories from other entries.

---

## Anti-Patterns

- Spawning Foragers sequentially — always spawn all four in a single message
- Reading Forager output files before passing them to the Architect — trust the Architect to read them
- Skipping the spec quality gate — a weak spec produces a weak decomposition
- Spawning the Architect before all four research briefs exist — partial inputs cause incomplete trails
- Re-spawning a Forager for exceeding the line cap — truncate at 100 lines and proceed
- Skipping the user approval gate (Step 3.5) — after research completes, the user must
  approve the plan before decomposition into tasks. Do not auto-proceed to the Architect.
