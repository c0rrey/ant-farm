# Correctness Review — Round 2

**Reviewer**: Correctness
**Round**: 2 (fix commits only)
**Commit range**: 21138d4~1..HEAD
**Timestamp**: 20260220-172051

**Fix commits in scope**:
- `41a9319` — fix: replace bash 4+ declare -A with POSIX-compatible constructs (ant-farm-35wk)
- `3bdee83` — fix: correct progress log filename, TIMESTAMP ref, and milestone naming (ant-farm-purh, ant-farm-yf5p, ant-farm-nq4f)
- `21138d4` — fix: clarify SSV PASS requires user approval by design (ant-farm-dxw2)

---

## Findings Catalog

### F-1 · P1 · Correctness — STEP_KEYS and completion check still use old step-numbered keys after milestone rename

**File:line**: `scripts/parse-progress-log.sh:62-72` (STEP_KEYS array), `scripts/parse-progress-log.sh:177` (step6 completion check), `scripts/parse-progress-log.sh:198` (RESUME_STEP fallback)

**Severity**: P1 — The crash recovery function is completely broken. Progress logs written by RULES.md (after ant-farm-nq4f) will never match the keys the script looks for.

**Description**: The ant-farm-nq4f fix updated RULES.md to emit event-named milestone keys (`SESSION_INIT`, `SCOUT_COMPLETE`, `WAVE_SPAWNED`, `WAVE_VERIFIED`, `REVIEW_COMPLETE`, `REVIEW_TRIAGED`, `DOCS_COMMITTED`, `XREF_VERIFIED`, `SESSION_COMPLETE`) but did NOT update `parse-progress-log.sh`. The script still:

1. Defines `STEP_KEYS` as `("step0" "step1" "step2" "step3" "step3b" "step3c" "step4" "step5" "step6")` — none of these strings will ever appear in a progress log written by the updated RULES.md.
2. Checks `map_has "completed" "step6"` to detect session completion (line 177), but RULES.md now emits `SESSION_COMPLETE` — this check will never fire, so a completed session will always be treated as incomplete (exit 0 with a spurious resume plan instead of the correct exit 2).
3. Falls back `RESUME_STEP="step6"` (line 198) — a key that no longer exists in any progress log.
4. `step_label()` and `step_resume_action()` case statements only handle `step0`-`step6`; all new event-named keys fall through to the `*` catchall, producing degraded output.

The POSIX compatibility fix (ant-farm-35wk) is correct and complete. The milestone rename (ant-farm-nq4f) is half-applied: RULES.md was updated but the script was not.

**Impact**: Any crash recovery attempt on a session started after this fix will: (a) never detect session completion correctly, (b) always report all steps as pending and resume at step 0, (c) present meaningless resume step labels.

**Suggested fix**: Update `parse-progress-log.sh` to match the new milestone naming:
- Replace `STEP_KEYS` with the event-named keys in progress order: `SESSION_INIT SCOUT_COMPLETE WAVE_SPAWNED WAVE_VERIFIED REVIEW_COMPLETE REVIEW_TRIAGED DOCS_COMMITTED XREF_VERIFIED SESSION_COMPLETE`
- Update the `step6` completion check (line 177) to use `SESSION_COMPLETE`
- Update the `step_label()` and `step_resume_action()` case statements to map event names to human labels
- Update the fallback on line 198 from `"step6"` to `"SESSION_COMPLETE"`

---

### F-2 · P2 · Correctness — ant-farm-yf5p acceptance criterion 1 not fully met: Step 3b-i still does not show an explicit TIMESTAMP assignment

**File:line**: `orchestration/RULES.md:132`

**Severity**: P2 — The fix is functional (the comment in Step 3b-v at line 166 conveys the intent), but the acceptance criterion is not technically met.

**Description**: ant-farm-yf5p acceptance criterion 1 states: "Step 3b-i explicitly assigns timestamp to a named variable." The fix added a comment at line 166 in Step 3b-v: `# TIMESTAMP was assigned at the start of Step 3b-i: TIMESTAMP=$(date +%Y%m%d-%H%M%S)`. However, Step 3b-i at line 132 still reads:

> Timestamp: The Queen generates ONE timestamp at the start of Step 3b using `date +%Y%m%d-%H%M%S` format (YYYYMMDD-HHMMSS)

This is prose instruction, not an explicit variable assignment. The acceptance criterion asks for explicit assignment in 3b-i. A reader following 3b-i could still miss that they need to assign it to `TIMESTAMP` — they know the format but not the variable name. The comment in 3b-v tells them the answer, but requires reading ahead to 3b-v to discover it.

**Suggested fix**: Update line 132 to include a concrete variable assignment example:

```
- Timestamp: `TIMESTAMP=$(date +%Y%m%d-%H%M%S)` — assign this at the start of Step 3b-i; used in 3b-v and the progress log.
```

---

### F-3 · P3 · Correctness — Progress log comment on line 157-158 still refers to "Multi-occurrence steps (step2, step3, step3b, step3c)" by old names

**File:line**: `scripts/parse-progress-log.sh:157-158`

**Severity**: P3 — Comment only; no runtime impact.

**Description**: The comment block says:
> `# Multi-occurrence steps (step2, step3, step3b, step3c) may appear multiple times (one per wave/round).`

After the ant-farm-nq4f rename, the equivalent multi-occurrence keys are `WAVE_SPAWNED`, `WAVE_VERIFIED`, `REVIEW_COMPLETE`, and `REVIEW_TRIAGED`. The comment still references the old step-numbered names.

