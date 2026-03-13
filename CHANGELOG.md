# Changelog

## 2026-03-13 — Session 20260313-021827 (Beads Migration + New Agent Infrastructure + Fix Loop)

### Summary

Two migration epics (ant-farm-irgq: 6 mechanical tasks; ant-farm-f4h5: 9 semantic tasks) replaced all `bd`/`.beads/` references with `crumb`/`.crumbs/` equivalents across 15 template, script, and documentation files in 3 waves. The same session also introduced the Architect and Forager agent definitions, a 7-step decomposition workflow (RULES-decompose.md), four slash-skill definitions (init, work, plan, status), and the setup.sh installer. Review round 1 covered 36 changed files, finding 3 P1 and 10 P2 root causes from 51 raw findings (23 consolidated); all 13 were fixed across 3 sub-waves. Round 2 found 1 residual P2 (ant-farm-tbis fix incomplete on pantry.md and big-head-skeleton.md); fixed in 1 commit. Round 3 found 1 P3 only — terminated. 46 commits total.

### Implementation (Wave 1: bd-to-crumb Mechanical Migration — 6 tasks)

- **ant-farm-6gg6** (`5708d88`): docs: migrate Scout and implementation templates to crumb CLI — all `bd` references replaced in `orchestration/templates/scout.md` and `orchestration/templates/implementation.md`
- **ant-farm-eifm** (`06c0011`): docs: migrate queen-state and session plan templates to crumb CLI — `orchestration/templates/queen-state.md` and `orchestration/templates/SESSION_PLAN_TEMPLATE.md`
- **ant-farm-gvd4** (`b0dab79`): chore: migrate dirt-pusher, nitpicker, scribe skeletons bd to crumb — `dirt-pusher-skeleton.md`, `nitpicker-skeleton.md`, `scribe-skeleton.md`
- **ant-farm-k03k** (`2ac0e86`): docs: replace bd references with crumb equivalents in reference and setup docs — `orchestration/reference/dependency-analysis.md`, `orchestration/SETUP.md`
- **ant-farm-mmo3** (`76d02ad`): docs: replace bd command references with crumb equivalents in agent definitions — `agents/scout-organizer.md`, `agents/nitpicker.md`
- **ant-farm-vjhe** (`37cce08`): docs: migrate project docs from bd/beads to crumb/crumbs — `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/installation-guide.md`

### Implementation (Waves 1–3: bd-to-crumb Semantic Migration — 9 tasks)

- **ant-farm-6d3f** (`8aa01a7`): chore: replace `bd show` with `crumb show` in `scripts/build-review-prompts.sh`
- **ant-farm-a50b** (`cb2204b`): fix: migrate big-head-skeleton.md bd commands to crumb CLI — `orchestration/templates/big-head-skeleton.md`
- **ant-farm-ax38** (`5260783`): docs: migrate CLAUDE.md bd references to crumb CLI — `CLAUDE.md` and `~/.claude/CLAUDE.md`
- **ant-farm-epmv** (`3fe4b6e`): docs: migrate pantry.md bd CLI references to crumb equivalents — `orchestration/templates/pantry.md`
- **ant-farm-h2gu** (`15fe938`): docs: migrate bd CLI references to crumb equivalents in checkpoints.md
- **ant-farm-n56q** (`b9892fe`): docs: migrate reviews.md bd CLI references to crumb CLI
- **ant-farm-o0wu** (`710ec47`): docs: migrate RULES-review.md bd commands and .beads/ paths to crumb/.crumbs/ — new file added (214 lines)
- **ant-farm-rue4** (`4147daf`): docs: migrate RULES.md bd commands and paths to crumb/.crumbs/ equivalents
- **ant-farm-veht** (`b8bbdb4`): docs: add TDV checkpoint definition to checkpoints.md

### Implementation (New Agent Infrastructure and Skills)

- **ant-farm-xtu9** (`eb1fae4`): feat: add Architect agent definition, decomposition workflow, and skeleton — `agents/architect.md`, `orchestration/templates/decomposition.md`, `orchestration/templates/architect-skeleton.md`
- **ant-farm-y4hl** (`8312b12`): feat: add Forager agent definition, workflow template, and skeleton — `agents/forager.md`, `orchestration/templates/forager.md`, `orchestration/templates/forager-skeleton.md`
- **ant-farm-rwsk** (`8ab12f5`): feat: add RULES-decompose.md with 7-step decomposition workflow (457 lines)
- **ant-farm-hlv6** (`ebcffeb`): feat: add full JSON payload example to decomposition orchestration template
- **ant-farm-3mdg** (`6f3485e`): docs: define Planner orchestrator profile in RULES-decompose.md
- **ant-farm-3imu** (`57d7a66`): feat: add /ant-farm:init skill definition — `skills/init.md` (239 lines)
- **ant-farm-2hx8** (`7fdcc1e`): feat: add /ant-farm:work skill definition — `skills/work.md` (142 lines)
- **ant-farm-a5lq** (`467aa6e`): feat: add /ant-farm:plan skill definition — `skills/plan.md` (169 lines)
- **ant-farm-n3qr** (`f54578b`): feat: add /ant-farm:status skill definition — `skills/status.md` (183 lines)
- **ant-farm-3bz5** (`7dde9ce`): feat: add setup.sh install script replacing sync-to-claude.sh — `scripts/setup.sh` (245 lines)

