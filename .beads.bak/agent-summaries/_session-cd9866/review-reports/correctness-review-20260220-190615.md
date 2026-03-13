# Report: Correctness Review

**Scope**: agents/big-head.md, docs/installation-guide.md, orchestration/_archive/pantry-review.md, orchestration/PLACEHOLDER_CONVENTIONS.md, orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/checkpoints.md, orchestration/templates/dirt-pusher-skeleton.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md, README.md, scripts/install-hooks.sh, scripts/scrub-pii.sh
**Reviewer**: Correctness Review (nitpicker)
**Commit range**: f9ad7d9..HEAD
**Review round**: 1

---

## Findings Catalog

### Finding 1: ant-farm-bi3 AC#4 lost when Section 2 deprecated

- **File(s)**: orchestration/templates/pantry.md (entire Section 2 body), orchestration/RULES.md:132
- **Severity**: P2
- **Category**: correctness
- **Description**: Task ant-farm-bi3 AC#4 required introducing `{REVIEW_TIMESTAMP}` as a canonical named placeholder for the review timestamp. The placeholder was added in commit d37419e to pantry.md Section 2's body ("Input from the Queen" line and "Use Timestamp" step). However, commit 05ba029 (ant-farm-yb95) removed Section 2's body entirely, taking `{REVIEW_TIMESTAMP}` with it. The placeholder now exists nowhere in the codebase. RULES.md uses a bare `TIMESTAMP` shell variable at line 132 (`TIMESTAMP=$(date +%Y%m%d-%H%M%S)`), but this is not the Tier 1 `{REVIEW_TIMESTAMP}` named placeholder that the acceptance criterion called for. The intent of AC#4 — giving the review timestamp a canonical placeholder name — is not satisfied in the final state.
- **Suggested fix**: Either (a) add `{REVIEW_TIMESTAMP}` to the PLACEHOLDER_CONVENTIONS.md audit table and reference it in RULES.md Step 3b-i where TIMESTAMP is generated, or (b) explicitly acknowledge in ant-farm-bi3 close notes that AC#4 was superseded by the Section 2 removal. If the intent was simply "give the timestamp a name," then documenting that the shell variable `TIMESTAMP` serves this role in RULES.md suffices — but it should be noted in the bead closure, not silently dropped.
- **Cross-reference**: Correctness domain (acceptance criterion gap). Not an edge case issue.

### Finding 2: ant-farm-1y4 fix pre-dates review commit range

- **File(s)**: orchestration/SETUP.md (not in git diff f9ad7d9..HEAD)
- **Severity**: P3
- **Category**: correctness
- **Description**: Task ant-farm-1y4 ("SETUP.md hardcoded personal path ~/projects/hs_website/ blocks new adopters") is included in the task IDs list for this review cycle. However, the fix for ant-farm-1y4 was committed in `c238ed6 fix: use relative paths instead of hardcoded home directory in SETUP.md`, which predates the review range start (`f9ad7d9`). SETUP.md is not in the `git diff f9ad7d9..HEAD` output. The acceptance criteria for ant-farm-1y4 ("no personal machine paths in documentation", "step executable by new adopter") cannot be verified from the current review scope. The task is closed but its verification falls in a prior session. The bead inclusion in this cycle's task IDs is a scout/pantry planning artifact — not a runtime failure — but it means this reviewer cannot confirm AC compliance for this task.
- **Suggested fix**: When compiling task IDs for review, exclude tasks whose fix commits pre-date the session's first commit. The Scout should compare fix commit timestamps against session start to avoid including out-of-scope tasks.
- **Cross-reference**: No cross-review message needed — this is a planning/scoping inconsistency, not a code logic error.

### Finding 3: PLACEHOLDER_CONVENTIONS.md example missing pc and summaries subdirs

