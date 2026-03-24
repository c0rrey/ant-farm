# Orchestration Rules
<!-- .local override: To customize, create RULES.local.md in the same directory. Your local file will not be overwritten by setup.sh. -->

> **Tool invocation**: Prefer MCP tool equivalents (`crumb_show`, `crumb_update`, `crumb_close`, `crumb_ready`, `crumb_blocked`, `crumb_create`, `crumb_link`, `crumb_trail_list`, `crumb_trail_show`, `crumb_trail_close`) over CLI calls. Fall back to `crumb <command>` via Bash if MCP is unavailable.

## Path Reference Convention

File paths in this document use **repo-root relative** format. At runtime: `orchestration/` → `~/.claude/orchestration/`; `agents/` → `~/.claude/agents/`. Shorthand like "templates/recon-planner.md" implies the `orchestration/` prefix.

## Orchestrator Prohibitions (read FIRST)

- **PREFER RULES.local.md** — If `RULES.local.md` exists in the same directory as this file, read and follow it instead of (or in addition to) this file. Local overrides take precedence.
- **NEVER** run `crumb show`, `crumb ready`, `crumb list`, `crumb blocked`, or any `crumb` query command — the Recon Planner does this
- **NEVER** read source code, tests, project data files, or config files — agents do this
- **NEVER** read agent **instruction files** (recon-planner.md, prompt-composer.md, implementation.md, checkpoints/*.md, reviews.md, etc.) — pass the path to the agent, let it read its own instructions
- **NEVER** send `shutdown_request` to any Reviewer team member before Step 4.
  - **Authorization**: Shutdown is authorized only by the Step 3c termination check (zero P1/P2 findings) — this sets a flag, not immediate dispatch.
  - **Dispatch timing**: Send `shutdown_request` only after the review loop fully converges and the session reaches Step 4+. Do NOT send at Step 3c or earlier.

## Orchestrator Read Permissions

**PERMITTED (must read):** `{SESSION_DIR}/briefing.md`, `{SESSION_DIR}/task-metadata/*.md`,
`{SESSION_DIR}/previews/*.md`, `{SESSION_DIR}/review-reports/*.md`, verdict tables from Checkpoint Auditor,
commit messages and git status/log/diff --stat output, agent notifications.

**PERMITTED (once per phase):** `orchestration/templates/implementer-skeleton.md` (per implementation wave),
`orchestration/templates/reviewer-skeleton.md` (per review cycle),
`orchestration/templates/review-consolidator-skeleton.md` (per review cycle),
`orchestration/templates/scribe-skeleton.md` (per session, to fill placeholders before spawning Session Scribe),
project `CLAUDE.md`, `{SESSION_DIR}/exec-summary.md` (only on session-complete escalation),
`orchestration/reference/crumb-cheatsheet.md` (when composing prompts with crumb commands).

**FORBIDDEN (agents read; Orchestrator never reads):**
- `orchestration/templates/recon-planner.md`, `orchestration/templates/prompt-composer.md`,
  `orchestration/templates/implementation.md`, `orchestration/templates/checkpoints/`,
  `orchestration/templates/reviews.md`, `orchestration/reference/dependency-analysis.md`,
  `orchestration/reference/known-failures.md`
- Source code, tests, project configs, application data files
- Raw `crumb show`, `crumb ready`, `crumb blocked`, `crumb list` output

## Workflow: "Let's Get to Work"

**Step 0:** Session setup — run the commands in the Session Directory section below to
            generate SESSION_ID and SESSION_DIR. Store both as variables in your context.
            Then immediately proceed to Step 1.
            Do NOT examine, read, or query any task/issue details.
            **Progress log:** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SESSION_INIT|complete|session_dir=${SESSION_DIR}|next_step=STEP_1_SCOUT" >> ${SESSION_DIR}/progress.log`

**Step 0a: Crash Recovery Check**
            > **[CONDITIONAL — only run if a prior session is indicated in the user's message.]**

            Run BEFORE generating a new SESSION_ID. If the user's message contains a session directory
            path, set `PRIOR_SESSION_DIR="<path from user message>"`. Then:
            1. Verify the directory exists: `[ -d "${PRIOR_SESSION_DIR}" ]` — if not, surface error and await instruction.
            2. Run `bash scripts/parse-progress-log.sh "${PRIOR_SESSION_DIR}"` (detects `handoff.json` automatically).
            3. **Exit 0**: read `{PRIOR_SESSION_DIR}/resume-plan.md` and present verbatim to user. Await `resume` or `fresh start`.
               - `resume`: restore SESSION_DIR to the prior value; use `context_notes`/`next_action` from `handoff.json` if present.
               - `fresh start`: generate a new SESSION_ID and proceed normally.
            4. **Exit 2**: prior session completed — proceed normally with a new SESSION_ID.
            5. **Exit 1**: surface the error to the user and await instruction.

## Position Check (MANDATORY — GLOBAL, applies at ALL phase transitions)

> **Global rule** — applies at every phase boundary (Steps 0→1, 1→2, 2→3, 3→3b, 3b→3c, etc.).
> `ant-farm-gate-enforcer.js` enforces this mechanically on every Task spawn. This prose covers the response path.

On position-check mismatch:
- **Match**: proceed normally.
- **Mismatch**: STOP. Re-read the full progress log to determine actual position, then reconcile.
- **Empty / no match**: Run `parse-progress-log.sh ${SESSION_DIR}` to diagnose and present the resume plan.

**Hard requirement**: If the last WAVE_VERIFIED entry shows `next_step=REVIEW_3B` and
no subsequent WAVE_SPAWNED entry is present, the next action MUST be Step 3b (Review).
Skipping Step 3b is a critical workflow violation.

**next_step value convention**: Progress log entries use descriptive step identifiers
            that match the step labels in this file. Valid values:
            `STEP_1_SCOUT`, `STEP_2_PANTRY`, `STEP_3_VERIFY`, `STEP_3_CLAIMS_VS_CODE`,
            `REVIEW_3B`, `NEXT_WAVE`, `STEP_3C_TRIAGE`, `FIX_SCOUT`, `FIX_AGENTS_SPAWN`,
            `FIX_INNER_LOOP`, `ROUND_TRANSITION`, `STEP_4_DOCS`, `STEP_4B_XREF`,
            `STEP_5_SCRIBE`, `STEP_6_ESV`, `STEP_7_PUSH`, `DONE`.

**Step 1:** Recon — Read `{SESSION_DIR}/briefing.md` written by the Recon Planner's previous run, or spawn the Recon Planner
            (`ant-farm-recon-planner` subagent, `model: "opus"`) if this is the first session. Include in Recon Planner's prompt:
            (1) `Session directory: <value of SESSION_DIR>`,
            (2) `Mode: <mode>` — derive from the user's message:
                - User specifies an epic → `epic <epic-id>`
                - User lists specific tasks → `tasks <id1>, <id2>, ...`
                - User describes a filter → `filter <description>`
                - User gives no specific scope (e.g., just "let's get to work") → `ready`
            (3) the path `orchestration/templates/recon-planner.md` as its instruction file.
            WAIT for the Recon Planner to return its briefing verdict (written to `{SESSION_DIR}/briefing.md`).

**Step 1b:** startup-check gate — Spawn Checkpoint Auditor (`ant-farm-checkpoint-auditor`, `model: "haiku"`) with `Session directory: <SESSION_DIR>` and paths `orchestration/templates/checkpoints/common.md` + `startup-check.md`. `ant-farm-gate-enforcer.js` blocks all downstream spawns until startup-check records a PASS.

            **On PASS**: Proceed directly to Step 2 (no user approval needed). Zero-task guard: if task count is 0, escalate to user instead.
            **On FAIL**: Re-run Recon Planner with specific violations (do NOT present a failed strategy to the user); re-run startup-check. **Max 1 retry** — if still failing, surface to user.

            **Progress log (after startup-check PASS):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SCOUT_COMPLETE|briefing=${SESSION_DIR}/briefing.md|startup_check=pass|tasks_accepted=<N>|next_step=STEP_2_PANTRY" >> ${SESSION_DIR}/progress.log`

**Step 2:** Spawn — Spawn Prompt Composer (`ant-farm-prompt-composer`, `model: "opus"`, → templates/prompt-composer.md) with `Session directory: <SESSION_DIR>`. Then spawn Checkpoint Auditor (`ant-farm-checkpoint-auditor`, `model: "haiku"`) for pre-spawn-check (reads common.md + pre-spawn-check.md). Only after all pre-spawn-check PASS: spawn agents via implementer-skeleton.md (`model: "sonnet"`, Agent Type from Prompt Composer verdict table).
            **Wave pipelining**: When spawning wave N Implementers, include the wave N+1 Prompt Composer
            (`ant-farm-prompt-composer`, `model: "opus"`) in the SAME message. Flow per wave boundary:
            1. Wave N pre-spawn-check PASS → spawn wave N Implementers + wave N+1 Prompt Composer (in a single Task call to achieve concurrency)
            2. Wave N+1 Prompt Composer returns → spawn wave N+1 pre-spawn-check
            3. Wave N Implementers finish → run scope-verify/claims-vs-code (Step 3)
            4. Wave N+1 pre-spawn-check PASS + wave N scope-verify + claims-vs-code both PASS → spawn wave N+1 Implementers + wave N+2 Prompt Composer
            For the final wave (no wave N+1), skip the Prompt Composer — just spawn Implementers alone.
            **Progress log (after each wave's Implementers are spawned):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|WAVE_SPAWNED|wave=<N>|spawned=<agent-ids>|previews_dir=${SESSION_DIR}/previews|next_step=STEP_3_VERIFY" >> ${SESSION_DIR}/progress.log`

**Step 3:** Verify — Run scope-verify, then claims-vs-code, for each wave. PASS/FAIL/WARN verdict behavior lives in the checkpoint templates (`ant-farm-gate-enforcer.js` records gate state in `gate-status.json`).

            **scope-verify mode** — spawn Checkpoint Auditor (`model: "haiku"`) per committed task:
            - **Serial mode** (agents spawned individually): gate each agent before spawning the next.
            - **Batch mode** (agents spawned in parallel): run all scope-verify checks concurrently after all commits arrive.
            **Mode selection rule**: single message → batch; separate messages → serial. N=1 → use serial.
            **Partial wave commit (batch mode)**: run scope-verify for the committed subset; log crashes as failures.
            **Progress log (after all scope-verify reports PASS):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|WAVE_SCOPE_VERIFY_PASS|wave=<N>|mode=<serial|batch>|tasks_checked=<ids>|next_step=STEP_3_CLAIMS_VS_CODE" >> ${SESSION_DIR}/progress.log`

            After all scope-verify reports PASS, spawn Checkpoint Auditor (`model: "sonnet"`) for claims-vs-code (pass task IDs, commit hashes, summary doc paths; Auditor reads common.md + claims-vs-code.md itself). Failed claims-vs-code → resume agent (max 2 retries).
            **Progress log (after claims-vs-code PASS for each wave):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|WAVE_VERIFIED|wave=<N>|claims_vs_code=pass|tasks_verified=<ids>|commits=<hashes>|next_step=REVIEW_3B" >> ${SESSION_DIR}/progress.log`
            Note: For non-final waves, use `next_step=NEXT_WAVE` instead.

**Step 3b:** Review (round 1: Clarity, Edge Cases, Correctness, Drift; round 2+: Correctness, Edge Cases only) — Read `orchestration/RULES-review.md` now for the full Step 3b workflow. Validate commit range format and file list completeness before composing review briefs (RULES-review.md 3b-i.5).

            **Progress log (after reviewer team completes round 1):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_COMPLETE|round=<N>|team=complete|report=${SESSION_DIR}/review-reports/review-consolidated-${TIMESTAMP}.md|next_step=STEP_3C_TRIAGE" >> ${SESSION_DIR}/progress.log`

**Step 3c:** User triage — Read `orchestration/RULES-review.md` now for the full Step 3c workflow.

            **Progress log (after fix Recon Planner startup-check PASS):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|FIX_SCOUT_COMPLETE|round=<N>|startup_check=pass|fix_crumbs=<crumb-ids>|next_step=FIX_AGENTS_SPAWN" >> ${SESSION_DIR}/progress.log`
            **Progress log (after fix agents spawned):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|FIX_AGENTS_SPAWNED|round=<N>|fix_cgs=<names>|fix_pcs=fix-pc-scope-verify,fix-pc-claims-vs-code|next_step=FIX_INNER_LOOP" >> ${SESSION_DIR}/progress.log`
            **Progress log (after all fix CGs verified):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|FIX_CLAIMS_VS_CODE_COMPLETE|round=<N>|verified_cgs=<names>|commits=<hashes>|next_step=ROUND_TRANSITION" >> ${SESSION_DIR}/progress.log`
            **Progress log (after round transition):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|ROUND_TRANSITION|from_round=<N>|to_round=<N+1>|fix_commits=<range>|next_step=REVIEW_3B" >> ${SESSION_DIR}/progress.log`
            **Progress log (after triage decision — fix path):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_TRIAGED|round=<N>|p1=<count>|p2=<count>|decision=<auto_fix|fix_now>|root_causes=<count>|next_step=FIX_SCOUT" >> ${SESSION_DIR}/progress.log`
            **Progress log (after triage decision — non-fix path):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_TRIAGED|round=<N>|p1=<count>|p2=<count>|decision=<defer|terminated>|root_causes=<count>|next_step=STEP_4_DOCS" >> ${SESSION_DIR}/progress.log`

**Step 4:** Documentation — update README and CLAUDE.md in single commit.
            Note: session narrative and changelog entry are handled by the Session Scribe at Step 5.
            Before committing: file issues for any remaining work; run quality gates (tests, linters,
            builds) if code changed; apply review-findings gate (if reviews found P1 issues, present
            to user before proceeding — user decides fix now or defer; do NOT push with undisclosed
            P1 blockers).
            **Progress log (after doc commit):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|DOCS_COMMITTED|complete|commit=<hash>|next_step=STEP_4B_XREF" >> ${SESSION_DIR}/progress.log`

**Step 4b:** Verify — cross-references valid, all tasks accounted for. Update issue status: close
            finished tasks, update in-progress items.
            **Progress log (after cross-reference check):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|XREF_VERIFIED|complete|tasks_closed=<ids>|next_step=STEP_5_SCRIBE" >> ${SESSION_DIR}/progress.log`

**Step 5:** Session Scribe — spawn the Session Scribe agent to write the session exec summary and CHANGELOG entry.
            ```
            Task(
              subagent_type="ant-farm-session-scribe",
              model="sonnet",
              prompt="Write session exec summary. Session dir: {SESSION_DIR}. Commit range: {RANGE}.
                      Open crumbs: {IDS}. CHANGELOG path: CHANGELOG.md.
                      Read orchestration/templates/scribe-skeleton.md for full instructions."
            )
            ```
            **Progress log (after Session Scribe completes):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SCRIBE_COMPLETE|exec_summary=${SESSION_DIR}/exec-summary.md|next_step=STEP_6_ESV" >> ${SESSION_DIR}/progress.log`

**Step 6:** session-complete — spawn Checkpoint Auditor for Exec Summary Verification. **Hard gate: must PASS before Step 7.**
            ```
            Task(
              subagent_type="ant-farm-checkpoint-auditor",
              model="haiku",
              prompt="session-complete checkpoint. Session dir: {SESSION_DIR}.
                      Session start commit: {SESSION_START_COMMIT} (first commit of this session).
                      Session end commit: {SESSION_END_COMMIT} (final commit before push, typically HEAD).
                      Session start date: {SESSION_START_DATE} (ISO 8601, e.g. 2026-02-22 — used to scope crumb list).
                      Verify exec-summary.md and CHANGELOG.md.
                      Read orchestration/templates/checkpoints/common.md and orchestration/templates/checkpoints/session-complete.md for full instructions."
            )
            ```
            > `SESSION_START_COMMIT` = first commit this session; `SESSION_END_COMMIT` = HEAD before Step 7's CHANGELOG commit; `SESSION_START_DATE` = UTC date of Step 0 (derivable from `SESSION_ID`).
            **On FAIL**: Re-spawn Session Scribe with violations (max 1 retry). On second FAIL: escalate to user.
            **Progress log (after session-complete PASS):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SESSION_COMPLETE_PASS|artifact=${SESSION_DIR}/pc/pc-session-complete-$(date +%Y%m%d-%H%M%S).md|next_step=STEP_7_PUSH" >> ${SESSION_DIR}/progress.log`

**Step 7:** Land the plane — Orchestrator commits the Session Scribe's CHANGELOG.md, copies the exec summary to history (local only), then pulls and pushes. NEVER `git add` any file under `.crumbs/` — the entire directory is gitignored.
            ```bash
            git add CHANGELOG.md && git commit -m "docs: add session {SESSION_ID} changelog entry"
            mkdir -p .crumbs/history
            cp "${SESSION_DIR}/exec-summary.md" ".crumbs/history/exec-summary-${SESSION_ID}.md"
            git pull --rebase
            git push
            ```
            Run `git status` after push — output MUST show "up to date with origin".

            **Post-push sync**: Run `./scripts/setup.sh` to sync orchestration files from repo to `~/.claude/`.
            Clean up stashes and remote branches. Provide hand-off context for the next session.
            **Progress log (after git push succeeds):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SESSION_COMPLETE|pushed=true|next_step=DONE" >> ${SESSION_DIR}/progress.log`

## Hard Gates

> Gate ordering (startup-check → pre-spawn-check → scope-verify → claims-vs-code → review-integrity → session-complete) is enforced by `ant-farm-gate-enforcer.js`. This table documents artifact paths.

| Gate | Blocks | Artifact |
|------|--------|----------|
| startup-check PASS | Prompt Composer spawn (and all downstream steps) | ${SESSION_DIR}/pc/pc-session-startup-check-<timestamp>.md |
| pre-spawn-check PASS (impl) | Agent spawn | ${SESSION_DIR}/pc/*-pre-spawn-check-*.md |
| pre-spawn-check PASS (review) | Reviewer team spawn | ${SESSION_DIR}/pc/pc-session-pre-spawn-check-review-<timestamp>.md |
| scope-verify PASS | Serial mode: next agent spawn; Batch mode: claims-vs-code spawn | ${SESSION_DIR}/pc/*-scope-verify-*.md |
| claims-vs-code PASS | Task closure (`crumb_close`) | ${SESSION_DIR}/pc/*-claims-vs-code-*.md |
| review-integrity PASS | Presenting results | ${SESSION_DIR}/pc/pc-session-review-integrity-<timestamp>.md |
| Reviews | Presenting findings to user (Step 3c) | ${SESSION_DIR}/review-reports/review-consolidated-<timestamp>.md |
| session-complete PASS | Git push (Step 7) | ${SESSION_DIR}/pc/pc-session-complete-<timestamp>.md |

> **Note (Reviews gate):** Reviews are mandatory after ALL implementation completes (round 1). If findings require a fix cycle, reviews re-run with reduced scope — Correctness and Edge Cases only; Clarity and Drift are dropped (round 2+).

## Agent Types and Models

- Agent types: `orchestration/reference/agent-types.md`
- Model assignments: `orchestration/reference/model-assignments.md` — MUST include `model` parameter on every `Task` call (omitting inherits Orchestrator's opus model, wasting tokens)

## Concurrency Rules

- Max 7 Implementers concurrent
- Max 12 total agents (Implementers + support agents: Prompt Composer, Checkpoint Auditor, Recon Planner)
- No two agents edit the same file — queue conflicting tasks sequentially
- Each agent runs `git pull --rebase` before committing
- Only the Orchestrator pushes to remote
- Only the Orchestrator updates README; the Session Scribe writes CHANGELOG.md (committed by Orchestrator at Step 7)
- Pipeline wave N Implementers with wave N+1 Prompt Composer in a single message

### Wave Management

**Retry counting**: Retry spawns count against the concurrent agent limit. A failed-and-respawned Implementer occupies a slot.

**Mid-wave decision tree**:

| Scenario | Action |
|----------|--------|
| Agent failure | Log failure, file a crumb for the failed task, continue with remaining agents. Re-attempt in next wave if slots available. |
| Early completion | Do NOT backfill mid-wave. Wait for the full wave to complete before starting the next. Rationale: backfilling creates interleaved commits that complicate review scope tracking. |
| All agents fail | Stop. Surface failures to user. Do not auto-retry the entire wave. |

## Session Directory

Read `orchestration/reference/session-directory.md` for full setup instructions and artifact layout.

At session start (Step 0), run:

    SESSION_ID="$(date +%Y%m%d-%H%M%S)-$(od -An -tx1 -N4 /dev/urandom | tr -d ' \n')"
    SESSION_DIR=".crumbs/sessions/_session-${SESSION_ID}"
    mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts,pc,summaries,signals}  # pc = checkpoint artifacts (legacy: "pest control")
    _PRUNE_ERR=$(crumb prune 2>&1 >/dev/null) || echo "WARNING: crumb prune failed (non-blocking): ${_PRUNE_ERR}"  # CLI only — no MCP equivalent

Store SESSION_DIR in your context and pass it explicitly to every agent that needs to write artifacts.

**Session directory prefixes**: `crumb prune` manages directories matching any of these prefixes under `.crumbs/sessions/`:
- `_session-` — standard work sessions (the default; used by the Orchestrator workflow)
- `_decompose-` — decomposition/planning sessions (used by `/ant-farm-plan`)
- `_review-` — reserved for future use (currently unused by any workflow)

## Anti-Patterns

- Reading every agent's output files — trust summaries and commit messages
- Spawning agents one at a time — batch by file/priority
- Re-reading the same metadata — read once, take notes in session state file
- Pushing mid-session — only push at end (atomic deployment)
- Updating docs per-agent — batch all doc updates in Step 4
- Verbose agent prompts — be concise, agents read their own task details from their task brief
- Running individual checkpoints per agent — spawn one Checkpoint Auditor with the full batch
- Using TaskOutput or Read on background agent output files — poll for sentinel files instead (see below)

## Sentinel-File Completion Protocol

Do NOT use TaskOutput or Read on background agent output files — use sentinel files instead.

**Protocol**: Background agents write a sentinel file as their absolute last action:
```bash
echo "VERDICT: {PASS|FAIL}
COMMIT: {hash|none}
FILES: {changed-file-list}
SUMMARY: {one-line-description}" > "${SESSION_DIR}/signals/{TASK_SUFFIX}.done"
```

**Orchestrator polling**: Poll for sentinel files using Bash, not TaskOutput:
1. **Activity check**: `stat -f '%m' "${SESSION_DIR}/signals/"` (macOS) or `stat -c '%Y' "${SESSION_DIR}/signals/"` (Linux) — directory mtime changes when agents write
2. **Completion check**: `ls "${SESSION_DIR}/signals/"*.done 2>/dev/null` — list completed agents
3. **Read verdict**: `cat "${SESSION_DIR}/signals/{TASK_SUFFIX}.done"` — compact verdict without JSONL
4. **Crash detection**: If no directory activity for >5 minutes and no `.done` file, the agent likely crashed. Escalate or respawn.

## Template Lookup

| Workflow Phase | Read This File |
|----------------|----------------|
| Composing agent prompts (Step 2) | orchestration/templates/prompt-composer.md |
| Agent skeleton for spawning (Step 2) | orchestration/templates/implementer-skeleton.md |
| Review skeleton for team (Step 3b) | orchestration/templates/reviewer-skeleton.md |
| Review Consolidator skeleton for consolidation (Step 3b) | orchestration/templates/review-consolidator-skeleton.md |
| Implementation details (read by the Prompt Composer) | orchestration/templates/implementation.md |
| Checkpoint details (read by Checkpoint Auditor) | orchestration/templates/checkpoints/ (common.md + specific checkpoint file) |
| Review details (read by build-review-prompts.sh) | orchestration/templates/reviews.md |
| Focus area definitions for reviewer prompts (read by build-review-prompts.sh) | orchestration/templates/review-focus-areas.md |
| Pre-flight recon (Step 1) | orchestration/templates/recon-planner.md |
| Conflict patterns (read by the Recon Planner) | orchestration/reference/dependency-analysis.md |
| Diagnosing a failure or post-mortem | orchestration/reference/known-failures.md |
| Creating/recovering the Orchestrator's state file | orchestration/templates/orchestrator-state.md |
| Exec summary authoring (Step 5) | orchestration/templates/scribe-skeleton.md |
| Setting up orchestration in new project | orchestration/SETUP.md |

## Retry Limits

> Global retry cap and per-type limits are tracked by `retry-tracker.js` (`retries.json`). Escalation paths below are PROMPT_ONLY — the hook enforces counts but cannot supply them.

| Situation | Max Retries | After Limit |
|-----------|-------------|-------------|
| Agent fails claims-vs-code | 2 | Escalate to user with full context |
| review-integrity fails | 1 | Present to user with verification report attached |
| Agent stuck (>10 min without commit — see Stuck-Agent Diagnostic Procedure) | 0 | Run stuck-agent diagnostic; escalate to user |
| Prompt Composer pre-spawn-check fails | 1 | Escalate to user; do not spawn Implementers without verified prompts |
| Recon Planner fails or returns no tasks | 1 | Escalate to user; do not proceed to Step 2 without task list |
| startup-check FAIL -> re-Recon Planner cycle | 1 | Escalate to user with startup-check violations; do not re-run Recon Planner a third time |
| Fix implementer (CG) stuck/crash (no commit in team) | 0 | Run stuck-agent diagnostic; file a crumb for the failed fix; escalate to user. Do NOT re-spawn without user approval |
| Fix PC crash (fix-pc-scope-verify or fix-pc-claims-vs-code) | 1 | Spawn replacement into team (`team_name: "reviewer-team"`); resume from last SendMessage |
| Reviewer failure (round 2+, re-task via SendMessage fails) | 1 | Spawn fresh reviewer into team as replacement; re-send the round transition message |
| Review Consolidator crash (before crumb filing complete) | 1 | Spawn fresh Review Consolidator into team with handoff brief describing which crumbs were filed and which remain; re-run review-integrity after |
| review-integrity material spot-check fail | 1 | Shut down current Review Consolidator; spawn fresh Review Consolidator into team with handoff brief identifying failed crumbs; re-run full crumb review then re-run review-integrity |
| Session Scribe fails session-complete | 1 | Escalate to user with session-complete report; user decides fix manually or push as-is |
| Total retries per session | 5 | Pause all new spawns; triage with user |

### Stuck-Agent Diagnostic Procedure

`ant-farm-gate-enforcer.js` emits WARNING at >10 min and CRITICAL at >15 min without a commit. Procedure is PROMPT_ONLY:

1. Read the task brief — confirm scope was unambiguous.
2. Check `.crumbs/sessions/_session-*/` for a partial summary showing how far it progressed.
3. Run `git log --oneline -10` — confirm no commit was silently made.
4. If still running: check most recent output for blocking question, permission error, or tool failure.
5. Escalate with: task ID, agent type, elapsed time, last-known output. Do NOT re-spawn without user approval.

### Wave Failure Threshold

`ant-farm-gate-enforcer.js` blocks new spawns when the previous wave's failure rate exceeds 50% (configurable). When this threshold is hit: stop new spawns → collect failure summaries → notify user (task ID, failure type, retry count) → await instruction (re-run subset, abort, or resolve blockers and resume).

**Failure counting**: claims-vs-code failure counts after 2 retries exhausted; stuck agent (>10 min) counts immediately; crash counts immediately. A wave = agents spawned concurrently in a single Step 2 batch; failures do not carry across waves.

## Crumb Priority Calibration

> For crumbs filed in the tracker (not reviewer severity, which is defined in `reviews.md`).

| Priority | Examples |
|----------|---------|
| **P1** | build failure, broken links, data loss, security vulnerability |
| **P2** | visual regression, accessibility issue, functional degradation |
| **P3** | style, naming, cleanup, polish |

Project-specific overrides belong in the project's CLAUDE.md or QUALITY_PROCESS.md.

## Context Preservation Targets

- Token budget: finish with >50% remaining (1M context window)
- File reads in the Orchestrator: <10 for 40+ task sessions
- Concurrent agents: typical 5-6 Implementers, max 12 total
- Commits per session: <20 (batch related work)

`ant-farm-context-monitor.js` warns at 35%/25% remaining; CRITICAL advisory instructs you to tell the user to run `/ant-farm-pause`.