### Review Fixes (Round 1, Wave 1 — 7 P1/P2 root causes)

- **ant-farm-5ujg** (`e668d8e`, `68006ac`): fix: remove non-existent `crumb sync` from AGENTS.md quick-reference and push block
- **ant-farm-rlne** (`6e6357c`): fix: clarify Condition 3 contamination detection with precise regex and example (`orchestration/templates/pantry.md`)
- **ant-farm-rgg3** (`d2d3f1f`): fix: add `-r` check to FOCUS_AREAS_FILE validation (`scripts/build-review-prompts.sh`)
- **ant-farm-9ahp** (`28baea2`): fix: add CLAUDE.md sync step to setup.sh (`scripts/setup.sh`)
- **ant-farm-52ka** (`b8bbdb4`): fix: add substitution instruction before brownfield detection block (`orchestration/RULES-decompose.md`)
- **ant-farm-5fq0** (`55381ec`): fix: add rollback error handling to Dolt mode switch (`orchestration/templates/decomposition.md`)
- **ant-farm-nmpw** (`34712c8`): fix: exclude error-status tasks from conflict analysis and wave 1 (`orchestration/templates/scout.md`)

### Review Fixes (Round 1, Wave 2 — 4 P2 root causes)

- **ant-farm-tbis** (`cef1915`): fix: update stale SESSION_DIR path in 6 files — `AGENTS.md`, `CLAUDE.md`, `scout.md`, `dependency-analysis.md`, `dirt-pusher-skeleton.md`, `scribe-skeleton.md`
- **ant-farm-5ohl** (`75aaea0`): fix: propagate resolve_arg failures from command substitutions (`scripts/build-review-prompts.sh`)
- **ant-farm-7fc3** (`2ef18a7`): fix: remove hardcoded polling timeout from big-head-skeleton (`orchestration/templates/big-head-skeleton.md`)
- **ant-farm-z305** (`e6a0a27`): fix: filter pre-flight task count to tasks only (`skills/work.md`)

### Review Fixes (Round 1, Wave 3 — 2 P2 root causes)

- **ant-farm-c47w** (`1749415`): fix: clarify crumb vs bd CLI relationship in AGENTS.md — added explanatory note; aligned prohibition language
- **ant-farm-qv4a** (`344a18d`): fix: clean up temp files on error paths in fill_slot and big-head dedup (`scripts/build-review-prompts.sh`, `orchestration/templates/big-head-skeleton.md`)

### Review Fixes (Round 2, 1 P2 root cause)

- **ant-farm-tack** (`ca13ddf`): fix: update stale SESSION_DIR examples in pantry.md and big-head-skeleton.md — two files missed by ant-farm-tbis in Round 1

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 36 files, 15 migration + infra tasks | 3 | 10 | 11+ | NEEDS WORK |
| 2 | 13 fix commits | 0 | 1 | 0 | PASS WITH ISSUES |
| 3 | 1 fix commit | 0 | 0 | 1 | PASS WITH ISSUES |

51 raw findings (round 1) → 23 root causes consolidated; 3 skipped (cross-session dedup); 13 P1/P2 root causes fixed across 3 sub-waves. Round 2: 2 raw findings → 1 root cause fixed. Round 3: 1 raw finding → 1 P3 auto-filed to Future Work (ant-farm-sj3f).

## 2026-03-13 — Session 20260313-001327 (Crumb CLI Build + Review Fix Loop)

### Summary

Epic ant-farm-e7em (Crumb CLI) completed in full: 9 feature tasks built crumb.py from scaffold to a production-ready single-file Python CLI across 4 waves (~47 minutes). Review round 1 found 0 P1 and 5 P2 root causes across 17 consolidated root causes (26 raw findings); all 5 P2s were auto-fixed in a serial fix cycle (5 commits, 1 agent, same file). Round 2 reviewed the 5 fix commits, found 1 new P2 regression (ant-farm-k040), deferred by user. 14 commits total.

### Implementation (Waves 1–4: 9 feature tasks)

