# Edge Cases Review Report
**Session**: _session-20260313-021827
**Review round**: 1
**Timestamp**: 20260313-034951
**Reviewer**: edge-cases

---

## Findings Catalog

### F-01
**File**: `scripts/build-review-prompts.sh:L149-153`
**Severity**: P1
**Category**: File operation without existence check (missing prerequisite enforcement)
**Description**: The script derives `FOCUS_AREAS_FILE` as `$(dirname "$NITPICKER_SKELETON")/review-focus-areas.md` and immediately errors out if it's missing (`exit 1`). However this check (L150-153) happens *after* the script has already created the three output directories (`${SESSION_DIR}/prompts/`, `${SESSION_DIR}/previews/`, `${SESSION_DIR}/review-reports/`) and allocated resources. More critically: the check for `FOCUS_AREAS_FILE` existence only validates the file exists as a path — it does not validate it is readable (`-r`). The two skeleton files checked at L59-68 do check both `-f` and `-r`, but `FOCUS_AREAS_FILE` only checks `-f`. If the file exists but is not readable by the current user (e.g., permission 000 after a botched sync), `extract_focus_block` will silently produce empty content for every review type, and the review prompts will be written with blank Focus sections. Big Head and the CCO will then see prompts with no focus guidance — leading to silently degraded review quality without any error.
**Suggested fix**: Add `-r` check to FOCUS_AREAS_FILE validation:
```bash
if [ ! -f "$FOCUS_AREAS_FILE" ] || [ ! -r "$FOCUS_AREAS_FILE" ]; then
    echo "ERROR: Focus areas file not found or not readable: $FOCUS_AREAS_FILE" >&2
    exit 1
fi
```

---

### F-02
**File**: `scripts/build-review-prompts.sh:L74-86`
**Severity**: P2
**Category**: Missing error propagation from @file resolution
**Description**: The `resolve_arg` function calls `exit 1` if the `@file` path is not found, but `exit` inside a function only exits the subshell created by `$()` — NOT the parent script. The assignment `CHANGED_FILES="$(resolve_arg "$CHANGED_FILES_RAW")"` runs `resolve_arg` in a subshell. If `resolve_arg` calls `exit 1`, the subshell exits with code 1, but the parent script sees only the empty string assigned to `CHANGED_FILES`. The script then proceeds to the CHANGED_FILES emptiness check (L97-100) and produces a misleading error about `CHANGED_FILES` being empty, rather than the accurate "file not found" message. The actual error message from `resolve_arg` is printed to stderr but the exit code from the subshell is silently swallowed. Under `set -euo pipefail`, command substitutions do NOT propagate non-zero exit codes — this is a known bash pitfall.
**Suggested fix**: Check the exit code explicitly after assignment, or restructure to avoid command substitution:
```bash
CHANGED_FILES="$(resolve_arg "$CHANGED_FILES_RAW")" || {
    echo "ERROR: resolve_arg failed for CHANGED_FILES_RAW='${CHANGED_FILES_RAW}'" >&2
    exit 1
}
```

---

### F-03
**File**: `scripts/build-review-prompts.sh:L168-202`
**Severity**: P2
**Category**: Temp file leak on error paths
**Description**: The `fill_slot` function creates a temp file via `mktemp` (L175) and removes it at the end (L201: `rm -f "$tmpval"`). However, the `awk` pipeline in L180-200 can fail (e.g., if `$file` is not writable, or if disk is full mid-write). If the `awk ... > "${file}.tmp"` command fails, the function returns early (the `&&` short-circuits) without executing `rm -f "$tmpval"`. The temp file is leaked. In a long-running review prompt build with many `fill_slot` calls across multiple review types, this can accumulate orphaned temp files in `/tmp`. Under disk-pressure conditions, the leaked temp files from failed calls can themselves contribute to the disk-full failure that caused the original problem.
**Suggested fix**: Use a trap to clean up the temp file:
```bash
fill_slot() {
    local slot="$1" value="$2" file="$3"
    local tmpval
    tmpval="$(mktemp)"
    trap "rm -f '$tmpval'" RETURN
    printf '%s' "$value" > "$tmpval"
    awk ... "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
}
```

---

