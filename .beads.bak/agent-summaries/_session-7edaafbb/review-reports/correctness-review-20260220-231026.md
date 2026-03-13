# Report: Correctness Review

**Scope**: orchestration/RULES.md, orchestration/SETUP.md, orchestration/reference/dependency-analysis.md, orchestration/templates/checkpoints.md, orchestration/templates/implementation.md, orchestration/templates/reviews.md, orchestration/templates/scout.md, scripts/compose-review-skeletons.sh, scripts/fill-review-slots.sh, scripts/install-hooks.sh, scripts/parse-progress-log.sh, scripts/scrub-pii.sh, scripts/sync-to-claude.sh
**Reviewer**: Correctness Review (nitpicker, sonnet)
**Commit range**: 60bdcb4..HEAD

---

## Findings Catalog

### Finding 1: extract_agent_section awk change produces empty output for single-separator skeleton files

- **File(s)**: scripts/compose-review-skeletons.sh:73
- **Severity**: P1
- **Category**: correctness
- **Description**: The fix in commit 614779c changed `extract_agent_section` from `awk '/^---$/{found=1; next} found{print}'` to `awk '/^---$/{count++; next} count>=2{print}'`. Both `nitpicker-skeleton.md` and `big-head-skeleton.md` contain exactly ONE `---` separator (confirmed: `grep -c '^---$'` returns 1 for both files). The new `count>=2` condition requires two `---` delimiters before printing any lines, so it returns EMPTY output for both skeleton files. Confirmed by simulation:
  - Old behavior: `awk '/^---$/{found=1; next} found{print}' nitpicker-skeleton.md` → 26 lines (all agent instructions)
  - New behavior: `awk '/^---$/{count++; next} count>=2{print}' nitpicker-skeleton.md` → 0 lines (empty)

  Impact: `compose-review-skeletons.sh` produces skeleton files with no agent instruction body — only the header comment and the Review Brief footer slots. The output files are non-empty (so the `-s` check passes) and the unfilled-marker check also passes (the only remaining markers are in the footer slots, which get filled). The generated review prompts would contain review metadata but no instructions, workflow steps, or format requirements. Every review cycle is broken silently.
- **Suggested fix**: Revert the awk pattern to the original `awk '/^---$/{found=1; next} found{print}'`, which correctly extracts content after the first and only `---` separator in these template files. Alternatively, the fix should only be applied if these skeleton files genuinely have two `---` delimiters (i.e., add a second `---` to both skeleton files as a YAML frontmatter close, and update the comment to match).
- **Cross-reference**: None

---

### Finding 2: big-head-skeleton.md still references stale variable name TIMED_OUT from reviews.md change

- **File(s)**: orchestration/templates/big-head-skeleton.md:91
- **Severity**: P2
- **Category**: correctness
- **Description**: Commit 1906d23 (`fix: replace LLM-interpreted IF ROUND 1 markers with shell conditionals`) renamed the timeout sentinel variable in `reviews.md` from `TIMED_OUT=1` (the "timed out" flag) to `REPORTS_FOUND=0` (inverted sentinel meaning "all reports found"). The polling loop in `reviews.md` now checks `if [ $REPORTS_FOUND -eq 0 ]` instead of `if [ $TIMED_OUT -eq 1 ]`. However, `big-head-skeleton.md` at line 91 still instructs Big Head: `**On timeout (TIMED_OUT=1)**: Before returning the error to the Queen...`. Since the consolidation brief is generated from the `reviews.md` template via `fill-review-slots.sh`, Big Head's runtime brief will contain the correct shell code (`REPORTS_FOUND`). However, the `big-head-skeleton.md` instructions reference the old variable name, which a Big Head agent reading the skeleton (not the filled brief) would see as the authoritative description. This is a cross-document inconsistency that could cause confusion or incorrect behavior if Big Head reads this prose.
- **Suggested fix**: Update `orchestration/templates/big-head-skeleton.md` line 91: change `**On timeout (TIMED_OUT=1)**` to `**On timeout (REPORTS_FOUND=0)**` to match the current variable name in `reviews.md`.
- **Cross-reference**: Related to reviews.md polling loop change in commit 1906d23

---

### Finding 3: install-hooks.sh pre-commit backup lacks explicit error handling added to pre-push backup