- **ant-farm-mg0r** (`03708ef`): feat: scaffold crumb.py with CLI framework and core infrastructure — argparse subparser dispatch, FileLock, atomic write via temp-then-rename, walk-up directory discovery, JSONL utilities (crumb.py, 599 lines)
- **ant-farm-l7pk** (`41004c4`): feat: implement crumb create, show, list commands — `_find_crumb`, sort key helpers; dual-mode create (--title / --from-json); filtering, sorting, limit, --short output (crumb.py)
- **ant-farm-cmcd** (`86770aa`): feat: implement crumb update, close, reopen commands — status transition guard, note appending, multi-ID close (idempotent), reopen clears closed_at (crumb.py)
- **ant-farm-h7af** (`a67cf4a`): feat: implement crumb link command — nested links dict; --parent, --blocked-by (dedup), --remove-blocked-by, --discovered-from flags (crumb.py)
- **ant-farm-jmvi** (`58c61b3`): feat: implement trail commands — trail create/show/list/close; auto-close and auto-reopen hooks in cmd_close and cmd_link (crumb.py)
- **ant-farm-vxpr** (`1ff6edc`): feat: implement crumb ready and blocked commands — `_get_blocked_by` + `_is_crumb_blocked` helpers; partition of open crumbs by readiness (crumb.py)
- **ant-farm-izng** (`bdcf2ed`): feat: implement crumb doctor command — two-pass syntax + semantic validation; malformed JSON, duplicate IDs, dangling parents (errors), orphan/dangling blocked_by (warnings); --fix flag (crumb.py)
- **ant-farm-fdz2** (`36dffe2`): feat: implement crumb import and --from-beads migration — plain JSONL import with line-level error recovery; beads-to-crumb format conversion; counter advancement (crumb.py)
- **ant-farm-dhh8** (`0627e70`): feat: implement crumb search and tree commands — case-insensitive keyword search; hierarchical tree view with orphan section (crumb.py)

### Review Fixes (Round 1, 5 P2 root causes)

- **ant-farm-35a5** (`500d88e`): fix: wrap open/touch calls in try/except OSError in read_tasks(), iter_jsonl(), FileLock.__enter__ (crumb.py)
- **ant-farm-ru51** (`d33fde5`): fix: dual-lookup parent/discovered_from in cmd_list filters and _auto_close_trail_if_complete (crumb.py)
- **ant-farm-l1en** (`87cdd8f`): fix: validate --from-json type (isinstance dict) and config counter fields in read_config() (crumb.py)
- **ant-farm-bzhs** (`74c5cf6`): fix: fix inverted blocks dependency direction in _convert_beads_record; add _apply_blocks_deps post-processing pass (crumb.py)
- **ant-farm-ch0z** (`96347af`): fix: expand FileLock scope in cmd_doctor to cover full read-validate-write sequence (crumb.py)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 1 file, 9 tasks | 0 | 5 | 12 | PASS WITH ISSUES |
| 2 | 1 file, 5 fix tasks | 0 | 1 | 0 | PASS WITH ISSUES |

26 raw findings (round 1) → 17 root causes consolidated; 1 raw finding (round 2) → 1 root cause. 5 P2 root causes fixed in round 1. 12 P3 findings not filed as beads. Round 2 P2 (ant-farm-k040) deferred by user.

## 2026-02-23 — Session 20260222-225628 (Persistent-Team Fix Loop + CCB Spot-Check)

### Summary

4 original tasks (ant-farm-ygmj.1–.4) upgraded the review-fix loop infrastructure: CCB model from haiku to sonnet with a new root cause spot-check, Big Head bead-list handoff step, full rewrite of the reviews.md fix workflow for the in-team persistent model, and RULES.md documentation of team persistence, fix inner loop, and 4 new progress log milestones. Review round 1 found 2 P1 and 6 P2 root causes across 23 raw findings (17 consolidated); all fixed in a batched fix cycle across 3 delivery agents. Round 2 found 2 P2 defects in the fix itself (pseudocode in shell, criteria drift); both fixed in 1 commit. Round 3 confirmed all fixes and found 1 P3, terminating the loop. 10 commits total.

### Implementation (Waves 1–3: 4 tasks)

- **ant-farm-ygmj.1** (`05ebb82`): feat: upgrade CCB to sonnet and add root cause spot-check — new Check 3b section in checkpoints.md with minor/material severity distinction, 6-step escalation path; CCB row updated in RULES.md Model Assignments table
- **ant-farm-ygmj.2** (`9f4c6da`): feat: add bead-list handoff step to Big Head skeleton — new Step 12 in big-head-skeleton.md with SendMessage format, round-conditional trigger, P1/P2/P3 separation
- **ant-farm-ygmj.3** (`f686f88`): refactor: rewrite fix workflow for in-team agents — replaced outdated standalone-agent Fix Workflow in reviews.md with 8 subsections covering Scout auto-approval, Pantry/CCO skip, naming, prompt structure, inner loop, wave composition, round transition, re-run reviews
- **ant-farm-ygmj.4** (`9fcfc87`): refactor: update RULES.md for persistent team and fix inner loop — Steps 3b/3c rewritten for persistent team; Model Assignments and Retry Limits tables expanded; 4 new progress log milestones added

### Review Fixes (Round 1, 8 P1/P2 root causes)