### F-04
**File**: `scripts/setup.sh:L137-149`
**Severity**: P2
**Category**: Unhandled find failure — silent skip of orchestration files
**Description**: The `while IFS= read -r -d '' src_file` loop at L137 reads output from `find "$REPO_ROOT/orchestration" -type f -print0`. If `find` itself fails (e.g., because `$REPO_ROOT/orchestration` has no read permission), the `while` loop body simply never executes — `orchestration_installed` stays 0, no error is reported, and the script prints a success message. The user would believe orchestration files were installed when none were. The `-d ''` null-delimiter form also silently handles paths with spaces, but that is not the issue here: the issue is no error propagation from `find`.
**Suggested fix**: Check that find succeeds before the loop, or capture its exit code:
```bash
if ! find "$REPO_ROOT/orchestration" -type f -print0 | \
     while IFS= read -r -d '' src_file; do
        ...
     done; then
    echo "[ant-farm] ERROR: find failed for orchestration directory" >&2
    exit 1
fi
```

---

### F-05
**File**: `scripts/setup.sh:L190-195`
**Severity**: P3
**Category**: PATH check is locale/shell dependent
**Description**: The PATH check `[[ ":${PATH}:" != *":${HOME}/.local/bin:"* ]]` works for a POSIX-style colon-delimited PATH. However on macOS (the target platform per the env block), `$HOME` expands to the user's home directory, and if the user has configured `~/.local/bin` using tilde-expansion in their shell profile rather than `$HOME`, the check may false-positive (warn unnecessarily). This is a minor robustness issue — the warning is not harmful, just potentially misleading.
**Suggested fix**: This is P3; leave as-is or document that the check is advisory only.

---

### F-06
**File**: `orchestration/RULES-decompose.md:L127-143`
**Severity**: P2
**Category**: `find` command uses template literal `{CODEBASE_ROOT}` in shell block
**Description**: The brownfield detection script at L127-143 contains the literal string `"{CODEBASE_ROOT}"` as a shell argument to `find`. This is a template placeholder, not a filled value. If an agent runs this block verbatim — which the `RULES-decompose.md` Step 0 instructs them to do — `find` will attempt to list a directory literally named `{CODEBASE_ROOT}` and fail, silently producing a count of 0. The Planner would then classify every project as **greenfield**, suppressing the Pattern Forager and potentially misconfiguring the entire decomposition. The Planner is supposed to have already substituted this value in its context, but the document gives no explicit instruction to do so before running the block, making the substitution expectation implicit.
**Suggested fix**: Add an explicit note before the block:
```
> Before running: substitute `{CODEBASE_ROOT}` with the absolute repo root path (e.g., `/Users/user/projects/myapp`). Do NOT run this block with the literal string `{CODEBASE_ROOT}`.
```

---

### F-07
**File**: `orchestration/templates/decomposition.md:L292-300`
**Severity**: P2
**Category**: Dolt mode switch with no rollback on error
**Description**: The Architect is instructed to switch to embedded Dolt mode (`bd dolt set mode embedded`), run all `bd dep add` commands, then switch back to server mode (`bd dolt set mode server && bd dolt start`). If any `bd dep add` command fails mid-sequence, or if `bd dolt set mode server` fails, the system is left in embedded mode. The RULES.md / MEMORY.md entries note that Dolt server mode is required for other parts of the workflow. Leaving the database in embedded mode after an Architect run could cause subsequent `bd` calls (by the Queen or Scout) to fail in unexpected ways.
**Suggested fix**: Wrap the sequence in error handling:
```bash
bd dolt set mode embedded || { echo "ERROR: could not switch to embedded mode"; exit 1; }
# run bd dep add commands
bd dolt set mode server || warn "WARNING: failed to restore server mode"
bd dolt start || warn "WARNING: failed to restart dolt server"
```

---

### F-08
**File**: `orchestration/templates/big-head-skeleton.md:L91-106`
**Severity**: P2
**Category**: Polling block instruction misrepresents timeout behavior
**Description**: The template instructs Big Head: "The polling timeout is 60 seconds (30 iterations × 2 seconds)." The actual polling bash block (referenced as "the while loop with sleep in the brief") lives in the consolidation brief written by `build-review-prompts.sh`, not directly in this skeleton. The skeleton contains no actual bash loop — it only references it. If `build-review-prompts.sh` changes the polling parameters (iterations × sleep duration) but the skeleton retains the "60 seconds" description, agents will see contradictory timeout information. More directly: the single-invocation constraint ("MUST be executed in a single Bash tool call") is sound, but if the actual polling loop written into the brief times out at a different interval, the skeleton's advice ("Queen should re-spawn Big Head") may be triggered at the wrong threshold.

