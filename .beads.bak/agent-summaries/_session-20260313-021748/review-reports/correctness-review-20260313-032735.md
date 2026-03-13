# Correctness Review — Round 1

**Timestamp**: 20260313-032735
**Commit range**: 0ec9ed2^..HEAD
**Reviewer**: correctness-nitpicker

---

## Findings Catalog

### F-01
**File**: `/Users/correy/projects/ant-farm/orchestration/templates/decomposition.md:208`
**Severity**: P1
**Category**: Acceptance criteria failure (ant-farm-hlv6 AC: "crumb trail create and crumb create --from-json command examples with full JSON payloads included")
**Description**: The Architect's workflow template instructs the agent to run `bd trail create "{trail-title}"` (line 208). This is the old `bd` CLI. The task's acceptance criterion explicitly requires `crumb trail create` command examples. An Architect following this template will use the wrong CLI binary and fail.
**Suggested fix**: Replace `bd trail create "{trail-title}"` with `crumb trail create --title "{trail-title}"`.

---

### F-02
**File**: `/Users/correy/projects/ant-farm/orchestration/templates/decomposition.md:265`
**Severity**: P1
**Category**: Acceptance criteria failure (ant-farm-hlv6 AC: "crumb trail create and crumb create --from-json command examples with full JSON payloads included") + wrong argument format
**Description**: The template instructs `bd create --from-json /tmp/crumb-session-store.json`. Two errors: (1) `bd create` should be `crumb create`; (2) `crumb`'s `--from-json` flag accepts an **inline JSON string**, not a file path (`json.loads(args.from_json)` — crumb.py:670). The current pattern would cause `crumb` to attempt to parse a file path as JSON and fail immediately.
**Suggested fix**: Replace the pattern with:
```bash
crumb create --from-json "$(cat /tmp/crumb-session-store.json)"
```
Or pass the JSON string inline without the temp-file intermediary.

---

### F-03
**File**: `/Users/correy/projects/ant-farm/orchestration/templates/decomposition.md:275`
**Severity**: P1
**Category**: Acceptance criteria failure (ant-farm-hlv6) + wrong CLI
**Description**: Line 275: `bd dep add {crumb-id} {trail-id} --type parent-child`. The `crumb` CLI has no `dep add` subcommand. The correct crumb equivalent is `crumb link {crumb-id} --parent {trail-id}`. An Architect following this template will fail to wire parent-child relationships.
**Suggested fix**: Replace with `crumb link {crumb-id} --parent {trail-id}`.

---

### F-04
**File**: `/Users/correy/projects/ant-farm/orchestration/templates/decomposition.md:287`
**Severity**: P1
**Category**: Acceptance criteria failure (ant-farm-hlv6) + wrong CLI + argument order inversion
**Description**: Line 287: `bd dep add {blocker-crumb-id} {blocked-crumb-id} --type blocks`. The `crumb` CLI equivalent **inverts the argument order**: `crumb link {blocked-crumb-id} --blocked-by {blocker-crumb-id}`. In `bd dep add`, the blocker is the first positional argument. In `crumb link`, the subject is the crumb being blocked (first arg), and the blocker ID is the `--blocked-by` value. This is a **semantic inversion**, not a mechanical name swap — a fix that only renames `bd` to `crumb` without also swapping the argument roles will silently wire dependencies backwards, causing crumbs to block their own dependencies.
**Suggested fix**: Replace with `crumb link {blocked-crumb-id} --blocked-by {blocker-crumb-id}` (note: argument order is reversed relative to `bd dep add`).

---

### F-05
**File**: `/Users/correy/projects/ant-farm/orchestration/templates/decomposition.md:280`
**Severity**: P1
**Category**: Wrong CLI command
**Description**: Line 280: `` `bd show {trail-id}` after wiring. `` — this is the `bd` CLI. The crumb equivalent is `crumb trail show {trail-id}`. An Architect following this template cannot verify trail wiring.
**Suggested fix**: Replace with `` `crumb trail show {trail-id}` ``.

---

### F-06
**File**: `/Users/correy/projects/ant-farm/orchestration/templates/decomposition.md:292-299`
**Severity**: P1
**Category**: Wrong CLI — dead code (bd dolt mode switching)
**Description**: Lines 292–299 contain a "Dolt mode warning" instructing the Architect to run `bd dolt set mode embedded` and `bd dolt set mode server && bd dolt start` around `bd dep add` calls. The `crumb` CLI has no Dolt dependency; these instructions are vestigial `bd` workflow artifacts. An Architect reading this will attempt commands that don't exist on the `crumb` path and may corrupt state or stall execution.
**Suggested fix**: Remove the entire Dolt mode warning block (lines 292–299).