- **File(s)**: orchestration/PLACEHOLDER_CONVENTIONS.md:88-91
- **Severity**: P3
- **Category**: correctness — DEFERRED TO CLARITY
- **Description**: The Tier 3 usage pattern example at lines 88-91 shows `mkdir -p ${SESSION_DIR}/{task-metadata,previews,prompts}`, but RULES.md:312 shows the authoritative command as `mkdir -p ${SESSION_DIR}/{task-metadata,previews,prompts,pc,summaries}`. The example omits `pc` and `summaries` subdirectories. Stale documentation inconsistency.
- **Deferred**: clarity-reviewer took ownership; filed as their Finding 12. No double-filing.

### Finding 5: Installation guide documents pre-fix "silent skip" behavior for missing scrub script

- **File(s)**: docs/installation-guide.md:47, scripts/install-hooks.sh:74-77
- **Severity**: P2
- **Category**: correctness
- **Description**: `docs/installation-guide.md:47` states that the pre-commit hook "Skips silently if `scrub-pii.sh` is not found or not executable." This was the pre-fix behavior that ant-farm-7yv was specifically created to eliminate. The fix (commit 769369c) changed the hook to block the commit with `exit 1` and an error message: `[ant-farm] ERROR: scrub-pii.sh not found or not executable — cannot scrub PII. Commit blocked.` The documentation was not updated to reflect this behavioral change. A developer reading the guide will expect silent permissiveness but encounter a commit-blocking error in practice. This is a correctness gap: the documented behavior contradicts the implemented (and intentionally correct) behavior.
- **Suggested fix**: Change `docs/installation-guide.md:47` from "Skips silently if `scrub-pii.sh` is not found or not executable" to "Blocks the commit with an error if `scrub-pii.sh` is not found or not executable — this is intentional to prevent PII from entering git history."
- **Cross-reference**: Flagged by clarity-reviewer as P2 clarity (misleading docs). Correctness angle confirmed: the blocking behavior is correct per ant-farm-7yv AC#1; the docs are wrong. Ownership: correctness reviewer files; clarity reviewer defers.

### Finding 4: PLACEHOLDER_CONVENTIONS.md audit table misclassifies RULES.md ${SESSION_DIR} in gates table

- **File(s)**: orchestration/PLACEHOLDER_CONVENTIONS.md:104, orchestration/RULES.md:248-253
- **Severity**: P3
- **Category**: correctness — DEFERRED TO CLARITY
- **Description**: The audit table row for `RULES.md` (line 104) classifies `${SESSION_DIR}` in the Hard Gates artifact column as Tier 1, but it appears in markdown prose (not a code block), technically violating the Tier 3 convention. The audit table claims PASS without flagging this dual-tier usage.
- **Deferred**: clarity-reviewer took ownership; filed as their Finding 13. No double-filing.

---

## Preliminary Groupings

### Group A: Acceptance Criteria Compliance Gaps
- Finding 1 — ant-farm-bi3 AC#4 (`{REVIEW_TIMESTAMP}` placeholder) was introduced but then deleted by a subsequent commit in the same session.
- Finding 5 — ant-farm-7yv fix changed hook behavior to blocking, but docs/installation-guide.md:47 still documents the old silent-skip behavior.
- **Root cause**: In both cases, a fix commit changed implementation behavior but a related file (pantry.md Section 2 / installation-guide.md) was not updated to stay consistent with the new state. Finding 1: two tasks had overlapping scopes — bi3 added content to Section 2, yb95 removed Section 2's body, net-zero for AC#4. Finding 5: the installation guide's hook behavior description was not revised when the silent-skip was intentionally changed to a blocking error.
- **Suggested combined fix for Finding 1**: Re-introduce `{REVIEW_TIMESTAMP}` in an appropriate location (e.g., RULES.md Step 3b-i documentation, or PLACEHOLDER_CONVENTIONS.md term table). **For Finding 5**: Update installation-guide.md:47 to describe the blocking behavior.