This is a documentation/drift concern at the boundary, but the edge case risk is: if reviewers consistently run near the timeout (e.g., 55–65s), the ambiguity about actual vs. documented timeout can cause the Queen to re-spawn Big Head unnecessarily. Not a crash, but operationally incorrect behavior.
**Suggested fix**: Source the timeout value from a single location (the consolidation brief template), not hardcode it in the skeleton.

---

### F-09
**File**: `orchestration/templates/scout.md:L83-110`
**Severity**: P2
**Category**: `crumb show` failure writes error metadata but continues, potentially producing invalid wave plans
**Description**: The error handling at L266-285 (Scout error handling section) instructs: "If `crumb show` fails for a task: Write a metadata file with `**Status**: error`... Continue with remaining tasks." The Scout then proceeds to Step 4 (conflict analysis) and Step 5 (propose strategies) with the errored task in its inventory. Tasks with `**Status**: error` have no `Affected Files`, no `Root Cause`, no `Agent Type`. The conflict matrix (Step 4) would have incomplete data for these tasks — the Scout might classify a HIGH-conflict file as LOW-conflict because the error task's file was never recorded. The wave plan could assign an agent to a task whose metadata is incomplete, causing the Pantry's fail-fast check (Condition 1 — File missing or Scout error) to catch it later, but only after Pantry runs.
**Suggested fix**: The Scout should at minimum warn that conflict analysis for error tasks is unreliable, and recommend excluding them from wave 1. The current behavior of silently including error tasks in strategy proposals is an edge case that can produce misleading strategies.

---

### F-10
**File**: `orchestration/templates/pantry.md:L44-89`
**Severity**: P1
**Category**: Fail-fast Condition 3 (placeholder contamination) has ambiguous detection for `{UPPERCASE}` vs `<angle-bracket>` patterns
**Description**: Pantry Step 2, Condition 3 notes: "Note: `{UPPERCASE}` tokens in this Pantry template are Pantry instruction text, not Scout placeholders — do NOT treat them as contamination." However, the real metadata files produced by the Scout may also legitimately contain `{UPPERCASE}` strings if the task's title, root cause, or acceptance criteria reference configuration placeholders. For example, a task fixing a `{SESSION_DIR}` reference in a template file might have `{SESSION_DIR}` appear in its root cause field — which would be misread as unfilled placeholder contamination under a naive scan. If the Pantry incorrectly flags valid task metadata as contaminated and refuses to produce a task brief, that task silently drops from the execution plan. The Queen receives a FAILED row and must manually intervene. Since the instructions say "Do NOT treat them as contamination" but the actual detection logic is left to model judgment rather than a concrete syntactic rule, this is a reliability gap at the boundary.
**Suggested fix**: Clarify the contamination detection rule with a precise syntactic definition: only flag `<angle-bracket text>` (specifically: starts with `<`, ends with `>`, contains only word chars/spaces inside). Explicitly state `{UPPERCASE}` patterns are never contamination in metadata files, with an example.

---

### F-11
**File**: `orchestration/templates/big-head-skeleton.md:L114-127`
**Severity**: P2
**Category**: `crumb list --open --short` failure aborts filing but success path lacks a write-back guard
**Description**: The cross-session dedup bash block at L114-127 correctly aborts if `crumb list` fails, and writes a failure artifact. However, the temp file used for dedup (`/tmp/open-crumbs-$$.txt`) is never cleaned up — whether the script succeeds or aborts. Under normal operation, the `$$` PID-based name prevents collisions, but the temp file persists until the OS cleans `/tmp`. In the edge case where the same shell PID is reused in a subsequent Big Head spawn (rare but possible), a stale open-crumbs file from the prior run could be read instead of fresh data, causing cross-session dedup to operate against a stale snapshot. Since the dedup `crumb list` result is written to `/tmp/open-crumbs-$$.txt` and later used for comparison, stale data here could cause a finding that was newly closed between runs to still appear as "open," triggering a false dedup skip.
**Suggested fix**: Add `rm -f /tmp/open-crumbs-$$.txt` after the dedup logic completes (or use `mktemp` with a trap).

---

### F-12
**File**: `skills/init.md:L38-43` (Step 1 — language detection)
**Severity**: P3
**Category**: Compound boolean detection in bash uses incorrect operator precedence — affects Python and Java detection
**Description**: The language detection block at L38-43 contains two affected lines:

