# Edge Cases Review Report

**Session**: 20260313-021748
**Timestamp**: 20260313-032735
**Review round**: 1
**Reviewer type**: Edge Cases
**Commit range**: 0ec9ed2^..HEAD

---

## Findings Catalog

### EC-01
**File**: `scripts/setup.sh:L100`
**Severity**: P2
**Category**: Boundary condition — glob expansion
**Description**: The agent install loop uses `for agent_file in "$REPO_ROOT/agents/"*.md`. If the `agents/` directory exists but contains no `.md` files, the glob does not expand and `$agent_file` takes the literal string `$REPO_ROOT/agents/*.md`. The subsequent `[ -f "$agent_file" ]` guard catches this and `continue`s, so no copy happens. The script does correctly emit a warning via `warn "agents/ directory exists but contains no .md files"`. However, if the directory contains no files at all (new repository state), the shell expands the glob to the literal pattern string. On bash with `nullglob` disabled (the default), this is silent misbehavior — the `[ -f ... ]` guard prevents a bad copy, but the warning about "no .md files" is only printed from the warning at L117 (`agents_installed -eq 0`), which is correct. This is borderline P2/P3: it is handled, but only coincidentally via the counter check, not by defensive glob handling.
**Suggested fix**: Add `shopt -s nullglob` before the glob (or use `find` instead), and restore it after. Alternatively, check `compgen -G "$REPO_ROOT/agents/*.md"` before entering the loop.

---

### EC-02
**File**: `scripts/setup.sh:L149`
**Severity**: P2
**Category**: File operation — find + process substitution with set -e
**Description**: The orchestration walk uses `find "$REPO_ROOT/orchestration" -type f -print0` piped via process substitution to a `while IFS= read -r -d '' src_file` loop. With `set -euo pipefail` active, if `find` exits non-zero (e.g., due to a permission error on a subdirectory), the script will abort silently mid-loop rather than logging a useful error. There is no `|| true` guard and no error message surfaced to stderr. The user would see a partial install with no explanation.
**Suggested fix**: Either capture `find` exit status explicitly:
```bash
find "$REPO_ROOT/orchestration" -type f -print0 2>/dev/null
```
or add a post-loop check that `orchestration_installed` is greater than zero, emitting a warning if not.

---

### EC-03
**File**: `scripts/setup.sh:L67`
**Severity**: P2
**Category**: Error handling — backup failure handling
**Description**: The `backup_and_copy` function's backup step includes `cp "$dst" "$bak" || { echo "[ant-farm] ERROR: backup failed for $dst" >&2; exit 1; }`. The `exit 1` call from inside a function called within a subshell-like context (process substitution, `while` loop reading from process substitution) exits the subshell but not the parent shell. In the orchestration walk loop (L149), `backup_and_copy` is called inside a `while` loop fed by a process substitution `< <(find ...)`. In bash, `exit 1` inside a function called from within the loop body exits the loop's subshell context, not the main script. The `set -e` flag would propagate the non-zero return, but the behavior is platform-dependent when called inside process substitutions.
**Suggested fix**: Use `return 1` in the error branch instead of `exit 1` and check the return value at the call site, or ensure error propagation is consistent across contexts.

---

### EC-04
**File**: `scripts/setup.sh:L190`
**Severity**: P3
**Category**: Platform assumption — PATH check syntax
**Description**: The PATH check at L190 uses `[[ ":${PATH}:" != *":${HOME}/.local/bin:"* ]]`. This is bash-specific (`[[` and `*...*` pattern matching). The shebang is `#!/usr/bin/env bash` so this is acceptable, but `set -euo pipefail` is already set. No actual edge case, but on macOS systems where `/usr/bin/env bash` resolves to bash 3.x (pre-Catalina default), the syntax is still valid. This is P3 (cosmetic platform note, not a real bug).
**Suggested fix**: No action required. Note: macOS ships bash 3.2 by default; `[[` is supported since bash 2.05b. No risk.

---

### EC-05
**File**: `skills/plan.md:L127-L145`
**Severity**: P2
**Category**: File operation — heredoc with special characters in INPUT_TEXT
**Description**: Step 3 writes `INPUT_TEXT` to a file using a heredoc:
```bash
cat > "${DECOMPOSE_DIR}/input.txt" <<'SPEC_EOF'
<INPUT_TEXT>
SPEC_EOF
```
The outer heredoc uses `<<'SPEC_EOF'` (single-quoted, no expansion), but `<INPUT_TEXT>` is a placeholder that the skill document says "substitute." If the actual `INPUT_TEXT` contains the string `SPEC_EOF` on a line by itself, it will prematurely terminate the heredoc, truncating the output and potentially leaving the command in a broken state. This is a real edge case for specs that happen to include code examples with that delimiter.
**Suggested fix**: Use a more obscure delimiter such as `<<'__SPEC_EOF_BOUNDARY__'` or use `printf '%s\n' "$INPUT_TEXT" > "${DECOMPOSE_DIR}/input.txt"` which is immune to content-based delimiter collisions.