### Group B: Documentation-as-Specification Inconsistency (examples vs authoritative) — DEFERRED TO CLARITY
- Finding 3 — PLACEHOLDER_CONVENTIONS.md example missing `pc` and `summaries` subdirs (clarity Finding 12)
- Finding 4 — PLACEHOLDER_CONVENTIONS.md misclassifies `${SESSION_DIR}` tier in gates table (clarity Finding 13)
- **Root cause**: PLACEHOLDER_CONVENTIONS.md was updated in this session to fix the SESSION_ID formula but surrounding examples and audit table were not refreshed. Clarity reviewer owns these; Big Head will consolidate under the clarity domain.

### Group C: Task ID Scope Inconsistency (planning artifact)
- Finding 2 — ant-farm-1y4 fix pre-dates the review range
- **Root cause**: The review task ID list may not have been filtered to exclude tasks whose fix commits pre-date the session's first commit. This is a scout/pantry planning issue, not a code correctness bug.

---

## Summary Statistics
- Total findings: 5
- By severity: P1: 0, P2: 2, P3: 3
- Preliminary groups: 3

---

## Cross-Review Messages

### Sent
- To clarity-reviewer: "Found documentation inconsistency in orchestration/PLACEHOLDER_CONVENTIONS.md:88-91 and :104 — example mkdir command is missing pc and summaries subdirs (vs RULES.md:312), and the RULES.md gate table row may have a tier classification issue. May also be clarity/consistency finding — your call whether to report separately."

### Received
- From clarity-reviewer: "docs/installation-guide.md:47 documents 'skips silently' behavior but install-hooks.sh:74-77 blocks with exit 1 — behavioral mismatch, correctness angle belongs to correctness reviewer." — Action taken: Verified the mismatch, confirmed blocking is the correct behavior per ant-farm-7yv AC#1, added as Finding 5 (P2).
- From clarity-reviewer: "Taking ownership of both PLACEHOLDER_CONVENTIONS.md findings — stale mkdir example (Finding 12) and audit table PASS claim (Finding 13). Please note as deferred in your report." — Action taken: Updated Findings 3 and 4 to DEFERRED TO CLARITY status. No double-filing.