Line 40:
```bash
[ -f pyproject.toml ] || [ -f setup.py ] || [ -f requirements.txt ] && echo "python"
```
Line 43:
```bash
[ -f pom.xml ] || [ -f build.gradle ] && echo "java"
```
Due to bash operator precedence, `&&` binds more tightly than `||`. Both lines parse with the rightmost OR operand grouped with `&&`:
- Line 40: `[ -f pyproject.toml ] || [ -f setup.py ] || ([ -f requirements.txt ] && echo "python")` — pyproject.toml and setup.py presence do NOT trigger `echo "python"`.
- Line 43: `[ -f pom.xml ] || ([ -f build.gradle ] && echo "java")` — pom.xml presence alone does NOT trigger `echo "java"`.

Confirmed introduced in this commit range (correctness reviewer verified against commit 4429953). Java detection case identified by correctness reviewer during cross-review.
**Suggested fix**: Use explicit grouping for all multi-OR language checks:
```bash
{ [ -f pyproject.toml ] || [ -f setup.py ] || [ -f requirements.txt ]; } && echo "python"
{ [ -f pom.xml ] || [ -f build.gradle ]; } && echo "java"
```

---

### F-13
**File**: `skills/init.md:L140-145` (Step 6 — .gitignore update)
**Severity**: P3
**Category**: `echo '' >> .gitignore` without write permission check
**Description**: The gitignore update block does `echo '' >> .gitignore` without checking write permissions first. On read-only filesystems (e.g., mounted read-only, or a `.gitignore` with `chmod 444`) this will fail with a permission error. The error reference table at the bottom of `skills/init.md` acknowledges `.gitignore` write failures but instructs "Warn user, provide manual fix command, continue." However, the bash block itself has no error handling — the agent would need to detect the error from bash output, which is not explicit in the instructions. The `set -euo pipefail` pattern is also not applied here (skills are prompts, not scripts), so the agent might continue silently after failure.
**Suggested fix**: This is P3 because `.gitignore` failure is low-impact and the error reference table covers the case. Add a note in the bash block to check the exit code.

---

### F-14
**File**: `skills/work.md:L37-43` (Step 0 — No tasks found check)
**Severity**: P2
**Category**: `crumb list --short | wc -l` includes trails in count, producing false negatives
**Description**: The check at L37-43 runs `crumb list --short 2>/dev/null | wc -l` to detect "zero crumbs." However, `crumb list` returns both crumbs (tasks) and trails (epics) unless filtered. If the project has 3 trails and 0 executable crumbs, `wc -l` returns 3 (not 0), and the check passes — allowing execution to proceed into the Scout with zero real work to do. The Scout would then run `crumb ready` and find nothing, but this wastes the Scout's context and produces a confusing "0 ready tasks" briefing rather than the clear "No crumbs found" message that the pre-flight check is meant to surface.
**Suggested fix**: Filter to crumbs only:
```bash
crumb list --type=task --short 2>/dev/null | wc -l
```
Or use a dedicated `crumb list --tasks-only` flag if available.

---

### F-15
**File**: `orchestration/templates/implementation.md:L59-61`
**Severity**: P3
**Category**: `git pull --rebase` in Step 5 not guarded against conflict requiring manual resolution
**Description**: The Dirt Pusher commit instructions at L59-61 mandate `git pull --rebase` before commit. If the rebase produces merge conflicts that cannot be auto-resolved, `git pull --rebase` exits non-zero, leaving the repo in a mid-rebase state. The instructions then say "you MUST repeat Step 4 (Per-File Correctness Review) on all files affected by the conflict resolution before committing." This is good guidance, but there is no instruction for what to do if the rebase conflict cannot be resolved by the agent (e.g., the conflict is in a shared utility that the agent has no context about). The agent may be stuck in a mid-rebase state with no clear escalation path.
**Suggested fix**: Add an explicit failure path: "If `git pull --rebase` exits with a conflict you cannot resolve, run `git rebase --abort`, commit to the current branch state without rebasing, and notify the Queen via your summary doc under `## Rebase Conflict`." This is P3 because the conflict scenario is described as "if it resolves" in the instructions — the gap is the unresolved case.

---

