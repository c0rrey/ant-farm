# Edge Cases Review Report
**Round**: 2
**Timestamp**: 20260220-172051
**Reviewer**: Edge Cases Nitpicker
**Commit range**: 21138d4~1..HEAD
**Fix commits reviewed**:
- `41a9319` fix: replace bash 4+ declare -A with POSIX-compatible constructs (ant-farm-35wk)
- `3bdee83` fix: correct progress log filename, TIMESTAMP ref, and milestone naming (ant-farm-purh, ant-farm-yf5p, ant-farm-nq4f)
- `21138d4` fix: clarify SSV PASS requires user approval by design (ant-farm-dxw2)

---

## Findings Catalog

### F1 — scripts/parse-progress-log.sh: STEP_KEYS array still uses old step key names; crash recovery broken for all new-format sessions

**File**: `scripts/parse-progress-log.sh`
**Lines**: 62–71, 177, 197–198
**Severity**: P1
**Category**: Contract break — RULES.md and parse-progress-log.sh use different step key names after fix commit 3bdee83

**Description**:
Commit `3bdee83` renamed all progress log step keys in RULES.md from positional names (`step0`, `step1`, `step2`, `step3`, `step3b`, `step3c`, `step4`, `step5`, `step6`) to descriptive names (`SESSION_INIT`, `SCOUT_COMPLETE`, `WAVE_SPAWNED`, `WAVE_VERIFIED`, `REVIEW_COMPLETE`, `REVIEW_TRIAGED`, `DOCS_COMMITTED`, `XREF_VERIFIED`, `SESSION_COMPLETE`).

However, `scripts/parse-progress-log.sh` was NOT updated in commit `41a9319`. The script's `STEP_KEYS` array (lines 62–71) still contains:
```bash
STEP_KEYS=(
    "step0"
    "step1"
    "step2"
    "step3"
    "step3b"
    "step3c"
    "step4"
    "step5"
    "step6"
)
```

And the completion check at line 177 still looks for `"step6"`:
```bash
if map_has "completed" "step6"; then
```

The actual log written by the new RULES.md will use `SESSION_COMPLETE` at step 6, not `step6`. The map will never find `step6`, so the check at line 177 will always be false.

**Consequence** (runtime failure, verified by test):
1. A fully completed session (all 9 milestones logged with new key names, including `SESSION_COMPLETE`) returns **exit 0** instead of **exit 2**. The Queen is told the session needs recovery when it is already done.
2. The resume plan shows every step as `pending` and `RESUME HERE` at Step 0, because none of the new key names match any entry in `STEP_KEYS`.
3. The Queen would present this incorrect resume plan to the user, causing unnecessary confusion and possibly re-running an already-completed session.

This was confirmed by running the script against a synthetic progress.log with all new-format keys — exit code was 0, resume point was Step 0.

**Suggested fix**: Update `scripts/parse-progress-log.sh` to match the new key names used in RULES.md:
- `STEP_KEYS` array: replace with `("SESSION_INIT" "SCOUT_COMPLETE" "WAVE_SPAWNED" "WAVE_VERIFIED" "REVIEW_COMPLETE" "REVIEW_TRIAGED" "DOCS_COMMITTED" "XREF_VERIFIED" "SESSION_COMPLETE")`
- `map_has "completed" "step6"` → `map_has "completed" "SESSION_COMPLETE"` (line 177)
- `RESUME_STEP="step6"` (line 198) → `RESUME_STEP="SESSION_COMPLETE"` (the fallback when all but the last step are done)
- `step_label()` and `step_resume_action()` case statements: rename all keys to match new names

Note: old-format sessions (written by RULES.md before fix commit 3bdee83) correctly return exit 2 because the old `step6` key is still checked. The breakage is one-directional — new sessions are broken, old sessions still work.

---

### F2 — scripts/parse-progress-log.sh:196–198: Fallback RESUME_STEP uses the wrong key after STEP_KEYS rename

**File**: `scripts/parse-progress-log.sh`
**Lines**: 196–198
**Severity**: P1 (shares root cause with F1)
**Category**: Logic error — part of the same key-mismatch introduced by the incomplete fix

**Description**:
The fallback case at line 196–198 is reached when every key in `STEP_KEYS` is found completed but `RESUME_STEP` was not set in the loop:
```bash
# If every step except step6 is done but step6 is absent, resume at step6
if [ -z "$RESUME_STEP" ]; then
    RESUME_STEP="step6"
fi
```
Since `STEP_KEYS` no longer contains `SESSION_COMPLETE` (the new last step), this branch is unreachable via normal flow. However, if `STEP_KEYS` were updated (F1 fix), then after all new-format keys appear in the map, `RESUME_STEP` would be empty and the fallback would set it to `"step6"` — which no longer exists in `step_label()` or `step_resume_action()`, causing those functions to fall through to the `*) echo "$1"` default.

**Suggested fix**: Update the fallback to `RESUME_STEP="SESSION_COMPLETE"` when F1 is addressed.

*Note*: This is listed as a separate finding for traceability but has the same root cause as F1 — it can be resolved in the same change.

---

## Preliminary Groupings

**Root cause A — Incomplete cross-file update when renaming progress log keys (F1, F2)**:
Commit `3bdee83` updated only `orchestration/RULES.md` with new step key names. The `scripts/parse-progress-log.sh` consumer of these keys was not updated in the same commit or in the companion POSIX-fix commit (`41a9319`). The fix was incomplete because the two files that form a contract (RULES.md writes progress.log; parse-progress-log.sh reads it) were not updated atomically.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1       | 2     |
| P2       | 0     |
| P3       | 0     |
| **Total** | **2** |

Both P1 findings share a single root cause and will be resolved by a single change.

---

## Cross-Review Messages

None sent. The root cause is an edge-case / contract-break (missing input: the script can never receive the new key names it needs to recognize). No findings were referred to other reviewers.

---

## Coverage Log

| File | Status |
|------|--------|
| `orchestration/RULES.md` | Reviewed — no runtime issues. Fix commit 3bdee83 correctly renamed progress log milestone keys. The RULES.md side of the contract is correct. No issues found in this file. |
| `orchestration/templates/checkpoints.md` | Reviewed — no issues. Fix commit 21138d4 added clarifying text to the SSV PASS verdict and Queen's response section. The added text does not change any conditional logic or boundary behavior. No edge cases introduced. |
| `scripts/parse-progress-log.sh` | Reviewed — **P1 findings F1 and F2**. POSIX-compatibility fix (commit 41a9319) is mechanically correct (map semantics, cleanup trap, `printf '%s'` safety, macOS `mktemp -d` compatibility all verified). However, the STEP_KEYS array and the `step6` completion check were not updated to match the renamed keys from RULES.md commit 3bdee83. |

---

## Overall Assessment

**Score**: 4/10

**Verdict**: NEEDS WORK

The POSIX associative-map replacement in `parse-progress-log.sh` (commit 41a9319) is technically correct — the map semantics, cleanup trap, and filename-based key storage all work as intended on macOS. The SSV PASS clarification (commit 21138d4) is a documentation-only addition with no behavioral edge cases.

However, the progress-log key rename in `orchestration/RULES.md` (commit 3bdee83) introduced a cross-file contract break that was not caught: the script that parses the progress log still expects the old key names. This renders crash recovery completely non-functional for any session started after the rename — a fully completed session will be reported as needing Step 0 resume. This is a runtime failure that would silently corrupt the Queen's understanding of session state, so it merits P1 priority.