---

### EC-06
**File**: `skills/plan.md:L119-L122`
**Severity**: P2
**Category**: File operation — manifest.json with unescaped input
**Description**: The manifest.json is written using a heredoc:
```bash
cat > "${DECOMPOSE_DIR}/manifest.json" <<EOF
{
  "decompose_id": "${DECOMPOSE_ID}",
  "input_source": "<INPUT_SOURCE>",
  "input_class": "<INPUT_CLASS>",
  "class_score": <CLASS_SCORE>,
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
```
If `INPUT_SOURCE` contains double-quote characters or backslash sequences (e.g., a file path with spaces containing `\"`), the resulting JSON will be malformed. Any downstream consumer that parses this JSON (e.g., `jq`) will fail. `INPUT_SOURCE` is derived from the user-supplied file path argument.
**Suggested fix**: Use `jq -n` to construct the JSON safely, or sanitize `INPUT_SOURCE` before interpolation.

---

### EC-07
**File**: `skills/work.md:L24-L26`
**Severity**: P2
**Category**: Input validation — incomplete initialization check
**Description**: The pre-flight check for initialization only checks for `.crumbs/tasks.jsonl`:
```bash
[ -f .crumbs/tasks.jsonl ] || echo "NOT_INITIALIZED"
```
But `skills/init.md` and `skills/plan.md` both check for both `.crumbs/tasks.jsonl` AND `.crumbs/config.json` to determine if initialized. Using only one file means a partially initialized project (e.g., `tasks.jsonl` exists but `config.json` was deleted) will pass the guard and proceed into the Queen pipeline, where downstream `crumb` CLI calls that depend on `config.json` will fail with unclear errors.
**Suggested fix**: Mirror the check from `plan.md` and `status.md`:
```bash
[ -f .crumbs/tasks.jsonl ] && [ -f .crumbs/config.json ] && echo "INITIALIZED" || echo "NOT_INITIALIZED"
```

---

### EC-08
**File**: `skills/work.md:L37-L43`
**Severity**: P3
**Category**: Boundary condition — crumb count check
**Description**: The "No tasks found" check uses:
```bash
crumb list --short 2>/dev/null | wc -l
```
`wc -l` counts newlines. If the last line of `crumb list` output has no trailing newline, `wc -l` will undercount by 1. If there is exactly one crumb and it lacks a trailing newline, `wc -l` returns 0, and the skill incorrectly blocks execution with "No crumbs found." This is unlikely in practice (well-behaved CLI tools emit trailing newlines) but is a boundary condition.
**Suggested fix**: Use `crumb list --short 2>/dev/null | wc -l | tr -d ' '` and verify the crumb CLI always emits a trailing newline. Or use `crumb list --count 2>/dev/null` if that flag exists.

---

### EC-09
**File**: `orchestration/RULES-decompose.md:L127`
**Severity**: P2
**Category**: Platform assumption — `find` with literal placeholder
**Description**: The brownfield detection command at Step 0 uses:
```bash
find "{CODEBASE_ROOT}" -maxdepth 2 \
  -not -path "*/.git/*" \
  ...
  -type f | wc -l
```
`{CODEBASE_ROOT}` is a literal placeholder in the document. If the Planner runs this bash command without substituting the value (e.g., due to a template fill error), `find` will attempt to find a directory literally named `{CODEBASE_ROOT}`, fail silently (exits non-zero, `wc -l` returns 0), and the Planner will incorrectly classify the project as greenfield (< 5 files). This would cause the Pattern Forager to write a skip file on a brownfield project, degrading decomposition quality.
**Suggested fix**: Document clearly (or assert at runtime) that `{CODEBASE_ROOT}` must be substituted before running the command. Add a guard:
```bash
[ -n "${CODEBASE_ROOT}" ] || { echo "ERROR: CODEBASE_ROOT is not set"; exit 1; }
```

---

