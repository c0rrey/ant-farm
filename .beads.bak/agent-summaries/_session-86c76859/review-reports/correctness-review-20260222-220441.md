# Report: Correctness Review

**Scope**: orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
**Reviewer**: Correctness Review / nitpicker (correctness-reviewer)
**Review round**: 1
**Commit range**: fb17de2..HEAD
**Task IDs reviewed**: ant-farm-q59z, ant-farm-vxcn, ant-farm-m4si

---

## Acceptance Criteria Summary

### ant-farm-q59z — Big Head CCB turn-based wait protocol

AC from `bd show`:
1. Big Head receives Pest Control's CCB verdict without timeout in a test session
2. No `sleep` calls used for message waiting in Big Head's workflow
3. No Queen intervention required to relay CCB verdicts
4. reviews.md Step 4 timeout protocol uses turn-count language, not wall-clock seconds
5. big-head-skeleton.md Step 10 explicitly instructs "end your turn" after sending to Pest Control

### ant-farm-vxcn — Pantry mandatory preview file output

AC from `bd show`:
1. Preview files are written before Pantry returns to Queen
2. CCO receives non-empty preview files on first Pantry run
3. Pantry halt/report if a preview file fails to write
4. No fabricated path returned for unwritten preview

### ant-farm-m4si — Rename tasks_approved to tasks_accepted

AC from `bd show`:
1. Progress log key at RULES.md:L116 no longer uses the word "approved"
2. The derivation of `<N>` (task count from briefing) is documented inline or in an adjacent comment
3. `parse-progress-log.sh` (if it parses `tasks_approved`) is updated to match the new key name

---

## Findings Catalog

### Finding 1: DEFERRED TO DRIFT-REVIEWER — stale "user approval" label in parse-progress-log.sh:80

- **File(s)**: `scripts/parse-progress-log.sh:80`
- **Severity**: P3
- **Category**: drift (deferred — see Cross-Review Messages)
- **Description**: During AC3 verification for ant-farm-m4si, I identified a stale "user approval" reference in the `SCOUT_COMPLETE` step label. Messaged drift-reviewer; they confirmed ownership and have filed it as Finding 6 in the drift report. Big Head should consolidate from drift-reviewer's report. This finding is retained here for traceability but is NOT counted in my statistics — drift-reviewer is the authoritative owner.
- **Suggested fix**: Owned by drift-reviewer.
- **Cross-reference**: Drift-reviewer confirmed ownership via team message.

### Finding 2: ant-farm-q59z AC1-5 — All acceptance criteria met

- **File(s)**: `orchestration/templates/big-head-skeleton.md:120-122`, `orchestration/templates/reviews.md:774-806`
- **Severity**: N/A (PASS)
- **Category**: correctness
- **Description**: Verified all 5 ACs:
  1. Turn-based protocol is documented — Big Head ends turn after SendMessage (no sleep); this is testable.
  2. No `sleep` language remains in either file; old "wait up to 60 seconds" language was fully replaced.
  3. Queen intervention is structurally eliminated by removing the sleep-based block.
  4. reviews.md now uses "2 subsequent turns" and "4 turns total" language — no wall-clock seconds remain.
  5. big-head-skeleton.md line 122 now reads "**End your turn** after sending to Pest Control. Do NOT sleep or poll".
- **Suggested fix**: None — all ACs satisfied.

### Finding 3: ant-farm-vxcn AC1-4 — All acceptance criteria met

- **File(s)**: `orchestration/templates/pantry.md:143-163, 210-213`
- **Severity**: N/A (PASS)
- **Category**: correctness
- **Description**: Verified all 4 ACs:
  1. "MANDATORY OUTPUT" header and "Pre-Step-4 verification" block both require preview files before returning.
  2. Immediate-write-and-verify instruction (step 3e) ensures CCO receives non-empty files on first run.
  3. `PREVIEW FAILED: {TASK_ID}` halt instruction is present at step 3e.
  4. Step 5 "MANDATORY" note says mark as `MISSING` rather than fabricate a path.
- **Suggested fix**: None — all ACs satisfied.

### Finding 4: ant-farm-m4si AC1-3 — All satisfied

- **File(s)**: `orchestration/RULES.md:116-117`
- **Severity**: N/A (PASS)
- **Category**: correctness
- **Description**:
  - AC1: `tasks_approved` no longer appears in RULES.md. The key is now `tasks_accepted`. Confirmed by grep — only occurrence of `tasks_approved` in the repo is in CHANGELOG.md (which is a historical record, not a live instruction).
  - AC2: Line 117 was added: "where `<N>` is the count of tasks in the briefing task list after SSV PASS (N=0 is not logged — it is caught by the zero-task guard earlier in Step 1b)." Derivation documented.
  - AC3: Script does not parse `tasks_approved` (it only checks for the presence of the `SCOUT_COMPLETE` step key), so no update was mechanically required. AC3 conditional is satisfied. A stale "user approval" label was identified at `scripts/parse-progress-log.sh:80` during this check; deferred to drift-reviewer (see Finding 1).
