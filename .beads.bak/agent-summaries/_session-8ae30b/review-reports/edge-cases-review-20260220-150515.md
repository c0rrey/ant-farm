# Report: Edge Cases Review

**Scope**: AGENTS.md, agents/pantry-review.md, orchestration/RULES.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md
**Reviewer**: Edge Cases Review (code-reviewer)

## Findings Catalog

### Finding 1: SESSION_ID collision produces shared artifact directories across concurrent Queens

- **File(s)**: `orchestration/RULES.md:219`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The session ID is generated as `SESSION_ID=$(date +%s | shasum | head -c 6)`, taking the first 6 hex characters of a SHA1 of the Unix epoch second. Two Queens launched within the same second produce the same SESSION_ID (epoch → same SHA1 → same 6-char prefix → same `_session-{id}` directory). Both Queens would read/write to the same session directory, silently corrupting briefings, task-metadata, summaries, prompts, and checkpoint artifacts.
- **Suggested fix**: Generate from a source with sub-second or random entropy: `SESSION_ID=$(cat /proc/sys/kernel/random/uuid 2>/dev/null | tr -d '-' | head -c 8 || LC_ALL=C tr -dc 'a-f0-9' < /dev/urandom | head -c 8)`. Alternatively append the PID: `$(date +%s)$$` before hashing. The multi-Queen concurrency concern is already documented in the file (line 234: "prevents collisions when multiple Queens run"), but the chosen algorithm does not actually prevent same-second collisions.
- **Cross-reference**: None; this is a pure edge-case / concurrency issue.

### Finding 2: REVIEW_ROUND=0 passes validation but triggers wrong branch in fill-review-slots.sh

- **File(s)**: `orchestration/RULES.md:104`, `orchestration/templates/pantry.md:293`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The review round is described as starting at 1 ("default: 1") and incrementing per round. However, the validation in `fill-review-slots.sh` accepts any non-negative integer (`^[0-9]+$`), which allows round 0. If a Queen passes round 0 (e.g., a bug where the state file is missing the field and defaults to 0), the script's `[ "$REVIEW_ROUND" -eq 1 ]` comparison evaluates false, so all-4-review-type mode is skipped and only correctness+edge-cases are produced — identical to round 2+ behavior but for the wrong reason, and clarity+excellence prompts are never written. The Pantry's own Section 2 prose says "default: 1" but does not enforce this at input. Neither the Queen's RULES.md instructions nor the pantry-review agent instructions guard against a zero round number before invoking the script.
- **Suggested fix**: In `fill-review-slots.sh` (out of scope here, but the in-scope doc should specify): document that REVIEW_ROUND must be >= 1 and that callers must validate before invoking the script. In `orchestration/RULES.md` Step 3b-i, add an explicit note: "Review round must be ≥ 1. If session state is missing the field, default to 1, not 0."
- **Cross-reference**: Deferred to correctness reviewer — this is also a correctness issue (wrong review types produced).

### Finding 3: Empty CHANGED_FILES input to fill-review-slots.sh is not guarded in the calling spec

- **File(s)**: `orchestration/RULES.md:108-113`, `orchestration/templates/pantry.md:275-285`
- **Severity**: P2
- **Category**: edge-case
- **Description**: `pantry.md` Section 2 Step 3 includes a guard: "GUARD: Empty File List Check" that aborts if the Queen passes an empty file list. However, `RULES.md` Step 3b-ii (the current canonical path, which calls `fill-review-slots.sh` directly) does not specify any equivalent guard before invoking the script. The script itself (`fill-review-slots.sh`) does not validate that CHANGED_FILES is non-empty. If `git diff --name-only <range>` returns nothing (e.g., all changes are reverts or the range is wrong), the script runs to completion writing skeleton prompts with an empty `{{CHANGED_FILES}}` slot, and Nitpickers receive a review prompt listing zero files to review. The script exits 0 and the Queen proceeds normally.
- **Suggested fix**: In `RULES.md` Step 3b-i or Step 3b-ii, add: "If `git diff --name-only <commit-range>` returns empty output, do NOT invoke `fill-review-slots.sh`. Surface an error to the user: 'Commit range produced no changed files — review cannot proceed.' Verify the commit range is correct." This mirrors the guard already present in the deprecated pantry-review Section 2.
- **Cross-reference**: None.

### Finding 4: Pantry Section 1 compose-review-skeletons.sh path is wrong in the canonical instruction

