# Report: Edge Cases Review

**Scope**: orchestration/RULES.md, orchestration/SETUP.md, orchestration/reference/dependency-analysis.md, orchestration/templates/checkpoints.md, orchestration/templates/implementation.md, orchestration/templates/reviews.md, orchestration/templates/scout.md, scripts/compose-review-skeletons.sh, scripts/fill-review-slots.sh, scripts/install-hooks.sh, scripts/parse-progress-log.sh, scripts/scrub-pii.sh, scripts/sync-to-claude.sh
**Reviewer**: Edge Cases Review | nitpicker (sonnet)

---

## Findings Catalog

### Finding 1: fill-review-slots.sh — `_TMPFILES` array cleanup is bash-only; script header claims portability

- **File(s)**: `scripts/fill-review-slots.sh:46` (declaration `_TMPFILES=()`), `scripts/fill-review-slots.sh:192` (`_TMPFILES+=("$mapfile")`)
- **Severity**: P2
- **Category**: edge-case
- **Description**: The comment in `fill_all_slots` claims the awk-based approach is chosen because it avoids "awk -v multiline and special-character limitations", but the cleanup mechanism — `_TMPFILES=()`, `_TMPFILES+=("$tmpval")`, and `local -a tmpfiles=()` — all use bash arrays, which are a bash-ism. The script's shebang is `#!/usr/bin/env bash` and uses `set -euo pipefail`, so it is bash. The issue is the `local -a tmpfiles=()` on line 194: `local -a` is valid in bash but the combination with `local` declarations inside a while loop (`while [ $# -ge 2 ]`) means each loop iteration appends to a local array that is then passed to `rm -f` after the loop. This is correct *in bash*, but if the array ever grows large (many slots), the `rm -f "${tmpfiles[@]}"` on line 248 will pass all paths as arguments to a single `rm` invocation, which can exceed `ARG_MAX` on some platforms when there are many slots. In practice the slot count is bounded (7 slots), so this is not a live defect. However, the primary edge case is subtler: `_TMPFILES+=("${file}.tmp")` on line 212 registers `${file}.tmp` with the EXIT trap **before** the awk invocation — if `mv "${file}.tmp" "$file"` succeeds, the `.tmp` file no longer exists, but `rm -f` is silent on missing files, so the EXIT trap is harmless. If awk writes `${file}.tmp` and then `mv` fails (disk full), the EXIT trap will remove `${file}.tmp`, which is correct. The concern is the reverse: if `awk ... > "${file}.tmp"` itself fails mid-write (disk full), `set -e` triggers EXIT before `mv`, and the EXIT trap correctly removes the partial `.tmp`. No live defect but the logic is fragile and worth documenting.
- **Suggested fix**: Add a comment at line 212 explaining why `${file}.tmp` is registered *before* the awk invocation: "Registered before awk write so EXIT trap removes partial .tmp on awk failure." This clarifies intent and prevents a future editor from reordering the `_TMPFILES+=` after the awk call.
- **Cross-reference**: None

---

### Finding 2: fill-review-slots.sh — `write_big_head_brief` passes `$out_file` as `{{DATA_FILE_PATH}}` value, substituting the file into itself