---

### F-07
**File**: `/Users/correy/projects/ant-farm/orchestration/templates/decomposition.md:397`
**Severity**: P1
**Category**: Wrong CLI in prohibitions list
**Description**: Prohibition #2 in the Prohibitions section reads: "No orphan crumbs. Every crumb must belong to exactly one trail via a `bd dep add --type parent-child` call." This contradicts the correct `crumb link --parent` pattern and will mislead agents checking themselves against the prohibitions.
**Suggested fix**: Replace with "No orphan crumbs. Every crumb must belong to exactly one trail via a `crumb link {crumb-id} --parent {trail-id}` call."

---

### F-08
**File**: `/Users/correy/projects/ant-farm/orchestration/templates/decomposition.md:115-117`
**Severity**: P1
**Category**: Acceptance criteria example uses wrong CLI
**Description**: Lines 115–117 show a "Good example" of acceptance criteria:
```
- Running `bd trail create "Add user login"` returns exit code 0 ...
- `bd show <trail-id>` displays the title ...
```
These examples use `bd` CLI. Since the Architect follows these as model acceptance criteria for crumbs, an Architect who writes crumbs using these examples will produce acceptance criteria that reference the wrong binary — dirt pushers verifying them will fail.
**Suggested fix**: Replace `bd trail create` with `crumb trail create --title` and `bd show` with `crumb trail show`.

---

### F-09
**File**: `/Users/correy/projects/ant-farm/orchestration/templates/architect-skeleton.md:77-80`
**Severity**: P1
**Category**: Acceptance criteria failure (ant-farm-xtu9 AC: "orchestration/templates/architect-skeleton.md contains the prompt template with input file placeholders") + wrong CLI
**Description**: The "Create via CLI" section in architect-skeleton.md (the spawn prompt sent directly to the Architect agent) contains:
```bash
bd trail create "{trail-title}"
bd create --from-json /tmp/crumb-{slug}.json
bd dep add {crumb-id} {trail-id} --type parent-child
bd dep add {blocker-id} {blocked-id} --type blocks
```
These are all `bd` CLI commands. The Architect is spawned with these instructions; it will use `bd` rather than `crumb`. Since `bd` is not the active CLI, all four commands will fail or produce no output.
**Suggested fix**: Replace with:
```bash
crumb trail create --title "{trail-title}"
crumb create --from-json "$(cat /tmp/crumb-{slug}.json)"
crumb link {crumb-id} --parent {trail-id}
crumb link {blocked-id} --blocked-by {blocker-id}
```

---

### F-10
**File**: `/Users/correy/projects/ant-farm/orchestration/templates/architect-skeleton.md:111`
**Severity**: P1
**Category**: Wrong CLI in prohibitions (spawn prompt)
**Description**: Line 111: "No orphan crumbs. Every crumb must be parented to a trail via `bd dep add --type parent-child`." This is in the actual spawn prompt sent to the Architect. The agent will check itself against this prohibition using `bd`, not `crumb`.
**Suggested fix**: Replace with `crumb link {crumb-id} --parent {trail-id}`.

---

### F-11
**File**: `/Users/correy/projects/ant-farm/orchestration/RULES-decompose.md:287`
**Severity**: P2
**Category**: Wrong CLI reference in Planner workflow
**Description**: Line 287 reads: "5. Wires dependencies via `bd dep add`". This is in the Architect step description read by the Planner. The Planner uses this text when validating the Architect's return summary. While the Planner itself is prohibited from calling `bd`, a Planner checking the Architect's work might accept a summary mentioning `bd dep add` rather than flagging the mismatch.
**Suggested fix**: Replace with "5. Wires dependencies via `crumb link --parent` and `crumb link --blocked-by`".

---

### F-12
**File**: `/Users/correy/projects/ant-farm/skills/init.md:107-115`
**Severity**: P2
**Category**: Acceptance criteria compliance — wrong config.json key schema
**Description**: `skills/init.md` generates `config.json` with:
```json
{
  "prefix": "<PREFIX>",
  "default_priority": "P2",
  "counters": { "task": 1, "trail": 1 },
  ...
}
```
But `crumb.py`'s `read_config()` reads `config.get("next_crumb_id", 1)` and `config.get("next_trail_id", 1)` (crumb.py:704, crumb.py:1173). The `"counters"` key does not match. On the first `crumb create`, the CLI falls back to the default `next_crumb_id=1` (correct starting value) and then writes back `"next_crumb_id": 2` — so no crash occurs. However, the config produced by init is structurally wrong. The acceptance criterion says "counters at 1" but the AC uses the wrong field names relative to what `crumb.py` actually reads.
**Suggested fix**: Replace the `"counters"` block with:
```json
"next_crumb_id": 1,
"next_trail_id": 1
```

