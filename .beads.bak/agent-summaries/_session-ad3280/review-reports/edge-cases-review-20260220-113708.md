# Edge Cases Review Report

**Review type**: edge-cases
**Reviewer**: Nitpicker (Edge Cases)
**Commit range**: 201ee96~1..HEAD
**Review round**: 1
**Timestamp**: 20260220-113708

---

## Findings Catalog

### Finding 1
- **File**: `/Users/correy/projects/ant-farm/scripts/fill-review-slots.sh:236-238`
- **Severity**: P2
- **Category**: Data truncation / incorrect string construction
- **Description**: The `write_big_head_brief` function builds `expected_paths` by appending `\n`-terminated lines with `printf '%b'`, then uses `sed '$d'` to "remove trailing newline." However, `sed '$d'` deletes the *last line* of the output, not a trailing newline character. When there are exactly 2 review types (round 2+), this means the expected paths list will contain only the first review type's path — the second type's path is deleted entirely. For round 1 (4 types), the last type (excellence) would be missing from the expected paths list. Big Head would then not know to wait for all reviewer reports.
- **Suggested fix**: Replace `sed '$d'` with a proper trailing-newline strip. For example, use `printf '%b' "$expected_paths"` piped to `sed '/^$/d'` to remove blank lines, or build the list without a trailing `\n` on the last entry (e.g., use a separator-first approach).

### Finding 2
- **File**: `/Users/correy/projects/ant-farm/scripts/fill-review-slots.sh:151-183`
- **Severity**: P2
- **Category**: Substitution corruption with special characters
- **Description**: The `fill_slot` function uses awk `sub()` for replacement. Awk's `sub()` interprets `&` in the replacement string as "the matched text." If any slot value contains an `&` character (e.g., a commit range like `abc&def`, or a file path containing `&`), the substitution will silently corrupt the output by inserting the matched slot marker text at each `&` position. While `&` in file paths is uncommon, it is a valid character and the script does not validate or escape against it.
- **Suggested fix**: Escape `&` characters in the replacement value before passing to `sub()`. In the awk script, after reading `val` from the temp file, add: `gsub(/&/, "\\\\&", val)` to escape ampersands for `sub()` safety.

### Finding 3
- **File**: `/Users/correy/projects/ant-farm/scripts/fill-review-slots.sh:59-71`
- **Severity**: P3
- **Category**: Missing validation for empty resolved content
- **Description**: The `resolve_arg` function handles `@file` references and literal values. When `@file` is used and the file exists but is empty (0 bytes), `cat` returns an empty string without error. The script continues with empty `CHANGED_FILES` or `TASK_IDS`, which will produce review prompts with blank slot fills. There is no validation that the resolved content is non-empty after resolution. The `compose-review-skeletons.sh` script (Script 1) similarly does not validate the `REVIEWS_MD` content beyond file existence.
- **Suggested fix**: After resolving both `CHANGED_FILES` and `TASK_IDS`, add a guard checking that each is non-empty (or at least non-whitespace). Print a warning to stderr if empty, since an empty changed-files list would produce a useless review prompt. Consider whether this should be a hard error (exit 1) or a warning.

### Finding 4
- **File**: `/Users/correy/projects/ant-farm/scripts/fill-review-slots.sh:78-83`
- **Severity**: P3
- **Category**: Review round 0 accepted as valid
- **Description**: The review round validation uses `grep -qE '^[0-9]+$'` which accepts `0` as a valid round number. The review system uses 1-based rounds (round 1, round 2+). A round of `0` would pass validation but produce incorrect behavior: the `-eq 1` check on line 137 would fall through to the `else` branch, producing only 2 review types (correctness, edge-cases) as if it were round 2+. This would silently skip clarity and excellence reviews on what should be a full first round.
- **Suggested fix**: Change the validation to reject 0: `grep -qE '^[1-9][0-9]*$'` or add an explicit check `if [ "$REVIEW_ROUND" -lt 1 ]`.

### Finding 5
- **File**: `/Users/correy/projects/ant-farm/scripts/compose-review-skeletons.sh:71-74`
- **Severity**: P3
- **Category**: Multiple YAML frontmatter delimiters cause incorrect extraction
- **Description**: The `extract_agent_section` function uses `awk '/^---$/{found=1; next} found{print}'` to extract everything after the first `---` line. However, YAML frontmatter in skeleton template files uses a pair of `---` delimiters (opening and closing). This awk pattern starts printing after the *first* `---` it encounters, which would include the YAML frontmatter content between the two `---` delimiters. The function's comment says "everything after the line containing only '---'" but the intent is everything after the *closing* `---` of the frontmatter. If the frontmatter body contains fields that look like template instructions, they would be included in the skeleton body.
- **Suggested fix**: Use an awk pattern that skips the frontmatter block entirely: count `---` occurrences and start printing after the second one. Example: `awk '/^---$/{count++; next} count>=2{print}'`.