### Deferred Items
- Finding 3 (PLACEHOLDER_CONVENTIONS.md:88-91 stale mkdir example) — Deferred to clarity-reviewer (their Finding 12). Root cause is a stale documentation example, better classified under clarity/consistency.
- Finding 4 (PLACEHOLDER_CONVENTIONS.md:104 tier misclassification) — Deferred to clarity-reviewer (their Finding 13). Root cause is an audit table consistency issue, better classified under clarity.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `agents/big-head.md` | Reviewed — no issues | 36 lines, 1 function (agent definition). Verified Edit tool removed from tools list (ant-farm-27x AC MET). No correctness issues. |
| `docs/installation-guide.md` | Findings: #5 | ~407 lines. Both hooks documented (ant-farm-033 AC MET). Uninstall paths use `.git/hooks/` not `~/.git/` (ant-farm-1b8 AC MET). pre-commit.bak mentioned (ant-farm-033 AC#2 MET). Line 47 documents old silent-skip behavior instead of new blocking behavior (Finding 5, P2). |
| `orchestration/_archive/pantry-review.md` | Reviewed — no issues | 74 lines. DEPRECATED notice present (ant-farm-yb95 AC MET). Retained as fallback reference. |
| `orchestration/PLACEHOLDER_CONVENTIONS.md` | Findings: #3, #4 (both deferred to clarity) | ~232 lines. Audit table updated for new SESSION_ID formula. Two inconsistencies noted and flagged to clarity-reviewer (stale mkdir example, gates table tier classification). Both deferred — clarity-reviewer filed as their Findings 12 and 13. |
| `orchestration/RULES.md` | Reviewed — no issues | ~420 lines. REVIEW_ROUND, CHANGED_FILES, TASK_IDS guards added (ant-farm-auas AC MET). SESSION_ID formula updated with $RANDOM (ant-farm-32gz AC MET). Crash recovery, SSV, wave pipelining all intact. |
| `orchestration/templates/big-head-skeleton.md` | Reviewed — no issues | 126 lines. Failure artifact convention documented at lines 77-86 (ant-farm-txw AC MET). Polling loop uses exact timestamp placeholders not globs (ant-farm-0gs). Big Head data file renamed to consolidation brief. |
| `orchestration/templates/checkpoints.md` | Reviewed — no issues | ~715 lines. small-file threshold defined as <100 lines (ant-farm-z3j AC#1 MET). DMVDC sampling formula corrected to min(N, max(3, min(5, ceil(N/3)))) (ant-farm-z3j AC#2 MET). CCB Check 7 scoped with --after={SESSION_START_DATE} (ant-farm-z3j AC#3 MET). |
| `orchestration/templates/dirt-pusher-skeleton.md` | Reviewed — no issues | 48 lines. No "data file" references to Pantry output remain (ant-farm-1e1 AC MET). |
| `orchestration/templates/nitpicker-skeleton.md` | Reviewed — no issues | 44 lines. No correctness issues found. {REVIEW_ROUND} placeholder present. |
| `orchestration/templates/pantry.md` | Findings: #1 | ~285 lines. FAIL-FAST pre-check for task-metadata dir added (ant-farm-bi3 AC#1 MET). Ambiguous "Read this file" fixed (ant-farm-bi3 AC#3 MET). Section 2 DEPRECATED and body removed (ant-farm-yb95). {REVIEW_TIMESTAMP} placeholder introduced then removed (ant-farm-bi3 AC#4 unmet). |
| `orchestration/templates/reviews.md` | Reviewed — no issues | ~891 lines. Step 0/0a polling loop uses exact paths with no globs (ant-farm-0gs AC MET). Fallback workflow filename corrected from review-clarify.md to review-clarity.md (ant-farm-9j6z AC MET). |
| `README.md` | Reviewed — no issues | ~333 lines. pantry-review DEPRECATED in agent table (ant-farm-yb95 AC MET). No Pantry "data file" references remaining (ant-farm-1e1 AC MET). Both hooks documented in architecture description. |
| `scripts/install-hooks.sh` | Reviewed — no issues | 99 lines. Pre-commit hook exits 1 (not 0) when scrub-pii.sh missing/non-executable (ant-farm-7yv AC#1 MET). chmod +x scrub-pii.sh added at lines 92-98 (ant-farm-7yv AC#2 MET). Pre-push hook wraps sync in error handler — sync failure is warning, not blocker (ant-farm-z69 AC#1 MET). |
| `scripts/scrub-pii.sh` | Reviewed — no issues | 59 lines. PII_PATTERN and post-scrub verification patterns do NOT use quote anchors — they match emails regardless of quoting context (ant-farm-cl8 AC MET). |

---

## Overall Assessment
**Score**: 7/10
**Verdict**: PASS WITH ISSUES

Two P2 correctness gaps were found, both in the "documentation not updated to match code change" category:

1. **Finding 1** (ant-farm-bi3 AC#4): `{REVIEW_TIMESTAMP}` placeholder introduced in one commit then silently removed by a subsequent commit in the same session. The PLACEHOLDER_CONVENTIONS system has a named-placeholder gap.

2. **Finding 5** (ant-farm-7yv doc gap): `docs/installation-guide.md:47` still says the hook "skips silently" when scrub-pii.sh is missing — the pre-fix behavior. The actual hook now blocks with exit 1. A developer reading the guide will be surprised by a commit-blocking error. The code is correct; the docs lag behind.

Three additional P3 documentation inconsistencies were found in PLACEHOLDER_CONVENTIONS.md (stale example, tier classification ambiguity) and a task ID scoping artifact. No P1 findings. All scripts, logic gates, guards, and acceptance criteria for 15 of 17 tasks are verified correct.