- **File(s)**: `orchestration/templates/pantry.md:148`
- **Severity**: P2
- **Category**: edge-case
- **Description**: `pantry.md` Section 1 Step 2.5 instructs the Pantry to call:
  ```
  bash ~/.claude/orchestration/scripts/compose-review-skeletons.sh ...
  ```
  But the actual script lives at `~/.claude/scripts/compose-review-skeletons.sh` (repo-root `scripts/`, synced via `sync-to-claude.sh`). The `orchestration/scripts/` subdirectory does not exist (confirmed by glob). If the Pantry follows this instruction literally, the script call fails with "No such file or directory" and the Pantry reports `REVIEW SKELETON ASSEMBLY FAILED`. The error is recoverable (the Queen can re-invoke) but the path mismatch means the system cannot self-heal without the Queen knowing the correct path.
- **Suggested fix**: Correct the path in `pantry.md:148` to `bash ~/.claude/scripts/compose-review-skeletons.sh ...`. Verify the analogous reference in `RULES.md:108-110` — the `fill-review-slots.sh` path is written as `bash ~/.claude/orchestration/scripts/fill-review-slots.sh`, which has the same mismatch and should be `bash ~/.claude/scripts/fill-review-slots.sh`.
- **Cross-reference**: Message sent to correctness reviewer — the wrong path also represents a correctness failure (the scripts simply won't run).

### Finding 5: Big Head polling loop uses `sleep` but shell state doesn't persist across Bash invocations

- **File(s)**: `orchestration/templates/reviews.md:508-545`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The Big Head report-waiting polling loop is presented as a bash snippet with a comment on line 508: "IMPORTANT: This entire block must execute in a single Bash invocation." The comment is correct — shell variables (`ELAPSED`, `TIMED_OUT`, etc.) do not persist across separate Bash tool calls. However, the constraint is documented only as a comment inside a code block. An agent reading this template might not recognize that a multi-step Bash call sequence (e.g., checking for files, then sleeping, then rechecking in separate tool invocations) would break the loop logic and always see `TIMED_OUT=1` on re-entry. Additionally, the loop polls every 2 seconds for up to 30 seconds. In a team context where reviewers run concurrently, 30 seconds may be too short if a reviewer is slow to write its report due to model latency or long files. There is no documented escalation path for the case where the reviewer is still running (not errored) but simply slow.
- **Suggested fix**: Strengthen the single-invocation constraint in the template prose (not just as a bash comment). Add a note above the code block: "This loop MUST be run as a single Bash tool call. Do not split across multiple Bash invocations." For the timeout, consider 120 seconds or a configurable value. Add language distinguishing "reviewer still running" from "reviewer crashed" to guide the escalation decision.
- **Cross-reference**: None.

### Finding 6: Pantry self-validation checklist has no guard for a missing pantry-review invocation after deprecation

- **File(s)**: `agents/pantry-review.md:56-71`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The `pantry-review` agent (`agents/pantry-review.md`) includes a self-validation checklist that verifies all 4 review data files, the Big Head file, timestamp consistency, and more. However, `RULES.md:180` marks `pantry-review` as "**Deprecated**: replaced by `fill-review-slots.sh` bash script called directly by Queen in Step 3b." If a future Queen is given a briefing that still references `pantry-review`, it would spawn the deprecated agent, which would attempt to write prompts using the old workflow. The agent's own self-validation checklist does not check whether it is running in deprecated mode, and gives no indication to the Queen that it should not have been spawned. This is a soft edge case — the workflow produces output, but it's output from the wrong path.
- **Suggested fix**: Add a first-step guard to `agents/pantry-review.md`: "STOP: If you were spawned by a Queen following RULES.md Step 3b, do NOT proceed. This agent is deprecated. The Queen should use `fill-review-slots.sh` directly. Return immediately with: 'pantry-review is deprecated — use fill-review-slots.sh instead.'"
- **Cross-reference**: Clarity reviewer may also have noted the deprecated agent's continued existence without a clear decommission signal.

### Finding 7: TASK_IDS slot left empty in review prompts for round 2+ but never validated

- **File(s)**: `orchestration/templates/pantry.md:299-301`, `orchestration/RULES.md:103`
- **Severity**: P3
- **Category**: edge-case
- **Description**: In round 2+, the Queen passes "fix task IDs only" as the TASK_IDS list. The prompt composition fills `{{TASK_IDS}}` with these IDs, which the correctness reviewer uses to run `bd show <task-id>`. However, if fix tasks were not formally created as beads (e.g., user chose "fix now" and the Queen assigned work without creating task beads), the TASK_IDS list may be empty or contain non-existent IDs. The `fill-review-slots.sh` script does not validate that TASK_IDS is non-empty, and neither does the review brief composition. The correctness reviewer would receive a prompt with empty task IDs and skip `bd show` lookups, potentially missing acceptance criteria verification entirely.
- **Suggested fix**: In `RULES.md` Step 3b-i, add: "If fix task IDs are unavailable (user fixed without bead creation), document this in the review prompt: 'No task IDs available for round N — verify fixes against P1/P2 beads listed in consolidated review summary from round N-1.'" Alternatively, link to the consolidated report path so the correctness reviewer can reference prior findings.
- **Cross-reference**: None.

### Finding 9: Fallback workflow references non-existent file `review-clarify.md` with no missing-file guard

- **File(s)**: `orchestration/templates/reviews.md:125`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The Fallback Workflow step 1 (line 125) instructs the Queen to provide "review prompt from `review-clarify.md`, `review-edge-cases.md`, etc." The canonical file name is `review-clarity.md` (not `review-clarify.md`). In fallback mode the Queen would attempt to read or pass a path that does not exist, causing the clarity Task agent to receive no valid prompt or fail at invocation. Flagged by the clarity reviewer via cross-review message; confirmed the typo is real and the surrounding fallback workflow has no guard for missing prompt files — there is no pre-check that all 4 review prompt files exist before spawning reviewers, unlike the CCO gate in the team protocol path (line 64: "Pre-spawn requirement: Before creating the Nitpickers, run CCO on all review prompts").
- **Suggested fix**: Correct `review-clarify.md` → `review-clarity.md` on line 125. Additionally, add a pre-spawn file-existence check to the Fallback Workflow step 1: before spawning any reviewer Task agents, verify each prompt file exists at `{session-dir}/prompts/review-{type}.md`. If any is missing, abort and surface the error rather than spawning agents with no prompt.
- **Cross-reference**: Received from clarity-reviewer (typo). The missing-file guard gap is an independent edge-case finding.

### Finding 8: Pantry Section 1 Step 2 fail-fast check: no timeout or max-retry on metadata file reads

- **File(s)**: `orchestration/templates/pantry.md:45-89`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The Pantry's fail-fast checks (Condition 1, 2, 3) correctly handle missing/incomplete/contaminated metadata. However, there is no guidance for what happens if a metadata file exists but is continuously being written by the Scout (a TOCTOU race). The Pantry reads the file once and makes a pass/fail decision. If the Scout is still writing the file at that moment, the Pantry may read a partial file (e.g., missing required sections), classify it as Condition 2 (incomplete metadata), and write a FAILED artifact — even though the Scout will complete the file moments later. This is an unlikely but possible race condition in concurrent multi-Queen scenarios.
- **Suggested fix**: Add a brief retry (1-2 attempts with a 2-second pause) before declaring Condition 1/2/3 failures, to allow in-flight Scout writes to complete. Document the retry in the Pantry's fail-fast check instructions.
- **Cross-reference**: None.

---

## Preliminary Groupings

### Group A: Wrong script paths (single root cause)
- Finding 4 — `orchestration/scripts/` does not exist; both `pantry.md:148` and `RULES.md:108-110` reference this non-existent subdirectory when calling `compose-review-skeletons.sh` and `fill-review-slots.sh`
- **Suggested combined fix**: Correct both references from `~/.claude/orchestration/scripts/` to `~/.claude/scripts/`. One search-and-replace across both files covers both surfaces.

### Group B: Missing empty-input guards in the Queen-owned review path
- Finding 3 (empty CHANGED_FILES) and Finding 7 (empty/missing TASK_IDS) — both are the same underlying pattern: the deprecated `pantry-review` Section 2 had explicit guards for empty inputs, but those guards were not carried over to the new `fill-review-slots.sh`-based path described in `RULES.md`.
- **Suggested combined fix**: Add a pre-flight validation section to `RULES.md` Step 3b-i that enumerates required non-empty inputs before calling `fill-review-slots.sh`: commit range (non-empty), changed files (non-empty), timestamp (matches format), round (≥ 1).

### Group D: Fallback workflow missing-file handling
- Finding 9 (`review-clarify.md` typo + no prompt file existence guard in fallback) — the typo is a symptom of broader missing-file handling in the fallback path; the team-protocol path has a CCO pre-spawn gate but the fallback has none.
- **Suggested combined fix**: Fix the typo and add a prompt-file existence pre-check in the Fallback Workflow section of `reviews.md`.

### Group C: Standalone findings
- Finding 1 (SESSION_ID collision) — concurrency issue, standalone
- Finding 2 (REVIEW_ROUND=0) — validation gap, standalone
- Finding 5 (Big Head polling loop shell-state constraint) — template instruction clarity, standalone
- Finding 6 (deprecated pantry-review no deprecation guard) — soft edge case, standalone
- Finding 8 (TOCTOU on metadata file reads) — race condition, standalone

---

## Summary Statistics
- Total findings: 9
- By severity: P1: 0, P2: 5, P3: 3
- Preliminary groups: 4

---

## Cross-Review Messages

### Sent
- To correctness-reviewer: "Finding 4 (wrong script path `orchestration/scripts/` vs `scripts/`) is also a correctness failure — the scripts cannot run at the documented path. Flagging in case correctness review wants to file it under correctness rather than edge-cases." — Action: Flagged for potential dedup by Big Head.
- To correctness-reviewer: "Finding 2 (REVIEW_ROUND=0 passes validation) causes wrong review types to be produced, which is a correctness failure (missing clarity+excellence prompts). Flagging for dedup." — Action: Flagged for potential dedup by Big Head.

### Received
- From clarity-reviewer: "Typo in fallback path: `review-clarify.md` should be `review-clarity.md` at `reviews.md:125`; fallback has no missing-file guard." — Action taken: Verified typo, confirmed fallback has no prompt-file existence check, added as Finding 9 (P2).
- From correctness-reviewer: "Both cross-domain findings confirmed. Finding 4 (script path) added to their report as Finding 7 (P2). Finding 2 (round=0) added as their Finding 8 (P3) — they rate it P3 from correctness standpoint." — Action taken: No report changes needed. Severity disagreement on Finding 2 (my P2 vs their P3) is appropriate for Big Head to resolve; Big Head should apply the higher severity (P2) on merge per the protocol.

### Deferred Items
- "Wrong script path" (Finding 4) — Partially deferred to correctness reviewer because the broken path also violates the functional correctness of the system; Big Head should dedup across both reports.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| AGENTS.md | Reviewed — no issues | 42 lines, 5 sections (Quick Reference, Landing the Plane). Pure documentation, no executable logic, no input handling, no file operations, no concurrency concerns. |
| agents/pantry-review.md | Findings: #6 | 72 lines, 10-item self-validation checklist, CCO compliance quality requirements. One edge case: deprecated agent has no self-guard to abort if spawned incorrectly. |
| orchestration/RULES.md | Findings: #1, #2, #3 | 296 lines, full workflow specification. SESSION_ID collision (Finding 1), REVIEW_ROUND=0 validation gap (Finding 2), empty CHANGED_FILES guard missing from Step 3b (Finding 3). Script paths also cross-reference Finding 4. |
| orchestration/templates/pantry.md | Findings: #2 (cross-ref), #4, #7, #8 | 454 lines, Sections 1-3. Wrong script path (Finding 4 primary source at line 148), TASK_IDS empty input gap (Finding 7), TOCTOU on metadata reads (Finding 8). |
| orchestration/templates/reviews.md | Findings: #5, #9 | 891 lines, full review protocol. Big Head polling loop single-invocation constraint inadequately documented (Finding 5). Fallback workflow: typo `review-clarify.md` → `review-clarity.md` and no prompt-file existence guard before spawning Task agents (Finding 9). All other sections reviewed; no additional edge-case issues found. |

---

## Overall Assessment
**Score**: 7.0/10
**Verdict**: PASS WITH ISSUES

The orchestration system has solid structural guards (fail-fast metadata checks, explicit exit codes, directory verification, round-aware routing), but five P2 gaps are worth addressing before production use: a wrong script path that would cause silent failures, missing empty-input validation on the canonical review path, a SESSION_ID collision window for concurrent Queens, an under-specified constraint in the Big Head polling loop, and a typo + missing file-existence guard in the fallback workflow that would cause clarity reviewers to fail silently.
