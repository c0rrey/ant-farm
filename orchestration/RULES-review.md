# Review & Fix Workflow (Steps 3b–3c)

> Continuation of the workflow defined in `orchestration/RULES.md`. The Queen reads this file when Step 3b is reached (after all implementation waves are verified).

**Step 3b:** Review — fill review slots and spawn Reviewers.

            **Team persistence**: The Reviewer team persists across the full review-fix-review loop.
            The team is NOT torn down after round 1 consolidation. Fix agents spawn into the same team
            (round 1 or later) and Correctness + Edge Cases reviewers are re-tasked in-place via
            SendMessage for round 2+. Team shutdown happens only at convergence (0 P1/P2) or the round 4
            cap. The one-TeamCreate-per-session constraint makes this the only viable path for
            team-based round 2+ reviews.

            **Team roster progression**:
            - **Round 1 (initial)**: base case 6 members — 4 Reviewers (Clarity, Edge Cases, Correctness, Drift) + Review Consolidator + Checkpoint Auditor (mixed-model: Correctness + Edge Cases use `opus`; Clarity + Drift use `sonnet`). When split reviewer instances are present, member count increases (e.g., 8 members for 2 Clarity + 2 Drift splits). Member names and count come from `build-review-prompts.sh` return table.
            - **After fix wave**: + N fix DPs + fix-pc-scope-verify + fix-pc-claims-vs-code (names: fix-dp-1..N, fix-pc-scope-verify, fix-pc-claims-vs-code; round suffixes for round 2+: fix-dp-r2-1, fix-pc-scope-verify-r2, fix-pc-claims-vs-code-r2)
            - **Peak**: up to 15 members in the base case (6 + 7 fix DPs + 2 fix PCs); higher with split instances. Only N+2 fix agents are active during the fix phase; the original reviewers are idle.
            - **Round 2+**: Clarity and Drift reviewers — including split instances (e.g., `clarity-1`, `clarity-2`, `drift-1`, `drift-2`) — remain idle; Correctness and Edge Cases are re-tasked via named-member SendMessage

            **3b-i. Gather inputs** from the Queen's state file:
            - Review round: read from session state (default: 1)
            - Commit range: round 1 = first session commit..HEAD; round 2+ = first fix commit..HEAD
            - File list: `git diff --name-only {commit-range}` (deduplicated; exclude `.crumbs/tasks.jsonl` and other auto-generated crumbs files)
            - Task IDs: round 1 = all task IDs; round 2+ = fix task IDs only
            - Timestamp: The Queen generates ONE timestamp at the start of Step 3b using `date +%Y%m%d-%H%M%S` format (YYYYMMDD-HHmmss). Store as `{TIMESTAMP}` (shell: `${TIMESTAMP}`):
              ```bash
              TIMESTAMP=$(date +%Y%m%d-%H%M%S)
              ```

            **3b-i.5. Validate review inputs** before proceeding:
            ```bash
            # REVIEW_ROUND: must be a positive integer
            REVIEW_ROUND="$(printf '%s' "${REVIEW_ROUND}" | tr -d '[:space:]')"
            if ! [[ "${REVIEW_ROUND}" =~ ^[1-9][0-9]*$ ]]; then
              echo "ERROR: REVIEW_ROUND is missing or non-numeric (got: '${REVIEW_ROUND}'). Expected: integer >= 1." >&2
              exit 1
            fi

            # CHANGED_FILES: must be non-empty (at least one changed file)
            # Use tr -d for POSIX-portable whitespace stripping (works under bash and zsh).
            if [ -z "$(printf '%s' "${CHANGED_FILES}" | tr -d '[:space:]')" ]; then
              echo "ERROR: CHANGED_FILES is empty. git diff returned no files for the commit range. Verify the commit range contains actual changes." >&2
              exit 1
            fi

            # TASK_IDS: must be non-empty (at least one task ID)
            if [ -z "$(printf '%s' "${TASK_IDS}" | tr -d '[:space:]')" ]; then
              echo "ERROR: TASK_IDS is empty. Round 1 requires all task IDs; round 2+ requires fix task IDs. Verify session state is populated." >&2
              exit 1
            fi
            ```
            On any validation failure: surface the error to the user and do NOT proceed to 3b-ii.

            **3b-ii. Build review prompts** (single script — reads templates and fills all values):
            ```bash
            bash ~/.claude/orchestration/scripts/build-review-prompts.sh \
              "${SESSION_DIR}" "{commit-range}" "{changed-files}" \
              "{task-IDs}" "{timestamp}" "{round}" \
              "$HOME/.claude/orchestration/templates/reviewer-skeleton.md" \
              "$HOME/.claude/orchestration/templates/review-consolidator-skeleton.md"
            ```
            Note: `{changed-files}` and `{task-IDs}` accept an `@filepath` prefix to read multiline
            values from a file (e.g., `@/tmp/changed-files.txt`). Use this to avoid shell quoting
            issues when the list contains many entries or paths with spaces.
            On exit 0: prompts/previews written to `${SESSION_DIR}/prompts/` and `${SESSION_DIR}/previews/`.
            On non-zero: surface stderr to user — do NOT proceed.

            **3b-iii. pre-spawn-check gate**: `mkdir -p "${SESSION_DIR}"/review-reports`, then spawn
            Checkpoint Auditor (`model: "haiku"`) for pre-spawn-check on review previews. Must PASS before spawning team.

            **3b-iv. Spawn reviewer team** (round 1 only — team persists for round 2+):
            - Round 1: base case is 6 members (4 reviewers + Review Consolidator + Checkpoint Auditor); may be more if `build-review-prompts.sh` produces split reviewer instances
            - **Dynamic member list**: The Queen reads the return table from `build-review-prompts.sh` to determine member count and names. Do NOT use a fixed 6-member list. The return table lists every filled slot (e.g., `clarity-1`, `clarity-2`, `drift-1`, `drift-2`) along with their prompt file paths. Build the `members` array from this table — each slot becomes one TeamCreate member entry.
            - **Split instance naming**: When a reviewer type is split across multiple instances, each instance is named `{review-type}-{N}` (e.g., `clarity-1`, `clarity-2`, `drift-1`, `drift-2`). The base-case single-instance names (`clarity-reviewer`, `drift-reviewer`) are used only when no split occurred.
            - Model assignments: Correctness (`model: "opus"`), Edge Cases (`model: "opus"`), Clarity and all clarity-N instances (`model: "sonnet"`), Drift and all drift-N instances (`model: "sonnet"`)
            - Round 2+: do NOT spawn a new team — re-task Correctness and Edge Cases reviewers via named-member SendMessage (see Step 3c fix workflow)
            - Review Consolidator MUST be a team member, NOT a separate Task agent
            - Checkpoint Auditor MUST be a team member so Review Consolidator can SendMessage to it
            - Templates: `reviewer-skeleton.md`, `review-consolidator-skeleton.md`
            - After team completes, claims-vs-code and review-integrity have already run inside the team

            **Constraint: one TeamCreate per session.** Claude Code supports only one `TeamCreate` call
            per session. The reviewer team uses this slot. Any agent that needs to communicate with
            another agent (e.g., Checkpoint Auditor receiving a message from Review Consolidator, fix PCs messaging fix DPs)
            MUST be added as a team member — it cannot be spawned separately as a Task agent and then
            contacted via SendMessage from inside the team. Fix agents spawn into the persistent reviewer
            team using the Task tool with `team_name: "reviewer-team"`. Do NOT add a second TeamCreate
            call anywhere in the workflow.

            **Progress log (after reviewer team completes round 1):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_COMPLETE|round={N}|team=complete|report=${SESSION_DIR}/review-reports/review-consolidated-${TIMESTAMP}.md|next_step=STEP_3C_TRIAGE" >> ${SESSION_DIR}/progress.log`