### EC-10
**File**: `orchestration/RULES-decompose.md:L250`
**Severity**: P3
**Category**: Boundary condition — Forager line cap enforcement
**Description**: The Forager line cap rule states: "If a Forager exceeds 100 lines, truncate at line 100 and proceed." However, the Planner only reads the Forager's return summary (not the file directly), and the truncation is supposed to happen before passing output downstream. The rule is stated but there is no described mechanism for the Planner to actually detect and apply the truncation — it relies on the Forager self-enforcing. If the Forager fails to self-truncate, the Planner's only detection point is reading the file contents, which the Planner is forbidden from doing (per L103-L108, Planner FORBIDDEN from reading research/*.md). This creates a gap: a Forager that violates the 100-line cap has no enforced truncation.
**Suggested fix**: Add a verification step in the Research complete gate: after the gate PASS, run `wc -l` on each research file and truncate any that exceed 100 lines via `head -100`. This can be done by the Planner as a bash command without reading the content.

---

### EC-11
**File**: `orchestration/templates/forager.md:L360-L365`
**Severity**: P3
**Category**: Error handling — decompose dir auto-creation
**Description**: The error handling section says: "Decompose dir does not exist: Create it with `mkdir -p {DECOMPOSE_DIR}/research`." However, by the time the Forager is spawned, the Planner has already created `DECOMPOSE_DIR` at Step 0. The Forager should never need to create the directory. If the Forager does create it (because DECOMPOSE_DIR was somehow missing), there is no notification back to the Planner that something went wrong. A missing DECOMPOSE_DIR at Forager spawn time indicates a Planner bug (Step 0 was skipped or failed silently), and silent recovery masks the root cause.
**Suggested fix**: Change the Forager's error handling to return an error to the Queen rather than silently creating the directory: `ERROR: DECOMPOSE_DIR does not exist at {DECOMPOSE_DIR}. Expected the Planner to create it at Step 0. Cannot proceed.`

---

### EC-12
**File**: `orchestration/templates/surveyor.md:L367-L375`
**Severity**: P2
**Category**: Error handling — empty feature request
**Description**: The error handling section says: "Feature request is empty: Return error to Queen: `ERROR: Feature request is empty.`" However, the Surveyor's spawn prompt structure (from `surveyor-skeleton.md`) places `{FEATURE_REQUEST}` inline in the prompt text. If the Planner fills the skeleton with an empty string for `{FEATURE_REQUEST}`, the resulting prompt will have no feature request text but the section header "**Feature request**:" will still be present. The Surveyor's check for "empty feature request" must examine the actual content after the header, not just whether the prompt exists. If the check is purely syntactic (does the prompt text contain anything after "**Feature request**:"), a blank line could pass.
**Suggested fix**: The Surveyor should check if the feature request text (after stripping whitespace) is non-empty before proceeding to Step 1. Document this check explicitly.

---

### EC-13
**File**: `orchestration/templates/decomposition.md:L294-L300`
**Severity**: P2
**Category**: File operation — Dolt server mode silent failure
**Description**: The Dolt mode warning at L294–300 documents that `bd dep add` silently fails in server mode (`--no-auto-commit`). The workaround requires switching to embedded mode, running deps, and switching back. The warning is informational — it is not enforced. If the Architect runs `bd dep add` without checking the current mode, all dependency wiring silently fails. The decomposition-brief.md will show deps as wired, but the actual database will have none. The TDV gate checks the brief (which the Architect writes), not the actual `bd` database state, so the gate will PASS even though dependencies were never persisted.
**Suggested fix**: Add a mandatory pre-condition step before any `bd dep add` call: `bd dolt set mode embedded` (with a note to switch back after). Make this a required step, not an optional warning.

---

### EC-14
**File**: `agents/forager.md:L32`
**Severity**: P3
**Category**: Input validation — hardcoded runtime path
**Description**: The Forager agent body instructs: "Read your workflow from `~/.claude/orchestration/templates/forager.md`." This path is hardcoded. If the orchestration files were installed to a non-default location (e.g., a different home directory, a CI environment, or a container where `~` resolves differently), the Forager cannot find its workflow and fails. There is no fallback or error message for this case.
**Suggested fix**: The spawn prompt could pass the template path explicitly as a variable, or the Forager could fall back to the repo-relative path. At minimum, the Forager's error handling section should include: "Workflow file not found at `~/.claude/orchestration/templates/forager.md`: Return error to Queen."

---

### EC-15
**File**: `skills/init.md:L170-L172`
**Severity**: P3
**Category**: Input validation — find scope for crumb.py
**Description**: Step 7 uses `find . -maxdepth 3 -name 'crumb.py' | head -1` to locate `crumb.py`. `maxdepth 3` means if `crumb.py` is at a depth of 4 or more (e.g., `src/tools/scripts/crumb.py`), it will not be found and the install step silently falls back to the "not found" warning path. This is a legitimate boundary condition that could cause confusion if the repo structure places `crumb.py` deeper than expected.
**Suggested fix**: Increase to `-maxdepth 5` or document the depth constraint explicitly so users know where to place `crumb.py`.

---

## Preliminary Groupings

### Group A: Shell script robustness (EC-01, EC-02, EC-03)
Root cause: `scripts/setup.sh` lacks defensive handling for glob expansion failure, `find` exit codes, and `exit`-vs-`return` in process substitution contexts. All three share the pattern of relying on implicit shell behavior rather than explicit error handling.

### Group B: Heredoc / shell injection via user input (EC-05, EC-06)
Root cause: `skills/plan.md` constructs file content via heredocs and string interpolation without sanitizing user-supplied content. Heredoc delimiter collision (EC-05) and JSON injection via unescaped paths (EC-06) stem from the same lack of input sanitization.

### Group C: Inconsistent initialization guards (EC-07)
Root cause: `skills/work.md` checks only `tasks.jsonl` while `skills/init.md`, `skills/plan.md`, and `skills/status.md` all check both `tasks.jsonl` and `config.json`. A copy-paste divergence that creates a gap in error detection.

### Group D: Silent failures in orchestration workflow (EC-09, EC-10, EC-13)
Root cause: Multiple points in `RULES-decompose.md` and `decomposition.md` rely on the agent correctly performing an action (substituting placeholders, self-truncating output, switching Dolt modes) without any enforced verification mechanism. Failures produce incorrect results rather than explicit errors.

### Group E: Missing error messages for unrecoverable states (EC-11, EC-12, EC-14)
Root cause: Several agents silently recover or proceed in conditions that indicate a Planner-level bug (missing DECOMPOSE_DIR) or ambiguous input (empty feature request, missing workflow file). Silent recovery masks root causes.

### Group F: Minor boundary conditions (EC-04, EC-08, EC-15)
Root cause: Cosmetic or low-probability boundary cases with minimal production impact.

---

## Summary Statistics

| Severity | Count | Finding IDs |
|----------|-------|-------------|
| P1       | 0     | —           |
| P2       | 8     | EC-02, EC-03, EC-05, EC-06, EC-07, EC-09, EC-12, EC-13 |
| P3       | 7     | EC-01, EC-04, EC-08, EC-10, EC-11, EC-14, EC-15 |
| **Total**| **15**|             |

No P1 findings. Most findings are process robustness issues in shell scripts and orchestration documentation rather than data-loss or crash-causing bugs.

---

## Cross-Review Messages

**Sent to Drift reviewer**: `orchestration/RULES-decompose.md` references `.beads/decompose/_decompose-{DECOMPOSE_ID}/` as the DECOMPOSE_DIR path (L118), but `skills/plan.md:L121` creates it under `.crumbs/sessions/_decompose-${DECOMPOSE_ID}`. These are different paths. Check if callers in `skills/plan.md` pass the correct path to the workflow in `RULES-decompose.md`.

**Sent to Correctness reviewer**: `skills/work.md:L24-L26` uses a weaker initialization guard than `skills/plan.md:L26-L27` and `skills/status.md:L22-L24`. If the correctness acceptance criteria require consistent initialization guards across all skills, this is a criteria gap (EC-07).

**Received**: None.

---

## Coverage Log

| File | Issues Found | Finding IDs |
|------|-------------|-------------|
| `agents/architect.md` | No issues found | — |
| `agents/forager.md` | 1 issue | EC-14 |
| `agents/surveyor.md` | No issues found | — |
| `orchestration/RULES-decompose.md` | 2 issues | EC-09, EC-10 |
| `orchestration/templates/architect-skeleton.md` | No issues found | — |
| `orchestration/templates/decomposition.md` | 1 issue | EC-13 |
| `orchestration/templates/forager-skeleton.md` | No issues found | — |
| `orchestration/templates/forager.md` | 1 issue | EC-11 |
| `orchestration/templates/surveyor-skeleton.md` | No issues found | — |
| `orchestration/templates/surveyor.md` | 1 issue | EC-12 |
| `scripts/setup.sh` | 4 issues | EC-01, EC-02, EC-03, EC-04 |
| `skills/init.md` | 1 issue | EC-15 |
| `skills/plan.md` | 2 issues | EC-05, EC-06 |
| `skills/status.md` | No issues found | — |
| `skills/work.md` | 2 issues | EC-07, EC-08 |

All 15 scoped files reviewed. No files skipped.

---

## Overall Assessment

**Score**: 7/10

**Verdict**: PASS WITH ISSUES

The codebase is structurally sound for a documentation/orchestration system. No P1 issues found. The P2 findings are real and actionable, with EC-07 (inconsistent initialization guard in `skills/work.md`) and EC-13 (silent Dolt dep wiring failure) being the highest priority to address. The shell script issues in `scripts/setup.sh` (EC-02, EC-03) are real robustness gaps that could produce confusing partial-install failures. The heredoc injection issues in `skills/plan.md` (EC-05, EC-06) are worth fixing before this system processes untrusted or adversarial input.
