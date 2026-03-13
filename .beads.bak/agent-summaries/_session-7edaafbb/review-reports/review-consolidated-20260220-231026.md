# Consolidated Review Report

**Session**: 7edaafbb
**Review Round**: 1
**Timestamp**: 20260220-231026
**Consolidator**: Big Head

---

## Read Confirmation

| Report | File | Findings | Status |
|--------|------|----------|--------|
| Clarity | clarity-review-20260220-231026.md | 10 | Read |
| Edge Cases | edge-cases-review-20260220-231026.md | 16 | Read |
| Correctness | correctness-review-20260220-231026.md | 5 | Read |
| Excellence | excellence-review-20260220-231026.md | 10 | Read |
| **Total raw findings** | | **41** | |

---

## Consolidated Findings by Root Cause

### RC-1: [P1] extract_agent_section awk pattern requires 2 delimiters but skeleton files have only 1

**Root cause**: The fix in commit 614779c changed `extract_agent_section` from `awk '/^---$/{found=1; next} found{print}'` to `awk '/^---$/{count++; next} count>=2{print}'`. Both `nitpicker-skeleton.md` and `big-head-skeleton.md` contain exactly one `---` separator. The new `count>=2` condition requires two delimiters before printing, so it returns EMPTY output for both skeleton files. Every generated review skeleton has no agent instruction body -- the review pipeline is silently broken.

**Affected files**: `scripts/compose-review-skeletons.sh:73`

**Severity**: P1 (highest across reviewers: Correctness rated P1)

**Source findings**:
- Correctness-1 (P1): Core finding -- empty output breaks all review cycles
- Clarity-4 (P3): Docstring not updated to reflect count>=2 behavior
- Edge-15 (P3): Trailing whitespace on `---` delimiter would also miss the match

