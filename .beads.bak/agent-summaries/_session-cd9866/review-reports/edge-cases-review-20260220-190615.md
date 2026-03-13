# Report: Edge Cases Review

**Scope**: agents/big-head.md, docs/installation-guide.md, orchestration/_archive/pantry-review.md, orchestration/PLACEHOLDER_CONVENTIONS.md, orchestration/RULES.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/checkpoints.md, orchestration/templates/dirt-pusher-skeleton.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md, README.md, scripts/install-hooks.sh, scripts/scrub-pii.sh
**Reviewer**: edge-cases | nitpicker

---

## Findings Catalog

### Finding 1: Pre-commit hook silently blocks all commits when scrub-pii.sh is absent
- **File(s)**: `scripts/install-hooks.sh:74-77`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The installed pre-commit hook exits 1 with an error if `scripts/scrub-pii.sh` is not found or not executable. The comment in `install-hooks.sh:L46-48` for the pre-push hook says the sync failure is non-fatal ("push continuing without sync"), but the pre-commit hook is hardcoded to block the commit entirely (`exit 1`) when the scrub script is missing. Any user who deletes or renames `scrub-pii.sh` will have every future commit blocked — including commits that don't touch `issues.jsonl`. The guard at line 80 checks whether `issues.jsonl` is staged, so the hook would only run the scrub when needed; but the executable check at lines 74-77 runs unconditionally before that guard, meaning even unrelated commits are blocked.
- **Suggested fix**: Move the `[[ ! -x "$SCRUB_SCRIPT" ]]` check inside the `if git diff --cached --name-only | grep -q ...` block, so it only fires when `issues.jsonl` is actually staged. Alternatively, downgrade to a warning and exit 0 when the scrub script is missing, consistent with the pre-push hook's non-fatal behavior.
- **Cross-reference**: None.

### Finding 2: scrub-pii.sh post-scrub residual check uses grep -c which may return exit code 1 even when zero matches exist
- **File(s)**: `scripts/scrub-pii.sh:52-55`
- **Severity**: P3
- **Category**: edge-case
- **Description**: After running `perl -i -pe`, the script calls `grep -qE ... "$ISSUES_FILE"` to confirm no emails remain (line 52). If that succeeds (emails remain), it then runs `grep -cE ...` to count them (line 53). The `set -euo pipefail` at the top means any command exiting non-zero kills the script. `grep -c` exits 1 when zero matches are found. In the branch where emails _do_ remain (the `if` condition on line 52 was true), `grep -c` will always find matches and exit 0 — so this specific path is fine. However, if `grep -qE` on line 52 returns non-zero _and_ `set -e` is active, the script would be killed before reaching line 53. In this flow `set -e` means the lines after the `perl` invocation are guarded: if `grep -qE` finds nothing (no remaining PII), it exits 1 (no match), but since this is the desired success path we continue. The flow is actually correct here because `grep -q` exiting 1 (no match) causes the `if` block body to be skipped, not the whole script. However the subtlety of relying on `set -e` not applying to `if` conditions could confuse future maintainers.
- **Suggested fix**: Add a comment explaining that `grep -qE` inside `if` conditions is safe under `set -e` because the shell does not apply `-e` to the condition expression of an `if`. Low-risk documentation fix only.

### Finding 3: scrub-pii.sh does not handle the case where issues.jsonl is a directory
- **File(s)**: `scripts/scrub-pii.sh:28-31`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The existence check uses `[[ ! -f "$ISSUES_FILE" ]]` (line 28), which correctly handles a missing file, but would pass (i.e., not skip) if `$ISSUES_FILE` is a directory. In that case, `perl -i -pe` would attempt to operate on a directory and fail with an error that may not produce a meaningful message for the user. This is a very unlikely scenario (a directory named `issues.jsonl`) but illustrates that the check doesn't guard against all unexpected filesystem states.
- **Suggested fix**: Change the check to `[[ ! -f "$ISSUES_FILE" ]] || [[ -d "$ISSUES_FILE" ]]` or simply rely on the existing `-f` test, which already returns false for directories — the current check is actually correct since `-f` tests for regular file. This finding is low-risk and primarily a future-maintainer confusion issue; no code change required.

