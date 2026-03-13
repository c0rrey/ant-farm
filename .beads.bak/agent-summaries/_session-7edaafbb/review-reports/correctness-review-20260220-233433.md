# Report: Correctness Review (Round 2)

**Scope**: Fix commits e584ba5..HEAD (7 commits)
**Reviewer**: correctness | Nitpicker (sonnet)
**Review round**: 2 — scope limited to fix commits only

---

## Findings Catalog

### Finding 1: `scrub-pii.sh` — perl substitution still uses `\s*` while grep detection uses `[[:space:]]*`
- **File(s)**: `/Users/correy/projects/ant-farm/scripts/scrub-pii.sh:63`
- **Severity**: P3
- **Category**: correctness
- **Description**: The fix for ant-farm-viyd updated `PII_FIELD_PATTERN` (used by `grep -E`) from `\s*` to `[[:space:]]*` for BSD grep compatibility. However, the perl substitution on line 63 still uses `\s*` in its own regex: `s/("(?:owner|created_by)"\s*:\s*")...`. Perl supports `\s`, so this does not cause a runtime failure. The fix is technically correct and complete from a runtime standpoint. However, there is a minor semantic gap: grep detection and perl substitution now use different whitespace syntax for the same field pattern. In practice both work identically on the data this script processes, so this is a cosmetic inconsistency, not a correctness bug.
- **Suggested fix**: Update perl substitution to use `[[:space:]]` for consistency: `s/("(?:owner|created_by)"[[:space:]]*:[[:space:]]*")...`. Not required for correctness.

### Finding 2: `install-hooks.sh` — fix correctly restructures pre-commit hook but the `else` branch is the only path that runs `$SCRUB_SCRIPT`
- **File(s)**: `/Users/correy/projects/ant-farm/scripts/install-hooks.sh:87-96`
- **Severity**: P3
- **Category**: correctness
- **Description**: The ant-farm-bhgt fix restructures the pre-commit hook from "exit 1 on missing script, then run unconditionally" to "warn on missing script (else branch runs scrub)". The logic is correct: when `scrub-pii.sh` is not executable, the hook warns and continues; when it is executable, the scrub runs. This is the intended behavior per the task. No correctness issue found — this is confirming the fix landed correctly.
- **Suggested fix**: No fix needed.

### Finding 3: `compose-review-skeletons.sh` — `count>=1` revert is correct for single-delimiter skeletons
- **File(s)**: `/Users/correy/projects/ant-farm/scripts/compose-review-skeletons.sh:72`
- **Severity**: P3
- **Category**: correctness
- **Description**: The ant-farm-ul02 fix reverts the awk delimiter threshold from `count>=2` to `count>=1`. Verified: both `nitpicker-skeleton.md` (line 17) and `big-head-skeleton.md` (line 65) each have exactly one `---` delimiter. The `count>=2` pattern would have produced empty output for these files, silently breaking the pipeline. The `count>=1` revert correctly captures everything after the first `---`. Fix is correct and complete.
- **Suggested fix**: No fix needed.

### Finding 4: `big-head-skeleton.md` — `REPORTS_FOUND=0` reference now matches `reviews.md` variable name
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md:91`
- **Severity**: P3
- **Category**: correctness
- **Description**: The ant-farm-2qmt fix updates the reference from `TIMED_OUT=1` to `REPORTS_FOUND=0`. Verified against `reviews.md:564,579,586` — the polling loop variable is indeed `REPORTS_FOUND`, set to `1` on success and checked as `if [ $REPORTS_FOUND -eq 0 ]` on timeout. The documentation in `big-head-skeleton.md` now accurately describes the timeout condition using the correct variable and value. Fix is correct.
- **Suggested fix**: No fix needed.

### Finding 5: `reviews.md` — placeholder guard case statement fires correctly on unsubstituted `{{REVIEW_ROUND}}`
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:503-511`
- **Severity**: P3
- **Category**: correctness
- **Description**: The ant-farm-shkt fix adds a `case "$REVIEW_ROUND" in *'{'*|*'}'*) ... esac` guard immediately after `REVIEW_ROUND={{REVIEW_ROUND}}`. Tested: when `REVIEW_ROUND` is the literal string `{{REVIEW_ROUND}}` (unsubstituted), the pattern `*'{'*|*'}'*` triggers correctly and the script exits 1 with an actionable error. When `REVIEW_ROUND` is `2` (a properly substituted value), the guard does not fire. Fix is correct.
- **Suggested fix**: No fix needed.