### Finding 6
- **File**: `/Users/correy/projects/ant-farm/scripts/compose-review-skeletons.sh:99-102`
- **Severity**: P3
- **Category**: Overly broad sed regex for placeholder conversion
- **Description**: The sed pattern `s/{\([A-Z][A-Z_]*\)}/{{\1}}/g` converts any `{UPPERCASE_WORD}` to `{{UPPERCASE_WORD}}`. This is intentional for slot markers, but it would also convert any legitimate single-brace uppercase references in the skeleton template content that are NOT meant to be slot markers. For example, if the template contains literal text like "See {README}" or code examples with `{HTTP}`, these would be incorrectly double-braced. The script relies on the convention that all single-brace uppercase tokens in the skeleton templates are intended as slot markers, but this assumption is not validated.
- **Suggested fix**: This is low risk given the current templates, but consider either: (a) using a whitelist of known slot names instead of a blanket regex, or (b) adding a comment documenting the assumption that templates must not contain non-slot `{UPPERCASE}` patterns.

### Finding 7
- **File**: `/Users/correy/projects/ant-farm/scripts/fill-review-slots.sh:151-183`
- **Severity**: P3
- **Category**: Temp file cleanup on abnormal exit
- **Description**: The `fill_slot` function creates a temp file with `mktemp` on line 158 and removes it on line 182. If the awk command or the `mv` on line 180 fails (triggering the `set -e` exit), the temp file is not cleaned up. Over many failed runs, orphaned temp files could accumulate in `/tmp`. Additionally, the `${file}.tmp` intermediate file created by awk on line 180 is not cleaned up on failure either.
- **Suggested fix**: Add a `trap` at the top of the script to clean up temp files on exit: `trap 'rm -f "$tmpval" "${file}.tmp" 2>/dev/null' EXIT`. Alternatively, since `set -e` will exit the entire script on failure, a top-level trap is more appropriate than per-function cleanup.

### Finding 8
- **File**: `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh:27-33`
- **Severity**: P3
- **Category**: Missing source scripts not reported
- **Description**: The sync loop on line 27 uses `[ -f "$script" ] || continue` to silently skip missing script files. If `compose-review-skeletons.sh` or `fill-review-slots.sh` is accidentally deleted or renamed in the repo, the sync would silently skip it without warning. The synced `~/.claude/orchestration/scripts/` directory would then contain stale versions of the scripts (or nothing at all if it is a fresh sync), leading to confusing runtime failures when the Queen invokes them.
- **Suggested fix**: Add a warning to stderr when a script file is missing: `echo "[ant-farm] WARNING: Script not found, skipping: $script" >&2` instead of a bare `continue`. Alternatively, treat missing scripts as an error since they are expected to exist.

### Finding 9
- **File**: `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh:23`
- **Severity**: P3
- **Category**: rsync --delete may remove scripts directory
- **Description**: Line 23 syncs `orchestration/` with `rsync --delete`, which removes files in the target that do not exist in the source. The scripts are stored in `scripts/` (repo root), NOT in `orchestration/scripts/`. However, lines 28-33 copy scripts into `~/.claude/orchestration/scripts/`. If the sync script runs again, the `rsync --delete` on line 23 would delete `~/.claude/orchestration/scripts/` (because `orchestration/scripts/` does not exist in the repo source), then lines 28-33 would recreate it. This creates a race-condition-like ordering dependency: `rsync --delete` must run before the script copy. Currently the ordering is correct (rsync on line 23, script copy on lines 27-33), but this is fragile — if the order were ever reversed, scripts would be deleted after being copied.
- **Suggested fix**: Add `--exclude=scripts/` to the rsync command to protect the scripts directory from deletion: `rsync -av --delete --exclude='scripts/' "$REPO_ROOT/orchestration/" ~/.claude/orchestration/`. This makes the ordering irrelevant and protects against future refactoring.

### Finding 10
- **File**: `/Users/correy/projects/ant-farm/orchestration/templates/scout.md:61`
- **Severity**: P3
- **Category**: Stale exclusion list entry
- **Description**: The exclusion list for Dirt Pusher recommendations includes `pantry-review`, which was deprecated in this commit range (RULES.md now marks it as `~~pantry-review~~` with strikethrough). While keeping it in the exclusion list is harmless (it will simply never match), it creates a maintenance inconsistency: the Scout references an agent type that the rest of the system considers deprecated.
- **Suggested fix**: Either remove `pantry-review` from the exclusion list or add a comment noting it is retained for backwards compatibility. Low priority since it causes no functional issue.

