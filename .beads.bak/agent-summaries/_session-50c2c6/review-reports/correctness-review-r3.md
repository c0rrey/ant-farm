# Correctness Review — Round 3
**Reviewer**: correctness-nitpicker
**Date**: 2026-02-20
**Commit range**: 1b5c6d7..5c63877 (2 commits)
**Scope**: Fix verification only — 2 targeted fixes for round-2 P2 findings
**Files reviewed**: orchestration/RULES.md, orchestration/templates/checkpoints.md

---

## Summary

| Metric | Value |
|--------|-------|
| Files reviewed | 2 |
| Files with findings | 0 |
| P1 findings | 0 |
| P2 findings | 0 |
| P3 findings | 0 |
| Score | 10/10 |
| Verdict | PASS |

Both round-2 P2 findings are resolved. No regressions introduced.

---

## Fix Verification

### Fix 1: ant-farm-oj79 — Remove DMVDC from WARN block
**Round-2 finding**: `orchestration/templates/checkpoints.md:54,57` — WARN block incorrectly listed DMVDC as a WARN checkpoint. DMVDC uses PARTIAL, not WARN. The header `**WARN** (checkpoints: CCO, WWD, DMVDC only)` and bullet `- DMVDC WARN: Partial failures detected. Agent can repair and resubmit.` contradicted the PARTIAL definition at line 58-59 and the table entries at lines 69-71.

**Fix applied** (commit 1b5c6d7):
- Line 54: Header changed from `**WARN** (checkpoints: CCO, WWD, DMVDC only):` to `**WARN** (checkpoints: CCO, WWD only):`
- Line 57 (old): `- DMVDC WARN: Partial failures detected. Agent can repair and resubmit.` — deleted

**Verification**:
- `orchestration/templates/checkpoints.md:54` now reads: `**WARN** (checkpoints: CCO, WWD only):` — DMVDC removed from scope
- Grep for "DMVDC WARN" in checkpoints.md: no matches — stale bullet fully deleted
- PARTIAL definition at line 58 intact: `**PARTIAL** (DMVDC and CCB only): Some checks failed. Agent can repair and resubmit, or consolidation can be amended. Does not escalate to user.`
- Table entries at lines 69-71 still correctly use PARTIAL for DMVDC/CCB rows — unchanged by this fix
- WARN prose now lists only CCO and WWD — consistent with WARN definition throughout

**Result**: RESOLVED. No regressions.

---

### Fix 2: ant-farm-gy9p — Reorder round cap before fix-now decision
**Round-2 finding**: `orchestration/RULES.md:117-127` — Round cap block was positioned after the "fix now" action it was meant to prevent. A Queen running round 4 would read "fix now" before seeing the cap, allowing a round 5 to be spawned. The cap fired one round late.

**Fix applied** (commit 5c63877):
- Round cap block moved to immediately follow `**If P1 or P2 issues found**:` (line 117)
- Added `(check this FIRST before any fix decision)` label to cap header
- Condition changed to `If current round >= 4` (explicit comparison, no ambiguity about when cap fires)
- Added `**Only if current round < 4**: proceed with fix-now/defer decision:` gate before the fix/defer options
- Old sibling cap block (post-defer position) removed

**Verification** (`orchestration/RULES.md:117-127`):
```
**If P1 or P2 issues found**:
**Round cap — escalate after round 4** (check this FIRST before any fix decision):
- If current round >= 4 and P1/P2 findings are still present, do NOT start another round
- Present full round history to user (round numbers, finding counts, bead IDs)
- Ask user: "Review loop has not converged after 4 rounds. Continue or abort?"
- Await user decision before taking any further action
**Only if current round < 4**: proceed with fix-now/defer decision:
- Present findings to user: "Reviews found X P1 and Y P2 issues. Fix now or defer?"
- **If "fix now"**: Spawn fix tasks (see reviews.md), then re-run Step 3b with round N+1
  - Update session state: increment review round, record fix commit range
- **If "defer"**: P1/P2 beads stay open; document in CHANGELOG; proceed to Step 4
```
- Cap check is the first action after "If P1 or P2 issues found" — fires before any fix decision
- "check this FIRST" label makes priority explicit
- `current round >= 4` condition is unambiguous
- `**Only if current round < 4**` gate prevents fix-now from executing on round 4
- Single cap location (no duplicate) — removed old post-defer position
- Grep for "round cap" in RULES.md returns exactly one match at line 118 — no stale duplicate

**Result**: RESOLVED. No regressions.

---

## Coverage Log

| File | Reviewed | Findings |
|------|----------|----------|
| `orchestration/RULES.md` | YES | None |
| `orchestration/templates/checkpoints.md` | YES | None |

---

## Regression Checks

| Check | Result |
|-------|--------|
| No "DMVDC WARN" in checkpoints.md | PASS (grep: 0 matches) |
| PARTIAL definition intact at checkpoints.md:58 | PASS |
| Table rows use PARTIAL for DMVDC/CCB (lines 69-71) | PASS (unchanged) |
| Round cap is first item under "If P1 or P2 issues found" in RULES.md | PASS (line 118) |
| "Only if current round < 4" gate present before fix-defer options | PASS (line 123) |
| Single cap location in RULES.md (no stale duplicate) | PASS (grep: 1 match) |

---

## Final Verdict: PASS

Both round-2 P2 findings are fully resolved with no regressions. The correctness review loop can terminate.