**Merge rationale**: All three findings target the same awk pattern in `extract_agent_section`. Correctness-1 identifies the critical regression (empty output). Clarity-4 identifies the stale docstring (says "after the ---" not "after the SECOND ---"). Edge-15 identifies an additional fragility in the same regex (`/^---$/` doesn't tolerate trailing whitespace). Same function, same line, same root cause: the awk pattern change was applied to files with a different delimiter structure than assumed.

**Suggested fix**: Revert to `awk '/^---$/{found=1; next} found{print}'`, or add a second `---` to both skeleton files as YAML frontmatter close. Update the docstring to match whichever approach is chosen. Optionally make the regex `/^---[[:space:]]*$/` to tolerate trailing whitespace.

---

### RC-2: [P2] BSD grep on macOS does not support `\s` in scrub-pii.sh verification

**Root cause**: `PII_FIELD_PATTERN` uses `\s` (a Perl-class metacharacter). On macOS BSD grep, `\s` is treated as a literal backslash-s, so `grep -qE "$PII_FIELD_PATTERN"` silently fails to match PII patterns preceded by whitespace. The main scrub uses `perl -i -pe` (which understands `\s`), so redaction works, but the verification pass falsely reports clean -- a silent PII leak in the safety check.

**Affected files**: `scripts/scrub-pii.sh:49`, `scripts/scrub-pii.sh:65`

**Severity**: P2 (Excellence-1 rated P2; has security/correctness implications)

**Source findings**:
- Excellence-1 (P2): Core finding -- `\s` not recognized by BSD grep

**Merge rationale**: Single-source finding. No other reviewers flagged this specific issue (Edge-8 flagged a TOCTOU in the same file but a different problem).

**Suggested fix**: Replace `\s` with `[[:space:]]` in `PII_FIELD_PATTERN`, or switch all grep calls to perl to match the main scrub engine.

---

### RC-3: [P2] Stale _archive/ files persist in ~/.claude/orchestration/ after --delete removal from rsync

**Root cause**: Commit removed `--delete` from `sync-to-claude.sh` rsync to preserve user-created files. Side effect: previously-synced `_archive/` files remain at `~/.claude/orchestration/_archive/`, which RULES.md explicitly forbids reading. No `--exclude='_archive/'` was added to prevent syncing the dangerous directory.

**Affected files**: `scripts/sync-to-claude.sh:27`

**Severity**: P2 (Edge-9 and Edge-10 both P2)

**Source findings**:
- Edge-9 (P2): --delete removal leaves stale files
- Edge-10 (P2): _archive/ exclusion absent from rsync
- Clarity-6 (P3): Orphaned manual-deletion comment lacks cross-reference to rationale

**Merge rationale**: All three findings target the same rsync command in sync-to-claude.sh:27. Edge-9 and Edge-10 are two facets of the same problem (stale dangerous files + no exclusion). Clarity-6 is the documentation gap for the same change. Same line, same root cause: the --delete removal was incomplete without an _archive/ exclusion.

**Suggested fix**: Add `--exclude='_archive/'` to the rsync command. Add a cleanup note mentioning `rm -rf ~/.claude/orchestration/_archive/` for environments with prior syncs.

---

### RC-4: [P2] REVIEW_ROUND placeholder substitution not guarded in reviews.md polling loop

**Root cause**: The polling loop shell block has `REVIEW_ROUND={{REVIEW_ROUND}}` (line 502). The placeholder guard (lines 519-553) checks report paths for unsubstituted markers but does NOT check `REVIEW_ROUND`. If `fill-review-slots.sh` fails to substitute this, the shell sets REVIEW_ROUND to the literal string `{{REVIEW_ROUND}}`, and the arithmetic comparison `[ "$REVIEW_ROUND" -eq 1 ]` produces a confusing integer expression error instead of a clear placeholder error.

**Affected files**: `orchestration/templates/reviews.md:502`, `orchestration/templates/reviews.md:519-553`

**Severity**: P2 (Edge-13 P2, Excellence-4 P2, Edge-14 P3)

**Source findings**:
- Edge-13 (P2): REVIEW_ROUND unsubstituted causes runtime arithmetic error
- Excellence-4 (P2): Same finding -- missing substitution check
- Edge-14 (P3): Placeholder guard doesn't cover all paths (maintenance concern)

**Merge rationale**: All three findings target the placeholder guard mechanism in the same code block. Edge-13 and Excellence-4 independently found the same gap (REVIEW_ROUND not checked). Edge-14 is the broader concern that the guard's path list is manually maintained. Same code block, same root cause: the placeholder guard was written to check paths but not the REVIEW_ROUND variable.

**Suggested fix**: Add a `case "$REVIEW_ROUND" in *'{'*|*'}'*) echo "PLACEHOLDER ERROR..."; exit 1 ;; esac` check before the arithmetic comparison. Add a comment noting the path list must be kept in sync with ACTIVE_REVIEW_TYPES.

---

### RC-5: [P2] SETUP.md Troubleshooting instructs Queen to run `bd show` directly

**Root cause**: The Troubleshooting section "Problem: Claude starts working without pre-flight analysis" includes "1. Gather all task metadata (`bd show <id>`)" -- directly contradicting the Queen Prohibition in RULES.md. This is pre-Scout-era content not updated when Scout delegation was introduced.

**Affected files**: `orchestration/SETUP.md:210-215`

**Severity**: P2 (Excellence-2 rated P2)

**Source findings**:
- Excellence-2 (P2): SETUP.md contradicts RULES.md Queen prohibition

**Merge rationale**: Single-source finding. No other reviewers flagged this specific issue.

**Suggested fix**: Replace the step with "1. Delegates ALL task discovery to the Scout subagent -- do NOT run `bd show` directly."

---

### RC-6: [P2] big-head-skeleton.md references stale TIMED_OUT variable name

**Root cause**: The variable rename from `TIMED_OUT` to `REPORTS_FOUND` in reviews.md (commit 1906d23) was not propagated to the prose reference in `big-head-skeleton.md` line 91, which still says `**On timeout (TIMED_OUT=1)**`.

**Affected files**: `orchestration/templates/big-head-skeleton.md:91`

**Severity**: P2 (Correctness-2 rated P2)

**Source findings**:
- Correctness-2 (P2): Stale TIMED_OUT reference in big-head-skeleton.md
- Clarity-2 (P3): REPORTS_FOUND flag lacks clarifying comment at test site (related -- same rename)

**Merge rationale**: Both findings stem from the TIMED_OUT-to-REPORTS_FOUND rename. Correctness-2 is the cross-document stale reference. Clarity-2 is the missing inline comment at the test site in reviews.md. Same root cause: the rename was applied to the shell code but not fully propagated to all documentation and inline comments.

**Suggested fix**: Update big-head-skeleton.md:91 to `**On timeout (REPORTS_FOUND=0)**`. Add an inline comment at reviews.md:577: `if [ $REPORTS_FOUND -eq 0 ]; then  # no reports arrived in time`.

---

### RC-7: [P2] pre-commit hook installation missing scrub-pii.sh installs a blocking hook

**Root cause**: `install-hooks.sh` installs the pre-commit hook even when `scrub-pii.sh` is not found, warning on stderr but not aborting. The installed hook body will `exit 1` when `scrub-pii.sh` is missing, blocking ALL commits. Unlike the pre-push hook (which skips sync non-fatally on missing scripts), the pre-commit hook is fully blocking.

**Affected files**: `scripts/install-hooks.sh:103-109`

**Severity**: P2 (Edge-12 rated P2)

**Source findings**:
- Edge-12 (P2): Pre-commit hook installs even if scrub-pii.sh missing

**Merge rationale**: Single-source finding. Distinct from RC-8 (which is about the backup error handling, not the missing-dependency problem).

**Suggested fix**: Either abort installation when `scrub-pii.sh` is absent, or make the hook body emit a non-fatal warning instead of `exit 1` when the script is missing. Document whichever choice is intentional.

---

### RC-8: [P3] install-hooks.sh pre-commit backup cp lacks explicit error handling (asymmetric with pre-push)

**Root cause**: The pre-push hook backup was hardened with `if ! cp ... then echo "ERROR..."; exit 1; fi` but the pre-commit hook backup retains bare `cp` without error handling. Under `set -euo pipefail`, a failed cp terminates silently with no diagnostic.

**Affected files**: `scripts/install-hooks.sh:69-72`

**Severity**: P3 (Clarity-5 P3, Edge-11 P3, Correctness-3 P3, Excellence-8 P3)

**Source findings**:
- Clarity-5 (P3): Asymmetric error handling between blocks
- Edge-11 (P3): Same finding -- pre-commit backup lacks explicit handling
- Correctness-3 (P3): Same finding -- inconsistent hardening
- Excellence-8 (P3): Same finding -- defensive programming gap

**Merge rationale**: All 4 reviewers independently found the exact same issue in the exact same code block (install-hooks.sh:69-72). Same file, same line, same missing error handling pattern. This is the most heavily cross-validated finding in the report.

**Suggested fix**: Apply the same `if ! cp ... then echo "ERROR..."; exit 1; fi` pattern to the pre-commit backup block.

---

### RC-9: [P3] Regex comment incorrectly claims `[A-Z][A-Z_]*` matches 2+ chars (matches 1+)

**Root cause**: The comment in `compose-review-skeletons.sh` says the regex `[A-Z][A-Z_]*` matches "2+ chars" and "Single-char tokens like {X} do NOT match". The regex actually matches 1+ chars (`[A-Z]` = 1 char, `[A-Z_]*` = 0+). Single-char tokens DO match. The comment appears in both `write_nitpicker_skeleton` and `write_big_head_skeleton`.

**Affected files**: `scripts/compose-review-skeletons.sh:103`, `scripts/compose-review-skeletons.sh:158`

**Severity**: P3 (Correctness-4 P3; Excellence-3 rated P2, downgraded to P3 -- comment inaccuracy with no runtime impact since no single-char tokens exist in current templates)

**Source findings**:
- Correctness-4 (P3): Comment claims 2+ but regex matches 1+
- Excellence-3 (P2): Same finding with same evidence

**Merge rationale**: Both findings target the exact same comment in the exact same file with the exact same analysis. Same root cause: the fix commit documented the regex behavior incorrectly.

**Priority note**: Excellence rated this P2 but Correctness rated P3. Since no single-char uppercase tokens exist in current skeleton files and the impact is documentation-only, P3 is appropriate. However, if the intent was to exclude single-char matches, the regex should be fixed to `[A-Z][A-Z_]+`.

**Suggested fix**: Either fix the comment to say "1+ chars" or change the regex to `[A-Z][A-Z_]+` if single-char exclusion was intended.

---

### RC-10: [P3] NUL-terminated sentinel comment incorrect in fill-review-slots.sh

**Root cause**: The comment at lines 176-178 in `fill-review-slots.sh` describes the map file format as using "NUL-terminated sentinel" but the actual format is tab-delimited newlines. The awk code at line 219 uses `index(entry, "\t")` confirming tab delimiter.

**Affected files**: `scripts/fill-review-slots.sh:176-178`

**Severity**: P3 (Clarity-1 P3, Clarity-9 P3)

**Source findings**:
- Clarity-1 (P3): NUL sentinel comment at line 178
- Clarity-9 (P3): Same NUL sentinel comment at block header (lines 176-178)

**Merge rationale**: Clarity explicitly cross-referenced these two findings as the same root cause. Both refer to the same incorrect comment block describing the map file format.

**Suggested fix**: Replace the comment with accurate format description: `# Map file format (one entry per slot): <slot_name>\t<tmpfile_path>\n`

---

### RC-11: [P3] RULES.md "more portable" comment for bash-specific `[[...]]` is misleading

**Root cause**: The comment says `[[ -z "${CHANGED_FILES//[[:space:]]/}" ]]` is "simpler and more portable than the tr+sed pipeline" but `[[` and `//` parameter expansion are bash-specific, not POSIX-portable. Additionally, the CHANGED_FILES check uses `[[` while the adjacent TASK_IDS check uses `[`, creating style inconsistency.

**Affected files**: `orchestration/RULES.md:151-154`, `orchestration/RULES.md:159`

**Severity**: P3 (Clarity-3 P3, Edge-16 P3, Correctness-5 P3, Excellence-7 P3)

**Source findings**:
- Clarity-3 (P3): Mixed `[[`/`[` bracket styles in validation block
- Edge-16 (P3): Bash-specific syntax in "portability" claim
- Correctness-5 (P3): Mixed whitespace-stripping styles CHANGED_FILES vs TASK_IDS
- Excellence-7 (P3): Comment claims portability but code is bash-specific

**Merge rationale**: All 4 reviewers found aspects of the same problem: the RULES.md validation block uses bash-specific syntax while claiming portability, and applies it inconsistently between two adjacent checks. Same code block, same root cause: the refactor updated one check style but not the adjacent one, and the comment mischaracterizes the portability.

**Suggested fix**: Change the comment to "simpler (bash-specific)" and either standardize both checks to `[[...]]` or both to `[...]`.

---

### RC-12: [P3] fill-review-slots.sh undocumented assumptions and printf '%b' fragility

**Root cause**: `fill_all_slots` and `write_big_head_brief` have implicit assumptions about path content (no tabs, no `%`, no backslash sequences) that are valid for current data but undocumented. The `printf '%b'` usage could corrupt paths containing backslash-letter combinations.

**Affected files**: `scripts/fill-review-slots.sh:46,192,261,277,301-305,315`

**Severity**: P3 (Edge-1 P2 downgraded -- no live defect given 7 fixed slots; Edge-2 P2 downgraded -- safe with hex session IDs; Edge-3 P3; Edge-4 P3; Excellence-5 P3; Excellence-6 P3)

**Source findings**:
- Edge-1 (P2): _TMPFILES array cleanup logic fragile (bash arrays, ARG_MAX with many slots)
- Edge-2 (P2): DATA_FILE_PATH self-referential, tab-in-path risk
- Edge-3 (P3): printf '%b' with trailing newline removal unreliable if % in path
- Edge-4 (P3): resolve_arg error message lacks file path
- Excellence-5 (P3): DATA_FILE_PATH self-referential undocumented
- Excellence-6 (P3): printf '%b' could corrupt paths with backslash

**Merge rationale**: All six findings share the root cause of undocumented assumptions in the fill-review-slots.sh data handling. Edge-1 and Edge-2 were rated P2 but are downgraded because the slot count is fixed at 7 (ARG_MAX impossible) and session IDs are hex-only (tabs/special chars impossible). The assumptions are sound for current data but should be documented.

**Priority note**: Edge reviewer rated Edge-1 and Edge-2 as P2 due to theoretical fragility, but both explicitly acknowledge "no live defect" given current constraints. P3 is appropriate for documentation-only improvements.

**Suggested fix**: Add comments documenting: (1) slot count is bounded, (2) session IDs are hex-only, (3) DATA_FILE_PATH is intentionally self-referential, (4) include file path in resolve_arg error message. Replace `printf '%b'` with `$'\n'` in bash.

---

### RC-13: [P3] scout.md references non-existent pantry-review agent type

**Root cause**: The agent exclusion list in scout.md:63 includes `pantry-review`, but RULES.md only defines `pantry-impl`. This is a stale reference from before agent consolidation.

**Affected files**: `orchestration/templates/scout.md:63`

**Severity**: P3 (Excellence-9 P3)

**Source findings**:
- Excellence-9 (P3): Stale pantry-review reference

**Merge rationale**: Single-source finding. Harmless (Scout won't find a non-existent agent to recommend) but indicates the list is not in sync with RULES.md.

**Suggested fix**: Remove `pantry-review` from the exclusions list.

---

### RC-14: [P3] RULES.md model assignment note for Nitpickers incorrectly references big-head-skeleton.md

**Root cause**: The Model Assignments table says Nitpicker model is "Set in big-head-skeleton.md" but the Nitpicker model is set by the Queen in TeamCreate, not in big-head-skeleton.md (which sets Big Head's model).

**Affected files**: `orchestration/RULES.md:301`

**Severity**: P3 (Excellence-10 P3)

**Source findings**:
- Excellence-10 (P3): Misleading model assignment note

**Merge rationale**: Single-source finding.

**Suggested fix**: Change to "Set by Queen in TeamCreate prompt".

---

### RC-15: [P3] Various minor clarity/documentation polish (not merged with other groups)

These are standalone P3 findings that do not share a root cause with any other finding:

**RC-15a**: UNREACHABLE comment ambiguous about "normal execution" qualifier
- `scripts/parse-progress-log.sh:203-206`
- Source: Clarity-7 (P3)

**RC-15b**: CONSTRAINT comment header inconsistent style in reviews.md shell block
- `orchestration/templates/reviews.md:513-515`
- Source: Clarity-8 (P3)

**RC-15c**: Nested markdown code fence mismatch in SETUP.md
- `orchestration/SETUP.md:36-56`
- Source: Clarity-10 (P3)

**RC-15d**: parse-progress-log.sh corrupt ordering causes false SESSION_COMPLETE
- `scripts/parse-progress-log.sh:164-176`
- Source: Edge-6 (P2 -- downgraded to P3; the log is append-only and corruption requires manual editing, as the reviewer noted)

**RC-15e**: resume-plan.md overwrite warning on stderr (confirmed correct behavior)
- Source: Edge-7 (P3) -- no action needed

**RC-15f**: scrub-pii.sh TOCTOU between grep -q and grep -c (not a live defect)
- Source: Edge-8 (P3) -- no action needed

**RC-15g**: Edge-5 confirmed REVIEW_ROUND=0 rejection is correct -- not a defect
- Source: Edge-5 (P3) -- no action needed

---

## Deduplication Log

| Raw Finding | Consolidated RC | Merge Reason |
|-------------|----------------|--------------|
| Correctness-1 (P1) | RC-1 | Core finding: extract_agent_section empty output |
| Clarity-4 (P3) | RC-1 | Same function, stale docstring for same awk change |
| Edge-15 (P3) | RC-1 | Same awk regex fragility in same function |
| Excellence-1 (P2) | RC-2 | Sole finding for BSD grep \s issue |
| Edge-9 (P2) | RC-3 | --delete removal without _archive/ exclusion |
| Edge-10 (P2) | RC-3 | Same rsync command, _archive/ not excluded |
| Clarity-6 (P3) | RC-3 | Documentation gap for same rsync change |
| Edge-13 (P2) | RC-4 | REVIEW_ROUND not in placeholder guard |
| Excellence-4 (P2) | RC-4 | Same finding independently discovered |
| Edge-14 (P3) | RC-4 | Broader placeholder guard maintenance concern |
| Excellence-2 (P2) | RC-5 | SETUP.md bd show contradiction |
| Correctness-2 (P2) | RC-6 | Stale TIMED_OUT reference in big-head-skeleton |
| Clarity-2 (P3) | RC-6 | Same rename, missing inline comment |
| Edge-12 (P2) | RC-7 | Missing scrub-pii.sh installs blocking hook |
| Clarity-5 (P3) | RC-8 | Pre-commit backup lacks error handling |
| Edge-11 (P3) | RC-8 | Same finding -- pre-commit backup |
| Correctness-3 (P3) | RC-8 | Same finding -- inconsistent hardening |
| Excellence-8 (P3) | RC-8 | Same finding -- defensive programming |
| Correctness-4 (P3) | RC-9 | Regex comment claims 2+ but matches 1+ |
| Excellence-3 (P2) | RC-9 | Same finding, downgraded to P3 |
| Clarity-1 (P3) | RC-10 | NUL sentinel comment incorrect |
| Clarity-9 (P3) | RC-10 | Same comment, block header |
| Clarity-3 (P3) | RC-11 | Mixed bracket styles in RULES.md |
| Edge-16 (P3) | RC-11 | Bash-specific "portability" claim |
| Correctness-5 (P3) | RC-11 | Mixed styles CHANGED_FILES vs TASK_IDS |
| Excellence-7 (P3) | RC-11 | Same portability comment |
| Edge-1 (P2) | RC-12 | Undocumented assumptions in fill-review-slots |
| Edge-2 (P2) | RC-12 | Same file, path assumptions |
| Edge-3 (P3) | RC-12 | Same file, printf '%b' fragility |
| Edge-4 (P3) | RC-12 | Same file, error message |
| Excellence-5 (P3) | RC-12 | Same file, self-referential path |
| Excellence-6 (P3) | RC-12 | Same file, printf '%b' risk |
| Excellence-9 (P3) | RC-13 | Stale pantry-review reference |
| Excellence-10 (P3) | RC-14 | Misleading model assignment note |
| Clarity-7 (P3) | RC-15a | Standalone -- UNREACHABLE comment |
| Clarity-8 (P3) | RC-15b | Standalone -- comment style inconsistency |
| Clarity-10 (P3) | RC-15c | Standalone -- nested code fence |
| Edge-6 (P2) | RC-15d | Standalone -- corrupt ordering (downgraded) |
| Edge-7 (P3) | RC-15e | Standalone -- confirmed correct (no action) |
| Edge-8 (P3) | RC-15f | Standalone -- TOCTOU not live (no action) |
| Edge-5 (P3) | RC-15g | Standalone -- confirmed correct (no action) |

---

## Priority Breakdown

| Priority | Count | Root Causes |
|----------|-------|-------------|
| P1 | 1 | RC-1 (extract_agent_section empty output) |
| P2 | 6 | RC-2, RC-3, RC-4, RC-5, RC-6, RC-7 |
| P3 | 8 | RC-8, RC-9, RC-10, RC-11, RC-12, RC-13, RC-14, RC-15 |
| **Total** | **15** | 41 raw findings consolidated to 15 root causes |

---

## Overall Verdict

**NEEDS WORK** -- 1 P1 blocker must be resolved.

RC-1 is a critical regression that silently breaks the entire review pipeline by producing empty agent instruction bodies. The 6 P2 issues are all addressable with targeted fixes (BSD grep portability, rsync exclusion, placeholder guard, stale documentation, pre-commit hook behavior). The 8 P3 root causes are documentation and polish items appropriate for the Queen's standard P3 flow.

**Score**: 6.5/10 (weighted average across reviewers: Clarity 8.5, Edge Cases 6.5, Correctness 6.0, Excellence 7.5)