- **ant-farm-ql6s** (`06cf404`): fix: wrong team name "nitpickers" → "nitpicker-team" in reviews.md Fix Workflow (reviews.md)
- **ant-farm-1pa0** (`06cf404`): fix: add single-invocation constraint comment and increase POLL_TIMEOUT_SECS from 30 to 60 (reviews.md, big-head-skeleton.md)
- **ant-farm-f7lg** (`06cf404`, `0463fa5`): fix: remove phantom briefs/ path; add explicit edge-cases output path to round-transition spec (reviews.md, RULES.md)
- **ant-farm-5zs0** (`06cf404`): fix: rewrite Round 2+ spawn instructions to use SendMessage re-tasking, not TeamCreate (reviews.md)
- **ant-farm-fp74** (`06cf404`): fix: add failure artifact write and Queen notification before exit 1 on bd list failure (reviews.md, big-head-skeleton.md)
- **ant-farm-01a8** (`365a0d9`): fix: restore conditional clarity/drift path check with REVIEW_ROUND pre-validation invariant comment (reviews.md)
- **ant-farm-1rof** + **ant-farm-evk2** (`a58c56f`, `0463fa5`): fix: add session dir existence check to crash recovery; add shutdown prohibition to Queen Prohibitions and Step 3c (RULES.md)
- **ant-farm-ccg8** (`4021909`): fix: add repo root commit guard to ESV Check 2 git log range (checkpoints.md)

### Review Fixes (Round 2, 2 P2 root causes)

- **ant-farm-fz32** (`50844a7`): fix: remove SendMessage pseudocode from shell error handler; add prose halt-and-notify instruction outside bash block (reviews.md, big-head-skeleton.md)
- **ant-farm-pj9t** (`50844a7`): fix: update ant-farm-01a8 acceptance criteria to document conditional-check approach and REVIEW_ROUND pre-validation invariant (bead metadata only)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 4 files, 4 tasks | 2 | 6 | 9 | PASS WITH ISSUES |
| 2 | 4 files, 9 fix tasks | 0 | 2 | 3 | PASS WITH ISSUES |
| 3 | 2 files, 2 fix tasks | 0 | 0 | 1 | PASS |

23 raw findings (round 1) → 17 root causes consolidated; 6 raw findings (round 2) → 5 root causes; 3 raw findings (round 3) → 1 root cause. 10 P1/P2 root causes fixed across rounds 1 and 2. 13 P3 beads filed (10 round 1 + 3 round 2+ auto-filed to Future Work epic ant-farm-66gl).

## 2026-02-22 — Session 86c76859 (CCB Timeout + Pantry Preview + Review Focus Areas)

### Summary

3 original tasks (ant-farm-q59z, ant-farm-vxcn, ant-farm-m4si) fixing CCB timeout, Pantry preview enforcement, and progress log key naming. Review round 1 found 0 P1, 4 P2, 9 P3 (13 root causes). 4 P2 fixes applied in-session across 3 waves. 12 review beads filed by Big Head. Mid-session fix: `build-review-prompts.sh` patched to inject per-type focus areas from `review-focus-areas.md` (CCO caught missing focus blocks).

### Implementation (Wave 1: 3 tasks, parallel)

- **ant-farm-q59z** (`a59d61e`): fix: replace sleep-based CCB wait with turn-based end-turn protocol in reviews.md and big-head-skeleton.md
- **ant-farm-vxcn** (`1b8f898`): fix: enforce preview file as mandatory output in Pantry Step 3 with read-back verification
- **ant-farm-m4si** (`55514c1`): fix: rename tasks_approved to tasks_accepted, document N derivation in RULES.md

### Review Fixes (Round 1, 4 P2 root causes)

- **RC-5** (ant-farm-m2cb, `ba0d70d`): fix: rename Priority Calibration to Bead Priority Calibration, consolidate Information Diet, move Review Quality Metrics
- **RC-10** (ant-farm-bzl6, `ed0a651`): fix: enforce REVIEW_ROUND >= 1 and non-empty CHANGED_FILES in build-review-prompts.sh
- **RC-6** (ant-farm-60em, `214ad51`): docs: expand incomplete mechanism descriptions in RULES.md and big-head-skeleton.md
- **RC-2** (ant-farm-zzdk, `f81bd86`): fix: resolve template-vs-runtime placeholder confusion, add post-write placeholder scan

### Infrastructure Fix (Mid-Session)

- `build-review-prompts.sh`: Added `extract_focus_block()` helper and `## Focus` section injection per review type, sourced from `review-focus-areas.md`. CCO caught identical generic prompts across all 4 review types.

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 4 files, 3 tasks | 0 | 4 | 9 | PASS WITH ISSUES |

13 root causes consolidated from 35 raw findings. 4 P2 root causes fixed in-session. 8 P3 beads filed. 1 P3 skipped (matched existing ant-farm-2sjc).

### Open beads filed this session