- **File(s)**: scripts/install-hooks.sh:71
- **Severity**: P3
- **Category**: correctness
- **Description**: Commit `739a370` (ant-farm-4fx) hardened the pre-push hook backup with explicit `if ! cp "$HOOK_TARGET" "$BACKUP"; then ... exit 1 fi` error handling and a descriptive diagnostic message. The pre-commit hook backup at line 71 still uses bare `cp "$PRECOMMIT_TARGET" "$BACKUP"` without an explicit error check. While `set -euo pipefail` would exit on cp failure, there is no diagnostic message. If cp fails (disk full, permissions), the script exits silently with no actionable message, unlike the pre-push case.
- **Suggested fix**: Apply the same explicit error handling pattern to the pre-commit backup: wrap in `if ! cp "$PRECOMMIT_TARGET" "$BACKUP"; then echo "ERROR: Failed to back up $PRECOMMIT_TARGET to $BACKUP — aborting. Check permissions and disk space." >&2; exit 1; fi`
- **Cross-reference**: None

---

### Finding 4: compose-review-skeletons.sh comment incorrectly claims regex matches 2+ char tokens only

- **File(s)**: scripts/compose-review-skeletons.sh:103, scripts/compose-review-skeletons.sh:158
- **Severity**: P3
- **Category**: correctness
- **Description**: The comment added in commit 338618f (ant-farm-yn1r) says: `Pattern: {WORD} → {{WORD}} where WORD matches [A-Z][A-Z_]* (2+ chars, all-caps with underscores). Single-char tokens like {X} do NOT match and are left unchanged.` The regex `[A-Z][A-Z_]*` matches exactly one `[A-Z]` character followed by zero or more `[A-Z_]` characters — minimum 1 character total, not 2. Confirmed: `echo "{X}" | sed 's/{\([A-Z][A-Z_]*\)}/{{\1}}/g'` outputs `{{X}}`. So `{X}` DOES match and would be converted to `{{X}}`. The comment's claim that single-char tokens "do NOT match" is factually incorrect. In practice, no single-char uppercase tokens exist in the current skeleton files, so there is no runtime impact. The same incorrect claim appears in both the `write_nitpicker_skeleton` and `write_big_head_skeleton` functions.
- **Suggested fix**: Fix the comment to accurately describe the regex behavior: `Pattern: {WORD} → {{WORD}} where WORD is one or more uppercase letters or underscores ([A-Z][A-Z_]*). All uppercase-only tokens (including single-char) are converted. This is safe because no single-char uppercase template tokens exist in the current skeleton files.`
- **Cross-reference**: None

---

### Finding 5: RULES.md uses mixed whitespace-stripping styles for CHANGED_FILES vs TASK_IDS

- **File(s)**: orchestration/RULES.md:153, orchestration/RULES.md:159
- **Severity**: P3
- **Category**: correctness
- **Description**: Commit ant-farm (whitespace check) updated the CHANGED_FILES validation to use bash-specific `[[ -z "${CHANGED_FILES//[[:space:]]/}" ]]` parameter expansion, but the adjacent TASK_IDS validation (line 159) retains the older POSIX-style `[ -z "$(echo "${TASK_IDS}" | tr -s ' \n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')" ]` subshell approach. Both are functionally correct in the bash environment where the Queen runs, but the inconsistency creates a maintenance hazard — a reader might wonder which approach is preferred and why the styles differ.
- **Suggested fix**: Either apply the bash parameter expansion style to TASK_IDS as well (`[[ -z "${TASK_IDS//[[:space:]]/}" ]]`), or revert CHANGED_FILES to use the consistent subshell style. The bash parameter expansion approach is preferable as it avoids subprocesses and is simpler.
- **Cross-reference**: None

---

## Preliminary Groupings

### Group A: Stale cross-reference from reviews.md variable rename (Finding 2)
- Finding 2 — standalone; the TIMED_OUT→REPORTS_FOUND variable rename in reviews.md was not propagated to big-head-skeleton.md
- **Underlying cause**: The two files reference each other via prose description, and the rename in reviews.md was applied with the assumption that the only reader is the shell script (which was correctly updated). The big-head-skeleton.md prose was overlooked as a secondary reference point.

### Group B: Script correctness regression in extract_agent_section (Finding 1)
- Finding 1 — standalone; the fix targeted YAML frontmatter behavior but the skeleton files use a single `---` visual separator, not YAML frontmatter.
- **Underlying cause**: The task (ant-farm-o058) appears to have been filed based on an assumption about how the skeleton files structure their content (YAML frontmatter with two `---` delimiters). The actual structure uses a single `---` separator as a visual divider, not frontmatter.

### Group C: Documentation/code comment inaccuracies (Findings 4, 5)
- Finding 4 — incorrect comment about regex minimum character requirement
- Finding 5 — inconsistent whitespace-stripping styles between CHANGED_FILES and TASK_IDS checks
- **Underlying cause**: Documentation written in the same commit session did not fully verify the exact regex behavior / the refactor only updated one of two parallel code blocks.

