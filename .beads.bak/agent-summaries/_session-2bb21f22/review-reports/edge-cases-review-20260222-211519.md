# Edge Cases Review — Round 1
**Timestamp**: 20260222-211519
**Reviewer**: Edge Cases Nitpicker
**Commit range**: 8af72c3^..HEAD
**Files reviewed**: orchestration/RULES.md

---

## Findings Catalog

### EC-01
**File**: `orchestration/RULES.md:97-99`
**Severity**: P2
**Category**: Missing boundary condition / unhandled state

**Description**:
The SSV PASS branch now auto-proceeds to Step 2 with no guard against a zero-task briefing. The retry table at line 524 handles "Scout fails or returns no tasks" with one retry, but that entry covers Scout agent failure — not the case where Scout succeeds (writes `briefing.md`) with a valid structure but selects zero tasks. In that scenario SSV would PASS (no file overlap, no intra-wave ordering violations, nothing to conflict) and the Queen would auto-proceed into a Pantry spawn with an empty task list, wasting a full Pantry + CCO cycle before the empty-task condition is surfaced.

Previously the user saw the briefing before approval and would have caught "zero tasks selected" immediately. That safety net is gone.

**Suggested fix**: Add an explicit check after SSV PASS: if the briefing's task count is 0, do not auto-proceed — escalate to the user with the zero-task briefing for review. This check belongs in Step 1b alongside the SSV PASS branch.

---

### EC-02
**File**: `orchestration/RULES.md:100-101`
**Severity**: P2
**Category**: Missing retry limit / potential infinite loop
**Note**: Pre-existing gap — the `On SSV FAIL` branch is unchanged in this diff. Confirmed with Correctness reviewer: no acceptance criterion in ant-farm-fomy requires a retry cap for this loop. Reported here because the gap is materially worsened by the change: previously the user could break an infinite SSV FAIL loop by refusing approval; that escape hatch is now gone.

**Description**:
The SSV FAIL branch reads: "Re-run Scout with the specific violations from the SSV report. After Scout revises `briefing.md`, re-run SSV." There is no retry cap for this Scout/SSV loop. The Retry Limits table (line 524) has an entry for "Scout fails or returns no tasks" (1 retry), but that entry does not clearly cover the SSV FAIL → re-run Scout → re-run SSV cycle. If the Scout repeatedly produces a briefing that fails SSV (e.g., persistent file overlap caused by the task set itself), the loop has no defined termination condition.

Before this change the user could break the loop by refusing approval. With auto-approval, the user has no visibility into or control over the loop until the Queen voluntarily escalates, which is not currently specified. The change did not introduce the gap but did remove the only existing escape hatch for it.

**Suggested fix**: Add an explicit cap to the SSV FAIL → re-Scout loop (e.g., 1 retry, matching the Scout retry limit), and specify the escalation action: "After N retries, surface the SSV violations to the user and await instruction." This cap should be referenced in or reconciled with the Retry Limits table.

---

### EC-03
**File**: `orchestration/RULES.md:111`
**Severity**: P3
**Category**: Missing input validation — placeholder in progress log

**Description**:
The progress log line uses `tasks_approved=<N>` where `<N>` is a literal placeholder. In the previous wording this was "tasks approved by the user" — a concrete count from an explicit approval step. With auto-approval there is no discrete approval event from which to derive N. The Queen must now infer N from the briefing content. If the briefing format is irregular (empty tasks section, malformed counts), `<N>` could be left unresolved or silently become `0`, making the progress log entry misleading for crash-recovery purposes.

This is a documentation/instrumentation concern rather than a runtime crash risk, hence P3.

**Suggested fix**: Specify exactly how `<N>` is populated (e.g., "count of tasks in the briefing's task list after SSV PASS") and whether a `0` value should block proceeding.

---

## Preliminary Groupings

**Root Cause A — Loss of human checkpoint as defensive boundary (EC-01, EC-02)**
The user-approval gate was the only path by which a user could observe and interrupt a problematic-but-SSV-passing briefing (zero tasks, persistent SSV failures). Both findings stem from the same root cause: the change removes a human checkpoint without specifying automated equivalents for the edge conditions it previously handled implicitly.

**Root Cause B — Instrumentation gap under auto-approval (EC-03)**
The progress log placeholder `<N>` was previously resolved by an explicit approval event. Under auto-approval the derivation of N is unspecified. This is a lower-impact gap that only affects crash recovery and audit logging.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1       | 0     |
| P2       | 2     |
| P3       | 1     |
| **Total**| **3** |

---

## Cross-Review Messages

**Sent**: Message to Correctness reviewer — "Logic at `orchestration/RULES.md:100-101` may not satisfy acceptance criterion for retry-loop termination (ant-farm-fomy) — check bd show ant-farm-fomy to verify whether the acceptance criteria require a retry cap for the SSV FAIL loop."

**Received**: From Correctness reviewer — "Checked ant-farm-fomy acceptance criteria: none of the three ACs require a retry cap for the SSV FAIL loop. The On SSV FAIL branch is unchanged in the diff. Pre-existing gap, not in scope for correctness review. Deferred to Edge Cases to report if warranted." EC-02 retained as a pre-existing gap materially worsened by the removal of the user-approval escape hatch; note added to finding.

---

## Coverage Log

| File | Status | Findings |
|------|--------|----------|
| `orchestration/RULES.md` | Reviewed in full | EC-01 (P2), EC-02 (P2), EC-03 (P3) |

---

## Overall Assessment

**Score**: 7/10
**Verdict**: PASS WITH ISSUES

The change is directionally sound — SSV is a mechanical gate and auto-proceeding on PASS eliminates unnecessary user friction for well-structured sessions. However, two P2 gaps appear in the removed human checkpoint's responsibilities: (1) zero-task briefing detection, and (2) SSV FAIL loop termination. Neither is a crash risk in isolation, but together they could cause a session to silently spin or consume resources on an empty/broken task set without surfacing to the user until far downstream. Neither is a P1 because the downstream gates (Pantry CCO, DMVDC) will eventually catch scope problems — they just do so later and more expensively than a guard at Step 1b would.

The P3 instrumentation gap (EC-03) is low-risk but should be clarified to keep crash-recovery reliable.
