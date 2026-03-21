# Orchestration Rules
<!-- .local override: To customize, create RULES.local.md in the same directory. Your local file will not be overwritten by setup.sh. -->

## Path Reference Convention

All file paths in this document use **repo-root relative** format: `orchestration/templates/scout.md`.

When code runs at runtime, agent files are synced to `~/.claude/agents/` and orchestration files are
accessible at `~/.claude/orchestration/templates/scout.md`. To translate repo paths to runtime paths:
- Replace `orchestration/` with `~/.claude/orchestration/`
- Replace `agents/` with `~/.claude/agents/`

**In-document shorthand** (e.g., "templates/scout.md") is informal and always refers to the repo-root path with the `orchestration/` prefix implied.

## Queen Prohibitions (read FIRST)

- **PREFER RULES.local.md** — If `RULES.local.md` exists in the same directory as this file, read and follow it instead of (or in addition to) this file. Local overrides take precedence.
- **NEVER** run `crumb show`, `crumb ready`, `crumb list`, `crumb blocked`, or any `crumb` query command — the Scout does this
- **NEVER** read source code, tests, project data files, or config files — agents do this
- **NEVER** read agent **instruction files** (scout.md, pantry.md, implementation.md, checkpoints/*.md, reviews.md, etc.) — pass the path to the agent, let it read its own instructions
- **NEVER** send `shutdown_request` to any Reviewer team member before Step 4. The **only** authorized shutdown trigger is the termination check in Step 3c (zero P1/P2 findings). Do NOT send shutdown_request at the Step 3c decision fork or anywhere else before convergence.

Your first instinct will be to "gather context" by running `crumb show` on the task list.
**Do not do this.** Spawn the Scout and let it gather context for you.

## Queen Read Permissions

The Queen's window is restricted to prevent context bloat, but certain files are explicitly PERMITTED.

**PERMITTED (Queen must read these):**
- `{SESSION_DIR}/briefing.md` — Scout-generated strategy summary; Queen reads after startup-check PASS to confirm task count before auto-proceeding to Step 2
- `{SESSION_DIR}/task-metadata/*.md` — Per-task scope, acceptance criteria (pre-digested by Scout)
- `{SESSION_DIR}/previews/*.md` — Combined prompt previews (pre-digested by Pantry)
- `{SESSION_DIR}/review-reports/*.md` — Individual reviewer reports and Review Consolidator consolidated summary
- Verdict tables from Prompt Composer and Checkpoint Auditor — pre-spawn-check, scope-verify, claims-vs-code, review-integrity verdicts
- Commit messages and git status/log/diff --stat output
- Agent notifications (as they complete)

**PERMITTED (Queen reads once per phase, for context only):**
- `orchestration/templates/crumb-gatherer-skeleton.md` — Once per implementation wave (skeleton structure; see [Glossary: wave](GLOSSARY.md#workflow-concepts))
- `orchestration/templates/reviewer-skeleton.md` — Once per review cycle (skeleton structure)
- `orchestration/templates/review-consolidator-skeleton.md` — Once per review cycle (skeleton structure)
- `orchestration/templates/scribe-skeleton.md` — Once per session (read to fill placeholders before spawning the Scribe at Step 5)
- Project's `CLAUDE.md` — Global project rules
- `{SESSION_DIR}/exec-summary.md` — Scribe output; read only when session-complete checkpoint escalates to user with a failed exec summary
- `orchestration/reference/crumb-cheatsheet.md` — crumb CLI quick reference; read when composing agent prompts that invoke crumb commands

**FORBIDDEN (agents read; Queen never reads):**
- `orchestration/templates/scout.md` — Scout's instruction file
- `orchestration/templates/pantry.md` — Pantry's instruction file
- `orchestration/templates/implementation.md` — Implementation details (read by Pantry)
- `orchestration/templates/checkpoints/` — Checkpoint definitions (read by Checkpoint Auditor; common.md + specific checkpoint file)
- `orchestration/templates/reviews.md` — Review protocol (read by build-review-prompts.sh)
- `orchestration/reference/dependency-analysis.md` — Used by Scout for conflict analysis
- `orchestration/reference/known-failures.md` — Reference material; for post-mortem only
- Source code files, tests, project configs, application data files
- Raw `crumb show`, `crumb ready`, `crumb blocked`, `crumb list` output (let the Scout digest this)

## Workflow: "Let's Get to Work"

**Step 0:** Session setup — run the commands in the Session Directory section below to
            generate SESSION_ID and SESSION_DIR. Store both as variables in your context.
            Then immediately proceed to Step 1.
            Do NOT examine, read, or query any task/issue details.
            **Progress log:** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SESSION_INIT|complete|session_dir=${SESSION_DIR}|next_step=STEP_1_SCOUT" >> ${SESSION_DIR}/progress.log`

            **Crash recovery detection (run BEFORE generating a new SESSION_ID):**
            Check whether the user's message contains a session directory path
            (e.g. `.crumbs/sessions/_session-<id>`). If a prior SESSION_DIR is
            supplied or you can identify an incomplete session from context:
            1. Verify the session directory exists:
               ```bash
               [ -d "<prior_SESSION_DIR>" ] || echo "Session directory not found: <prior_SESSION_DIR>"
               ```
               If the directory does not exist, surface the message to the user and await instruction.
               Do NOT proceed to run `parse-progress-log.sh` on a missing directory.
            2. Run `bash scripts/parse-progress-log.sh <prior_SESSION_DIR>`
            3. On exit 0: read `<prior_SESSION_DIR>/resume-plan.md` and present it verbatim to the user.
               Wait for the user to reply `resume` or `fresh start` before taking any further action.
               - `resume`: restore SESSION_DIR to the prior value and continue from the indicated step.
               - `fresh start`: generate a new SESSION_ID and proceed normally.
            4. On exit 2: the prior session completed — proceed normally with a new SESSION_ID.
            5. On exit 1: surface the error (including the path that was not found) to the user and await instruction.
            If no prior session is indicated, skip crash recovery and proceed normally.

**Position Check (MANDATORY):**

            **Run this check before every major phase transition.** This is required after every wave
            completion (WAVE_VERIFIED) and after every fix agent completion (FIX_CMVCC_COMPLETE).
            It is also recommended at any Step boundary where context may have been refreshed.

            ```bash
            tail -1 "${SESSION_DIR}/progress.log" | grep -o 'next_step=[^|]*'
            ```

            Compare the `next_step=` value against the step you are about to execute:
            - **Match**: proceed normally.
            - **Mismatch**: STOP. Do not execute the intended step. Re-read the full progress log
              to determine the actual workflow position, then reconcile before continuing.
            - **Empty / no match**: progress.log may be missing or malformed. Run
              `parse-progress-log.sh ${SESSION_DIR}` to diagnose and present the resume plan.

            **Hard requirement**: If the last WAVE_VERIFIED entry shows `next_step=REVIEW_3B` and
            no subsequent WAVE_SPAWNED entry is present, the next action MUST be Step 3b (Review).
            Skipping Step 3b is a critical workflow violation.

**Step 1:** Recon — Read `{SESSION_DIR}/briefing.md` written by the Scout's previous run, or spawn the Scout
            (`ant-farm-recon-planner` subagent, `model: "opus"`) if this is the first session. Include in Scout's prompt:
            (1) `Session directory: <value of SESSION_DIR>`,
            (2) `Mode: <mode>` — derive from the user's message:
                - User specifies an epic → `epic <epic-id>`
                - User lists specific tasks → `tasks <id1>, <id2>, ...`
                - User describes a filter → `filter <description>`
                - User gives no specific scope (e.g., just "let's get to work") → `ready`
            (3) the path `orchestration/templates/scout.md` as its instruction file.
            Do NOT read the scout template yourself. Do NOT run `crumb show`, `crumb ready`, `crumb blocked`,
            or any other `crumb` commands — the Scout handles all task discovery and metadata gathering.
            WAIT for the Scout to return its briefing verdict (written to `{SESSION_DIR}/briefing.md`).

**Step 1b:** startup-check gate — After Scout writes `{SESSION_DIR}/briefing.md`, spawn Checkpoint Auditor
            (`ant-farm-checkpoint-auditor`, `model: "haiku"`) for Scout Strategy Verification (startup-check).
            Pass `Session directory: <value of SESSION_DIR>` and the paths `orchestration/templates/checkpoints/common.md`
            and `orchestration/templates/checkpoints/startup-check.md` as its instruction files. Checkpoint Auditor reads `{SESSION_DIR}/briefing.md` itself and runs all three
            mechanical checks (file overlap within waves, file list match against crumbs, intra-wave dependency
            ordering). **startup-check must PASS before proceeding.**

            **On startup-check PASS**: Proceed directly to Step 2. Do NOT wait for user approval. startup-check is the
            mechanical safety gate — a passing strategy is structurally sound and ready to execute.
            No complexity threshold applies; auto-approve regardless of task count.
            **Zero-task guard:** If the briefing's task count is 0, do NOT auto-proceed to Step 2.
            Escalate to the user with the zero-task briefing for review and await instruction.
            **On startup-check FAIL**: Re-run Scout with the specific violations from the startup-check report (do NOT present
            a failed strategy to the user). After Scout revises briefing.md, re-run startup-check.
            **Retry cap:** The startup-check FAIL -> re-Scout cycle has a maximum of 1 retry. If startup-check fails again
            after one re-Scout run, do NOT re-run Scout a second time. Surface the startup-check violations to
            the user and await instruction.

            **Progress log (after startup-check PASS):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SCOUT_COMPLETE|briefing=${SESSION_DIR}/briefing.md|startup_check=pass|tasks_accepted=<N>|next_step=STEP_2_PANTRY" >> ${SESSION_DIR}/progress.log`
            where `<N>` is the count of tasks in the briefing task list after startup-check PASS (N=0 is not logged — it is caught by the zero-task guard earlier in Step 1b).

**Step 2:** Spawn — Spawn the Prompt Composer (`ant-farm-prompt-composer`, `model: "opus"`) for task briefs + combined previews
            (→ orchestration/templates/pantry.md, Section 1). Include `Session directory: <value of SESSION_DIR>`
            in Prompt Composer's prompt. Pass preview file paths and SESSION_DIR to Checkpoint Auditor
            (`ant-farm-checkpoint-auditor`, `model: "haiku"`) for pre-spawn-check; Checkpoint Auditor reads `orchestration/templates/checkpoints/common.md` and `orchestration/templates/checkpoints/pre-spawn-check.md` itself.
            Only after all pre-spawn-check PASS: spawn agents using skeleton
            (→ orchestration/templates/crumb-gatherer-skeleton.md, using Agent Type from Prompt Composer verdict table, `model: "sonnet"` for all Crumb Gatherers regardless of subagent_type).
            **Wave pipelining**: When spawning wave N Crumb Gatherers, include the wave N+1 Prompt Composer
            (`ant-farm-prompt-composer`, `model: "opus"`) in the SAME message so they launch concurrently.
            The Prompt Composer reads from task-metadata (written by Scout) and has no dependency on wave N's output.
            This eliminates the idle gap between waves. The flow per wave boundary:
            1. Wave N pre-spawn-check PASS → spawn wave N Crumb Gatherers + wave N+1 Prompt Composer (in a single Task call to achieve concurrency)
            2. Wave N+1 Prompt Composer returns → spawn wave N+1 pre-spawn-check
            3. Wave N Crumb Gatherers finish → run scope-verify/claims-vs-code (Step 3)
            4. Wave N+1 pre-spawn-check PASS + wave N scope-verify + claims-vs-code both PASS → spawn wave N+1 Crumb Gatherers + wave N+2 Prompt Composer
            For the final wave (no wave N+1), skip the Pantry — just spawn Crumb Gatherers alone.
            **Progress log (after each wave's Crumb Gatherers are spawned):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|WAVE_SPAWNED|wave=<N>|spawned=<agent-ids>|previews_dir=${SESSION_DIR}/previews|next_step=STEP_3_VERIFY" >> ${SESSION_DIR}/progress.log`

**Step 3:** Verify — Run scope-verify, then claims-vs-code, for each wave.

            **scope-verify execution mode depends on how agents in the wave were spawned:**
            - **Serial mode** (agents spawned sequentially, one at a time): After each agent commits, spawn
              one Checkpoint Auditor (`model: "haiku"`) instance for that agent's commit. This is a true per-agent
              gate — the next agent must not be spawned until scope-verify PASS is received for the previous one.
            - **Batch mode** (agents spawned in parallel in a single message): After ALL wave agents have
              committed, spawn one Checkpoint Auditor (`model: "haiku"`) instance per committed task (can be
              concurrent). Wait for ALL scope-verify reports before proceeding to claims-vs-code. This is a post-hoc batch
              check — per-agent serial gating is mechanically impossible when commits arrive nearly
              simultaneously.
            **Mode selection rule**: If you spawned agents in a single message (parallel wave), use batch
            mode. If you spawned agents individually in separate messages, use serial mode.
            **Progress log (after all scope-verify reports PASS for the wave):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|WAVE_SCOPE_VERIFY_PASS|wave=<N>|mode=<serial|batch>|tasks_checked=<ids>|next_step=STEP_3_CLAIMS_VS_CODE" >> ${SESSION_DIR}/progress.log`

            After all scope-verify reports PASS, spawn Checkpoint Auditor (`model: "sonnet"`) for claims-vs-code
            (pass task IDs, commit hashes, summary doc paths; Checkpoint Auditor reads
            `orchestration/templates/checkpoints/common.md` + `orchestration/templates/checkpoints/claims-vs-code.md` + task-metadata/ + git diffs itself).
            Failed claims-vs-code → resume agent (max 2 retries).
            **Progress log (after claims-vs-code PASS for each wave):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|WAVE_VERIFIED|wave=<N>|claims_vs_code=pass|tasks_verified=<ids>|commits=<hashes>|next_step=REVIEW_3B" >> ${SESSION_DIR}/progress.log`
            Note: For non-final waves, use `next_step=NEXT_WAVE` instead. The Position Check (see below) uses this value to confirm the correct next action.

**Step 3b:** Review — Read `orchestration/RULES-review.md` now for the full Step 3b workflow.

            **Progress log (after reviewer team completes round 1):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_COMPLETE|round=<N>|team=complete|report=${SESSION_DIR}/review-reports/review-consolidated-${TIMESTAMP}.md|next_step=STEP_3C_TRIAGE" >> ${SESSION_DIR}/progress.log`

**Step 3c:** User triage — Read `orchestration/RULES-review.md` now for the full Step 3c workflow.

            **Progress log (after fix Scout startup-check PASS):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|FIX_SCOUT_COMPLETE|round=<N>|startup_check=pass|fix_crumbs=<crumb-ids>|next_step=FIX_AGENTS_SPAWN" >> ${SESSION_DIR}/progress.log`

            **Progress log (after fix agents spawned):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|FIX_AGENTS_SPAWNED|round=<N>|fix_dps=<names>|fix_pcs=fix-pc-scope-verify,fix-pc-claims-vs-code|next_step=FIX_INNER_LOOP" >> ${SESSION_DIR}/progress.log`

            **Progress log (after all fix DPs verified by fix-pc-claims-vs-code):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|FIX_CLAIMS_VS_CODE_COMPLETE|round=<N>|verified_dps=<names>|commits=<hashes>|next_step=ROUND_TRANSITION" >> ${SESSION_DIR}/progress.log`

            **Progress log (after round transition messages sent):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|ROUND_TRANSITION|from_round=<N>|to_round=<N+1>|fix_commits=<range>|next_step=REVIEW_3B" >> ${SESSION_DIR}/progress.log`

            **Progress log (after triage decision — fix path):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_TRIAGED|round=<N>|p1=<count>|p2=<count>|decision=<auto_fix|fix_now>|root_causes=<count>|next_step=FIX_SCOUT" >> ${SESSION_DIR}/progress.log`

            **Progress log (after triage decision — non-fix path):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_TRIAGED|round=<N>|p1=<count>|p2=<count>|decision=<defer|terminated>|root_causes=<count>|next_step=STEP_4_DOCS" >> ${SESSION_DIR}/progress.log`

**Step 4:** Documentation — update README and CLAUDE.md in single commit.
            Note: session narrative and changelog entry are handled by the Scribe at Step 5.
            Before committing: file issues for any remaining work; run quality gates (tests, linters,
            builds) if code changed; apply review-findings gate (if reviews found P1 issues, present
            to user before proceeding — user decides fix now or defer; do NOT push with undisclosed
            P1 blockers).
            **Progress log (after doc commit):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|DOCS_COMMITTED|complete|commit=<hash>|next_step=STEP_4B_XREF" >> ${SESSION_DIR}/progress.log`

**Step 4b:** Verify — cross-references valid, all tasks accounted for. Update issue status: close
            finished tasks, update in-progress items.
            **Progress log (after cross-reference check):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|XREF_VERIFIED|complete|tasks_closed=<ids>|next_step=STEP_5_SCRIBE" >> ${SESSION_DIR}/progress.log`

**Step 5:** Scribe — spawn the Scribe agent to write the session exec summary and CHANGELOG entry.
            ```
            Task(
              subagent_type="ant-farm-session-scribe",
              model="sonnet",
              prompt="Write session exec summary. Session dir: {SESSION_DIR}. Commit range: {RANGE}.
                      Open crumbs: {IDS}. CHANGELOG path: CHANGELOG.md.
                      Read orchestration/templates/scribe-skeleton.md for full instructions."
            )
            ```
            The Scribe reads all session artifacts ({SESSION_DIR}/briefing.md, summaries/*.md,
            review-reports/review-consolidated-*.md, progress.log), runs git diff/log for the commit
            range, and produces two outputs:
            1. `{SESSION_DIR}/exec-summary.md` — canonical session record
            2. Prepends a CHANGELOG entry to `CHANGELOG.md`
            **Progress log (after Scribe completes):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SCRIBE_COMPLETE|exec_summary=${SESSION_DIR}/exec-summary.md|next_step=STEP_6_ESV" >> ${SESSION_DIR}/progress.log`

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
            > **Field derivation**: `SESSION_START_COMMIT` is the first commit the Queen or any agent made this session (visible in `git log` since the pre-session HEAD). `SESSION_END_COMMIT` is the commit at HEAD immediately before Step 7's `git add CHANGELOG.md` commit. `SESSION_START_DATE` is the calendar date (UTC) when Step 0 ran (stored in queen-state.md or derivable from `SESSION_ID`).
            session-complete checks: task coverage, commit coverage, open crumb accuracy, CHANGELOG derivation
            fidelity, section completeness, metric consistency.
            Artifact written to `{SESSION_DIR}/pc/pc-session-complete-{timestamp}.md`.
            **On session-complete FAIL**: Re-spawn Scribe with specific violations from session-complete report (max 1 retry).
            **On second session-complete FAIL**: Escalate to user — present failed checks, await decision.
            **Progress log (after session-complete PASS):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SESSION_COMPLETE_PASS|artifact=${SESSION_DIR}/pc/pc-session-complete-$(date +%Y%m%d-%H%M%S).md|next_step=STEP_7_PUSH" >> ${SESSION_DIR}/progress.log`

**Step 7:** Land the plane — Queen commits the Scribe's CHANGELOG.md, copies the exec summary to history (local only), then pulls and pushes. NEVER `git add` any file under `.crumbs/` — the entire directory is gitignored.
            ```bash
            git add CHANGELOG.md && git commit -m "docs: add session {SESSION_ID} changelog entry"
            cp "${SESSION_DIR}/exec-summary.md" ".crumbs/history/exec-summary-${SESSION_ID}.md"
            git pull --rebase
            git push
            ```
            Run `git status` after push — output MUST show "up to date with origin".

            Clean up stashes and remote branches. Provide hand-off context for the next session.
            **Progress log (after git push succeeds):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SESSION_COMPLETE|pushed=true|next_step=DONE" >> ${SESSION_DIR}/progress.log`

## Hard Gates

| Gate | Blocks | Artifact |
|------|--------|----------|
| startup-check PASS | Prompt Composer spawn (and all downstream steps) | ${SESSION_DIR}/pc/pc-session-startup-check-{timestamp}.md |
| pre-spawn-check PASS (impl) | Agent spawn | ${SESSION_DIR}/pc/*-pre-spawn-check-*.md |
| pre-spawn-check PASS (review) | Reviewer team spawn | ${SESSION_DIR}/pc/pc-session-pre-spawn-check-review-{timestamp}.md |
| scope-verify PASS | Serial mode: next agent spawn; Batch mode: claims-vs-code spawn (all wave agents checked before claims-vs-code) | ${SESSION_DIR}/pc/*-scope-verify-*.md |
| claims-vs-code PASS | Task closure (crumb close) | ${SESSION_DIR}/pc/*-claims-vs-code-*.md |
| review-integrity PASS | Presenting results | ${SESSION_DIR}/pc/pc-session-review-integrity-{timestamp}.md |
| Reviews | Presenting findings to user (Step 3c) | ${SESSION_DIR}/review-reports/review-consolidated-{timestamp}.md |
| session-complete PASS | Git push (Step 7) | ${SESSION_DIR}/pc/pc-session-complete-{timestamp}.md |

> **Note (Reviews gate):** Reviews are mandatory after ALL implementation completes (round 1). If findings require a fix cycle, reviews re-run with reduced scope — correctness and edge-cases only (round 2+).

## Agent Types

Read `orchestration/reference/agent-types.md` for the full Agent Types table.

## Model Assignments

Read `orchestration/reference/model-assignments.md` for the full Model Assignments table. Every `Task` tool call the Queen makes MUST include the `model` parameter — omitting it causes the agent to inherit the Queen's opus model, wasting tokens.

## Concurrency Rules

- Max 7 Crumb Gatherers concurrent
- Max 12 total agents (Crumb Gatherers + support agents: Pantry, Checkpoint Auditor, Scout)
- No two agents edit the same file — queue conflicting tasks sequentially
- Each agent runs `git pull --rebase` before committing
- Only the Queen pushes to remote
- Only the Queen updates README; the Scribe writes CHANGELOG.md (Queen commits it at Step 7)
- Pipeline wave N Crumb Gatherers with wave N+1 Pantry in a single message (see Step 2 wave pipelining)

### Wave Management

**Retry counting**: Retry spawns count against the concurrent agent limit. A failed-and-respawned Crumb Gatherer occupies a slot.

**Mid-wave decision tree**:

| Scenario | Action |
|----------|--------|
| Agent failure | Log failure, file a crumb for the failed task, continue with remaining agents. Re-attempt in next wave if slots available. |
| Early completion | Do NOT backfill mid-wave. Wait for the full wave to complete before starting the next. Rationale: backfilling creates interleaved commits that complicate review scope tracking. |
| All agents fail | Stop. Surface failures to user. Do not auto-retry the entire wave. |

## Session Directory

Read `orchestration/reference/session-directory.md` for full setup instructions and artifact layout.

At session start (Step 0), run:

    SESSION_ID=$(date +%Y%m%d-%H%M%S)
    SESSION_DIR=".crumbs/sessions/_session-${SESSION_ID}"
    mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts,pc,summaries}
    crumb prune >/dev/null || true

Store SESSION_DIR in your context and pass it explicitly to every agent that needs to write artifacts.

## Anti-Patterns

- Reading every agent's output files — trust summaries and commit messages
- Spawning agents one at a time — batch by file/priority
- Re-reading the same metadata — read once, take notes in session state file
- Pushing mid-session — only push at end (atomic deployment)
- Updating docs per-agent — batch all doc updates in Step 4
- Verbose agent prompts — be concise, agents read their own task details from their task brief
- Running individual checkpoints per agent — spawn one Checkpoint Auditor with the full batch

## Template Lookup

| Workflow Phase | Read This File |
|----------------|----------------|
| Composing agent prompts (Step 2) | orchestration/templates/pantry.md |
| Agent skeleton for spawning (Step 2) | orchestration/templates/crumb-gatherer-skeleton.md |
| Review skeleton for team (Step 3b) | orchestration/templates/reviewer-skeleton.md |
| Review Consolidator skeleton for consolidation (Step 3b) | orchestration/templates/review-consolidator-skeleton.md |
| Implementation details (read by the Pantry) | orchestration/templates/implementation.md |
| Checkpoint details (read by Checkpoint Auditor) | orchestration/templates/checkpoints/ (common.md + specific checkpoint file) |
| Review details (read by build-review-prompts.sh) | orchestration/templates/reviews.md |
| Pre-flight recon (Step 1) | orchestration/templates/scout.md |
| Conflict patterns (read by the Scout) | orchestration/reference/dependency-analysis.md |
| Diagnosing a failure or post-mortem | orchestration/reference/known-failures.md |
| Creating/recovering the Queen's state file | orchestration/templates/queen-state.md |
| Exec summary authoring (Step 5) | orchestration/templates/scribe-skeleton.md |
| Setting up orchestration in new project | orchestration/SETUP.md |

## Retry Limits

| Situation | Max Retries | After Limit |
|-----------|-------------|-------------|
| Agent fails claims-vs-code | 2 | Escalate to user with full context |
| review-integrity fails | 1 | Present to user with verification report attached |
| Agent stuck (no commit within 15 turns) | 0 | Run stuck-agent diagnostic (see below); escalate to user |
| Prompt Composer pre-spawn-check fails | 1 | Escalate to user; do not spawn Crumb Gatherers without verified prompts |
| Scout fails or returns no tasks | 1 | Escalate to user; do not proceed to Step 2 without task list |
| startup-check FAIL -> re-Scout cycle | 1 | Escalate to user with startup-check violations; do not re-run Scout a third time |
| Fix DP stuck/crash (no commit in team) | 0 | Run stuck-agent diagnostic; file a crumb for the failed fix; escalate to user. Do NOT re-spawn without user approval |
| Fix PC crash (fix-pc-scope-verify or fix-pc-claims-vs-code) | 1 | Spawn replacement into team (`team_name: "reviewer-team"`); resume from last SendMessage |
| Reviewer failure (round 2+, re-task via SendMessage fails) | 1 | Spawn fresh reviewer into team as replacement; re-send the round transition message |
| Review Consolidator crash (before crumb filing complete) | 1 | Spawn fresh Review Consolidator into team with handoff brief describing which crumbs were filed and which remain; re-run review-integrity after |
| review-integrity material spot-check fail | 1 | Shut down current Review Consolidator; spawn fresh Review Consolidator into team with handoff brief identifying failed crumbs; re-run full crumb review then re-run review-integrity |
| Scribe fails session-complete | 1 | Escalate to user with session-complete report; user decides fix manually or push as-is |
| Total retries per session | 5 | Pause all new spawns; triage with user |

Track retry count in the Queen's state file (→ templates/queen-state.md).

### Stuck-Agent Diagnostic Procedure

When an agent has not produced a commit within 15 turns, follow these steps before escalating:

1. Read the agent's task brief to confirm the scope and acceptance criteria were unambiguous.
2. Check `.crumbs/sessions/_session-*/` for any partial summary the agent may have written, which can reveal how far it progressed before stalling.
3. Check `git log --oneline -10` to determine whether a commit was made but not reported back correctly.
4. If the agent is still running, check its most recent output for a blocking question, permission error, or tool failure message.
5. If the agent exited without a commit and no diagnostic information is available, escalate to the user with: the task ID, the agent type, the turn count, and any last-known output.

Do not re-spawn the agent or attempt a fix without user approval after the stuck-agent limit (0 retries) is reached.

### Wave Failure Threshold

If more than 50% of agents in a single wave fail (claims-vs-code failure, stuck, or unrecoverable error), the Queen must:

1. Stop spawning new agents for the remainder of the current wave.
2. Collect failure summaries from all failed agents in the wave.
3. Notify the user immediately: list each failed task ID, the failure type, and retry count consumed.
4. Await explicit user instruction before continuing — options include: re-run the failed subset, abort the session, or manually resolve blockers and resume.

A wave is defined as a set of agents spawned concurrently in a single Step 2 batch. Failures from earlier waves do not carry over into the threshold calculation for a new wave.

## Crumb Priority Calibration

> **Note**: This section defines project-level issue priorities for crumbs filed in the tracker. Reviewer severity (P1/P2/P3) is defined separately in `orchestration/templates/reviews.md` and applies to review findings, not crumb filing priority.

**P1** = build failure, broken links, data loss, security vulnerability

**P2** = visual regression, accessibility issue, functional degradation

**P3** = style, naming, cleanup, polish

Project-specific overrides belong in the project's CLAUDE.md or QUALITY_PROCESS.md.

## Context Preservation Targets

- Token budget: finish with >50% remaining (1M context window)
- File reads in the Queen: <10 for 40+ task sessions
- Concurrent agents: typical 5-6 Crumb Gatherers, max 12 total
- Commits per session: <20 (batch related work)
