# Orchestration Rules

## Path Reference Convention

All file paths in this document use **repo-root relative** format: `orchestration/templates/scout.md`.

When code runs at runtime, agent files are synced to `~/.claude/agents/` and orchestration files are
accessible at `~/.claude/orchestration/templates/scout.md`. To translate repo paths to runtime paths:
- Replace `orchestration/` with `~/.claude/orchestration/`
- Replace `agents/` with `~/.claude/agents/`

**In-document shorthand** (e.g., "templates/scout.md") is informal and always refers to the repo-root path with the `orchestration/` prefix implied.

## Queen Prohibitions (read FIRST)

- **NEVER** run `crumb show`, `crumb ready`, `crumb list`, `crumb blocked`, or any `crumb` query command — the Scout does this
- **NEVER** read source code, tests, project data files, or config files — agents do this
- **NEVER** read agent **instruction files** (scout.md, pantry.md, implementation.md, checkpoints.md, reviews.md, etc.) — pass the path to the agent, let it read its own instructions
- **NEVER** send `shutdown_request` to any Nitpicker team member before Step 4. The **only** authorized shutdown trigger is the termination check in Step 3c (zero P1/P2 findings). Do NOT send shutdown_request at the Step 3c decision fork or anywhere else before convergence.

Your first instinct will be to "gather context" by running `crumb show` on the task list.
**Do not do this.** Spawn the Scout and let it gather context for you.

## Queen Read Permissions

The Queen's window is restricted to prevent context bloat, but certain files are explicitly PERMITTED.

**PERMITTED (Queen must read these):**
- `{SESSION_DIR}/briefing.md` — Scout-generated strategy summary; Queen reads after SSV PASS to confirm task count before auto-proceeding to Step 2
- `{SESSION_DIR}/task-metadata/*.md` — Per-task scope, acceptance criteria (pre-digested by Scout)
- `{SESSION_DIR}/previews/*.md` — Combined prompt previews (pre-digested by Pantry)
- `{SESSION_DIR}/review-reports/*.md` — Individual reviewer reports and Big Head consolidated summary
- Verdict tables from Pantry and Pest Control — CCO, WWD, DMVDC, CCB verdicts
- Commit messages and git status/log/diff --stat output
- Agent notifications (as they complete)

