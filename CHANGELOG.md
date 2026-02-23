# Changelog

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