### F-16
**File**: `orchestration/RULES-review.md:L33-51`
**Severity**: P3
**Category**: Input validation uses bash parameter expansion that silently passes on unset variables when `set -u` is not in effect
**Description**: The CHANGED_FILES whitespace check at L42-45:
```bash
if [[ -z "${CHANGED_FILES//[[:space:]]/}" ]]; then
```
This is inside the Queen's context (not a bash script), so `set -u` is not in effect. If `CHANGED_FILES` is genuinely unset (not empty string, but unset), the expansion `${CHANGED_FILES//...}` would throw "unbound variable" in a strict bash context. In the Queen's LLM context, the check is interpreted as prose/instruction — the actual validation happens when the Queen generates the bash block. If the Queen omits initializing `CHANGED_FILES` (e.g., due to a git diff returning nothing), the variable may be undefined rather than empty-string, and the check may not trigger as expected. This is a P3 because the surrounding instructions are clear about intent, and the Queen is expected to set these variables.

---

## Preliminary Groupings

### Group A: Shell script error propagation failures (root cause: bash subshell exit code swallowing)
- **F-02** (resolve_arg exit in subshell silently swallowed)
- **F-03** (fill_slot temp file leak on awk failure)
This shared root cause is: bash `$()` command substitution does not propagate `exit 1` from nested functions to the outer script under `set -euo pipefail`. The same pattern appears twice.

### Group B: Missing read-permission checks on critical files (root cause: `-f` without `-r`)
- **F-01** (FOCUS_AREAS_FILE missing `-r` check)
This is isolated but follows the same pattern as the two skeleton files that DO check `-r`. An inconsistency in the validation pattern.

### Group C: Temp file lifecycle management (root cause: missing cleanup on error paths)
- **F-03** (fill_slot temp file in build-review-prompts.sh)
- **F-11** (open-crumbs temp file in big-head-skeleton.md)
Both create temp files without ensuring cleanup on error paths.

### Group D: Agent-facing shell placeholder substitution ambiguity (root cause: template placeholders used in executable blocks without clear substitution guidance)
- **F-06** (CODEBASE_ROOT literal in find command in RULES-decompose.md)
- **F-10** (Pantry Condition 3 ambiguous detection of {UPPERCASE} vs <angle-bracket>)
Both involve placeholder conventions bleeding into executable contexts without clear boundaries.

### Group E: Incomplete pre-flight checks in skills (root cause: skills are prose instructions, not enforced scripts)
- **F-12** (bash operator precedence in init.md language detection)
- **F-14** (wc -l includes trails in work.md task count)
Both are in skill files where the bash blocks are agent-interpreted, not mechanically executed, introducing subtle correctness gaps.

### Group F: Error continuity with stale/partial data (root cause: continue-on-error leaves system in potentially invalid state)
- **F-07** (Dolt mode switch with no rollback)
- **F-09** (Scout continues with errored tasks in wave plan)

---

## Summary Statistics

| Severity | Count | Finding IDs |
|----------|-------|-------------|
| P1 | 2 | F-01, F-10 |
| P2 | 9 | F-02, F-04, F-06, F-07, F-08, F-09, F-11, F-14, F-16 |
| P3 | 5 | F-05, F-12, F-13, F-15, F-16 |
| **Total** | **16** | — |

Note: F-16 is borderline P2/P3; assigned P3 because it's an LLM-interpreted prose context, not mechanically executed.

Revised counts:
| Severity | Count |
|----------|-------|
| P1 | 2 |
| P2 | 8 |
| P3 | 6 |
| **Total** | **16** |

---

## Cross-Review Messages

**Sent to drift-reviewer**:
- "Function `fill_slot` in `scripts/build-review-prompts.sh` references `review-focus-areas.md` via a derived path at L149. If this file was renamed or relocated from a prior location, callers still using the old path would silently produce empty focus blocks. May want to check cross-file path assumptions."

**Sent to correctness-reviewer**:
- "Logic in `skills/init.md:L38-43` (language detection) has bash operator precedence issue where `||` and `&&` interact incorrectly — `pyproject.toml` and `setup.py` presence does not trigger `echo 'python'`. May not satisfy the acceptance criterion that python projects are correctly detected."

**Messages received**:
- From drift-reviewer: "`orchestration/templates/review-focus-areas.md` exists at the exact sibling path that `build-review-prompts.sh:149` derives. No drift — the file is present and the heuristic resolves correctly. Not filing a finding."
- From correctness-reviewer: Confirmed operator precedence bug at `skills/init.md:L40` and extended it to `skills/init.md:L43` (Java detection: `[ -f pom.xml ] || ([ -f build.gradle ] && echo "java")`). No AC citation from correctness side (task ant-farm-3imu not in correctness brief scope). Deferred filing to edge-cases. Finding F-12 updated to cover both affected lines.

