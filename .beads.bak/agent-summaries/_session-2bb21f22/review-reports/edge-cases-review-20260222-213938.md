# Edge Cases Review — Round 2 (Fix-Scope)
**Timestamp**: 20260222-213938
**Reviewer**: Edge Cases Nitpicker
**Commit range**: 29d1c0b^..HEAD
**Review round**: 2 — fix-scope only
**Files reviewed**: orchestration/RULES.md, orchestration/reference/dependency-analysis.md, orchestration/templates/checkpoints.md

---

## Fix Commits in Scope

- `29d1c0b` — docs: remove user-approval references from SSV and Scout pre-flight docs (ant-farm-or8q)
- `934ce51` — docs: add SSV guards, retry cap, and fix stale briefing.md descriptions (ant-farm-i7wl, ant-farm-sfe0)

---

## Findings Catalog

### R2-EC-01
**File**: `orchestration/RULES.md:100-101`
**Severity**: P3
**Category**: Missing input validation — zero-task guard trigger condition unspecified

**Description**:
The zero-task guard added in commit 934ce51 reads: "If the briefing's task count is 0, do NOT auto-proceed." However the guard does not specify how the Queen determines task count from `briefing.md`. The `briefing.md` file is Scout-authored; if its format is inconsistent (e.g., tasks listed under a header with no count field, or structured differently across Scout runs), the Queen has no defined extraction rule and could silently skip the guard by reading the count incorrectly.

This is a P3 because in practice the Scout writes a structured briefing that the Queen can parse visually, and a zero-task session is already an unlikely condition. However the guard as written depends on an implicit format contract that is not specified here or in the Scout's template.

**Suggested fix**: Add a note specifying how to read the count — e.g., "Task count is the number of tasks listed in the briefing's wave plan; if the briefing contains no wave plan section or lists zero tasks across all waves, treat as task count = 0."

---

### R2-EC-02
**File**: `orchestration/RULES.md:534`
**Severity**: P3
**Category**: Missing boundary condition — session retry counter interaction for new SSV row

**Description**:
The Retry Limits table counter interaction note (line 534) explicitly calls out CCB re-runs as counting toward the session total of 5. The new "SSV FAIL -> re-Scout cycle" row (line 530) is not mentioned in this counter interaction note. It is ambiguous whether a re-Scout after SSV FAIL consumes one of the 5 session-wide retry slots.

This is a pre-existing omission pattern (other rows like Pantry CCO fails, Scout fails, Scribe ESV are also unmentioned in the counter interaction note), so this is not a regression introduced by the fix — the new row follows the same omission pattern as existing rows. However the fix added the new row without addressing the gap in counter interaction coverage, leaving it equally ambiguous.

**Suggested fix**: Either extend the counter interaction note to cover all rows in the table, or explicitly state that only CCB is the exception (all others do count / do not count toward the session total).

---

## Preliminary Groupings

**Root Cause A — Implicit format contracts (R2-EC-01)**
The zero-task guard is behaviorally correct but depends on an unspecified format contract for how the Queen reads task count from briefing.md. The guard works in practice but is fragile to briefing format variation.

**Root Cause B — Counter interaction note not extended to new row (R2-EC-02)**
Pre-existing omission pattern; the new SSV FAIL retry row was added without updating the counter interaction note. Not a regression, but the gap persists.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1       | 0     |
| P2       | 0     |
| P3       | 2     |
| **Total**| **2** |

---

## Fixes Assessment

All three Round 1 P2 findings are addressed:

**EC-01 (zero-task briefing, P2)**: Fixed. The zero-task guard at `orchestration/RULES.md:100-101` explicitly blocks auto-proceed when task count is 0 and escalates to the user. The Queen Read Permissions entry at line 28 was also updated to confirm the Queen reads `briefing.md` after SSV PASS specifically to confirm task count. Consistent.

**EC-02 (SSV FAIL retry cap, P2)**: Fixed. The retry cap is specified in three consistent locations:
- Inline in Step 1b at `orchestration/RULES.md:104-106`: "maximum of 1 retry"
- Retry Limits table at `orchestration/RULES.md:530`: "SSV FAIL -> re-Scout cycle | 1 | Escalate to user with SSV violations"
- checkpoints.md SSV Queen's Response at line 729: "If SSV fails a second time, escalate to user"
All three agree. Fix is coherent.

**EC-03 (tasks_approved=<N> placeholder, P3)**: Partially addressed. The Queen Read Permissions bullet (line 28) now explains the Queen reads briefing.md after SSV PASS "to confirm task count before auto-proceeding to Step 2", which implicitly answers how `<N>` is derived. However the progress log line itself (line 116) still uses the literal `tasks_approved=<N>` placeholder without a derivation note. The fix addressed the spirit of the concern but not the letter. This is acceptable for a P3.

---

## Cross-Review Messages

**Sent**: None.

**Received**: None.

---

## Coverage Log

| File | Status | Findings |
|------|--------|----------|
| `orchestration/RULES.md` | Reviewed in full | R2-EC-01 (P3), R2-EC-02 (P3) |
| `orchestration/reference/dependency-analysis.md` | Reviewed in full | No issues found |
| `orchestration/templates/checkpoints.md` | Reviewed in full | No issues found |

### Notes on clean files

**`orchestration/reference/dependency-analysis.md`**: Line 64 updated from "presents strategy to user and waits for approval" to "auto-proceeds to SSV and then spawns Pantry on PASS". Change is accurate, no edge-case issues.

**`orchestration/templates/checkpoints.md`**: SSV verdict line 689 updated to "auto-proceed to spawn Pantry". SSV Queen's Response line 717 updated to remove user-approval requirement. FAIL procedure at lines 719-729 retains the 5-step escalation path including "if SSV fails a second time, escalate" at step 5 — consistent with the 1-retry cap in RULES.md. No edge-case issues introduced.

---

## Overall Assessment

**Score**: 9/10
**Verdict**: PASS

Both Round 1 P2 findings (zero-task guard, SSV FAIL retry cap) are correctly implemented and internally consistent across all three files. The Round 1 P3 (tasks_approved placeholder) is addressed in spirit. The two new P3s found in this round (R2-EC-01, R2-EC-02) are minor polish issues — neither would cause a runtime failure or silently wrong results in any realistic scenario. The fixes landed correctly and did not introduce regressions.