- ant-farm-sf3v (P3): Stale "user approval" label in parse-progress-log.sh
- ant-farm-yufy (P3): Deprecated pantry.md Section 2 stale and misleading
- ant-farm-8evt (P3): Lifecycle metadata mixed into operational steps
- ant-farm-az7u (P3): Pantry step numbering namespace collision
- ant-farm-e26s (P3): Post-push sync check documentation gaps
- ant-farm-8kds (P3): fill_slot temp file leak on awk failure
- ant-farm-d1rx (P3): Polling loop off-by-one (28s vs 30s)
- ant-farm-kf0y (P3): RULES.md bash blocks missing edge-case handling

## 2026-02-22 — Session 2bb21f22 (Auto-Approve Scout Strategy)

### Summary

1 feature task (ant-farm-fomy) to auto-approve Scout strategy after SSV PASS, removing the user approval gate from Step 1b. Review round 1 found 1 P1 + 2 P2 + 1 P3 (4 root causes). P1 and P2 fixes applied in-session. Review round 2 found 0 P1/P2 (3 P3s auto-filed to Future Work). 3 implementation commits + 2 fix commits.

### Implementation (Wave 1: 1 task)

- **ant-farm-fomy**: docs: auto-approve Scout strategy after SSV PASS in Step 1b — removed user approval gate, added risk analysis block documenting safety nets, rejected complexity threshold

### Review Fixes (Round 1, 3 root causes)

- **RC-2** (ant-farm-i7wl): fix: add zero-task guard and SSV FAIL retry cap to RULES.md Step 1b
- **RC-3** (ant-farm-sfe0): fix: update stale briefing.md descriptions in RULES.md (lines 28, 474)
- **RC-4** (ant-farm-or8q, partial): fix: remove user-approval references from checkpoints.md and dependency-analysis.md; CLAUDE.md and README.md updated by Queen in Step 4

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 1 file, 1 task | 1 | 2 | 1 | PASS WITH ISSUES |
| 2 | 3 files, 3 fix tasks | 0 | 0 | 3 | PASS |

4 root causes consolidated from 11 raw findings (round 1). 3 P1/P2 root causes fixed in-session. 1 P3 (RC-1, ant-farm-m4si) filed. Round 2: 3 P3s auto-filed to Future Work epic.

### Open beads filed this session

- ant-farm-m4si (P3): Progress log key tasks_approved misleading after auto-approve change
- ant-farm-vxcn (P2): Pantry skips writing preview file to previews/ directory
- ant-farm-q59z (P2): Big Head cannot receive Pest Control messages — timeout on every CCB exchange
- Plus 3 P3s auto-filed by Big Head to Future Work epic (round 2)

## 2026-02-22 — Session d81536bb (Exec Summary Scribe Infrastructure)

### Summary

Epic ant-farm-68di: Created the Scribe agent infrastructure for automated session exec summaries and CHANGELOG entries. Added ESV (Exec Summary Verification) as the 6th Pest Control checkpoint. 5 implementation tasks across 3 waves, plus 7 P2 review fixes. 11 commits total (5 implementation + 6 fixes).

### Implementation (3 waves, 5 tasks)

- **ant-farm-68di.1**: feat: add Scribe skeleton template — new orchestration/templates/scribe-skeleton.md with 7-source input table, embedded exec-summary format, CHANGELOG derivation rules, and duration calculation instructions
- **ant-farm-68di.2**: feat: add ESV checkpoint to checkpoints.md — 6 mechanical checks (task coverage, commit coverage, open bead accuracy, CHANGELOG fidelity, section completeness, metric consistency) with bd show guard and retry-then-escalate flow
- **ant-farm-68di.3**: docs: integrate Scribe and ESV workflow into RULES.md — new Steps 5b/5c, Hard Gates table, Agent Types/Model Assignments tables, Session Directory artifacts, Template Lookup, Retry Limits
- **ant-farm-68di.4**: feat: add SCRIBE_COMPLETE and ESV_PASS milestones to crash recovery script (parse-progress-log.sh)
- **ant-farm-68di.5**: docs: update cross-references from Step 4 CHANGELOG to Step 5b/Scribe across reviews.md, SESSION_PLAN_TEMPLATE.md, README.md, GLOSSARY.md, queen-state.md

### Review Fixes (Round 1, 7 P2 root causes)

- **RC-1** (ant-farm-nra7): fix: propagate ESV to GLOSSARY checkpoint counts ("five" -> "six"), acronyms table, Pest Control role
- **RC-2** (ant-farm-lbr9): fix: add ESV row to README Hard Gates table
- **RC-3** (ant-farm-ru2v): fix: update RULES.md Step 3c defer path from "document in CHANGELOG" to Scribe/Step 5b
- **RC-8** (ant-farm-tx0z): fix: complete ESV input specification — empty bead list handling, ^.. commit range, spawn fields
- **RC-9** (ant-farm-ye5r): fix: add empty-data fallback instructions to Scribe skeleton (missing CHANGELOG, zero summaries)
- **RC-16** (ant-farm-hodh): fix: move scribe-skeleton.md from FORBIDDEN to PERMITTED in Queen Read Permissions
- **RC-22** (ant-farm-7026): fix: add empty-string guard to Big Head polling placeholder check

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 9 files, 5 tasks | 0 | 7 | 16 | PASS WITH ISSUES |