---

## Coverage Log

| File | Status | Findings |
|------|--------|----------|
| `AGENTS.md` | Reviewed | No issues found — documentation only; no executable code. |
| `agents/architect.md` | Reviewed | No issues found — delegates to template; no inline edge cases. |
| `agents/forager.md` | Reviewed | No issues found — delegates to template. |
| `agents/nitpicker.md` | Reviewed | No issues found — role-description file with no executable paths. |
| `agents/scout-organizer.md` | Reviewed | No issues found — delegates to template. |
| `CLAUDE.md` | Reviewed | No issues found — prose instructions with no executable code. |
| `CONTRIBUTING.md` | Reviewed | No issues found — documentation. |
| `docs/installation-guide.md` | Reviewed | No issues found — instructions/documentation. |
| `orchestration/reference/dependency-analysis.md` | Reviewed | No issues found — reference documentation. |
| `orchestration/RULES-decompose.md` | Reviewed | F-06 (P2) — `{CODEBASE_ROOT}` literal in executable find block. |
| `orchestration/RULES-review.md` | Reviewed | F-16 (P3) — unset variable edge case in validation block. |
| `orchestration/RULES.md` | Reviewed | No edge case issues found within edge-cases scope. |
| `orchestration/SETUP.md` | Reviewed | No issues found. |
| `orchestration/templates/architect-skeleton.md` | Reviewed | No issues found. |
| `orchestration/templates/big-head-skeleton.md` | Reviewed | F-08 (P2) — polling timeout documentation vs actual implementation gap; F-11 (P2) — temp file leak. |
| `orchestration/templates/checkpoints.md` | Reviewed | No edge case issues within scope (complex but self-consistent). |
| `orchestration/templates/decomposition.md` | Reviewed | F-07 (P2) — Dolt mode switch with no error rollback. |
| `orchestration/templates/dirt-pusher-skeleton.md` | Reviewed | No issues found. |
| `orchestration/templates/forager-skeleton.md` | Reviewed | No issues found. |
| `orchestration/templates/forager.md` | Reviewed | No issues found — error handling section is well-specified. |
| `orchestration/templates/implementation.md` | Reviewed | F-15 (P3) — git rebase conflict with no escalation path. |
| `orchestration/templates/nitpicker-skeleton.md` | Reviewed | No issues found. |
| `orchestration/templates/pantry.md` | Reviewed | F-10 (P1) — ambiguous placeholder contamination detection. |
| `orchestration/templates/queen-state.md` | Reviewed | No issues found — schema template. |
| `orchestration/templates/reviews.md` | Reviewed | No issues found within edge-cases scope. |
| `orchestration/templates/scout.md` | Reviewed | F-09 (P2) — error tasks included in wave plans without conflict analysis. |
| `orchestration/templates/scribe-skeleton.md` | Reviewed | No issues found. |
| `orchestration/templates/SESSION_PLAN_TEMPLATE.md` | Reviewed | No issues found. |
| `README.md` | Reviewed | No issues found — documentation. |
| `scripts/build-review-prompts.sh` | Reviewed | F-01 (P1), F-02 (P2), F-03 (P2). |
| `scripts/setup.sh` | Reviewed | F-04 (P2), F-05 (P3). |
| `skills/init.md` | Reviewed | F-12 (P3), F-13 (P3). |
| `skills/plan.md` | Reviewed | No issues found — error handling is well-specified. |
| `skills/status.md` | Reviewed | No issues found — all error paths documented. |
| `skills/work.md` | Reviewed | F-14 (P2) — task count includes trails. |

---

## Overall Assessment

**Score**: 6.5 / 10

**Verdict**: PASS WITH ISSUES

**Rationale**: The codebase shows strong defensive design in most areas — skills have comprehensive error reference tables, templates include fail-fast checks, and the scout/pantry pipeline has explicit failure conditions. The two P1 findings (F-01, F-10) are real but not immediately crash-inducing: F-01 requires a specific permission failure scenario, and F-10 affects reliability of a model-judgment check rather than causing a hard crash. The P2 cluster is more concerning as a group: several shell script robustness issues (F-02 exit code swallowing, F-03/F-11 temp file leaks, F-04 silent find failure) could mask problems in the sync and review pipelines. The Dolt mode rollback gap (F-07) is operationally risky in a database workflow. None of these individually block shipping, but the P2 cluster in `build-review-prompts.sh` and `setup.sh` warrants targeted fixes before production use at scale.