- **File(s)**: `scripts/fill-review-slots.sh:315` (`"{{DATA_FILE_PATH}}"  "$out_file"`)
- **Severity**: P2
- **Category**: edge-case
- **Description**: `write_big_head_brief` fills `{{DATA_FILE_PATH}}` with `$out_file`, which is the path of the file being modified in-place by `fill_all_slots`. This means `fill_all_slots` is reading `$out_file`, substituting `{{DATA_FILE_PATH}}` with the value of `$out_file` (the same path), and writing the result back to `$out_file`. If `{{DATA_FILE_PATH}}` itself contains `{{` or `}}` sequences (impossible here since it is a filesystem path), this would cause infinite substitution. The real edge case: `$out_file` is `${SESSION_DIR}/prompts/review-big-head-consolidation.md`. If that path happens to contain the string `{{DATA_FILE_PATH}}` (it does — before substitution), the substitution replaces it with the path itself. After substitution, the path is embedded verbatim. Correct behavior. BUT: the `fill_all_slots` function uses an atomic `awk ... > "${file}.tmp" && mv "${file}.tmp" "$file"` pattern. When `$out_file` is both the input file to awk and the target of `mv`, and awk reads `$out_file` while awk also writes to `${out_file}.tmp`, there is no race: awk reads from `$out_file` and writes to a different file (`${file}.tmp`). This is safe. However, the slot value for `{{DATA_FILE_PATH}}` is `$out_file`, which is the path that is currently being modified. After `fill_all_slots` completes, the file at `$out_file` will contain its own path embedded. This is intentional (self-referential data-file path for Big Head), but if the session directory path contains special awk metacharacters (e.g., `&`, `\`), the `while ((pos = index(line, slot_name)) > 0)` substitution loop uses `substr` concatenation (not `sub`/`gsub`), so it is safe from `&` expansion. The actual edge case that remains: a session directory path containing a tab character would corrupt the map-file format (`printf '%s\t%s\n'`), since the map file uses `\t` as a separator between slot name and tmpfile path. Session IDs are generated via `shasum | head -c 8` (hex), so tabs cannot appear in the path. Low practical risk, but undocumented.
- **Suggested fix**: Add a comment at the map-file format specification (line 207 area) noting the tab-separator limitation: "Assumption: slot names and tmpfile paths do not contain tab characters. Session paths are hex-only (safe). Custom paths with tabs would corrupt map parsing."
- **Cross-reference**: None

---

### Finding 3: fill-review-slots.sh — `write_big_head_brief` builds `expected_paths` with `printf '%b'` and `sed '/^$/d'`, but the trailing-newline removal is unreliable

- **File(s)**: `scripts/fill-review-slots.sh:301–305`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The loop appends `\n` literally to `expected_paths`:
  ```bash
  expected_paths="${expected_paths}- ${SESSION_DIR}/review-reports/${rt}-review-${TIMESTAMP}.md\n"
  ```
  Then:
  ```bash
  expected_paths="$(printf '%b' "$expected_paths" | sed '/^$/d')"
  ```
  `printf '%b'` interprets the literal `\n` sequences as newlines. `sed '/^$/d'` deletes empty lines, which removes the trailing blank line introduced by the last `\n`. This works correctly on macOS and Linux. However, if `SESSION_DIR` or `TIMESTAMP` contains a `%` character, `printf '%b'` would interpret it as a format specifier. Session IDs are hex (no `%`), and `TIMESTAMP` is `YYYYMMDD-HHmmss` (no `%`), so this is safe in practice. The edge case is: a future caller passing unusual values through. No validation guards against `%` in `TIMESTAMP` or `SESSION_DIR`.
- **Suggested fix**: Prefer `printf '%s\n'` in the loop instead of accumulating `\n` literals, then strip trailing newline with a different method. Or add an explicit validation that `TIMESTAMP` matches `^[0-9]{8}-[0-9]{6}$` before use — this is already implicitly assumed by the slot-fill contract but is not enforced.
- **Cross-reference**: None

---

### Finding 4: fill-review-slots.sh — `resolve_arg` empty-file check (new `! -s`) can mask intentionally empty argument files

- **File(s)**: `scripts/fill-review-slots.sh:87–90`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The new check `if [ ! -s "$fpath" ]; then ... exit 1; fi` rejects a zero-byte `@file` argument. This is correct for `CHANGED_FILES` and `TASK_IDS`, which must be non-empty. However, the function is generic and shared; any future caller passing an optional `@file` argument that might legitimately be empty would be blocked. The error message "ERROR: @file argument is empty (0 bytes)" does not tell the caller which argument was empty (CHANGED_FILES or TASK_IDS), making diagnosis harder when there are multiple `@file` arguments.
- **Suggested fix**: Include the file path in the error message: `"ERROR: @file argument is empty (0 bytes): $fpath — $(basename $fpath) must not be empty"`. This is a minor diagnostic improvement.
- **Cross-reference**: None

---

### Finding 5: fill-review-slots.sh — `REVIEW_ROUND=0` is now correctly rejected, but the error message says ">= 1" while the old message just said "positive integer"

- **File(s)**: `scripts/fill-review-slots.sh:103–106`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The validation was tightened from `^[0-9]+$` (which accepted `0`) to `^[1-9][0-9]*$` (which requires >= 1). The new error message "ERROR: REVIEW_ROUND must be a positive integer (>= 1), got: $REVIEW_ROUND" is clearer. No defect. This is a note confirming correctness of the fix.
- **Suggested fix**: No change needed. Confirmed correct.
- **Cross-reference**: None

---

### Finding 6: parse-progress-log.sh — malformed log lines with a valid `step_key` but a malformed timestamp are skipped, but the `step_key` check happens BEFORE the timestamp check

- **File(s)**: `scripts/parse-progress-log.sh:164–176`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The parsing loop does:
  ```bash
  [ -z "$step_key" ] && continue
  if ! [[ "$timestamp" =~ ^[0-9]{4}-... ]]; then
      echo "WARNING: Skipping malformed ..."
      continue
  fi
  map_set "completed" "$step_key" "yes"
  ```
  A blank-line check (`step_key` empty) comes first, then timestamp validation. This means a line like `|SESSION_INIT|extra` (empty timestamp field, non-empty step_key) would pass the blank-line check and then be rejected by the timestamp regex. Correct behavior. But a line like `SESSION_INIT|` (timestamp = "SESSION_INIT", step_key = "") would pass as an empty step_key and be `continue`d. Also correct.

  The actual edge case: a log line like `2026-02-20T23:10:26|SESSION_INIT|pushed=true|extra_pipe_field` — here `rest` would be `pushed=true|extra_pipe_field` because `IFS='|' read -r timestamp step_key rest` assigns everything after the second `|` to `rest`. Since `rest` is only used for `map_set "details"`, extra pipe characters in the details field are benign.

  The real gap: a line with EXACTLY the right format but where `step_key` is a known key (e.g., `SESSION_COMPLETE`) that appears BEFORE it should in a corrupt log would cause `exit 2` (session already completed). There is no validation that the SESSION_COMPLETE step is last. A corrupted log with `SESSION_COMPLETE` in the middle would cause false "session already complete" reporting. The new timestamp validation mitigates injected lines but does not protect against valid-timestamp corrupt ordering.
- **Suggested fix**: Document this known limitation in a comment: "A corrupt log with SESSION_COMPLETE logged before other steps will cause exit 2 (false 'already complete'). Mitigation: the log is append-only; corruption requires manual editing. If suspected, user should inspect the log directly."
- **Cross-reference**: None

---

### Finding 7: parse-progress-log.sh — overwrite warning for resume-plan.md uses stderr but does not surface to the caller

- **File(s)**: `scripts/parse-progress-log.sh:216–218`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The new `WARNING: Overwriting existing resume plan` check correctly warns on stderr. However, the RULES.md crash recovery protocol (Step 0) says the Queen runs this script and reads `resume-plan.md`. If the script is re-run after a partial failure, the overwrite warning is emitted on stderr but the Queen's prompt only checks exit code. The warning is informational only, but a Queen prompt that captures only stdout would silently miss the warning. Low risk since the Queen spawns this as a Bash tool call which captures stderr too in Claude Code.
- **Suggested fix**: No action needed; the warning is correctly surfaced on stderr which Claude Code captures.
- **Cross-reference**: None

---

### Finding 8: scrub-pii.sh — `grep -cE` with `|| true` guard: comment says "grep -c returns exit code 1 when match count is zero", but this branch is only reached when `grep -q` confirmed a match exists

- **File(s)**: `scripts/scrub-pii.sh:70`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The comment correctly explains the `|| true` guard. However, there is a subtle TOCTOU (time-of-check-time-of-use) between the `grep -qE` check and the `grep -cE` call: if the file is modified between the two greps (extremely unlikely for a local file in a hook context), the `-c` call could return 0 even without `|| true`. In practice, hooks run atomically and no external process modifies `issues.jsonl` mid-hook. This is a documentation-quality note, not a live defect. The `|| true` guard is the right defensive pattern.
- **Suggested fix**: No change needed; comment and implementation are correct.
- **Cross-reference**: None

---

### Finding 9: sync-to-claude.sh — removed `--delete` from rsync: stale files in `~/.claude/orchestration/` are never cleaned up

- **File(s)**: `scripts/sync-to-claude.sh:27` (`rsync -av --exclude='scripts/' ...`)
- **Severity**: P2
- **Category**: edge-case
- **Description**: The diff removed `--delete` from the rsync command with the stated rationale: "preserves any custom files adopters have placed under `~/.claude/orchestration/`." The edge case: when a source file is *renamed* or *deleted* in the repo, its old path persists in `~/.claude/orchestration/` forever. For example, if `orchestration/_archive/colony-tsa.md` was previously synced and then `_archive/` was added to the exclusion list, the archived file would persist in `~/.claude/orchestration/_archive/colony-tsa.md`. More critically: the `_archive/` directory is explicitly flagged as FORBIDDEN in RULES.md ("contains deprecated documents that contradict current workflows"). If `_archive/` files were synced in a previous push (before the exclusion was added), they remain at `~/.claude/orchestration/_archive/` and could be read by agents using glob patterns. There is no way for the current rsync to clean them up. The comment says "If you need to remove a stale source file from the target, delete it manually from `~/.claude/orchestration/`." This is correct but puts the burden on the user and is easy to miss.
- **Suggested fix**: Either restore `--delete` with an explicit exclusion of user-added paths, or add a one-time cleanup step in the comments that lists known stale files to remove (e.g., `rm -rf ~/.claude/orchestration/_archive/`). At minimum, add a note: "Stale files from renamed/deleted sources persist in target. Manually remove ~/.claude/orchestration/_archive/ if it exists from a prior sync." Cross-reference RULES.md prohibition on `_archive/`.
- **Cross-reference**: RULES.md line 273 (`NEVER READ: orchestration/_archive/`). Finding 9 and Finding 10 share this root cause.

---

### Finding 10: sync-to-claude.sh — `_archive/` exclusion absent from rsync; previously-synced archive files remain dangerous

- **File(s)**: `scripts/sync-to-claude.sh:27`
- **Severity**: P2
- **Category**: edge-case
- **Description**: This is a direct consequence of Finding 9. The rsync command does NOT exclude `_archive/` from the source sync. If `orchestration/_archive/` exists in the repo and was previously synced, those files now live at `~/.claude/orchestration/_archive/`. Without `--delete`, subsequent syncs do not remove them. RULES.md explicitly prohibits reading `_archive/` files: "A glob like `orchestration/**/*.md` will match these stale files. Exclude `_archive/` from all searches and reads." This prohibition is runtime advice for LLMs; it does not prevent filesystem access. An agent using a glob that matches `_archive/` files would read stale, contradictory instructions.
- **Suggested fix**: Add `--exclude='_archive/'` to the rsync command to prevent syncing `_archive/` files in the first place:
  ```bash
  rsync -av --exclude='scripts/' --exclude='_archive/' "$REPO_ROOT/orchestration/" ~/.claude/orchestration/
  ```
  This is the minimal fix. The broader issue (stale files from prior syncs) still requires manual cleanup.
- **Cross-reference**: Finding 9 (same root cause: removal of `--delete` without adding exclusions for known-dangerous directories).

---

### Finding 11: install-hooks.sh — pre-commit backup of existing hook does not have explicit error handling (unlike the pre-push backup)

- **File(s)**: `scripts/install-hooks.sh:69–71`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The pre-push hook backup was upgraded to explicit error handling:
  ```bash
  if ! cp "$HOOK_TARGET" "$BACKUP"; then
      echo "ERROR: Failed to back up ..." >&2
      exit 1
  fi
  ```
  But the pre-commit hook backup (line 69–71) retained the old pattern:
  ```bash
  cp "$PRECOMMIT_TARGET" "$BACKUP"
  ```
  Under `set -euo pipefail`, a failed `cp` (disk full, permission denied) would terminate the script with a generic exit code and no diagnostic message, just as the pre-push case used to do. The fix was applied asymmetrically.
- **Suggested fix**: Apply the same explicit error handling to the pre-commit backup:
  ```bash
  if ! cp "$PRECOMMIT_TARGET" "$BACKUP"; then
      echo "ERROR: Failed to back up $PRECOMMIT_TARGET to $BACKUP — aborting. Check permissions and disk space." >&2
      exit 1
  fi
  ```
- **Cross-reference**: Finding 11 and Finding 12 share the root cause: asymmetric hardening between pre-push and pre-commit hook installation.

---

### Finding 12: install-hooks.sh — pre-commit hook installs even if the scrub-pii.sh file is missing; the warning does not abort

- **File(s)**: `scripts/install-hooks.sh:103–109`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The final block of `install-hooks.sh` warns if `scrub-pii.sh` is not found:
  ```bash
  if [[ -f "$SCRUB_SCRIPT_PATH" ]]; then
      chmod +x "$SCRUB_SCRIPT_PATH"
  else
      echo "WARNING: scripts/scrub-pii.sh not found — pre-commit hook will block commits until it is present." >&2
  fi
  ```
  The pre-commit hook is installed regardless, with a hook body that will `exit 1` if `scrub-pii.sh` is not executable. This means: install succeeds, but the first commit after this state is blocked. The operator is warned via stderr, but the install itself is not aborted. This is a deliberate "non-fatal" design for the pre-commit hook (mirrors the pre-push hook's non-fatal sync failure). However, the consequence here is worse: the pre-push hook only skips the sync (git push succeeds), whereas the pre-commit hook blocks all commits. The comment says "pre-commit hook will block commits until it is present" which is accurate but might surprise users.
- **Suggested fix**: Either escalate the pre-commit warning to an error that aborts installation if `scrub-pii.sh` is absent, or change the hook body to emit a non-fatal warning instead of `exit 1` when `scrub-pii.sh` is missing. The current behavior (warn on install, block on commit) is an asymmetric severity. Document the deliberate design choice if it is intentional.
- **Cross-reference**: Finding 12 is standalone.

---

### Finding 13: reviews.md — `REVIEW_ROUND={{REVIEW_ROUND}}` in the shell polling script is a double-brace slot marker embedded in template prose; if `fill-review-slots.sh` fails to substitute it, the shell script emits a syntax error, not a clear placeholder error

- **File(s)**: `orchestration/templates/reviews.md:502` (`REVIEW_ROUND={{REVIEW_ROUND}}`)
- **Severity**: P2
- **Category**: edge-case
- **Description**: The polling loop script in `reviews.md` now declares:
  ```bash
  REVIEW_ROUND={{REVIEW_ROUND}}
  ```
  This is a shell statement where `{{REVIEW_ROUND}}` is a slot marker to be replaced by `fill-review-slots.sh` with an integer (e.g., `1`). The placeholder guard at lines 519–553 checks for `<angle-bracket>` and `{curly-brace}` patterns in the *report paths*, but it does NOT check whether `{{REVIEW_ROUND}}` itself was substituted before the script runs. If Big Head receives this brief with `{{REVIEW_ROUND}}` unsubstituted (e.g., if `fill-review-slots.sh` was not invoked or silently failed), the shell would interpret `REVIEW_ROUND={{REVIEW_ROUND}}` as a valid assignment, setting `REVIEW_ROUND` to the literal string `{{REVIEW_ROUND}}`. Then `if [ "$REVIEW_ROUND" -eq 1 ]` would produce a `[: {{REVIEW_ROUND}}: integer expression expected` error, which is confusing but does terminate the script.

  The placeholder guard at lines 519–553 does guard against `{` and `}` characters in the *file paths*, but only checks the specific report path variables, not `REVIEW_ROUND`. So an unsubstituted `{{REVIEW_ROUND}}` in the shell variable assignment would pass the placeholder guard and cause a runtime arithmetic error instead of a clear substitution-failure error.

  Note: `fill-review-slots.sh` does validate that all `{{...}}` markers are removed from the output files (lines 362–370). So if `fill-review-slots.sh` runs and succeeds, this is safe. The gap is: what if Big Head receives the brief from a different code path that bypasses `fill-review-slots.sh`?
- **Suggested fix**: Extend the placeholder guard to also check that `REVIEW_ROUND` was substituted — either add a check like `case "$REVIEW_ROUND" in *'{'*|*'}'*) echo "PLACEHOLDER ERROR..." ;; esac` before the `if [ "$REVIEW_ROUND" -eq 1 ]` checks, or rely on the existing `fill-review-slots.sh` unfilled-marker verification (which already catches this). The latter is preferred since `fill-review-slots.sh` already does this. Document the dependency: "This script is only valid when delivered via `fill-review-slots.sh`, which guarantees all `{{...}}` markers are substituted."
- **Cross-reference**: reviews.md line 583 (Script responsibility note) partially addresses this but does not mention the `REVIEW_ROUND` variable assignment specifically.

---

### Finding 14: reviews.md — placeholder guard checks paths for `<` and `>` but not paths that have been partially substituted (only one placeholder replaced)

- **File(s)**: `orchestration/templates/reviews.md:519–553`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The placeholder guard checks for `<` or `>` or `{` or `}` in the paths:
  ```bash
  case "$_path" in
      *'<'*|*'>'*|*'{'*|*'}'*)
  ```
  This correctly catches unsubstituted `<session-dir>` and `{{SLOT}}` patterns. However, it only checks the specific hardcoded paths listed in the `for _path in` loop. If a future review type is added (e.g., `security-review`), its expected path would need to be added to this guard manually. There is no systematic guarantee. This is a maintenance concern, not a live defect in the current code.
- **Suggested fix**: Add a comment noting the list must be kept in sync with `ACTIVE_REVIEW_TYPES` in `fill-review-slots.sh`.
- **Cross-reference**: None

---

### Finding 15: compose-review-skeletons.sh — `extract_agent_section` now uses `count>=2` (correct fix), but the second `---` delimiter must be at the start of a line exactly; trailing spaces would cause it to be missed

- **File(s)**: `scripts/compose-review-skeletons.sh:73`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The awk pattern `/^---$/` requires exactly three dashes on a line with nothing else (no trailing whitespace, no leading spaces). The fix from `found=1` to `count++; count>=2` is correct for skipping the YAML frontmatter section (between the first and second `---` delimiter) and extracting only the agent-facing content after the second `---`. If a template file has trailing whitespace on a `---` line (e.g., `--- ` with a trailing space), that line would not match `/^---$/` and `count` would not increment. The agent section would not be extracted, and `skeleton_body` would be empty. The empty check at lines 207–221 would then report an empty output file error. This is a latent bug triggered only if template files gain trailing whitespace on their delimiter lines.
- **Suggested fix**: Make the pattern more lenient: `/^---[[:space:]]*$/` to tolerate trailing whitespace on delimiter lines. Or add a note that delimiter lines must not have trailing whitespace.
- **Cross-reference**: None

---

### Finding 16: orchestration/RULES.md — `${CHANGED_FILES//[[:space:]]/}` uses bash `[[` and parameter expansion, but the RULES.md code block is presented as documentation that the Queen pastes into a shell; if the Queen's shell is not bash, this fails silently

- **File(s)**: `orchestration/RULES.md:153`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The CHANGED_FILES empty-check uses:
  ```bash
  if [[ -z "${CHANGED_FILES//[[:space:]]/}" ]]; then
  ```
  This is bash-specific (`[[` and `//` parameter expansion). The comment says "simpler and more portable than the tr+sed pipeline." The "portability" claim is relative: it is more portable in the sense of not spawning subprocesses, but `[[` and `//[[:space:]]/` are bash extensions not available in POSIX sh. If this code block is ever run in a context that invokes `sh` rather than `bash`, it would fail with a syntax error. In Claude Code's context, the Queen invokes this as a Bash tool call, which uses the system shell. If the system shell is zsh or bash, `[[` and `//` work. If it is /bin/sh (dash on Ubuntu), they fail. The comment about portability is misleading.
- **Suggested fix**: Either correct the comment to say "bash-specific but avoids subprocesses" instead of "more portable", or use a POSIX-compatible alternative: `if [ -z "$(echo "$CHANGED_FILES" | tr -d '[:space:]')" ]`. The original `tr+sed` pipeline was POSIX-compatible; the replacement is faster but less portable. The comment should reflect this accurately.
- **Cross-reference**: None

---

## Preliminary Groupings

### Group A: Asymmetric Hardening in install-hooks.sh
- Finding 11, Finding 12 — shared root cause: the pre-push hook received defensive improvements (explicit error handling for backup, extended diagnostic messages), but the pre-commit hook was not updated symmetrically. This creates inconsistent failure behavior.
- **Suggested combined fix**: Apply the same explicit error handling to the pre-commit hook backup (Finding 11) and decide whether a missing `scrub-pii.sh` should abort installation or not (Finding 12).

### Group B: stale `~/.claude/orchestration/_archive/` files from removed `--delete`
- Finding 9, Finding 10 — shared root cause: removing `--delete` from rsync was done to preserve adopter customizations, but it has the side effect of leaving dangerous `_archive/` files in place if they were previously synced. Adding `--exclude='_archive/'` to the rsync command would fix the `_archive/` problem without re-adding `--delete`.
- **Suggested combined fix**: Add `--exclude='_archive/'` to the rsync invocation.

### Group C: Undocumented assumptions in fill-review-slots.sh
- Finding 1, Finding 2, Finding 3 — all relate to implicit assumptions in `fill_all_slots` and `write_big_head_brief` about path and value content (no tabs, no `%`, safe for awk). None are live defects given current data, but the assumptions are undocumented.
- **Suggested combined fix**: Add comments documenting these assumptions in `fill_all_slots` and `write_big_head_brief`.

### Group D: `REVIEW_ROUND` placeholder substitution gaps in reviews.md
- Finding 13, Finding 14 — related: both concern the robustness of the placeholder guard for the `REVIEW_ROUND` variable and active review type paths in the polling loop template.

---

## Summary Statistics

- **Total findings**: 16
- **By severity**: P1: 0, P2: 7 (Findings 1, 2, 6, 9, 10, 12, 13), P3: 9 (Findings 3, 4, 5, 7, 8, 11, 14, 15, 16)
- **Preliminary groups**: 4

---

## Cross-Review Messages

### Sent
- To correctness-reviewer: "Finding 9/10 (sync-to-claude.sh removal of --delete leaving _archive/ files): this may be a correctness issue beyond edge-cases — specifically whether RULES.md's prohibition on reading _archive/ is enforced by the sync pipeline. Recommend correctness reviewer checks whether any acceptance criteria addressed _archive/ exclusion in the rsync fix."
- To excellence-reviewer: "Finding 16 (RULES.md CHANGED_FILES check claims portability but uses bash-specific syntax): this is both an edge case (wrong shell environment) and a documentation/clarity issue. The comment says 'more portable' but the code is bash-specific. Consider noting as a clarity finding too."

### Received
- None at time of report writing.

### Deferred Items
- None

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `orchestration/RULES.md` | Findings: #16 | 444 lines examined; Step 3b-i validation block reviewed; tmux guard block reviewed |
| `orchestration/SETUP.md` | Reviewed — no issues | 268 lines, 5 code blocks, 3 troubleshooting sections examined; minor doc-only changes in diff (verify description update); no edge-case issues |
| `orchestration/reference/dependency-analysis.md` | Reviewed — no issues | 197 lines; diff shows only example project-name substitution (`hs_website` → `my-project`); extraction algorithm unchanged; no edge-case issues |
| `orchestration/templates/checkpoints.md` | Reviewed — no issues | 718 lines examined; diff shows only project-name example substitution in 4 locations; no logic changes; no edge-case issues |
| `orchestration/templates/implementation.md` | Reviewed — no issues | 270 lines; diff shows only project-name example substitution in 5 locations; no logic changes; no edge-case issues |
| `orchestration/templates/reviews.md` | Findings: #13, #14 | 926 lines examined; polling loop refactor reviewed in detail; placeholder guard reviewed; round-aware logic reviewed |
| `orchestration/templates/scout.md` | Reviewed — no issues | 293 lines; diff shows addition of error metadata fields (Title, Type, Priority, Epic, Note) in the bd show failure template; no edge-case issues in added fields |
| `scripts/compose-review-skeletons.sh` | Findings: #15 | 235 lines; `extract_agent_section` awk fix reviewed; comment additions reviewed |
| `scripts/fill-review-slots.sh` | Findings: #1, #2, #3, #4, #5 | 398 lines; new `fill_all_slots` function reviewed in full; temp file registry and EXIT trap reviewed; `resolve_arg` empty check reviewed; round validation reviewed |
| `scripts/install-hooks.sh` | Findings: #11, #12 | 119 lines; pre-push and pre-commit hook installation blocks compared; asymmetric hardening identified |
| `scripts/parse-progress-log.sh` | Findings: #6, #7 | 293 lines; timestamp validation addition reviewed; resume-plan overwrite warning reviewed; RESUME_STEP unreachable comment reviewed |
| `scripts/scrub-pii.sh` | Findings: #8 | 83 lines; perl dependency guard reviewed; `|| true` guard reviewed; standalone reminder message reviewed |
| `scripts/sync-to-claude.sh` | Findings: #9, #10 | 68 lines; rsync flag changes reviewed; `--delete` removal rationale reviewed; `_archive/` exclusion absence noted |

---

## Overall Assessment

**Score**: 6.5/10
**Verdict**: PASS WITH ISSUES

The session's changes introduce meaningful improvements (atomic temp file cleanup, single-pass awk substitution, timestamp validation in progress.log, tmux guard, tighter REVIEW_ROUND validation). The edge-case concerns center on two clusters: (1) the removal of `--delete` from rsync without adding `--exclude='_archive/'` leaves a known-dangerous directory potentially reachable by agents; (2) the asymmetric hardening in `install-hooks.sh` (pre-push backup now has explicit error handling, pre-commit backup does not). Neither is a data-loss or security vulnerability, but the `_archive/` leak (Findings 9 and 10) could cause agent misbehavior in environments where a prior sync deposited deprecated instruction files. All P2 findings are addressable with small targeted changes.
