# Edge Cases Review — Round 3
**Timestamp**: 20260220-173352
**Reviewer**: r3-edge-cases
**Commit range**: 5dba086~1..HEAD
**Commits reviewed**:
- `d6e4927` fix: update parse-progress-log.sh milestone keys to match RULES.md event names (ant-farm-fuje)
- `5dba086` fix: add explicit TIMESTAMP assignment to Step 3b-i (ant-farm-ovw8)

---

## Findings Catalog

### F1 — Stale old-format description at RULES.md:310

- **File:line**: `orchestration/RULES.md:310`
- **Severity**: P2
- **Category**: Cross-file contract inconsistency (runtime failure risk)
- **Description**: The Session Directory section documents the crash recovery script's exit-2 behavior using the old step key name:
  ```
  Exit 2: session already completed (step6 logged); no resume-plan written; proceed with fresh start
  ```
  The fix commit (d6e4927) updated the script's internal check from `map_has "completed" "step6"` to `map_has "completed" "SESSION_COMPLETE"`, and updated the header comment from `(step6 present)` to `(SESSION_COMPLETE present)`. However, line 310 of RULES.md — the Queen-facing documentation — was NOT updated. It still says `(step6 logged)`.

  **Runtime failure risk**: The Queen reads `RULES.md` and interprets this documentation when deciding how to handle exit code 2. The stale label is misleading — a Queen that reads this line may conclude the old `step6` key is what the script checks, which could cause confusion when reading a progress.log that uses the new `SESSION_COMPLETE` key. This does not cause a silent wrong result in normal operation (exit-2 path is not key-dependent), but it is a direct contract inconsistency between the fix's stated goal (aligning naming across script and docs) and what was actually updated.
- **Suggested fix**: Update `orchestration/RULES.md:310` from:
  ```
  - Exit 2: session already completed (step6 logged); no resume-plan written; proceed with fresh start
  ```
  to:
  ```
  - Exit 2: session already completed (SESSION_COMPLETE logged); no resume-plan written; proceed with fresh start
  ```

---

## Preliminary Groupings

### Group A — Incomplete rename across RULES.md (1 finding)
- F1: The fix updated all progress.log format examples (lines 59, 98, 115, 123, 190, 211, 214, 217, 220) and the script itself, but missed the crash recovery summary table in the Session Directory section (line 310). This is part of the same root cause as ant-farm-fuje: the old step numbering scheme appearing in documentation that should have been updated.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1       | 0     |
| P2       | 1     |
| P3       | 0     |
| **Total**| **1** |

---

## Cross-Review Messages

Messaging r3-correctness about F1 — the stale `step6` reference at RULES.md:310 is directly within the scope of task ant-farm-fuje (milestone key alignment), so correctness should verify whether the acceptance criterion for that task covers documentation prose in the Session Directory section, not just progress.log examples and the script itself.

---

## Coverage Log

| File | Issues Found | Notes |
|------|-------------|-------|
| `scripts/parse-progress-log.sh` | 0 | Fix landed correctly. All 9 STEP_KEYS match RULES.md progress.log examples exactly. The `_key_file` function is safe: new step keys are uppercase+underscore only, all valid as filenames. The `SESSION_COMPLETE` check at L177 is correct. The fallback at L198 (`RESUME_STEP="SESSION_COMPLETE"`) is correct. Comment at L127 updated correctly. |
| `orchestration/RULES.md` | 1 | F1: line 310 still uses old `step6` terminology in crash recovery exit-code docs. All 9 progress.log inline examples (lines 59, 98, 115, 123, 190, 211, 214, 217, 220) are correctly updated. Step 0 crash recovery procedure (lines 61-72) is correct. TIMESTAMP fix (lines 132-134) is correct. |

---

## Overall Assessment

**Score**: 8/10

**Verdict**: PASS WITH ISSUES

The two fix commits accomplished their primary goals:
1. `d6e4927` successfully updated all 9 step keys in `parse-progress-log.sh` from old numeric names to RULES.md-canonical event names. Script behavior is correct. All event keys now match RULES.md progress.log examples.
2. `5dba086` added the explicit `TIMESTAMP=$(date +%Y%m%d-%H%M%S)` assignment to Step 3b-i prose, which is the stated fix for ant-farm-ovw8.

One issue remains: the Session Directory section of RULES.md still documents exit code 2 with the old `step6` terminology (line 310). This is a P2 because it is a direct contract inconsistency left behind by the ant-farm-fuje fix, and it could mislead a developer or Queen reading this section.