---

## Preliminary Groupings

### Group A: String/text manipulation edge cases in fill-review-slots.sh (Findings 1, 2)
**Root cause**: The `fill_slot` helper and `write_big_head_brief` function use text manipulation patterns (awk `sub()` and `sed '$d'`) that have well-known gotchas with special characters and line-counting semantics. These are independent bugs but share the pattern of "shell text processing with implicit assumptions about content."

### Group B: Input validation gaps in scripts (Findings 3, 4)
**Root cause**: Both scripts validate argument count and file existence but do not validate the semantic content of the arguments (empty content, out-of-range values). The validation is structural but not semantic.

### Group C: Template processing assumptions (Findings 5, 6)
**Root cause**: The `compose-review-skeletons.sh` script makes assumptions about the structure of its input templates (single `---` delimiter, no non-slot `{UPPERCASE}` patterns) that are not enforced or validated.

### Group D: File lifecycle / cleanup (Findings 7, 8, 9)
**Root cause**: Temp files, synced scripts, and rsync-managed directories have lifecycle assumptions that could lead to stale or orphaned artifacts under non-happy-path conditions.

### Group E: Stale reference (Finding 10)
**Root cause**: The deprecation of `pantry-review` was not fully propagated to all files that reference it.

---

## Summary Statistics

| Severity | Count |
|----------|-------|
| P1       | 0     |
| P2       | 2     |
| P3       | 8     |
| **Total**| **10** |

---

## Cross-Review Messages

| Direction | Recipient | Content | Finding Ref |
|-----------|-----------|---------|-------------|
| (none sent) | — | No cross-domain issues requiring another reviewer's attention were identified. All findings fall within edge-cases scope (input validation, boundary conditions, error handling, I/O operations). | — |

---

## Coverage Log

| File | Path | Findings | Status |
|------|------|----------|--------|
| agents/big-head.md | `/Users/correy/projects/ant-farm/agents/big-head.md` | 0 | Reviewed: No edge-case issues found. Changes add severity conflict guidance which is documentation-only. |
| agents/nitpicker.md | `/Users/correy/projects/ant-farm/agents/nitpicker.md` | 0 | Reviewed: No edge-case issues found. Changes add per-type specialization blocks which are documentation/instruction content. |
| orchestration/RULES.md | `/Users/correy/projects/ant-farm/orchestration/RULES.md` | 0 | Reviewed: No edge-case issues found. Changes update Step 3b workflow and deprecate pantry-review references. |
| orchestration/templates/pantry.md | `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md` | 0 | Reviewed: No edge-case issues found. Changes add Step 2.5 and deprecation notice, both documentation. |
| orchestration/templates/scout.md | `/Users/correy/projects/ant-farm/orchestration/templates/scout.md` | 1 (Finding 10) | Reviewed: One stale reference found in exclusion list. |
| scripts/compose-review-skeletons.sh | `/Users/correy/projects/ant-farm/scripts/compose-review-skeletons.sh` | 2 (Findings 5, 6) | Reviewed: Template extraction and placeholder conversion have edge-case assumptions. |
| scripts/fill-review-slots.sh | `/Users/correy/projects/ant-farm/scripts/fill-review-slots.sh` | 5 (Findings 1, 2, 3, 4, 7) | Reviewed: Most findings concentrated here as the primary new executable code. |
| scripts/sync-to-claude.sh | `/Users/correy/projects/ant-farm/scripts/sync-to-claude.sh` | 2 (Findings 8, 9) | Reviewed: Script sync and rsync ordering issues. |

---

## Overall Assessment

**Score**: 7 / 10

**Verdict**: PASS WITH ISSUES

**Rationale**: The two new bash scripts (`compose-review-skeletons.sh` and `fill-review-slots.sh`) are well-structured with good argument validation, output verification, and clear error messages. The documentation changes (nitpicker specializations, big-head severity conflicts, scout tie-breaking) are clean and internally consistent.

The two P2 findings are substantive: Finding 1 (`sed '$d'` deleting the last report path instead of a trailing newline) would cause Big Head to receive an incomplete list of expected report paths, potentially blocking or confusing the consolidation step. Finding 2 (awk `sub()` ampersand interpretation) is a latent corruption risk that would manifest if any slot value contains `&`.

The P3 findings are genuine but low-impact: they represent defensive checks that would only matter in unusual conditions (empty files, round 0, stale agent names, temp file leaks). The core happy-path functionality appears solid.