---

### F-13
**File**: `/Users/correy/projects/ant-farm/skills/plan.md:120` vs `/Users/correy/projects/ant-farm/orchestration/RULES-decompose.md:119`
**Severity**: P2
**Category**: Missing research/ subdirectory creation
**Description**: `skills/plan.md` Step 3 creates `DECOMPOSE_DIR` with `mkdir -p "${DECOMPOSE_DIR}"` but does NOT create the `research/` subdirectory. Then it routes to `RULES-decompose.md` from **Step 1 onward** (skipping Step 0). RULES-decompose Step 0 creates `mkdir -p "${DECOMPOSE_DIR}/research"` — but that step is skipped. The Forager agents write to `{DECOMPOSE_DIR}/research/{focus}.md`. Without the `research/` directory pre-existing, Forager writes will fail (or silently create the directory themselves if their own error handling creates it). The Forager template does contain: "Decompose dir does not exist: Create it with `mkdir -p {DECOMPOSE_DIR}/research`" — so individual Foragers may self-heal, but it is not guaranteed for all four Foragers.
**Suggested fix**: Change the mkdir in skills/plan.md Step 3 from `mkdir -p "${DECOMPOSE_DIR}"` to `mkdir -p "${DECOMPOSE_DIR}/research"`.

---

### F-14
**File**: `/Users/correy/projects/ant-farm/skills/init.md:40,43`
**Severity**: P1
**Category**: Logic error — shell operator precedence, wrong output for common inputs
**Description**: Two lines in the language detection block have a shell operator-precedence bug. Due to `&&` binding tighter than `||`:

```bash
[ -f pyproject.toml ] || [ -f setup.py ] || [ -f requirements.txt ] && echo "python"  # line 40
[ -f pom.xml ] || [ -f build.gradle ] && echo "java"                                  # line 43
```

Both evaluate as `A || B || (C && echo ...)` rather than `(A || B || C) && echo ...`. The `echo` only fires if the **last** file in the chain exists. For Python: projects using `pyproject.toml` or `setup.py` without `requirements.txt` (the majority of modern Python projects including pip-installable packages) will not be detected. For Java: projects using `pom.xml` without `build.gradle` will not be detected. The detection silently returns nothing, and Step 6 defaults to `general-purpose` agent type suggestion instead of `python-pro`, producing wrong output for common inputs.

This was flagged by the clarity reviewer (obscured intent); the logic-bug determination is a correctness finding.

**Suggested fix**:
```bash
{ [ -f pyproject.toml ] || [ -f setup.py ] || [ -f requirements.txt ]; } && echo "python"
{ [ -f pom.xml ] || [ -f build.gradle ]; } && echo "java"
```

---

## Preliminary Groupings

### Group A — `bd` CLI not replaced in decomposition templates (F-01 through F-10)

Root cause: The migration from `bd` to `crumb` CLI (commits `ebcffeb`, `8aa01a7`) updated some files but left `orchestration/templates/decomposition.md` and `orchestration/templates/architect-skeleton.md` with `bd trail create`, `bd create --from-json`, `bd dep add`, `bd show`, and a `bd dolt` warning block. These are the two files the Architect agent reads and executes. All P1 findings in this group share a single root cause: the CLI migration was incomplete for the Architect's executable templates.

Additionally: two non-mechanical changes are required beyond binary renaming:
- `crumb create --from-json` takes an **inline JSON string**, not a file path (F-02) — `"$(cat /tmp/...)"` pattern needed
- `crumb link --blocked-by` **inverts argument order** relative to `bd dep add --type blocks` (F-04) — a rename-only fix wires dependencies backwards

### Group B — Config schema mismatch in init skill (F-12)

Root cause: `skills/init.md` was written against a draft config schema (`"counters": {...}`) while `crumb.py` was implemented with flat top-level keys (`"next_crumb_id"`, `"next_trail_id"`). The files are out of sync. No crash results due to default fallback behavior, but the generated config.json contains a key that `crumb.py` ignores.

### Group D — Shell operator-precedence in init skill language detection (F-14)