**PERMITTED (Queen reads once per phase, for context only):**
- `orchestration/templates/dirt-pusher-skeleton.md` — Once per implementation wave (skeleton structure; see [Glossary: wave](GLOSSARY.md#workflow-concepts))
- `orchestration/templates/nitpicker-skeleton.md` — Once per review cycle (skeleton structure)
- `orchestration/templates/big-head-skeleton.md` — Once per review cycle (skeleton structure)
- `orchestration/templates/scribe-skeleton.md` — Once per session (read to fill placeholders before spawning the Scribe at Step 5b)
- Project's `CLAUDE.md` — Global project rules
- `{SESSION_DIR}/exec-summary.md` — Scribe output; read only when ESV escalates to user with a failed exec summary

**FORBIDDEN (agents read; Queen never reads):**
- `orchestration/templates/scout.md` — Scout's instruction file
- `orchestration/templates/pantry.md` — Pantry's instruction file
- `orchestration/templates/implementation.md` — Implementation details (read by Pantry)
- `orchestration/templates/checkpoints.md` — Checkpoint definitions (read by Pest Control)
- `orchestration/templates/reviews.md` — Review protocol (read by build-review-prompts.sh)
- `orchestration/reference/dependency-analysis.md` — Used by Scout for conflict analysis
- `orchestration/reference/known-failures.md` — Reference material; for post-mortem only
- `orchestration/_archive/*` — Deprecated documents; stale instructions that contradict current workflows. **No agent should read these.**
- Source code files, tests, project configs, application data files
- Raw `crumb show`, `crumb ready`, `crumb blocked`, `crumb list` output (let the Scout digest this)

## Workflow: "Let's Get to Work"

**Step 0:** Session setup — run the commands in the Session Directory section below to
            generate SESSION_ID and SESSION_DIR. Store both as variables in your context.
            Then immediately proceed to Step 1.
            Do NOT examine, read, or query any task/issue details.
            **Progress log:** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SESSION_INIT|complete|session_dir=${SESSION_DIR}" >> ${SESSION_DIR}/progress.log`

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

**Step 1:** Recon — Read `{SESSION_DIR}/briefing.md` written by the Scout's previous run, or spawn the Scout
            (`ant-farm-scout-organizer` subagent, `model: "opus"`) if this is the first session. Include in Scout's prompt:
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

**Step 1b:** SSV gate — After Scout writes `{SESSION_DIR}/briefing.md`, spawn Pest Control
            (`ant-farm-pest-control`, `model: "haiku"`) for Scout Strategy Verification (SSV).
            Pass `Session directory: <value of SESSION_DIR>` and the path `orchestration/templates/checkpoints.md`
            as its instruction file. Pest Control reads `{SESSION_DIR}/briefing.md` itself and runs all three
            mechanical checks (file overlap within waves, file list match against crumbs, intra-wave dependency
            ordering). **SSV must PASS before proceeding.**

            **On SSV PASS**: Proceed directly to Step 2. Do NOT wait for user approval. SSV is the
            mechanical safety gate — a passing strategy is structurally sound and ready to execute.
            No complexity threshold applies; auto-approve regardless of task count.
            **Zero-task guard:** If the briefing's task count is 0, do NOT auto-proceed to Step 2.
            Escalate to the user with the zero-task briefing for review and await instruction.
            **On SSV FAIL**: Re-run Scout with the specific violations from the SSV report (do NOT present
            a failed strategy to the user). After Scout revises briefing.md, re-run SSV.
            **Retry cap:** The SSV FAIL -> re-Scout cycle has a maximum of 1 retry. If SSV fails again
            after one re-Scout run, do NOT re-run Scout a second time. Surface the SSV violations to
            the user and await instruction.

            **Progress log (after SSV PASS):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SCOUT_COMPLETE|briefing=${SESSION_DIR}/briefing.md|ssv=pass|tasks_accepted=<N>" >> ${SESSION_DIR}/progress.log`
            where `<N>` is the count of tasks in the briefing task list after SSV PASS (N=0 is not logged — it is caught by the zero-task guard earlier in Step 1b).

**Step 2:** Spawn — Spawn the Pantry (`ant-farm-pantry-impl`, `model: "opus"`) for task briefs + combined previews
            (→ orchestration/templates/pantry.md, Section 1). Include `Session directory: <value of SESSION_DIR>`
            in Pantry's prompt. Pass preview file paths and SESSION_DIR to Pest Control
            (`ant-farm-pest-control`, `model: "haiku"`) for Colony Cartography Office (CCO); Pest Control reads orchestration/templates/checkpoints.md itself.
            Only after all CCO PASS: spawn agents using skeleton
            (→ orchestration/templates/dirt-pusher-skeleton.md, using Agent Type from Pantry verdict table, `model: "sonnet"` for all Dirt Pushers regardless of subagent_type).
            **Wave pipelining**: When spawning wave N Dirt Pushers, include the wave N+1 Pantry
            (`ant-farm-pantry-impl`, `model: "opus"`) in the SAME message so they launch concurrently.
            The Pantry reads from task-metadata (written by Scout) and has no dependency on wave N's output.
            This eliminates the idle gap between waves. The flow per wave boundary:
            1. Wave N CCO PASS → spawn wave N Dirt Pushers + wave N+1 Pantry (in a single Task call to achieve concurrency)
            2. Wave N+1 Pantry returns → spawn wave N+1 CCO
            3. Wave N Dirt Pushers finish → run WWD/DMVDC (Step 3)
            4. Wave N+1 CCO PASS + wave N WWD + DMVDC both PASS → spawn wave N+1 Dirt Pushers + wave N+2 Pantry
            For the final wave (no wave N+1), skip the Pantry — just spawn Dirt Pushers alone.
            **Progress log (after each wave's Dirt Pushers are spawned):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|WAVE_SPAWNED|wave=<N>|spawned=<agent-ids>|previews_dir=${SESSION_DIR}/previews" >> ${SESSION_DIR}/progress.log`

**Step 3:** Verify — Run WWD, then DMVDC, for each wave.

            **WWD execution mode depends on how agents in the wave were spawned:**
            - **Serial mode** (agents spawned sequentially, one at a time): After each agent commits, spawn
              one Pest Control (`model: "haiku"`) instance for that agent's commit. This is a true per-agent
              gate — the next agent must not be spawned until WWD PASS is received for the previous one.
            - **Batch mode** (agents spawned in parallel in a single message): After ALL wave agents have
              committed, spawn one Pest Control (`model: "haiku"`) instance per committed task (can be
              concurrent). Wait for ALL WWD reports before proceeding to DMVDC. This is a post-hoc batch
              check — per-agent serial gating is mechanically impossible when commits arrive nearly
              simultaneously.
            **Mode selection rule**: If you spawned agents in a single message (parallel wave), use batch
            mode. If you spawned agents individually in separate messages, use serial mode.
            **Progress log (after all WWD reports PASS for the wave):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|WAVE_WWD_PASS|wave=<N>|mode=<serial|batch>|tasks_checked=<ids>" >> ${SESSION_DIR}/progress.log`

            After all WWD reports PASS, spawn Pest Control (`model: "sonnet"`) for Dirt Moved vs Dirt Claimed (DMVDC)
            (pass task IDs, commit hashes, summary doc paths; Pest Control reads
            checkpoints.md + task-metadata/ + git diffs itself).
            Failed DMVDC → resume agent (max 2 retries).
            **Progress log (after DMVDC PASS for each wave):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|WAVE_VERIFIED|wave=<N>|dmvdc=pass|tasks_verified=<ids>|commits=<hashes>" >> ${SESSION_DIR}/progress.log`

**Step 3b:** Review — fill review slots and spawn Nitpickers.

            **Team persistence**: The Nitpicker team persists across the full review-fix-review loop.
            The team is NOT torn down after round 1 consolidation. Fix agents spawn into the same team
            (round 1 or later) and Correctness + Edge Cases reviewers are re-tasked in-place via
            SendMessage for round 2+. Team shutdown happens only at convergence (0 P1/P2) or the round 4
            cap. The one-TeamCreate-per-session constraint makes this the only viable path for
            team-based round 2+ reviews.

            **Team roster progression**:
            - **Round 1 (initial)**: 6 members — 4 Nitpickers (Clarity, Edge Cases, Correctness, Drift) + Big Head + Pest Control
            - **During fix wave**: + N fix DPs + fix-pc-wwd + fix-pc-dmvdc (names: fix-dp-1..N, fix-pc-wwd, fix-pc-dmvdc; round suffixes for round 2+: fix-dp-r2-1, fix-pc-wwd-r2, fix-pc-dmvdc-r2)
            - **Peak**: up to 15 members (6 + 7 fix DPs + 2 fix PCs), but only N+2 fix agents are active during the fix phase; the original 6 are idle
            - **After fix wave verified**: fix DPs + fix-pc-wwd + fix-pc-dmvdc are shut down (Step 3c-iv). Roster returns to 6 persistent members before round transition.
            - **Round 2+**: Clarity and Drift reviewers remain idle; Correctness and Edge Cases are re-tasked via SendMessage. If round 2+ needs fixes, fresh fix agents are spawned (not re-used from prior round).

            **3b-i. Gather inputs** from the Queen's state file:
            - Review round: read from session state (default: 1)
            - Commit range: round 1 = first session commit..HEAD; round 2+ = first fix commit..HEAD
            - File list: `git diff --name-only <commit-range>` (deduplicated; exclude `.crumbs/tasks.jsonl` and other auto-generated crumbs files)
            - Task IDs: round 1 = all task IDs; round 2+ = fix task IDs only
            - Timestamp: The Queen generates ONE timestamp at the start of Step 3b using `date +%Y%m%d-%H%M%S` format (YYYYMMDD-HHmmss). Store as `{TIMESTAMP}` (shell: `${TIMESTAMP}`):
              ```bash
              TIMESTAMP=$(date +%Y%m%d-%H%M%S)
              ```

            **3b-i.5. Validate review inputs** before proceeding:
            ```bash
            # REVIEW_ROUND: must be a positive integer
            if ! [[ "${REVIEW_ROUND}" =~ ^[1-9][0-9]*$ ]]; then
              echo "ERROR: REVIEW_ROUND is missing or non-numeric (got: '${REVIEW_ROUND}'). Expected: integer >= 1." >&2
              exit 1
            fi

            # CHANGED_FILES: must be non-empty (at least one changed file)
            # Use bash parameter expansion to strip all whitespace — simpler and
            # more portable than the tr+sed pipeline (no subprocesses, no
            # platform-specific tr/sed behavior differences).
            if [[ -z "${CHANGED_FILES//[[:space:]]/}" ]]; then
              echo "ERROR: CHANGED_FILES is empty. git diff returned no files for the commit range. Verify the commit range contains actual changes." >&2
              exit 1
            fi

            # TASK_IDS: must be non-empty (at least one task ID)
            if [[ -z "${TASK_IDS//[[:space:]]/}" ]]; then
              echo "ERROR: TASK_IDS is empty. Round 1 requires all task IDs; round 2+ requires fix task IDs. Verify session state is populated." >&2
              exit 1
            fi
            ```
            On any validation failure: surface the error to the user and do NOT proceed to 3b-ii.

            **3b-ii. Build review prompts** (single script — reads templates and fills all values):
            ```bash
            bash ~/.claude/orchestration/scripts/build-review-prompts.sh \
              "${SESSION_DIR}" "<commit-range>" "<changed-files>" \
              "<task-IDs>" "<timestamp>" "<round>" \
              "$HOME/.claude/orchestration/templates/nitpicker-skeleton.md" \
              "$HOME/.claude/orchestration/templates/big-head-skeleton.md"
            ```
            Note: `<changed-files>` and `<task-IDs>` accept an `@filepath` prefix to read multiline
            values from a file (e.g., `@/tmp/changed-files.txt`). Use this to avoid shell quoting
            issues when the list contains many entries or paths with spaces.
            On exit 0: prompts/previews written to `${SESSION_DIR}/prompts/` and `${SESSION_DIR}/previews/`.
            On non-zero: surface stderr to user — do NOT proceed.

            **3b-iii. Create review-reports directory, then run CCO gate**:
            Run `mkdir -p "${SESSION_DIR}"/review-reports` **before** spawning any review agents — the
            directory must exist so every Nitpicker can write its report without racing to create it.
            After the directory is created, spawn Pest Control (`model: "haiku"`) for CCO on review
            previews. The CCO gate must PASS before spawning the Nitpicker team.

            **3b-iv. Spawn Nitpicker team** (round 1 only — team persists for round 2+):
            - Round 1: 6 members — 4 reviewers + Big Head + Pest Control
            - Round 2+: do NOT spawn a new team — re-task Correctness and Edge Cases reviewers via SendMessage (see Step 3c fix workflow)
            - Big Head MUST be a team member, NOT a separate Task agent
            - Pest Control MUST be a team member so Big Head can SendMessage to it
            - Templates: `nitpicker-skeleton.md`, `big-head-skeleton.md`
            - After team completes, DMVDC and CCB have already run inside the team

            **Constraint: one TeamCreate per session.** Claude Code supports only one `TeamCreate` call
            per session. The Nitpicker team uses this slot. Any agent that needs to communicate with
            another agent (e.g., Pest Control receiving a message from Big Head, fix PCs messaging fix DPs)
            MUST be added as a team member — it cannot be spawned separately as a Task agent and then
            contacted via SendMessage from inside the team. Fix agents spawn into the persistent Nitpicker
            team using the Task tool with `team_name: "nitpicker-team"`. Do NOT add a second TeamCreate
            call anywhere in the workflow.

            **Stale team recovery:** If `TeamCreate` fails because a team already exists from a prior
            session, do NOT delete the team (`TeamDelete`). Instead, spawn agents into the existing team
            using the Agent tool with `team_name` set to the existing team name. Read
            `~/.claude/teams/*/config.json` to discover the team name if needed. Deleting and recreating
            is not possible within a single session — the TeamCreate slot is already consumed.

            **Progress log (after Nitpicker team completes round 1):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_COMPLETE|round=<N>|team=complete|report=${SESSION_DIR}/review-reports/review-consolidated-${TIMESTAMP}.md" >> ${SESSION_DIR}/progress.log`

**Step 3c:** User triage — **after CCB PASS and Big Head consolidation completes**:
            1. Read the consolidated review summary (Big Head sends crumb list to Queen via SendMessage — see big-head-skeleton.md step 12)
            2. Check finding counts: P1, P2, P3
            **Termination check**: If zero P1 and zero P2 findings:
            - Round 2+: P3s already auto-filed by Big Head to "Future Work" epic
            - Round 1: P3s filed via "Handle P3 Issues" flow in reviews.md
            - Update session state: `Termination: terminated (round N: 0 P1/P2)`
            - Shutdown is authorized at this point — but do NOT send `shutdown_request` yet. Proceed to Step 4 first; send `shutdown_request` to team members during session teardown (Step 6 cleanup).
            **If P1 or P2 issues found**:
            **DO NOT send shutdown_request to any team member.** The team must remain active for the fix workflow.
            **Round cap — escalate after round 4** (check this FIRST before any fix decision):
            - If current round >= 4 and P1/P2 findings are still present, do NOT start another round
            - Present full round history to user (round numbers, finding counts, crumb IDs)
            - Ask user: "Review loop has not converged after 4 rounds. Continue or abort?"
            - Await user decision before taking any further action
            **Only if current round < 4**: determine fix action:
            **Auto-fix (round 1, ≤5 root causes)**: If round == 1 AND total P1+P2 root causes ≤ 5:
            - Announce (do NOT wait for user input):
              "**Auto-fix**: Round 1 review found X P1 and Y P2 issues (Z root causes, within 5-threshold). Spawning fix tasks automatically."
            - Proceed directly to fix workflow (below)
            - After fixes complete + DMVDC passes, transition to round N+1 via SendMessage (see Fix Workflow below)
            - Update session state: increment review round, record fix commit range
            **Escalation (round 1, >5 root causes)**: If round == 1 AND total P1+P2 root causes > 5:
            - Present findings to user: "Round 1 review found Z root causes (>5 threshold). This suggests a systemic issue. Fix now or defer?"
            - Await user decision (same as round 2+ behavior below)
            **User prompt (round 2+)**: If round >= 2:
            - Present findings to user: "Reviews found X P1 and Y P2 issues. Fix now or defer?"
            - **If "fix now"**: proceed to Fix Workflow below, then transition to round N+1 via SendMessage
              - Update session state: increment review round, record fix commit range
            - **If "defer"**: P1/P2 crumbs stay open; note deferred items for the Scribe to document at Step 5b; proceed to Step 4

            **Fix Workflow** (triggered by auto-fix or "fix now"):

            Fix agents spawn **into the persistent Nitpicker team** (not as standalone Task agents) using
            the Task tool with `team_name: "nitpicker-team"` so they can communicate with reviewers and
            iterate within the team via SendMessage.

            **Step 3c-i. Fix-cycle Scout** — Before spawning fix agents, run a fix-cycle Scout
            (`ant-farm-scout-organizer`, `model: "opus"`) to plan the fix strategy: which crumbs to fix, wave
            grouping, and file conflict analysis. The fix-cycle Scout reads the crumb list from Big Head's
            SendMessage handoff (big-head-skeleton.md step 12).

            **Auto-approval**: The fix-cycle Scout's strategy is auto-approved — no user confirmation
            gate. The Scout's strategy drives fix agent spawning directly.

            **SSV gate**: SSV runs as a mechanical safety net on the Scout's fix strategy:
            - SSV PASS → proceed to fix agent spawning (auto-approved)
            - SSV FAIL → re-run Scout with violations listed (max 1 retry); if still failing, escalate to user

            **Progress log (after fix Scout SSV PASS):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|FIX_SCOUT_COMPLETE|round=<N>|ssv=pass|fix_crumbs=<crumb-ids>" >> ${SESSION_DIR}/progress.log`

            **Step 3c-ii. Spawn fix agents into team** — Pantry and CCO are skipped for fix agents
            (the Big Head crumb IS the brief; crumb content passed CCB; SSV independently verified the
            strategy). Spawn fix agents into the team in a single message:
            - **N fix DPs** (`model: "sonnet"`, `team_name: "nitpicker-team"`): names `fix-dp-1..N`
              (round 2+: `fix-dp-r2-1..N`)
            - **fix-pc-wwd** (`model: "haiku"`, `team_name: "nitpicker-team"`): one per round; serves
              all fix DPs in the round via SendMessage
            - **fix-pc-dmvdc** (`model: "sonnet"`, `team_name: "nitpicker-team"`): one per round;
              serves all fix DPs in the round via SendMessage

            **Fix DP prompt structure**: minimal — crumb is the source of truth:
            ```
            You are fix-dp-N, a fix Dirt Pusher in the Nitpicker team.
            Your task crumb: <crumb-id>
            Run: crumb show <crumb-id>
            Implement the fix. Follow the acceptance criteria exactly.
            After committing:
            1. Record commit hash: crumb update <crumb-id> --note="commit: <hash>"
            2. SendMessage to fix-pc-wwd: "Fix committed. Crumb: <crumb-id>. Commit: <hash>. Files changed: <list>."
            Then go idle and wait.
            ```

            **Progress log (after fix agents spawned):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|FIX_AGENTS_SPAWNED|round=<N>|fix_dps=<names>|fix_pcs=fix-pc-wwd,fix-pc-dmvdc" >> ${SESSION_DIR}/progress.log`

            **Step 3c-iii. Fix inner loop** — fully asynchronous via SendMessage within the team:
            ```
            fix-dp-N  -->  [commit]  -->  SendMessage(fix-pc-wwd)
                                                |
                                          fix-pc-wwd runs WWD check (haiku)
                                                |
                                     PASS ------+------ FAIL
                                      |                   |
                           SendMessage(fix-pc-dmvdc)   SendMessage(fix-dp-N) with specifics
                                      |                   |
                                fix-pc-dmvdc          fix-dp-N iterates (max 2 retries total)
                                runs DMVDC                |
                                (sonnet)        if retry limit hit → SendMessage(Queen)
                                      |
                           PASS ------+------ FAIL
                            |                  |
                        fix-dp-N           SendMessage(fix-dp-N) with specifics
                        goes idle          fix-dp-N iterates (max 2 retries total)
                                           if retry limit hit → SendMessage(Queen)
            ```

            Retry limit: each fix DP has a maximum of 2 retries total across both WWD and DMVDC
            failures. On the third failure, the DP sends a message to the Queen and goes idle.
            The Queen escalates to the user.

            **Progress log (after all fix DPs verified by fix-pc-dmvdc):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|FIX_DMVDC_COMPLETE|round=<N>|verified_dps=<names>|commits=<hashes>" >> ${SESSION_DIR}/progress.log`

            **Step 3c-iv. Round transition via SendMessage** — after all fix DPs complete and
            fix-pc-dmvdc has issued PASS for each:

            **First, shut down fix agents from this round.** Send `shutdown_request` to each
            fix DP, fix-pc-wwd, and fix-pc-dmvdc from round N. These agents have served their
            purpose — round N+1 fixes (if needed) will be fresh spawns with no stale context
            from the prior round's approach. Do NOT re-use fix DPs across rounds.

            **Then, re-task the persistent review members for round N+1:**
            1. **Re-task Correctness reviewer**: SendMessage to `correctness` with review round N+1,
               fix commit range, changed files, and task IDs; provide new report output path
               `{SESSION_DIR}/review-reports/correctness-r<N+1>-<timestamp>.md`
            2. **Re-task Edge Cases reviewer**: SendMessage to `edge-cases` with review round N+1,
               fix commit range, changed files, and task IDs; provide new report output path
               `{SESSION_DIR}/review-reports/edge-cases-r<N+1>-<timestamp>.md`
            3. **Re-task Big Head**: SendMessage to `ant-farm-big-head` with review round N+1, expected report
               count 2, both report paths, and new consolidated output path
               `{SESSION_DIR}/review-reports/review-consolidated-r<N+1>-<timestamp>.md`
            4. **Clarity and Drift**: leave idle — not re-tasked in round 2+ (fix-scope reviews cover
               only fix commits; style/drift are out of scope)

            **Progress log (after round transition messages sent):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|ROUND_TRANSITION|from_round=<N>|to_round=<N+1>|fix_commits=<range>" >> ${SESSION_DIR}/progress.log`

            After the round transition, the loop returns to the top of Step 3c: Big Head consolidates
            round N+1 reports, CCB runs inside the team, and the Queen reads the new crumb list from
            Big Head's SendMessage. If zero P1/P2 → proceed to Step 4. If P1/P2 remain and round < 4
            → repeat fix workflow. If round >= 4 → escalate to user.

            **Progress log (after triage decision):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_TRIAGED|round=<N>|p1=<count>|p2=<count>|decision=<auto_fix|fix_now|defer|terminated>|root_causes=<count>" >> ${SESSION_DIR}/progress.log`

**Step 4:** Documentation — update README and CLAUDE.md in single commit.
            Note: session narrative and changelog entry are handled by the Scribe at Step 5b.
            Before committing: file issues for any remaining work; run quality gates (tests, linters,
            builds) if code changed; apply review-findings gate (if reviews found P1 issues, present
            to user before proceeding — user decides fix now or defer; do NOT push with undisclosed
            P1 blockers).
            **Progress log (after doc commit):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|DOCS_COMMITTED|complete|commit=<hash>" >> ${SESSION_DIR}/progress.log`

**Step 5:** Verify — cross-references valid, all tasks accounted for. Update issue status: close
            finished tasks, update in-progress items.
            **Progress log (after cross-reference check):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|XREF_VERIFIED|complete|tasks_closed=<ids>" >> ${SESSION_DIR}/progress.log`

**Step 5b:** Scribe — spawn the Scribe agent to write the session exec summary and CHANGELOG entry.
            ```
            Task(
              subagent_type="ant-farm-technical-writer",
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
            **Progress log (after Scribe completes):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SCRIBE_COMPLETE|exec_summary=${SESSION_DIR}/exec-summary.md" >> ${SESSION_DIR}/progress.log`

**Step 5c:** ESV — spawn Pest Control for Exec Summary Verification. **Hard gate: must PASS before Step 6.**
            ```
            Task(
              subagent_type="ant-farm-pest-control",
              model="haiku",
              prompt="ESV checkpoint. Session dir: {SESSION_DIR}.
                      Session start commit: {SESSION_START_COMMIT} (first commit of this session).
                      Session end commit: {SESSION_END_COMMIT} (final commit before push, typically HEAD).
                      Session start date: {SESSION_START_DATE} (ISO 8601, e.g. 2026-02-22 — used to scope crumb list).
                      Verify exec-summary.md and CHANGELOG.md.
                      Read orchestration/templates/checkpoints.md for full instructions."
            )
            ```
            > **Field derivation**: `SESSION_START_COMMIT` is the first commit the Queen or any agent made this session (visible in `git log` since the pre-session HEAD). `SESSION_END_COMMIT` is the commit at HEAD immediately before Step 6's `git add CHANGELOG.md` commit. `SESSION_START_DATE` is the calendar date (UTC) when Step 0 ran (stored in queen-state.md or derivable from `SESSION_ID`).
            ESV checks: task coverage, commit coverage, open crumb accuracy, CHANGELOG derivation
            fidelity, section completeness, metric consistency.
            Artifact written to `{SESSION_DIR}/pc/pc-session-esv-{timestamp}.md`.
            **On ESV FAIL**: Re-spawn Scribe with specific violations from ESV report (max 1 retry).
            **On second ESV FAIL**: Escalate to user — present failed checks, await decision.
            **Progress log (after ESV PASS):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|ESV_PASS|artifact=${SESSION_DIR}/pc/pc-session-esv-$(date +%Y%m%d-%H%M%S).md" >> ${SESSION_DIR}/progress.log`

**Step 6:** Land the plane — Queen commits the Scribe's CHANGELOG.md, copies the exec summary to history, then pulls and pushes.
            ```bash
            git add CHANGELOG.md && git commit -m "docs: add session {SESSION_ID} changelog entry"
            cp "${SESSION_DIR}/exec-summary.md" ".crumbs/history/exec-summary-${SESSION_ID}.md"
            git add ".crumbs/history/exec-summary-${SESSION_ID}.md"
            git commit -m "chore: archive session {SESSION_ID} exec summary"
            git pull --rebase
            git push
            ```
            Run `git status` after push — output MUST show "up to date with origin".

            Clean up stashes and remote branches. Provide hand-off context for the next session.
            **Progress log (after git push succeeds):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|SESSION_COMPLETE|pushed=true" >> ${SESSION_DIR}/progress.log`

## Hard Gates

| Gate | Blocks | Artifact |
|------|--------|----------|
| SSV PASS | Pantry spawn (and all downstream steps) | ${SESSION_DIR}/pc/pc-session-ssv-{timestamp}.md |
| CCO PASS (impl) | Agent spawn | ${SESSION_DIR}/pc/*-cco-*.md |
| CCO PASS (review) | Nitpicker team spawn | ${SESSION_DIR}/pc/pc-session-cco-review-{timestamp}.md |
| WWD PASS | Serial mode: next agent spawn; Batch mode: DMVDC spawn (all wave agents checked before DMVDC) | ${SESSION_DIR}/pc/*-wwd-*.md |
| DMVDC PASS | Task closure (crumb close) | ${SESSION_DIR}/pc/*-dmvdc-*.md |
| CCB PASS | Presenting results | ${SESSION_DIR}/pc/pc-session-ccb-{timestamp}.md |
| Reviews | Presenting findings to user (Step 3c) | ${SESSION_DIR}/review-reports/review-consolidated-{timestamp}.md |
| ESV PASS | Git push (Step 6) | ${SESSION_DIR}/pc/pc-session-esv-{timestamp}.md |

> **Note (Reviews gate):** Reviews are mandatory after ALL implementation completes (round 1). If findings require a fix cycle, reviews re-run with reduced scope — correctness and edge-cases only (round 2+).

## Agent Types

| Agent | subagent_type | Rationale |
|-------|---------------|-----------|
| Scout | `ant-farm-scout-organizer` | Custom agent: agent-organizer + Bash for crumb CLI |
| Pantry (impl) | `ant-farm-pantry-impl` | Custom agent: CCO-aligned implementation prompt composer |
| Pest Control | `ant-farm-pest-control` | Custom agent: verification auditor, catches fabrication + scope creep |
| Dirt Pushers | from Pantry verdict table | Specialist per task — Scout recommends via dynamic agent discovery, Pantry passes through |
| Nitpickers | `ant-farm-nitpicker` | Custom agent: file:line specificity, calibrated severity, complete coverage |
| Big Head | `ant-farm-big-head` | Custom agent: deduplication, root-cause grouping, issue filing |
| Scribe | `ant-farm-technical-writer` | Reads session artifacts, writes exec summary + CHANGELOG |
| PC — ESV | `ant-farm-pest-control` | Custom agent: mechanical exec-summary verification against session artifacts |

## Model Assignments

Every `Task` tool call the Queen makes MUST include the `model` parameter from this table. Omitting `model` causes the agent to inherit the Queen's opus model, wasting tokens on agents that don't need it.

| Agent | Spawn Method | Model | Notes |
|-------|-------------|-------|-------|
| Scout | Task (`ant-farm-scout-organizer`) | opus | Orchestration role |
| Pantry (impl) | Task (`ant-farm-pantry-impl`) | opus | Prompt composition + review skeleton assembly (Script 1) |
| Dirt Pushers | Task (dynamic type) | sonnet | All dirt pushers regardless of subagent_type |
| PC — SSV | Task (`ant-farm-pest-control`) | haiku | Set comparisons only — no judgment required |
| PC — CCO | Task (`ant-farm-pest-control`) | haiku | Mechanical checklist |
| PC — WWD | Task (`ant-farm-pest-control`) | haiku | Mechanical file comparison |
| PC — DMVDC | Task (`ant-farm-pest-control`) | sonnet | Judgment: claims vs actual code |
| PC — CCB | Task (`ant-farm-pest-control`) | sonnet | Judgment: crumb quality and dedup correctness |
| Nitpickers (all 4) | TeamCreate member | sonnet | Set in big-head-skeleton.md |
| Big Head | TeamCreate member | opus | Set in big-head-skeleton.md (`{MODEL}`) |
| PC (team member) | TeamCreate member | sonnet | Runs DMVDC inside team; needs sonnet |
| Fix Dirt Pushers | Task (dynamic type) into team | sonnet | Same model as regular Dirt Pushers; spawned with `team_name: "nitpicker-team"` |
| fix-pc-wwd | Task into team | haiku | WWD for fix DPs: lightweight scope check; spawned with `team_name: "nitpicker-team"` |
| fix-pc-dmvdc | Task into team | sonnet | DMVDC for fix DPs: substance check; spawned with `team_name: "nitpicker-team"` |
| Scribe | Task (`ant-farm-technical-writer`) | sonnet | Reads session artifacts; writes exec-summary.md + CHANGELOG entry |
| PC — ESV | Task (`ant-farm-pest-control`) | haiku | Mechanical verification — 6 checks, no judgment required |

## Concurrency Rules

- Max 7 Dirt Pushers concurrent
- Max 12 total agents (Dirt Pushers + support agents: Pantry, Pest Control, Scout)
- No two agents edit the same file — queue conflicting tasks sequentially
- Each agent runs `git pull --rebase` before committing
- Only the Queen pushes to remote
- Only the Queen updates README and CLAUDE.md; the Scribe writes CHANGELOG.md (Queen commits it at Step 6)
- Pipeline wave N Dirt Pushers with wave N+1 Pantry in a single message (see Step 2 wave pipelining)

### Wave Management

**Retry counting**: Retry spawns count against the concurrent agent limit. A failed-and-respawned Dirt Pusher occupies a slot.

**Mid-wave decision tree**:

| Scenario | Action |
|----------|--------|
| Agent failure | Log failure, file a crumb for the failed task, continue with remaining agents. Re-attempt in next wave if slots available. |
| Early completion | Do NOT backfill mid-wave. Wait for the full wave to complete before starting the next. Rationale: backfilling creates interleaved commits that complicate review scope tracking. |
| All agents fail | Stop. Surface failures to user. Do not auto-retry the entire wave. |

## Session Directory

At session start (Step 0), generate a session ID and create the session artifact directory:

    SESSION_ID=$(date +%Y%m%d-%H%M%S)
    SESSION_DIR=".crumbs/sessions/_session-${SESSION_ID}"
    mkdir -p "${SESSION_DIR}"/{task-metadata,previews,prompts,pc,summaries}
    crumb prune >/dev/null || true

Note: `review-reports/` is created lazily at Step 3b-iii — it does not exist until reviews run.

Store SESSION_DIR in your context. Pass it explicitly to every agent that needs to write artifacts:
Scout receives it as "Session directory: <SESSION_DIR>".
Pantry receives it as "Session directory: <SESSION_DIR>".
Pest Control receives it as "Session directory: <SESSION_DIR>" (when writing checkpoint artifacts).

All session-scoped artifacts go here (6 subdirectories total; `review-reports/` is lazy-created):
- `task-metadata/` — per-task scope files written by Scout
- `previews/` — combined prompt previews written by Pantry
- `prompts/` — full task and review prompt files written by Pantry
- `pc/` — Pest Control checkpoint artifact files
- `summaries/` — Dirt Pusher summary docs
- `review-reports/` — Nitpicker and Big Head reports (created lazily at Step 3b-iii via `mkdir -p`, not at Step 0)

Root-level artifacts in `${SESSION_DIR}`:
- `queen-state.md` — session state for context recovery
- `briefing.md` — written by Scout (Step 1a); strategy summary read by Queen after SSV PASS before auto-proceeding to Step 2
- `session-summary.md` — written by Pantry (optional); end-of-session narrative summary
- `exec-summary.md` — written by Scribe (Step 5b); canonical session record covering work completed, review findings, open issues, and narrative observations; source for the CHANGELOG derivative
- `progress.log` — append-only milestone log; one pipe-delimited line per completed step; written by the Queen at each workflow milestone; never read or overwritten during normal operation; recovery sessions read this once to determine the resume point
- `resume-plan.md` — written by `scripts/parse-progress-log.sh` on crash recovery; structured markdown resume plan presented to the user for approval before any action is taken

**Crash recovery script**: `scripts/parse-progress-log.sh <SESSION_DIR>`
- Exit 0: resume-plan.md written; present to user and await `resume` or `fresh start`
- Exit 1: error (missing log, unreadable); surface to user and await instruction
- Exit 2: session already completed (SESSION_COMPLETE logged); no resume-plan written; proceed with fresh start

The `_session-` prefix distinguishes session directories from other entries in `.crumbs/sessions/`.
This prevents collisions when multiple Queens run in the same repo.

## Anti-Patterns

- Reading every agent's output files — trust summaries and commit messages
- Spawning agents one at a time — batch by file/priority
- Re-reading the same metadata — read once, take notes in session state file
- Pushing mid-session — only push at end (atomic deployment)
- Updating docs per-agent — batch all doc updates in Step 4
- Verbose agent prompts — be concise, agents read their own task details from their task brief
- Running individual checkpoints per agent — spawn one Pest Control with the full batch

## Template Lookup

| Workflow Phase | Read This File |
|----------------|----------------|
| Composing agent prompts (Step 2) | orchestration/templates/pantry.md |
| Agent skeleton for spawning (Step 2) | orchestration/templates/dirt-pusher-skeleton.md |
| Review skeleton for team (Step 3b) | orchestration/templates/nitpicker-skeleton.md |
| Big Head skeleton for consolidation (Step 3b) | orchestration/templates/big-head-skeleton.md |
| Implementation details (read by the Pantry) | orchestration/templates/implementation.md |
| Checkpoint details (read by Pest Control) | orchestration/templates/checkpoints.md |
| Review details (read by build-review-prompts.sh) | orchestration/templates/reviews.md |
| Pre-flight recon (Step 1) | orchestration/templates/scout.md |
| Conflict patterns (read by the Scout) | orchestration/reference/dependency-analysis.md |
| Diagnosing a failure or post-mortem | orchestration/reference/known-failures.md |
| Creating/recovering the Queen's state file | orchestration/templates/queen-state.md |
| Exec summary authoring (Step 5b) | orchestration/templates/scribe-skeleton.md |
| Setting up orchestration in new project | orchestration/SETUP.md |

## Retry Limits

| Situation | Max Retries | After Limit |
|-----------|-------------|-------------|
| Agent fails DMVDC | 2 | Escalate to user with full context |
| CCB fails | 1 | Present to user with verification report attached |
| Agent stuck (no commit within 15 turns) | 0 | Run stuck-agent diagnostic (see below); escalate to user |
| Pantry CCO fails | 1 | Escalate to user; do not spawn Dirt Pushers without verified prompts |
| Scout fails or returns no tasks | 1 | Escalate to user; do not proceed to Step 2 without task list |
| SSV FAIL -> re-Scout cycle | 1 | Escalate to user with SSV violations; do not re-run Scout a third time |
| Fix DP stuck/crash (no commit in team) | 0 | Run stuck-agent diagnostic; file a crumb for the failed fix; escalate to user. Do NOT re-spawn without user approval |
| Fix PC crash (fix-pc-wwd or fix-pc-dmvdc) | 1 | Spawn replacement into team (`team_name: "nitpicker-team"`); resume from last SendMessage |
| Reviewer failure (round 2+, re-task via SendMessage fails) | 1 | Spawn fresh reviewer into team as replacement; re-send the round transition message |
| Big Head crash (before crumb filing complete) | 1 | Spawn fresh Big Head into team with handoff brief describing which crumbs were filed and which remain; re-run CCB after |
| CCB material spot-check fail | 1 | Shut down current Big Head; spawn fresh Big Head into team with handoff brief identifying failed crumbs; re-run full crumb review then re-run CCB |
| Scribe fails ESV | 1 | Escalate to user with ESV report; user decides fix manually or push as-is |
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

If more than 50% of agents in a single wave fail (DMVDC failure, stuck, or unrecoverable error), the Queen must:

1. Stop spawning new agents for the remainder of the current wave.
2. Collect failure summaries from all failed agents in the wave.
3. Notify the user immediately: list each failed task ID, the failure type, and retry count consumed.
4. Await explicit user instruction before continuing — options include: re-run the failed subset, abort the session, or manually resolve blockers and resume.

A wave is defined as a set of agents spawned concurrently in a single Step 2 batch. Failures from earlier waves do not carry over into the threshold calculation for a new wave.

## Crumb Priority Calibration

> **Note**: This section defines project-level issue priorities for crumbs filed in the tracker. Nitpicker review severity (P1/P2/P3) is defined separately in `orchestration/templates/reviews.md` and applies to review findings, not crumb filing priority.

**P1** = build failure, broken links, data loss, security vulnerability

**P2** = visual regression, accessibility issue, functional degradation

**P3** = style, naming, cleanup, polish

Project-specific overrides belong in the project's CLAUDE.md or QUALITY_PROCESS.md.

## Context Preservation Targets

- Token budget: finish with >75% remaining (1M context window)
- File reads in the Queen: <10 for 40+ task sessions
- Concurrent agents: typical 5-6 Dirt Pushers, max 12 total
- Commits per session: <20 (batch related work)