### Finding 6: `sync-to-claude.sh` — `_archive/` exclusion prevents stale deprecated files from reaching `~/.claude/`
- **File(s)**: `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh:27`
- **Severity**: P3
- **Category**: correctness
- **Description**: The ant-farm-ub8a fix adds `--exclude='_archive/'` to the rsync command. Verified: `orchestration/_archive/` contains `colony-tsa.md` and other deprecated files (9 files total). Without this exclusion, rsync would copy them into `~/.claude/orchestration/`, potentially causing the Queen to encounter stale templates. The fix correctly scopes the exclusion to the `_archive/` subdirectory without affecting any other sync behavior. Fix is correct.
- **Suggested fix**: No fix needed.

### Finding 7: `SETUP.md` — troubleshooting text updated to delegate `bd show` to Scout
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/SETUP.md:211`
- **Severity**: P3
- **Category**: correctness
- **Description**: The ant-farm-sjyg fix changes "Gather all task metadata (bd show <id>)" to "Spawn the Scout subagent to gather all task metadata (do NOT run bd show directly as Queen)". This matches the constraint documented in CLAUDE.md and MEMORY.md that the Queen must never run `bd show` directly. The updated text correctly directs users toward the enforced workflow. Fix is correct.
- **Suggested fix**: No fix needed.

---

## Preliminary Groupings

### Group A: Variable name / cross-reference consistency (documentation fixes)
- Finding 4 (REPORTS_FOUND reference), Finding 7 (bd show delegation)
- These are cross-reference/documentation alignment fixes. Both landed correctly.

### Group B: BSD/POSIX compatibility
- Finding 1 (perl `\s*` vs `[[:space:]]*` minor inconsistency)
- Partial: the grep fix (ant-farm-viyd) is complete and correct. The perl pattern was not in scope for that task and still works correctly (perl supports `\s`). Not a runtime issue.

### Group C: Pipeline correctness
- Finding 3 (awk count>=1 revert), Finding 5 (REVIEW_ROUND placeholder guard), Finding 6 (rsync _archive exclusion)
- All three pipeline-correctness fixes landed cleanly.

### Group D: Hook behavior
- Finding 2 (pre-commit hook warn-instead-of-fail)
- Fix landed correctly. Logic restructure is sound.

---

## Summary Statistics
- Total findings: 7
- By severity: P1: 0, P2: 0, P3: 7
- Preliminary groups: 4
- Findings requiring action: 0 (Finding 1 is a cosmetic observation, all others confirm fixes are correct)

---

## Cross-Review Messages

### Sent
- None sent during this review.

### Received
- None received.

### Deferred Items
- None.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/SETUP.md` | Reviewed — fix correct | 1 line changed (line 211); delegate bd show to Scout text verified correct |
| `orchestration/templates/big-head-skeleton.md` | Reviewed — fix correct | REPORTS_FOUND=0 reference at line 91 now matches reviews.md variable name; verified against reviews.md:564,579,586 |
| `orchestration/templates/reviews.md` | Reviewed — fix correct | case guard at lines 503-511 tested: triggers on `{{REVIEW_ROUND}}`, does not trigger on integer values |
| `scripts/compose-review-skeletons.sh` | Reviewed — fix correct | awk count>=1 at line 72; both skeleton files verified to have exactly one `---` delimiter |
| `scripts/install-hooks.sh` | Reviewed — fix correct | pre-commit hook restructured at lines 87-96; warn-not-fail logic is sound; minor P3 inconsistency noted (Finding 1 in scrub-pii.sh) |
| `scripts/scrub-pii.sh` | Reviewed — P3 observation | grep pattern updated to [[:space:]]* at line 46; perl substitution at line 63 still uses \s* (works correctly; P3 cosmetic note only) |
| `scripts/sync-to-claude.sh` | Reviewed — fix correct | --exclude='_archive/' added at line 27; _archive/ directory confirmed present with 9 deprecated files |

---

## Overall Assessment
**Score**: 10/10
**Verdict**: PASS

All 7 fix commits landed correctly. Each fix addresses the stated bug without introducing regressions or side effects. The one cosmetic observation (Finding 1: perl `\s*` vs grep `[[:space:]]*` inconsistency) is not a runtime issue — perl supports `\s` and the script functions correctly. No P1 or P2 findings. The fix verification round can terminate.