Root cause: `skills/init.md` Step 1 detection block uses `||` and `&&` without grouping, relying on the incorrect mental model that `||` and `&&` have equal precedence left-to-right. In shell, `&&` binds tighter. Python detection via `pyproject.toml`/`setup.py` and Java detection via `pom.xml` are silently suppressed. Flagged by clarity reviewer; correctness owns the logic-error classification.

### Group E — Missing subdirectory creation in plan skill (F-13)

Root cause: `skills/plan.md` handles DECOMPOSE_DIR setup (Step 3) and then passes control to RULES-decompose Step 1 (skipping Step 0). Step 0 contains the `research/` mkdir. The handoff creates a gap: the directory that Forager agents need to write to may not exist when they run.

### Group F — Stale `bd` reference in RULES-decompose Planner workflow (F-11)

Root cause: RULES-decompose.md was partially migrated. The Architect summary step at line 287 still mentions `bd dep add` rather than the `crumb link` equivalent.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1       | 11 (F-01 through F-10, F-14) |
| P2       | 3 (F-11, F-12, F-13) |
| P3       | 0 |
| **Total** | **14** |

---

## Cross-Review Messages

**Sent to drift-reviewer**: "RULES-decompose.md:287 still references `bd dep add` — stale cross-file reference after CLI migration. decomposition.md and architect-skeleton.md also have unresolved bd→crumb migration. May want to audit the full migration scope."

**Received from clarity-reviewer**: Shell operator-precedence bug in `skills/init.md:40,43` — Python detection via pyproject.toml/setup.py and Java detection via pom.xml silently fail. Filed as F-14 (P1 correctness finding).

**Received from drift-reviewer**: Confirmed DRIFT-006 (P1) — full bd command inventory across decomposition.md and architect-skeleton.md matches F-01 through F-10. Added important note: `bd dep add {blocker} {blocked}` → `crumb link {blocked} --blocked-by {blocker}` is a semantic argument order inversion, not a mechanical rename. Updated F-04 description accordingly. Also noted DRIFT-007 (P3) for prohibition/documentation references in RULES-decompose.md lines 20, 27, 47, 108, 287, 289 — these are Drift scope and not duplicated here.

---

## Coverage Log

| File | Issues Found |
|------|-------------|
| `agents/architect.md` | No issues — correctly references decomposition.md by path without hardcoding CLI commands |
| `agents/forager.md` | No issues — correctly references forager.md template by path |
| `agents/surveyor.md` | No issues — correctly references surveyor.md template by path |
| `orchestration/RULES-decompose.md` | F-11 (P2) — `bd dep add` reference at line 287 |
| `orchestration/templates/architect-skeleton.md` | F-09 (P1), F-10 (P1) — bd CLI commands in spawn prompt |
| `orchestration/templates/decomposition.md` | F-01 (P1), F-02 (P1), F-03 (P1), F-04 (P1), F-05 (P1), F-06 (P1), F-07 (P1), F-08 (P1) |
| `orchestration/templates/forager-skeleton.md` | No issues |
| `orchestration/templates/forager.md` | No issues |
| `orchestration/templates/surveyor-skeleton.md` | No issues |
| `orchestration/templates/surveyor.md` | No issues |
| `scripts/setup.sh` | No issues — all acceptance criteria met |
| `skills/init.md` | F-12 (P2) — config.json uses wrong key names; F-14 (P1) — shell operator-precedence bug in language detection |
| `skills/plan.md` | F-13 (P2) — DECOMPOSE_DIR mkdir missing research/ subdirectory |
| `skills/status.md` | No issues — all acceptance criteria met |
| `skills/work.md` | No issues — all acceptance criteria met |

---

## Overall Assessment

**Score**: 3/10

**Verdict**: NEEDS WORK

The core decomposition path is broken for any user who invokes `/ant-farm:plan` → Architect execution. The Architect agent receives `architect-skeleton.md` as its spawn prompt, which instructs it to run `bd trail create`, `bd create --from-json`, and `bd dep add`. These commands do not exist in the active `crumb` CLI. The Architect will fail to create any trails, crumbs, or dependency links. The detailed workflow in `decomposition.md` has the same problem throughout its CLI examples section.

The migration commits (`ebcffeb`, `8aa01a7`) updated the agent definition files and some surrounding documentation but left the **executable** portions of the templates (the CLI command blocks the Architect actually runs) in the `bd` CLI format. This is the primary blocking issue.

Secondary issues (F-11, F-12, F-13) are real but less urgent — they cause degraded behavior or incorrect generated artifacts rather than hard failures.
