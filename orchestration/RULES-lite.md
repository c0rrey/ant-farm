# Orchestration Rules — Lite Mode
<!-- .local override: To customize, create RULES-lite.local.md in the same directory. Your local file will not be overwritten by setup.sh. -->

> **Tool invocation note**: Where this file instructs the Orchestrator or Implementer to call crumb
> operations, prefer the MCP tool equivalents (`crumb_show`, `crumb_update`, `crumb_close`,
> `crumb_ready`, `crumb_list`, `crumb_create`). If the MCP server is unavailable, fall back to the
> equivalent `crumb <command>` CLI call via Bash.

## What Is Lite Mode

Lite mode is a single-crumb execution path designed for small, isolated changes where the full pipeline overhead (Recon Planner wave analysis, Prompt Composer pre-digestion, Reviewer review team) is unnecessary. It preserves the quality gates that matter for any change — prompt auditing (pre-spawn-check), substance verification (claims-vs-code), atomic commits, and crumb tracking — while eliminating the multi-agent orchestration scaffolding.

**Use lite mode when:**
- Exactly one crumb is being worked
- The task scope is self-contained (no file conflicts with other in-flight work)
- The change is low-risk and the crumb's acceptance criteria are already well-specified

**Do NOT use lite mode when:**
- Multiple crumbs are being worked concurrently
- Tasks share files (conflict analysis requires the Recon Planner)
- The change needs peer review (use full-mode RULES.md instead)

## What Lite Mode Does NOT Include

The following full-mode components are intentionally absent:

| Omitted component | Reason |
|-------------------|--------|
| Recon Planner (recon planner) | No wave analysis needed for a single crumb |
| startup-check | startup-check verifies Recon Planner wave groupings — no Recon Planner, no startup-check |
| Prompt Composer (prompt composer) | The Orchestrator passes the task brief directly; no pre-digestion step |
| Reviewer review team | Peer review is replaced by a mandatory self-review step |
| review-integrity | review-integrity verifies the Reviewer team's output — no team, no check |
| session-complete | session-complete verifies the Session Scribe's exec summary — lite mode has no Session Scribe |
| Session Scribe (session scribe) | Lite mode omits the exec summary; session narrative is the commit message |

## Path Reference Convention

All file paths in this document use **repo-root relative** format: `orchestration/templates/checkpoints/pre-spawn-check.md`.

At runtime, orchestration files are accessible at `~/.claude/orchestration/`. To translate:
- Replace `orchestration/` with `~/.claude/orchestration/`

## Orchestrator Prohibitions