23 root causes consolidated from 36 raw findings. 7 P2s fixed in-session. 15 P3s filed as beads (backlog). 1 no-action (RC-23).

### Open P3 beads filed this session

ant-farm-ix7m, ant-farm-3vye, ant-farm-7l1z, ant-farm-6t89, ant-farm-5vs8, ant-farm-hefc, ant-farm-qm8d, ant-farm-by3g, ant-farm-21q7, ant-farm-l70g, ant-farm-cqzj, ant-farm-hiyh, ant-farm-9p9q, ant-farm-0xr1, ant-farm-5nhs

## 2026-02-22 — Session 5da05acb (Documentation Bug Fixes + Review Fix Cycle)

### Summary

6 P2 documentation bugs fixed across orchestration docs, README, CONTRIBUTING, GLOSSARY, sync script, and SESSION_PLAN_TEMPLATE. Review round 1 found 0 P1, 2 P2, 8 P3 (13 root causes, 3 deduplicated against existing beads). 5 root causes fixed in-session (RC-3, RC-4, RC-5, RC-6, RC-11). 5 P3s dropped by user decision. 6 implementation commits + 3 fix commits.

### Implementation (Wave 1: 4 agents, 6 tasks)

- **ant-farm-2yww + ant-farm-80l0**: fix: update reader attributions from Pantry (review mode) to build-review-prompts.sh across RULES.md, README.md, GLOSSARY.md, CONTRIBUTING.md; add missing SSV row to README Hard Gates table
- **ant-farm-q84z + ant-farm-zg7t**: fix: unify TIMESTAMP naming (remove dual REVIEW_TIMESTAMP), replace macOS-incompatible shell commands with bash-native equivalents in RULES.md
- **ant-farm-tour**: fix: update SESSION_PLAN_TEMPLATE review sections to match parallel TeamCreate workflow and root-cause-based triage
- **ant-farm-sje5**: fix: add preflight check for missing code-reviewer.md agent in sync-to-claude.sh

### Review Fixes (Round 1 auto-fix, 5 root causes)

- **RC-3**: fix: update skeleton template attributions from Pantry to build-review-prompts.sh (nitpicker-skeleton.md, big-head-skeleton.md)
- **RC-4**: fix: add warning when agents/ directory exists but contains no .md files (sync-to-claude.sh)
- **RC-5**: fix: replace fixed sleep 5 with 15s readiness poll in dummy reviewer tmux launch (RULES.md)
- **RC-6**: fix: replace single-item for-loop with direct cp (sync-to-claude.sh)
- **RC-11**: fix: add explicit error guard on backup cp (sync-to-claude.sh)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 6 files, 6 tasks | 0 | 2 | 8 | PASS WITH ISSUES |

13 root causes consolidated. 3 skipped (existing beads: ant-farm-2yww, ant-farm-q84z, ant-farm-4lcv). 5 fixed in-session. 5 P3s dropped per user decision.

## 2026-02-22 — Session db790c8d + e7ff7c0d (P1 Bug Fixes + Deferred Reviews)

### Summary

4 P1 bug fixes completed in session db790c8d, with reviews deferred and completed in continuation session e7ff7c0d. 1 P2 review finding fixed (WAVE_WWD_PASS missing from crash recovery). Reviews terminated at round 2 (0 P1, 1 dismissed P2 false positive). 6 P3 findings filed. 5 implementation commits.

### Implementation (Session db790c8d — 2 waves, 4 tasks)

- **x8iw**: fix: update Scout and Pantry model references from sonnet to opus (GLOSSARY.md, README.md, scout-organizer.md)
- **h94m**: docs: correct checkpoints.md Pest Control architecture to direct execution
- **wg2i**: fix: regenerate pre-push hook with non-fatal sync, fix CONTRIBUTING.md sync docs
- **zuae**: fix: document WWD batch vs serial execution modes in RULES.md + checkpoints.md

### Review Fix (Session e7ff7c0d)

- **951b**: fix: add WAVE_WWD_PASS to parse-progress-log.sh STEP_KEYS (P2 — unmet crash recovery criterion)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 6 files, 4 tasks | 0 | 1 | 6 | PASS WITH ISSUES |
| 2 | 1 file, 1 fix task | 0 | 1 (dismissed) | 0 | Terminated |

7 review beads filed in round 1 (1 P2 + 6 P3). Round 2 P2 dismissed as false positive (reviewer misread acceptance criteria). P3s remain open for future work.

## 2026-02-21 — Session 068ecc83 (Documentation Cleanup + Pantry-Review Deprecation)

### Summary

6 tasks completed (3 original P3 doc bugs + 3 P2 review fixes) across 8 files. Reviews converged at round 2 (0 P1/P2). 16 P3 findings filed to Future Work epic. 6 commits, +30/-19 lines.

### Implementation (Wave 1: 3 tasks)

