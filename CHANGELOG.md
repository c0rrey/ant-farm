# Changelog

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