### Group D: Incomplete hardening propagation (Finding 3)
- Finding 3 — pre-push backup was hardened but pre-commit backup was not
- **Underlying cause**: The fix (ant-farm-4fx) targeted the pre-push backup only; the pre-commit backup block in the same function was not updated in parallel.

---

## Summary Statistics
- Total findings: 5
- By severity: P1: 1, P2: 1, P3: 3
- Preliminary groups: 4

---

## Cross-Review Messages

### Sent
- None sent.

### Received
- None received at time of report writing.

### Deferred Items
- None.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| orchestration/RULES.md | Findings: #5 | ~444 lines reviewed; Step 3b-i validation block, dummy reviewer guard, workflow steps, hard gates, session directory section, anti-patterns, concurrency rules all reviewed |
| orchestration/SETUP.md | Reviewed — no issues | ~266 lines; Quick Setup, Full Setup, Troubleshooting sections reviewed; doc change (line 78) clarifies Queen delegation to Scout — correct |
| orchestration/reference/dependency-analysis.md | Reviewed — no issues | ~196 lines; Term Definitions, Pre-Flight Checklist, Decision Matrix, Conflict Patterns, Subagent Type Mapping reviewed; example path change from hs_website to my-project verified consistent |
| orchestration/templates/checkpoints.md | Reviewed — no issues | ~718 lines; all checkpoint definitions (SSV, CCO, WWD, DMVDC, CCB) reviewed; my-project example replacements verified; placeholder guard in CCO Nitpickers section reviewed and correct |
| orchestration/templates/implementation.md | Reviewed — no issues | ~270 lines; 6-step agent template, scope boundary insert, Queen pre-spawn checklist, information diet section reviewed; my-project example replacements verified consistent with checkpoints.md and dependency-analysis.md |
| orchestration/templates/reviews.md | Reviewed — no issues (change correct, but creates stale reference in big-head-skeleton.md) | ~926 lines; Big Head consolidation protocol, polling loop shell variable rename (TIMED_OUT→REPORTS_FOUND), IF ROUND 1 → shell conditional changes all reviewed; the polling loop in reviews.md is now correct shell but big-head-skeleton.md prose is stale (Finding 2) |
| orchestration/templates/scout.md | Reviewed — no issues | ~293 lines; error metadata template enrichment (Title, Type, Priority, Epic fields added), step definitions, archive exclusion notes reviewed; changes are correct additions |
| scripts/compose-review-skeletons.sh | Findings: #1, #4 | ~235 lines; extract_agent_section function (Finding 1 — critical regression), sed conversion pattern (Finding 4 — comment inaccuracy), write_nitpicker_skeleton, write_big_head_skeleton, output verification all reviewed |
| scripts/fill-review-slots.sh | Reviewed — no issues | ~398 lines; EXIT trap registration, fill_all_slots awk single-pass implementation, @file resolution, unfilled slot verification, round-aware review type selection, write_filled_review and write_big_head_brief helpers all reviewed; DATA_FILE_PATH self-reference safe; awk loop cannot infinite-loop because slot values are filesystem paths |
| scripts/install-hooks.sh | Findings: #3 | ~119 lines; pre-push backup hardening (correct), pre-commit backup (Finding 3 — inconsistent), hook content, scrub/sync script chmod additions reviewed |
| scripts/parse-progress-log.sh | Reviewed — no issues | ~292 lines; malformed line timestamp guard, overwrite warning for existing resume-plan.md, UNREACHABLE branch comment, POSIX-compatible key-value store, all STEP_KEYS reviewed; SESSION_COMPLETE confirmed present in STEP_KEYS array, validating dead-branch claim |
| scripts/scrub-pii.sh | Reviewed — no issues | ~83 lines; perl dependency check, [REDACTED] replacement, PII_FIELD_PATTERN variable consistency, grep -c || true defensive fix, GIT_INDEX_FILE hook detection, --check mode reviewed; all changes correct |
| scripts/sync-to-claude.sh | Reviewed — no issues | ~68 lines; --delete removal, PID-appended backup timestamp, agents/ directory existence guard, missing script warning reviewed; changes correct |

---

## Overall Assessment

**Score**: 6/10
**Verdict**: NEEDS WORK

The session contains 30 commits covering substantive fixes to script robustness (EXIT traps, empty @file handling, malformed log detection), documentation improvements, and the reviews.md polling loop refactor. Most changes are correct and improve reliability. However, there is one critical regression: the `extract_agent_section` fix (ant-farm-o058) changes the awk pattern from `found=1` (triggers on first `---`) to `count>=2` (requires two `---`), but both skeleton files use exactly one `---` separator. This silently produces empty agent instruction bodies in all generated review skeleton files, breaking every review cycle without any error output. This P1 must be resolved before the review pipeline is usable.