- **NEVER** read source code, tests, project data files, or config files — the implementer agent does this
- **NEVER** read agent instruction files (implementation.md, checkpoints/*.md, etc.) — pass the path to the agent
- **NEVER** skip the pre-spawn-check gate — even a single-agent spawn must be audited
- **NEVER** skip the claims-vs-code gate — the self-review step does not replace claims-vs-code

## Workflow: Lite Mode Execution

**Step 0:** Session setup — generate SESSION_ID and SESSION_DIR, create directories.

```bash
SESSION_ID="$(date +%Y%m%d-%H%M%S)-$(head -c4 /dev/urandom | xxd -p)"
SESSION_DIR=".crumbs/sessions/_session-${SESSION_ID}"
mkdir -p "${SESSION_DIR}"/{prompts,pc,summaries,signals}
crumb prune >/dev/null || true  # CLI only — no MCP equivalent
```

Store SESSION_DIR in context and pass it to every agent that needs to write artifacts.

**Progress log:**
```
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SESSION_INIT|complete|mode=lite|session_dir=${SESSION_DIR}|next_step=STEP_1_SELECT" >> ${SESSION_DIR}/progress.log
```

**Step 1:** Task selection — identify the single crumb to work. Call `crumb_show(crumb_id="<TASK_ID>")` (MCP) to read the task's title, description, acceptance criteria, and affected files. Store the task ID and acceptance criteria in context.

> **Note**: In lite mode the Orchestrator reads the crumb directly. There is no Recon Planner subagent. The Orchestrator's context budget is protected by the single-crumb scope — there is no wave analysis or briefing doc to read.

**Step 2:** Compose and audit the implementer prompt — write the task brief for the implementer agent, then spawn the Checkpoint Auditor to audit it before spawning.

The task brief MUST include:
- Real task ID (e.g., `my-project-abc`)
- Real file paths with line ranges (e.g., `src/parser.py:L42-87`)
- Root cause text (copied from the crumb description)
- All 6 mandatory implementer steps (claim, design, implement, review, commit, summary doc)
- Explicit scope boundaries (which files to read and which are off-limits)
- `git pull --rebase` before commit instruction
- `Session directory: ${SESSION_DIR}` so the implementer writes artifacts to the correct path

The implementer reads the task file(s) directly — there is no Prompt Composer pre-digestion step. Pass the crumb's acceptance criteria and affected file list verbatim in the prompt.

Spawn Checkpoint Auditor for pre-spawn-check:

```
Task(
  subagent_type="ant-farm-checkpoint-auditor",
  model="haiku",
  prompt="pre-spawn-check (lite mode — single Implementer prompt).
          Session directory: ${SESSION_DIR}.
          Read orchestration/templates/checkpoints/common.md and
          orchestration/templates/checkpoints/pre-spawn-check.md for full instructions.
          <prompt>{paste the composed implementer prompt here}</prompt>"
)
```

**On pre-spawn-check PASS:** Proceed to Step 3.
**On pre-spawn-check FAIL:** Fix the specific gaps in the prompt, then re-run pre-spawn-check. Do NOT spawn the implementer until PASS. Maximum 1 retry; on second FAIL escalate to user.

**Progress log (after pre-spawn-check PASS):**
```
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|WAVE_SPAWNED|wave=1|mode=lite|task=${TASK_ID}|pre_spawn_check=pass|next_step=STEP_3_IMPLEMENT" >> ${SESSION_DIR}/progress.log
```

**Step 3:** Implementation — write the scope sidecar, then spawn the implementer agent (Implementer).

**Write .ant-farm-scope.json atomically (temp file + rename) before spawning:**

> **AFFECTED_FILES_LIST** is the space-separated list of `file:line-range` strings from the crumb's `Scope.files` field (populated in Step 1 when you called `crumb_show`). Construct this list from the crumb's affected files before running the snippet below.

```bash
# Build the allowed_files JSON array from the crumb's affected files list
# Each entry must be a quoted string with optional line range, e.g. "src/foo.py:10-50"
SCOPE_JSON=$(python3 -c "
import json, sys
crumb_id = sys.argv[1]
files = sys.argv[2:]
print(json.dumps({'crumb_id': crumb_id, 'allowed_files': files}))
" "${TASK_ID}" ${AFFECTED_FILES_LIST}) || { echo "ERROR: scope JSON generation failed" >&2; exit 1; }

# Write atomically: temp file in same directory, then rename
python3 -c "
import json, os, sys
data = json.loads(sys.argv[1])
tmp = '.ant-farm-scope.json.tmp'
with open(tmp, 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
os.replace(tmp, '.ant-farm-scope.json')
" "${SCOPE_JSON}"
```

```
Task(
  subagent_type="ant-farm-general-purpose",   # or the agent type matching the task
  model="sonnet",
  prompt="{the composed implementer prompt from Step 2}"
)
```

The implementer executes the standard 6 mandatory steps:
1. **Claim**: `crumb_show(crumb_id="<TASK_ID>")` + `crumb_update(crumb_id="<TASK_ID>", status="in_progress")` (MCP)
2. **Design**: 4+ genuinely distinct approaches with tradeoffs; document chosen approach before coding
3. **Implement**: Write clean, minimal code satisfying the acceptance criteria
4. **Self-review** (MANDATORY): Re-read every changed file. For each file, verify the acceptance criteria are met. Document the review in the summary doc with file-specific notes — generic "looks clean" language fails claims-vs-code Check 4. This self-review step replaces the Reviewer team; it must be substantive.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (<TASK_ID>)"`
6. **Summary doc**: Write to `${SESSION_DIR}/summaries/<TASK_SUFFIX>.md` with all required sections (approaches considered, selected approach, implementation description, correctness review per-file, build/test validation, acceptance criteria checklist)

**Step 4:** Verify — spawn the Checkpoint Auditor for claims-vs-code.

```
Task(
  subagent_type="ant-farm-checkpoint-auditor",
  model="sonnet",
  prompt="claims-vs-code checkpoint (lite mode).
          Task ID: ${TASK_ID}.
          Summary doc: ${SESSION_DIR}/summaries/${TASK_SUFFIX}.md.
          Session directory: ${SESSION_DIR}.
          Read orchestration/templates/checkpoints/common.md and
          orchestration/templates/checkpoints/claims-vs-code.md for full instructions."
)
```

**On claims-vs-code PASS:** Proceed to Step 5.
**On claims-vs-code PARTIAL or FAIL:** Resume the implementer agent with the specific gaps (max 2 retries). If it fails after 2 retries, escalate to user.

**Progress log (after claims-vs-code PASS):**
```
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|WAVE_VERIFIED|wave=1|mode=lite|claims_vs_code=pass|tasks_verified=${TASK_ID}|commits=<hash>|next_step=STEP_5_CLOSE" >> ${SESSION_DIR}/progress.log
```

**Step 5:** Close — update crumb status, clean up sidecar, and push.

Call `crumb_close(ids=["<TASK_ID>"])` (MCP) to close the crumb.
If MCP is unavailable: `crumb close <TASK_ID>` via Bash.

```bash
rm -f .ant-farm-scope.json
git pull --rebase
git push
git status   # MUST show "up to date with origin"
```

**Progress log (after git push succeeds):**
```
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SESSION_COMPLETE|mode=lite|task=${TASK_ID}|pushed=true|next_step=DONE" >> ${SESSION_DIR}/progress.log
```

## Hard Gates

| Gate | Blocks | Artifact |
|------|--------|----------|
| pre-spawn-check PASS | Implementer spawn | `${SESSION_DIR}/pc/pc-session-pre-spawn-check-impl-{timestamp}.md` |
| claims-vs-code PASS | Crumb close and push | `${SESSION_DIR}/pc/pc-{TASK_SUFFIX}-claims-vs-code-{timestamp}.md` |

## Progress Log Format

All lite-mode entries include `mode=lite` as a pipe-delimited field. This field is parseable by `scripts/parse-progress-log.sh` because the script reads the step_key field (field 2) to determine workflow position — the `mode=lite` field (in the rest fields, field 3+) is carried through as metadata and appears in resume plan output under "Details."

**Full entry format:**
```
{ISO8601_TIMESTAMP}|{STEP_KEY}|{field=value}|...|mode=lite|{field=value}|...
```

**Lite-mode step keys and their progress.log entries:**

| Step | step_key | Example entry |
|------|----------|---------------|
| Session setup | `SESSION_INIT` | `2026-01-01T00:00:00Z\|SESSION_INIT\|complete\|mode=lite\|session_dir=.crumbs/sessions/_session-abc\|next_step=STEP_1_SELECT` |
| Implementer spawned | `WAVE_SPAWNED` | `2026-01-01T00:01:00Z\|WAVE_SPAWNED\|wave=1\|mode=lite\|task=my-project-abc\|pre_spawn_check=pass\|next_step=STEP_3_IMPLEMENT` |
| claims-vs-code PASS | `WAVE_VERIFIED` | `2026-01-01T00:05:00Z\|WAVE_VERIFIED\|wave=1\|mode=lite\|claims_vs_code=pass\|tasks_verified=my-project-abc\|commits=a1b2c3d\|next_step=STEP_5_CLOSE` |
| Session complete | `SESSION_COMPLETE` | `2026-01-01T00:06:00Z\|SESSION_COMPLETE\|mode=lite\|task=my-project-abc\|pushed=true\|next_step=DONE` |

> **Compatibility note**: Lite-mode step keys (`SESSION_INIT`, `WAVE_SPAWNED`, `WAVE_VERIFIED`, `SESSION_COMPLETE`) are a subset of the full-mode step keys defined in `scripts/parse-progress-log.sh`. The `mode=lite` field in the rest fields does not affect step_key parsing — it is metadata for human inspection and resume plan output.

## Retry Limits

| Situation | Max Retries | After Limit |
|-----------|-------------|-------------|
| pre-spawn-check FAIL | 1 | Escalate to user |
| claims-vs-code PARTIAL or FAIL | 2 | Escalate to user with full context |

## Template Lookup

| Workflow Phase | Read This File |
|----------------|----------------|
| Task brief audit (Step 2) | `orchestration/templates/checkpoints/common.md` + `orchestration/templates/checkpoints/pre-spawn-check.md` |
| Substance verification (Step 4) | `orchestration/templates/checkpoints/common.md` + `orchestration/templates/checkpoints/claims-vs-code.md` |
| Implementer agent type reference | `orchestration/reference/agent-types.md` |
| crumb CLI quick reference | `orchestration/reference/crumb-cheatsheet.md` |