**Step 3c:** User triage — **after review-integrity PASS and Review Consolidator consolidation completes**:
            1. Read the consolidated review summary (Review Consolidator sends crumb list to Queen via SendMessage — see review-consolidator-skeleton.md step 12)
            2. Check finding counts: P1, P2, P3
            **Termination check**: If zero P1 and zero P2 findings:
            - Round 2+: P3s already auto-filed by Review Consolidator to "Future Work" epic
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
            **Auto-fix (round 1, ≤10 root causes)**: If round == 1 AND total P1+P2 root causes ≤ 10:
            - Announce (do NOT wait for user input):
              "**Auto-fix**: Round 1 review found X P1 and Y P2 issues (Z root causes, within 10-threshold). Spawning fix tasks automatically."
            - Proceed directly to fix workflow (below)
            - After fixes complete + claims-vs-code passes, transition to round N+1 via SendMessage (see Fix Workflow below)
            - Update session state: increment review round, record fix commit range
            **Escalation (round 1, >10 root causes)**: If round == 1 AND total P1+P2 root causes > 10:
            - Present findings to user: "Round 1 review found Z root causes (>10 threshold). This suggests a systemic issue. Fix now or defer?"
            - Await user decision (same as round 2+ behavior below)
            **User prompt (round 2+)**: If round >= 2:
            - Present findings to user: "Reviews found X P1 and Y P2 issues. Fix now or defer?"
            - **If "fix now"**: proceed to Fix Workflow below, then transition to round N+1 via SendMessage
              - Update session state: increment review round, record fix commit range
            - **If "defer"**: P1/P2 crumbs stay open; note deferred items for the Scribe to document at Step 5; proceed to Step 4

            **Fix Workflow** (triggered by auto-fix or "fix now"):

            Fix agents spawn **into the persistent reviewer team** (not as standalone Task agents) using
            the Task tool with `team_name: "reviewer-team"` so they can communicate with reviewers and
            iterate within the team via SendMessage.

            **Step 3c-i. Fix-cycle Scout** — Before spawning fix agents, run a fix-cycle Scout
            (`ant-farm-recon-planner`, `model: "opus"`) to plan the fix strategy: which crumbs to fix, wave
            grouping, and file conflict analysis. The fix-cycle Scout reads the crumb list from Review Consolidator's
            SendMessage handoff (review-consolidator-skeleton.md step 12).

            **Auto-approval**: The fix-cycle Scout's strategy is auto-approved — no user confirmation
            gate. The Scout's strategy drives fix agent spawning directly.

            **startup-check gate**: startup-check runs as a mechanical safety net on the Scout's fix strategy:
            - startup-check PASS → proceed to fix agent spawning (auto-approved)
            - startup-check FAIL → re-run Scout with violations listed (max 1 retry); if still failing, escalate to user

            **Progress log (after fix Scout startup-check PASS):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|FIX_SCOUT_COMPLETE|round={N}|startup_check=pass|fix_crumbs={crumb-ids}|next_step=FIX_AGENTS_SPAWN" >> ${SESSION_DIR}/progress.log`

            **Step 3c-ii. Spawn fix agents into team** — Prompt Composer and pre-spawn-check are skipped for fix agents
            (the Review Consolidator crumb IS the brief; crumb content passed review-integrity; startup-check independently verified the
            strategy). Spawn fix agents into the team in a single message:
            - **N fix DPs** (`model: "sonnet"`, `team_name: "reviewer-team"`): names `fix-dp-1..N`
              (round 2+: `fix-dp-r2-1..N`)
            - **fix-pc-scope-verify** (`model: "haiku"`, `team_name: "reviewer-team"`): one per round; serves
              all fix DPs in the round via SendMessage
            - **fix-pc-claims-vs-code** (`model: "sonnet"`, `team_name: "reviewer-team"`): one per round;
              serves all fix DPs in the round via SendMessage

            **Fix DP prompt structure**: minimal — crumb is the source of truth:
            ```
            You are fix-dp-N, a fix Crumb Gatherer in the Reviewer team.
            Your task crumb: {crumb-id}
            Run: crumb show <crumb-id>
            Implement the fix. Follow the acceptance criteria exactly.
            After committing:
            1. Record commit hash: crumb update <crumb-id> --note="commit: <hash>"
            2. SendMessage to fix-pc-scope-verify: "Fix committed. Crumb: {crumb-id}. Commit: {hash}. Files changed: {list}."
            Then go idle and wait.
            ```

            **Progress log (after fix agents spawned):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|FIX_AGENTS_SPAWNED|round={N}|fix_dps={names}|fix_pcs=fix-pc-scope-verify,fix-pc-claims-vs-code|next_step=FIX_INNER_LOOP" >> ${SESSION_DIR}/progress.log`

            **Step 3c-iii. Fix inner loop** — fully asynchronous via SendMessage within the team:
            ```
            fix-dp-N  -->  [commit]  -->  SendMessage(fix-pc-scope-verify)
                                                |
                                          fix-pc-scope-verify runs scope-verify check (haiku)
                                                |
                                     PASS ------+------ FAIL
                                      |                   |
                           SendMessage(fix-pc-claims-vs-code)   SendMessage(fix-dp-N) with specifics
                                      |                   |
                                fix-pc-claims-vs-code fix-dp-N iterates (max 2 retries total)
                                runs claims-vs-code       |
                                (sonnet)        if retry limit hit → SendMessage(Queen)
                                      |
                           PASS ------+------ FAIL
                            |                  |
                        fix-dp-N           SendMessage(fix-dp-N) with specifics
                        goes idle          fix-dp-N iterates (max 2 retries total)
                                           if retry limit hit → SendMessage(Queen)
            ```

            Retry limit: each fix DP has a maximum of 2 retries total across both scope-verify and claims-vs-code
            failures. On the third failure, the DP sends a message to the Queen and goes idle.
            The Queen escalates to the user.

            **Progress log (after all fix DPs verified by fix-pc-claims-vs-code):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|FIX_CLAIMS_VS_CODE_COMPLETE|round={N}|verified_dps={names}|commits={hashes}|next_step=ROUND_TRANSITION" >> ${SESSION_DIR}/progress.log`

            **Step 3c-iv. Round transition via SendMessage** — after all fix DPs complete and
            fix-pc-claims-vs-code has issued PASS for each, the Queen sends messages to re-task the persistent
            team members for round N+1. Model assignments do NOT change in round 2+: Correctness and
            Edge Cases remain `opus` (they were spawned with opus in round 1; SendMessage does not change model):
            1. **Re-task Correctness reviewer** (`opus` — unchanged): SendMessage to `correctness-reviewer` with review round N+1,
               fix commit range, changed files, and task IDs; provide new report output path
               `{SESSION_DIR}/review-reports/correctness-r{N+1}-{timestamp}.md`
            2. **Re-task Edge Cases reviewer** (`opus` — unchanged): SendMessage to `edge-cases-reviewer` with review round N+1,
               fix commit range, changed files, and task IDs; provide new report output path
               `{SESSION_DIR}/review-reports/edge-cases-r{N+1}-{timestamp}.md`
            3. **Re-task Review Consolidator**: SendMessage to `ant-farm-review-consolidator` with review round N+1, expected report
               count 2, both report paths, and new consolidated output path
               `{SESSION_DIR}/review-reports/review-consolidated-r{N+1}-{timestamp}.md`
            4. **Clarity and Drift — idle semantics**: These reviewers are NOT re-tasked in round 2+ (fix-scope reviews cover
               only fix commits; style/drift are out of scope). This applies equally to split instances: if round 1 spawned
               `clarity-1` and `clarity-2` (or `drift-1` and `drift-2`), ALL of those instances remain idle in round 2+.
               Do NOT send them any message. Named-member SendMessage is required — never use broadcast, which would
               inadvertently wake idle Clarity and Drift split instances.

            **Progress log (after round transition messages sent):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|ROUND_TRANSITION|from_round={N}|to_round={N+1}|fix_commits={range}|next_step=REVIEW_3B" >> ${SESSION_DIR}/progress.log`

            After the round transition, the loop returns to the top of Step 3c: Review Consolidator consolidates
            round N+1 reports, review-integrity runs inside the team, and the Queen reads the new crumb list from
            Review Consolidator's SendMessage. If zero P1/P2 → proceed to Step 4. If P1/P2 remain and round < 4
            → repeat fix workflow. If round >= 4 → escalate to user.

            **Progress log (after triage decision — fix path):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_TRIAGED|round={N}|p1={count}|p2={count}|decision={auto_fix|fix_now}|root_causes={count}|next_step=FIX_SCOUT" >> ${SESSION_DIR}/progress.log`

            **Progress log (after triage decision — non-fix path):** `echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|REVIEW_TRIAGED|round={N}|p1={count}|p2={count}|decision={defer|terminated}|root_causes={count}|next_step=STEP_4_DOCS" >> ${SESSION_DIR}/progress.log`


