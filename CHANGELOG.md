# Changelog

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