- **6jxn**: fix: update stale pantry-review references across 4 documentation surfaces (reviews.md, README.md, pantry.md, _archive/pantry-review.md)
- **oc9v**: docs: remove stale pantry-review from Scout exclusion list (scout.md)
- **n0or**: docs: clarify comments and fix code fence nesting (SETUP.md, parse-progress-log.sh, compose-review-skeletons.sh)

### Review Fixes (Round 2)

- **xybg**: fix: re-add pantry-review to Scout exclusion list (P2 — stale agent on disk unguarded)
- **aqlp**: fix: tighten sed regex from * to + and document canonical slot names (P2 — blanket uppercase conversion)
- **wzno**: fix: correct POSIX-compatible comment to Bash 3+-compatible (P2 — misleading portability claim)

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 8 files, 3 tasks | 0 | 3 | 16 | PASS WITH ISSUES |
| 2 | 3 files, 3 fix tasks | 0 | 0 | 0 | PASS |

19 review beads filed (round 1: 3 P2 + 16 P3; round 2: 0). P3s filed to Future Work epic (ant-farm-bkco).

### Epics

- **ant-farm-bkco** (Future Work): 16 new P3 children added from review findings

## 2026-02-21 — Session 7edaafbb (Shell Script Hardening + P2 Bugs)

### Summary

30 tasks completed (4 P2 bugs + 26 P3 shell script hardening) across 14 files. 7 review findings fixed in round 2 (1 P1, 6 P2). Reviews converged at round 2 (0 P1/P2). 37 commits, +310/-127 lines.

### Implementation (Wave 1: 26 tasks, Wave 2: 4 tasks)

**fill-review-slots.sh** (4 tasks):
- **39zq**: perf: batch fill_slot awk calls into single pass per file
- **i2zd**: fix: add EXIT trap to clean up temp files on abnormal exit
- **lc97**: fix: reject empty @file arguments in resolve_arg with error
- **ti6g**: fix: reject review round 0

**scrub-pii.sh** (5 tasks):
- **9wk8**: fix: replace magic 'ctc' token with self-documenting '[REDACTED]'
- **ns95**: docs: document intentional email regex coverage scope
- **9vq**: fix: use PII_FIELD_PATTERN variable in post-scrub verification grep calls
- **50m**: fix: check perl availability at startup with clear error message
- **wtp**: fix: print re-staging reminder when run standalone outside a git hook

**sync-to-claude.sh** (5 tasks):
- **40z**: fix: remove rsync --delete to preserve custom user files
- **g29r**: fix: warn to stderr when expected sync scripts are missing
- **szcy**: docs: add comment explaining why only two scripts are synced
- **3r9**: fix: append PID to backup timestamp to eliminate collision risk
- **rja**: fix: warn to stderr when agents/ directory is missing

**install-hooks.sh** (4 tasks):
- **3mg**: fix: ensure sync-to-claude.sh is executable after clone
- **4fx**: fix: use timestamped backup filenames to preserve backup history
- **4g7**: fix: add descriptive error message with remediation on sync failure
- **dv9g**: docs: add rationale comment for non-fatal sync failure design

**compose-review-skeletons.sh + parse-progress-log.sh** (3 tasks):
- **o058**: fix: count both frontmatter delimiters in extract_agent_section
- **yn1r**: fix: document sed regex 2+ char minimum and blanket-conversion assumption
- **npfx**: fix: harden parse-progress-log.sh (overwrite warning, dead branch, timestamp validation)

**RULES.md** (2 tasks):
- **e1u6**: fix: add $TMUX guard around dummy reviewer tmux commands
- **qoig**: fix: add tmux binary availability check to dummy reviewer guard

**SETUP.md + scout.md** (3 tasks):
- **a66**: fix: replace hardcoded hs_website example paths with generic my-project
- **kwp**: fix: clarify test checklist — Queen delegates bd show to Scout
- **lhq**: fix: enrich Scout error metadata template with context fields

**Cross-cutting Wave 2** (4 tasks):
- **352c.1**: fix: replace LLM-interpreted IF ROUND 1 markers with shell conditionals
- **w2i1**: fix: add unfilled slot marker validation to fill-review-slots.sh
- **j6jq**: refactor: replace magic numbers, fix inverted sentinel in reviews.md polling loop
- **a1rf**: fix: harden grep -c set-e interaction, simplify whitespace check, wrap backup cp

### Review Fixes (Round 2)

- **ul02**: fix: revert extract_agent_section awk to count>=1 for single-delimiter skeletons (P1)
- **viyd**: fix: replace grep \s with POSIX [[:space:]] for BSD compatibility
- **ub8a**: fix: exclude _archive/ from rsync to prevent stale deprecated files
- **shkt**: fix: add placeholder guard for REVIEW_ROUND assignment
- **sjyg**: fix: reword troubleshooting to delegate bd show to Scout
- **2qmt**: fix: update stale TIMED_OUT reference to REPORTS_FOUND
- **bhgt**: fix: make pre-commit hook warn instead of fail when scrub-pii.sh missing

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 13 files, 30 tasks | 1 | 6 | 8 | NEEDS WORK |
| 2 | 7 files, 7 fix tasks | 0 | 0 | 3 | PASS |