**Suggested fix**: Update the comment to list the new event-named keys.

---

## Preliminary Groupings

**Root cause A — Half-applied milestone rename (F-1, F-3)**
ant-farm-nq4f updated RULES.md but did not propagate the new milestone key names into `parse-progress-log.sh`. F-1 (the STEP_KEYS array and completion check) is the blocking failure. F-3 (the comment) is a cosmetic residue of the same root cause.

**Root cause B — TIMESTAMP variable assignment not explicit in 3b-i (F-2)**
The ant-farm-yf5p fix conveyed the intent via a comment in 3b-v, but did not add the explicit assignment to 3b-i that the acceptance criterion requires. Standalone issue, narrow scope.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1       | 1     |
| P2       | 1     |
| P3       | 1     |
| **Total**| **3** |

---

## Acceptance Criteria Verification

### ant-farm-35wk — POSIX bash compatibility fix

**Criterion 1**: Script exits with clear error on bash < 4 (not exit code 2), OR script works on bash 3.2 and zsh.
- **MET**: The fix replaces all `declare -A` usage with a file-based POSIX-compatible key-value store. No bash 4+ features remain in the updated code. The script runs under `/usr/bin/env bash` (bash 3.2 on macOS) and under zsh without syntax errors.

**Criterion 2**: All step detection, completion check, and resume point determination produce correct results on macOS.
- **PARTIALLY MET** (blocked by F-1): The POSIX compatibility layer itself is correct — `map_set`, `map_get`, `map_has` all work correctly. However, the keys used (step0-step6) no longer match what RULES.md writes (SESSION_INIT, etc.), so correct results are not produced in practice.

### ant-farm-purh — step3b filename fix

**Criterion 1**: step3b progress log entry references the correct consolidated report filename.
- **MET**: RULES.md line 187 now reads `review-consolidated-${TIMESTAMP}.md` instead of `big-head-summary.md`.

**Criterion 2**: Filename matches the pattern used by Big Head in reviews.md.
- **MET**: Pattern `review-consolidated-${TIMESTAMP}.md` matches the documented convention.

### ant-farm-yf5p — TIMESTAMP variable fix

**Criterion 1**: Step 3b-i explicitly assigns timestamp to a named variable.
- **NOT MET** (F-2): Line 132 describes timestamp generation in prose without explicit variable assignment.

**Criterion 2**: Step 3b-v TIMESTAMP reference resolves correctly.
- **PARTIALLY MET**: The comment at line 166 correctly names the variable and shows the assignment expression, so a careful reader following 3b-i through 3b-v will understand what to do. But the explicit assignment is in a comment in 3b-v, not in 3b-i's instructions.

### ant-farm-nq4f — milestone naming fix

**Criterion 1**: Progress log milestone names match authoritative spec.
- **PARTIALLY MET**: RULES.md was updated with event-named keys. `parse-progress-log.sh` was NOT updated, so the parser cannot parse logs produced by the updated RULES.md.

**Criterion 2**: Per-agent recovery granularity is either implemented or explicitly descoped.
- **NOT EVALUATED**: The milestone names changed but the per-agent granularity question (multiple WAVE_SPAWNED entries, one per wave) is unchanged from the prior round.

### ant-farm-dxw2 — SSV PASS approval gate documentation

**Criterion 1**: Bead spec and implementation agree on whether SSV PASS requires human approval.
- **MET**: Both RULES.md and checkpoints.md now explicitly state user approval is required and explain the rationale.

**Criterion 2**: If approval retained, bead documents rationale.
- **MET**: The note field on the bead records the design decision. checkpoints.md line 698 now reads "User approval is required even on SSV PASS — this is a deliberate design choice, not an omission."

---

## Cross-Review Messages

Sending to edge-cases reviewer: F-1 at `scripts/parse-progress-log.sh:62-72,177,198` is both a correctness issue (keys never match) and an edge case (completed-session detection always fails, always exits 0 instead of 2). Reporting here as correctness root cause; edge-cases reviewer may want to flag the behavioral edge (exit code contract broken).

---

## Coverage Log

| File | Status |
|------|--------|
| `orchestration/RULES.md` | Reviewed — ant-farm-purh and ant-farm-yf5p fixes verified. ant-farm-nq4f milestone renames verified. ant-farm-dxw2 approval gate clarification verified. F-2 found at line 132. |
| `orchestration/templates/checkpoints.md` | Reviewed — ant-farm-dxw2 fix at lines 667 and 698 verified. No issues found. |
| `scripts/parse-progress-log.sh` | Reviewed — ant-farm-35wk POSIX fix verified as correct. F-1 (P1) found: STEP_KEYS and completion check not updated for ant-farm-nq4f rename. F-3 (P3) found in comment at line 157. |

---

## Overall Assessment

**Score**: 5/10

**Verdict**: NEEDS WORK

The three-commit fix batch landed two of four tasks cleanly (ant-farm-purh, ant-farm-dxw2) and implemented the POSIX compatibility layer correctly (ant-farm-35wk, the mechanical part). However, ant-farm-nq4f was only half-applied: RULES.md emits new event-named milestone keys but `parse-progress-log.sh` still looks for the old step-numbered keys. This breaks the core crash recovery contract — the very bug that the original issue identified was partially replicated in a different form. A completed session now emits `SESSION_COMPLETE` but the script checks for `step6`; a crash mid-session writes `WAVE_SPAWNED` but the script looks for `step2`. The result is that crash recovery silently fails in all real-world cases post-fix.