- **Suggested fix**: None — all ACs satisfied.

### Finding 5: Post-push sync check scope in RULES.md is broader than intended

- **File(s)**: `orchestration/RULES.md:365-371`
- **Severity**: P3
- **Category**: correctness
- **Description**: The diff for Step 6 adds a post-push sync check. The `diff -rq` command excludes `--exclude=scripts` and `--exclude=_archive` but does NOT exclude the `reference/` subdirectory. If `reference/` contains files that are intentionally different between the repo and `~/.claude/orchestration/` (e.g., session-specific or developer-local files), the diff will produce spurious warnings and trigger `sync-to-claude.sh` unnecessarily. This is a minor correctness risk — the exclusion list may be incomplete — but in the current project structure `reference/` contains only static files (`dependency-analysis.md`, `known-failures.md`) that should be synced, so it is not an active bug. The logic is correct for the current state; the risk is future drift if `reference/` grows.
- **Suggested fix**: No action required now. If `reference/` gains session-local files in the future, add `--exclude=reference` or a more targeted exclusion.

---

## Preliminary Groupings

### Group A: Stale label in parse-progress-log.sh (Finding 1 — deferred to drift-reviewer)

- Finding 1 — deferred; ownership confirmed by drift-reviewer. Not counted in my statistics.

### Group B: All three tasks fully landed (Findings 2, 3, 4)

- Findings 2, 3, 4 — acceptance criteria all satisfied
- No functional defects found in the implemented changes

### Group C: Post-push sync scope (Finding 5)

- Finding 5 — standalone; theoretical incompleteness in exclusion list
- Low risk given current project structure

---

## Summary Statistics

- Total findings (owned by this reviewer): 1 substantive finding (Finding 5); Finding 1 deferred to drift-reviewer
- By severity: P1: 0, P2: 0, P3: 1 (Finding 5)
- Preliminary groups: 2 (Group B — all tasks passed; Group C — post-push sync scope)

---

## Cross-Review Messages

### Sent

- To drift-reviewer: "Found stale 'user approval' label at scripts/parse-progress-log.sh:L80 — label references user-approval step removed in ant-farm-fomy. This is likely a drift issue (stale label from prior workflow change not propagated to this file). May want to flag."

### Received

- From drift-reviewer: "Confirmed drift-domain. scripts/parse-progress-log.sh:L80 stale label is drift — filed as Finding 6 in drift report. Drop your Finding 1 — Big Head will consolidate from drift report." — Action taken: dropped Finding 1 from my statistics; retained as deferred-to-drift entry for traceability.

### Deferred Items

- "Stale 'user approval' in parse-progress-log.sh:80 step label" — Deferred to drift-reviewer (confirmed ownership). Not counted in my totals.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/RULES.md` | Findings: #4, #5 (AC verification + post-push scope) | Lines 113-117 (tasks_accepted change), lines 361-374 (Step 6 post-push sync), full file read for AC verification |
| `orchestration/templates/big-head-skeleton.md` | Findings: #2 (AC verification — PASS) | Lines 119-125 (Step 9-10 turn protocol), full file read |
| `orchestration/templates/pantry.md` | Findings: #3 (AC verification — PASS) | Lines 140-163, 210-213 (preview mandatory block and Step 5 note), full file read |
| `orchestration/templates/reviews.md` | Findings: #2 (AC verification — PASS) | Lines 771-806 (Big Head Step 4 turn-based protocol), full file read |
| `scripts/parse-progress-log.sh` | Findings: #1 (stale label) | Line 80 (SCOUT_COMPLETE label references "user approval") — read as part of AC3 verification for ant-farm-m4si |

---

## Overall Assessment

**Score**: 9/10
**Verdict**: PASS WITH ISSUES

All three tasks (ant-farm-q59z, ant-farm-vxcn, ant-farm-m4si) landed their core logic correctly and satisfy their acceptance criteria. The one owned finding (Finding 5, P3) is a mildly incomplete exclusion list in the post-push sync check at `orchestration/RULES.md:365-371` — the `reference/` subdirectory is not excluded, but this is correct for the current project structure. A second finding (stale "user approval" label in `scripts/parse-progress-log.sh:80`) was identified and deferred to drift-reviewer, who confirmed ownership.
