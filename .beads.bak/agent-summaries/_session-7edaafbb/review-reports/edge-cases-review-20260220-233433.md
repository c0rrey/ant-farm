# Report: Edge Cases Review

**Scope**: orchestration/SETUP.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/reviews.md, scripts/compose-review-skeletons.sh, scripts/install-hooks.sh, scripts/scrub-pii.sh, scripts/sync-to-claude.sh
**Reviewer**: edge-cases | Nitpicker (sonnet)
**Review round**: 2 (fix commits only: e584ba5..HEAD)

---

## Findings Catalog

### Finding 1: `scrub-pii.sh` grep pattern and perl pattern diverge — no runtime failure, correctly scoped

- **File(s)**: `/Users/correy/projects/ant-farm/scripts/scrub-pii.sh:46` (grep pattern) vs `scripts/scrub-pii.sh:63` (perl pattern)
- **Severity**: P3
- **Category**: edge-case
- **Description**: The grep-based `PII_FIELD_PATTERN` was correctly updated in the viyd fix from `\s*` to `[[:space:]]*` for BSD compatibility. However, the perl substitution on line 63 still uses `\s*`. In perl, `\s` is a valid built-in character class (perl's regex engine is not POSIX grep), so this is NOT a bug — perl works correctly on BSD/macOS with `\s`. The divergence creates a subtle asymmetry: the grep detection pattern and the perl replacement pattern use different whitespace metacharacters, but they match the same bytes in practice for realistic JSON content (no embedded newlines between key and value). No runtime failure results.
- **Suggested fix**: None required for correctness. If desired for consistency, add a comment explaining why perl uses `\s` while grep uses `[[:space:]]` — but this is out of scope for round 2 (style/docs).
- **Cross-reference**: None

### Finding 2: `compose-review-skeletons.sh` `extract_agent_section` — applied to both skeleton types, both have exactly one `---`

- **File(s)**: `/Users/correy/projects/ant-farm/scripts/compose-review-skeletons.sh:73`
- **Severity**: P3 — observation only, fix is confirmed correct
- **Category**: edge-case
- **Description**: The ul02 fix reverts `count>=2` to `count>=1` in `extract_agent_section`. Both skeleton files (`nitpicker-skeleton.md` line 17, `big-head-skeleton.md` line 65) have exactly one `---` delimiter. `count>=1` correctly begins emitting after the first delimiter. Edge case confirmed: if a skeleton file were to gain a second `---` (e.g., inside a fenced code block), the function would not skip it because the awk pattern matches `^---$` (exact line match), not fenced-block `---`. Since markdown fenced blocks use three dashes without a blank line guard, any literal `---` on its own line inside the template would be counted. Current templates do not have this — the fix is sound for the current structure.
- **Suggested fix**: No action required. The fix is correct for the current skeleton format.
- **Cross-reference**: None

### Finding 3: `reviews.md` polling loop — `REVIEW_ROUND` case guard fires before `[ "$REVIEW_ROUND" -eq 1 ]` comparison, but the exit is inside the code block presented as example shell, not actually executed as shell

- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:503-510` (new case guard block)
- **Severity**: P2
- **Category**: edge-case
- **Description**: The polling loop code in `reviews.md` is presented inside a markdown fenced code block as documentation/template content — it is NOT directly executed by the shell. It is delivered to Big Head as part of a brief for Big Head to run as a Bash invocation. The shkt fix adds a `case "$REVIEW_ROUND"` guard immediately after the assignment `REVIEW_ROUND={{REVIEW_ROUND}}`. This is correct in concept. However, the guard must `exit 1` to prevent the rest of the block from running with an unsubstituted value. The `exit 1` on line 509 is correct.

  The edge case: when Big Head runs this code block, if `REVIEW_ROUND` is the literal string `{{REVIEW_ROUND}}` (unsubstituted), the `exit 1` inside the case guard will terminate the Bash subshell running the block. Big Head will see the `PLACEHOLDER ERROR` echoes and a non-zero exit code. The surrounding instruction text says "Do NOT proceed. Return this error to the Queen immediately." — this relies on Big Head (an LLM) interpreting the exit code and printed error. Since the code block has `set -euo pipefail` at the top (inherited from the pre-existing block structure), the `exit 1` will correctly terminate. This is functional.

  **Actual risk**: If the `case` guard is the ONLY protection and `REVIEW_ROUND={{REVIEW_ROUND}}` is substituted literally (e.g., by a broken `fill-review-slots.sh`), then `[ "$REVIEW_ROUND" -eq 1 ]` at line ~545 would fail with a non-numeric comparison error under `set -euo pipefail`, which would also terminate the script. So there are two layers of protection. The fix adds an explicit, descriptive error layer before the implicit arithmetic failure — this is an improvement. No silently wrong results are possible.
- **Suggested fix**: No action required. The fix is correctly placed and functional.
- **Cross-reference**: None

### Finding 4: `install-hooks.sh` pre-commit hook backup — inconsistent error handling vs pre-push hook (pre-existing, out-of-scope observation)

- **File(s)**: `/Users/correy/projects/ant-farm/scripts/install-hooks.sh:70-71`
- **Severity**: [OUT-OF-SCOPE] — pre-existing asymmetry, not introduced by bhgt fix
- **Category**: edge-case
- **Description**: The pre-push backup block (lines 33-36) uses `if ! cp ... ; then ... exit 1; fi` with explicit error handling. The pre-commit backup block (lines 70-71) uses bare `cp` with no explicit error handling. Under `set -euo pipefail`, a failed `cp` will terminate the script, but without a diagnostic message. This asymmetry predates the bhgt fix. The bhgt fix only changed the logic inside the `if git diff --cached ... ; then` block. Not reportable as a round 2 fix-scope finding — would only cause a non-descriptive error message, not a runtime failure or silently wrong results.
- **Suggested fix**: Out of scope for this review round.
- **Cross-reference**: None

---

## Preliminary Groupings

### Group A: Fix scope — all 7 fixes landed correctly, no edge case failures

Findings 1, 2, 3: Each fix was verified against the actual file content and execution paths. No finding represents a runtime failure or silently wrong result introduced by the fixes.

- Finding 1 (viyd): perl `\s` is intentionally not changed — perl handles `\s` natively. No mismatch with the grep pattern for realistic JSON.
- Finding 2 (ul02): `count>=1` is correct for single-`---` skeleton files. Both skeletons verified.
- Finding 3 (shkt): REVIEW_ROUND guard fires correctly; `exit 1` terminates on unsubstituted placeholder; backed by implicit arithmetic guard downstream.

### Group B: Pre-existing issue — out of scope

Finding 4 (bhgt): asymmetric error handling in backup steps predates this fix session.

---

## Summary Statistics

- Total findings: 4
- By severity: P1: 0, P2: 1 (Finding 3 — confirmed functional, no action required), P3: 2 (Findings 1 and 2), Out-of-scope: 1 (Finding 4)
- Preliminary groups: 2

Note: The P2 finding (Finding 3) is labeled P2 for thoroughness but the analysis concludes no action is required — the fix is correct, and the edge case is covered by two independent guards.

---

## Cross-Review Messages

### Sent
- None

### Received
- None

### Deferred Items
- None

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `/Users/correy/projects/ant-farm/orchestration/SETUP.md` | Reviewed — no issues | sjyg fix: 1 line changed (doc reword, line 211). Wording is accurate. No edge cases introduced. |
| `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md` | Reviewed — no issues | 2qmt fix: `TIMED_OUT` → `REPORTS_FOUND` variable name at line 91. Consistent with polling loop variable name (`REPORTS_FOUND=0` at line ~564 of reviews.md). Fix is correct. |
| `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md` | Findings: #3 | shkt fix: REVIEW_ROUND case guard added at lines 503-510. Analyzed in Finding 3. |
| `/Users/correy/projects/ant-farm/scripts/compose-review-skeletons.sh` | Findings: #2 | ul02 fix: `count>=2` → `count>=1` at line 73. Analyzed in Finding 2. Both skeleton delimiter counts verified. |
| `/Users/correy/projects/ant-farm/scripts/install-hooks.sh` | Findings: #4 (out-of-scope) | bhgt fix: restructured `if [[ ! -x "$SCRUB_SCRIPT" ]]` block. Logic is correct. Pre-existing backup asymmetry noted as out-of-scope. |
| `/Users/correy/projects/ant-farm/scripts/scrub-pii.sh` | Findings: #1 | viyd fix: `\s*` → `[[:space:]]*` in grep pattern at line 46. Perl pattern on line 63 retains `\s` — correct for perl. Analyzed in Finding 1. |
| `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh` | Reviewed — no issues | ub8a fix: `--exclude='_archive/'` added to rsync at line 27. Correct. No edge cases: rsync `--exclude` applies to relative paths under the source directory; `_archive/` matches the `orchestration/_archive/` subdirectory correctly. |

---

## Overall Assessment

**Score**: 9.5/10
**Verdict**: PASS

All 7 fixes landed correctly. The awk revert (ul02), BSD grep fix (viyd), rsync exclude (ub8a), placeholder guard (shkt), doc reword (sjyg), variable name fix (2qmt), and warn-instead-of-fail (bhgt) each address their stated bug and introduce no new edge case failures. The one P2-labeled finding (Finding 3) is a thorough analysis that concludes the fix is sound with double-layered protection. No runtime failures or silently wrong results were found in any of the 7 fix commits.