18 review beads filed (round 1: 1 P1 + 6 P2 + 8 P3; round 2: 3 P3 auto-filed to Future Work).

### Epics

- **ant-farm-352c** (Future Work): 11 new P3 children added from review findings

## 2026-02-20 — Session cd9866 (Bug Sweep)

### Summary

17 P2 bugs fixed across 14 files (orchestration templates, scripts, docs). 5 P2 review findings fixed in round 2, 1 P2 fix regression fixed in round 3. Reviews converged at round 3 (0 P1/P2).

### Implementation (Wave 1 + Wave 2)

- **bi3**: add directory pre-check and fix ambiguous file reference in pantry.md
- **yfnj**: inline Big Head Step 0a error return format in pantry.md Section 2
- **yb95**: remove deprecated pantry-review agent, stub Section 2, clean RULES.md rows
- **txw**: add failure artifact convention to Big Head skeleton
- **auas**: add input validation guards for REVIEW_ROUND, CHANGED_FILES, TASK_IDS
- **0gs**: replace glob patterns with exact timestamp placeholders in reviews.md error template
- **32gz**: add $RANDOM to SESSION_ID entropy to prevent same-second collision
- **033**: add pre-commit PII scrub hook documentation to installation guide
- **1b8**: fix uninstall path (~/.git/ -> .git/) and add pre-commit hook uninstall
- **7yv**: block commits when scrub-pii.sh missing/non-executable, chmod +x on install
- **z69**: make pre-push hook resilient to sync-to-claude.sh failures
- **cl8**: remove quote anchors from PII regexes to match unquoted occurrences
- **1e1**: complete "data file" -> "task brief" rename in skeleton and README
- **1y4**: verified already fixed (no changes needed)
- **27x**: remove Edit tool from big-head.md tools list (least-privilege)
- **9j6z**: verified already fixed (review-clarify -> review-clarity rename)
- **z3j**: define small-file threshold, guard DMVDC sampling formula, scope CCB bead list

### Review Fixes (Round 2)

- **4bna**: move scrub-pii.sh check inside staged-file guard (was blocking all commits)
- **yjrj**: scope PII scrub regex to owner/created_by fields only
- **l3d5**: add placeholder substitution validation guards at consumption points
- **88zh**: register {REVIEW_TIMESTAMP} in placeholder conventions
- **2gde**: replace dead GLOSSARY.md links with inline wave definition

### Review Fix (Round 3)

- **12u9**: add IF ROUND 1 markers to placeholder guard path list in reviews.md

### Review Statistics

| Round | Scope | P1 | P2 | P3 | Verdict |
|-------|-------|----|----|-----|---------|
| 1 | 14 files, 17 tasks | 0 | 5 | 16 | PASS WITH ISSUES |
| 2 | 7 files, 5 fix tasks | 0 | 1 | 0 | PASS WITH ISSUES |
| 3 | 1 file, 1 fix task | 0 | 0 | 1 | PASS |

21 review beads filed (round 1: 5 P2 + 15 P3; round 2: 1 P2; round 3: 1 P3 auto-filed to Future Work).

### Epics

- **ant-farm-753** (Verification & Checkpoints): closed (17/17 children)

## 2026-02-17 — Session 6ecb64 (Review Cycle)

### Review Summary

Code review of 6 tasks across 4 epics (d6k, 21d, 753, amk) from session 795d29.

- 72 raw findings from 4 Nitpicker reviewers (clarity, edge-cases, correctness, excellence)
- 40 root causes after Big Head deduplication (44% dedup rate)
- 1 P1, 6 P2, 33 P3

### Deferred P1

- **ant-farm-0mx**: PII scrub regression — `bd sync` (commit f455361) reverted the email scrub from task i0c (commit 047f1be). All records in `.beads/issues.jsonl` still contain owner email at HEAD. User decision: defer fix, document here.

### Epic Verdicts

| Epic | Verdict | Score |
|------|---------|-------|
| d6k (Setup & Forkability) | NEEDS WORK | 6.5/10 |
| 21d (Orchestration Reliability) | PASS WITH ISSUES | 9/10 |
| 753 (Review Pipeline Improvements) | PASS WITH ISSUES | 8/10 |
| amk (Documentation & Standards) | PASS | 7.5/10 |

### Tasks Completed (Session 795d29)

- **pq7**: fix: add mkdir -p guards and CLAUDE.md backup to sync script
- **4gi**: feat: add install-hooks.sh and document hook installation step
- **i0c**: fix: scrub owner email PII from issues.jsonl and document fork/init step
- **nr2**: fix: prevent silent task dropping with structured error metadata
- **z6r**: docs: clarify Big Head verification pipeline boundaries and add read confirmation
- **p33**: docs: add placeholder conventions canonical reference