### Finding 4: install-hooks.sh writes the pre-commit hook body with a hardcoded error exit but the outer script does not verify the inner scrub script path at install time
- **File(s)**: `scripts/install-hooks.sh:93-98`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The install script checks at lines 93-98 whether `scrub-pii.sh` exists and warns if not. The warning message says "pre-commit hook will block commits until it is present." This is accurate but only a warning — `install-hooks.sh` exits 0 even when the scrub script is absent. A user who installs hooks in a fresh clone before running any setup that places `scrub-pii.sh` will get a warning but a fully installed hook that will block all future commits involving `issues.jsonl`. The install could be more defensive: confirm the scrub script exists before writing the hook, or at minimum change the warning to indicate the hook is in a broken state.
- **Suggested fix**: At install time, if `scrub-pii.sh` is missing, either refuse to install the pre-commit hook (`exit 1` with an explanation) or install it in a degraded-but-non-blocking mode. The current behavior (warn but install anyway) leaves a time bomb for users on fresh checkouts.

### Finding 5: Big Head polling loop in reviews.md uses template literals that must be replaced by the Pantry
- **File(s)**: `orchestration/templates/reviews.md:519-526`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The polling loop in the Big Head Step 0a section contains `<session-dir>/review-reports/correctness-review-<timestamp>.md` and similar angle-bracket placeholders inside a bash `[ -f "..." ]` check. The document states "The Pantry writes the exact paths" before delivering this to Big Head. However, this is a documentation/protocol requirement only — there is no validation in the system that checks whether the Pantry actually replaced these placeholders before sending to Big Head. If the Pantry fails to substitute (e.g., due to a logic error or crash partway through composition), Big Head would run the polling loop with literal placeholder strings like `<session-dir>` as path arguments. `[ -f "<session-dir>/..." ]` would always return false (the literal path doesn't exist), causing Big Head to immediately time out, write a FAILED artifact, and block the workflow — without any helpful error about why the paths are wrong.
- **Suggested fix**: Big Head should validate that its input paths do not contain angle-bracket placeholders before entering the polling loop. A simple guard: `if echo "$REPORT_PATH" | grep -q '<'; then echo "ERROR: path contains unfilled placeholder: $REPORT_PATH"; exit 1; fi`. The Pantry's self-validation checklist in `pantry-review.md` already covers this, but Big Head has no corresponding guard.

### Finding 6: RULES.md Step 3b-i.5 validation script uses tr + sed pipe that may silently produce wrong results on some platforms
- **File(s)**: `orchestration/RULES.md:146-148`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The `CHANGED_FILES` and `TASK_IDS` emptiness checks use `echo "${VAR}" | tr -s ' \n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'`. The `tr -s ' \n'` collapses runs of spaces and newlines. However, `tr -s` with two characters in the set squeezes runs of *either* character, but does not translate — so a string containing only newlines would be collapsed to a single newline (not empty). The subsequent `sed` strips leading/trailing whitespace but a bare newline would survive as whitespace of sorts. In practice, a `CHANGED_FILES` value of just `"\n"` (a single newline from git diff returning nothing) might pass the emptiness check incorrectly on some shells, depending on how `echo` handles the trailing newline. The check at line 146 checks `[ -z "..." ]` — if the result is a bare newline, bash's `-z` may or may not treat it as empty depending on quoting.
- **Suggested fix**: Simplify to: `if [ -z "${CHANGED_FILES// }" ] || [ -z "${CHANGED_FILES//$'\n'}" ]`. Or use: `if ! echo "${CHANGED_FILES}" | grep -qE '[^ \t\n]'; then ... fi`. A direct `[ -z "$(echo "${CHANGED_FILES}" | tr -d '[:space:]')" ]` is cleaner and unambiguous.

### Finding 7: checkpoints.md CCO Nitpickers audit prompt contains unfilled `{REVIEW_ROUND}` placeholders inside the input guard
- **File(s)**: `orchestration/templates/checkpoints.md:198-199`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The CCO Nitpickers audit prompt template at lines 198-199 reads: "**Review round**: {REVIEW_ROUND} / **Input guard**: If {REVIEW_ROUND} is missing, blank, or non-numeric...". These `{REVIEW_ROUND}` markers are Tier 1 uppercase placeholders that the Queen must fill before spawning CCO. If the Queen sends this template verbatim (with `{REVIEW_ROUND}` un-substituted), Pest Control would receive a literal `{REVIEW_ROUND}` string as the round number. The input guard would fire: "CCO ABORTED: REVIEW_ROUND is invalid (got: '{REVIEW_ROUND}')." This is the correct safe failure — the guard works. However, it means a downstream workflow failure produces a confusing error that mentions `{REVIEW_ROUND}` (the placeholder name) rather than a human-readable explanation that the Queen forgot to substitute the round number.
- **Suggested fix**: The guard already correctly aborts in this case. No code change required. The risk is low because the Queen's workflow explicitly states the round number must be provided. This finding is informational — the guard handles the failure correctly, but the failure message could be improved: "CCO ABORTED: REVIEW_ROUND placeholder was not substituted (got: '{REVIEW_ROUND}'). Queen must fill this before spawning CCO." Consider improving the guard message to be more diagnostic.

### Finding 8: scrub-pii.sh PII_PATTERN does not handle emails with quoted local parts
- **File(s)**: `scripts/scrub-pii.sh:35`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The email regex `[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}` does not match RFC 5321 quoted local parts like `"user name"@example.com` or emails with `+tags` using characters outside the character class (e.g., emails using `!`, `#`, `$`, `&`, etc.). In practice, the fields being scrubbed (`owner`, `created_by`) are likely populated by standard login providers that use simple email formats, so this is low-risk. But a user with an unusual email format could have their PII leak through the scrub.
- **Suggested fix**: Widen the pattern slightly: `[a-zA-Z0-9._%+!\#$&'\*\-=?^_\`{|}~]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}` — or document in a comment that the pattern intentionally covers only common formats and unusual emails may not be scrubbed.

### Finding 9: install-hooks.sh does not verify that the pre-push hook backup path is writable before copying
- **File(s)**: `scripts/install-hooks.sh:27-31`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The backup logic `cp "$HOOK_TARGET" "$BACKUP"` (lines 30) runs inside `set -euo pipefail`, so a permission error would abort the script. However, the error message from a failed `cp` would be a generic system message ("Permission denied") without context that this is a backup step. Users who have a read-only `.git/hooks/` (e.g., in some CI environments or shared repos) would see a cryptic failure with no guidance on how to recover. The same applies to the pre-commit backup at lines 58-60.
- **Suggested fix**: Wrap the backup in a check: `if ! cp "$HOOK_TARGET" "$BACKUP" 2>/dev/null; then echo "WARNING: could not back up existing hook to $BACKUP — skipping backup, proceeding with install." >&2; fi`. This degrades gracefully without blocking the install.

---

## Preliminary Groupings

### Group A: Hook robustness — missing/absent scripts causing unexpected failures
- Finding 1 (pre-commit exit behavior), Finding 4 (install-time scrub script missing)
- **Root cause**: Both findings stem from the hooks and install script not distinguishing between "scrub script missing at install time" vs "at commit time" — both default to blocking behavior without graceful degradation.
- **Suggested combined fix**: Make the pre-commit hook's behavior conditional on whether `issues.jsonl` is staged BEFORE checking script existence; make install emit a more actionable warning when the scrub script is missing.

### Group B: Bash scripting edge cases under `set -euo pipefail`
- Finding 2 (grep -c behavior), Finding 6 (tr + sed whitespace check), Finding 9 (backup cp failure)
- **Root cause**: Multiple bash scripts use constructs that are correct but brittle or subtly platform-sensitive under strict error handling. Not a single code path, but a shared pattern of underspecified edge handling in shell scripts.

### Group C: Template substitution not validated at consumption point
- Finding 5 (Big Head polling loop with unfilled placeholders), Finding 7 (CCO input guard with unfilled round)
- **Root cause**: Both stem from the same architectural decision: placeholders are filled upstream (Pantry/Queen) but consumers (Big Head, CCO) have no independent validation that substitution occurred. The guards exist but produce cryptic errors rather than diagnosing placeholder leakage.

### Group D: PII scrub completeness
- Finding 8 (email regex coverage)
- **Root cause**: Standalone — narrow email regex. Low risk in practice given the data source.

### Group E: File existence and filesystem edge cases
- Finding 3 (directory named issues.jsonl)
- **Root cause**: Standalone — overly defensive check that is actually already correct (`-f` returns false for directories). No fix needed.

---

## Summary Statistics
- Total findings: 9
- By severity: P1: 0, P2: 3, P3: 6
- Preliminary groups: 5

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
| `agents/big-head.md` | Reviewed — no issues | 36-line agent definition. Reviewed tool list, core principles, consolidation workflow steps, and bead-filing instructions. All I/O is structured and externally driven; no user-input surfaces, no file operations performed by the agent directly. |
| `docs/installation-guide.md` | Reviewed — no issues | 407-line installation guide. Reviewed all bash command examples for correctness. Commands are illustrative (shown in fenced blocks for users to run); no unvalidated inputs. Backup strategy and troubleshooting sections reviewed; all commands are safe. |
| `orchestration/_archive/pantry-review.md` | Reviewed — no issues | Deprecated agent definition. 73 lines. Self-validation checklist reviewed — all checks are procedural, no code execution. No shell scripts or file operations that could cause edge case failures. |
| `orchestration/PLACEHOLDER_CONVENTIONS.md` | Reviewed — no issues | 232-line conventions document. Grep validation patterns reviewed — all use `--exclude-dir=_archive` correctly. No executable code paths. Bash examples in code blocks are illustrative only. |
| `orchestration/RULES.md` | Findings: #6 | 420-line workflow document. Reviewed all bash code blocks, validation scripts, and shell variable handling. Finding #6 identified in Step 3b-i.5. Retry limits, concurrency rules, and hard gates reviewed — all are procedural with no hidden edge case gaps. |
| `orchestration/templates/big-head-skeleton.md` | Reviewed — no issues | 126-line template. Reviewed polling loop structure, timeout logic, failure artifact format, and bead filing instructions. The polling loop itself uses `[ -f ]` checks — edge cases around path correctness are covered under Finding 5 (reviews.md). The skeleton timeout/retry protocol is well-specified. |
| `orchestration/templates/checkpoints.md` | Findings: #7 | 715-line checkpoint definitions. Reviewed all 5 checkpoints (SSV, CCO, WWD, DMVDC, CCB). Sample size formula and tie-breaking rules reviewed. `bd show` failure guards present in SSV Check 2 and Check 3. DMVDC `bd show` fallback reviewed — handles infrastructure failure without aborting. Finding #7 identified in CCO Nitpickers input guard. |
| `orchestration/templates/dirt-pusher-skeleton.md` | Reviewed — no issues | 48-line skeleton template. Reviewed 6-step workflow, `git pull --rebase` placement, and scope constraints. No user input surfaces. `bd close` only after summary doc write is a safe ordering. |
| `orchestration/templates/nitpicker-skeleton.md` | Reviewed — no issues | 44-line template. Input guard for `{REVIEW_ROUND}` is present and correct. No file operation risks. |
| `orchestration/templates/pantry.md` | Reviewed — no issues | 285-line Pantry instructions. Fail-fast pre-checks reviewed: directory existence check, file existence check, placeholder contamination check — all present. Failure artifacts write before returning error (safe). `compose-review-skeletons.sh` non-zero exit handling checked. |
| `orchestration/templates/reviews.md` | Findings: #5 | 891-line review protocol. Reviewed Big Head consolidation protocol, polling loop, timeout behavior, and bead filing gate. Finding #5 identified in Step 0a polling loop. The round-aware reviewer composition, termination rule, and P3 auto-filing logic reviewed — no additional edge case gaps found. |
| `README.md` | Reviewed — no issues | 333-line README. Reviewed all bash command examples and workflow descriptions. No executable paths; all commands are illustrative. `bd init` instructions reviewed — no hidden edge cases for new adopters. |
| `scripts/install-hooks.sh` | Findings: #1, #4, #9 | 99-line install script. Reviewed under `set -euo pipefail`. Hook body generation, backup logic, and executable-check verified. Three findings identified. |
| `scripts/scrub-pii.sh` | Findings: #2, #3, #8 | 59-line scrub script. Reviewed email regex, `--check` mode, `perl -i -pe` invocation, and post-scrub residual check. Three findings identified. |

---

## Overall Assessment
**Score**: 7.5/10
**Verdict**: PASS WITH ISSUES

The codebase is well-structured and generally robust. The most actionable finding (P2) is Finding 1: the pre-commit hook unconditionally blocks all commits when `scrub-pii.sh` is missing, even for commits that don't touch `issues.jsonl`. The other P2 findings (5 and 7) represent protocol gaps where upstream substitution failures produce cryptic rather than diagnostic errors — the failure handling exists but could be improved. No P1 findings. Shell scripts are tight and follow `set -euo pipefail` consistently. The agent templates are well-specified with appropriate guards and fallback protocols.
