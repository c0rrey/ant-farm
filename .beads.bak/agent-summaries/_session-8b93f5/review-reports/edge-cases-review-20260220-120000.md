# Report: Edge Cases Review

**Scope**: README.md, orchestration/GLOSSARY.md, orchestration/PLACEHOLDER_CONVENTIONS.md, orchestration/RULES.md, orchestration/templates/SESSION_PLAN_TEMPLATE.md, orchestration/templates/big-head-skeleton.md, orchestration/templates/checkpoints.md, orchestration/templates/dirt-pusher-skeleton.md, orchestration/templates/implementation.md, orchestration/templates/nitpicker-skeleton.md, orchestration/templates/pantry.md, orchestration/templates/reviews.md, orchestration/templates/scout.md
**Reviewer**: Edge Cases Review / code-reviewer

## Findings Catalog

### Finding 1: Polling loop shell-state caveat may not prevent multi-invocation failures
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:456-499`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The reviews.md Step 0a polling loop includes the comment "IMPORTANT: This entire block must execute in a single Bash invocation. Shell state (variables) does not persist across separate Bash tool calls." This caveat is inside the polling loop code block but is marked as a comment, not an enforcement mechanism. If the Pantry adapts this block and splits it across two Bash tool calls (e.g., sets variables in one call, checks them in another), the TIMED_OUT and ELAPSED variables are lost, and the timeout mechanism silently breaks. There is no verification step to ensure the block was executed atomically. The Pantry receives the template and adapts it — a future Pantry implementation could break the invariant without knowing.
- **Suggested fix**: Add an explicit instruction in prose (outside the code block) to the Pantry: "The polling loop MUST be issued as a single Bash tool call. Do not split across multiple calls." Alternatively, restructure the loop to be self-contained with a `(...)` subshell guard.
- **Cross-reference**: Primarily an edge-case / process robustness issue; the clarity reviewer may want to flag the in-comment-only placement of this constraint.

### Finding 2: Big Head escalation paths to the Queen are unexecutable inside TeamCreate — BOTH timeout and FAIL paths affected
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:656-665`, `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:668-677`, `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md:88-92`
- **Severity**: P1
- **Category**: edge-case
- **Description**: The Pest Control TIMEOUT path (reviews.md:657-665) and the FAIL path (reviews.md:668-677) both instruct Big Head to "escalate to the Queen immediately." However, Big Head runs inside a TeamCreate team — it can only SendMessage to team members (Nitpickers, Pest Control). There is no mechanism to reach the Queen mid-execution. Neither path specifies a fallback disk-write artifact, so if Big Head halts in either error state, the Queen reads a missing consolidated report file with no explanation of what went wrong. Both escalation paths are unactionable and leave the system in a silent dead-end state.
  - Confirmed by cross-review with correctness-reviewer, who verified: RULES.md Step 3b says "After team completes, DMVDC and CCB have already run inside the team" — the Queen reads a file post-hoc, with no in-band channel from a running team.
- **Suggested fix**: Replace both escalation paths with a disk-write artifact. Big Head should write a BLOCKED artifact to `{session-dir}/review-reports/review-consolidated-BLOCKED-{timestamp}.md` with the failure details. RULES.md Step 3c should be updated to check for BLOCKED artifacts before proceeding: "If `review-consolidated-BLOCKED-*.md` exists, surface the error to the user before attempting to read the consolidated summary."
- **Cross-reference**: Also filed in correctness review (Finding 8 in that report). Big Head skeleton lines 88-92 reference the same broken timeout mechanism.

### Finding 3: `shasum` not universally available; `head -c 6` may produce non-hex characters
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/RULES.md:183`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The session ID generation command is:
  ```bash
  SESSION_ID=$(date +%s | shasum | head -c 6)
  ```
  `shasum` is a macOS/BSD utility. On Linux, the equivalent is `sha1sum`. On a Linux-hosted Claude Code deployment or CI environment, `shasum` would not exist and the command fails silently — `SESSION_ID` becomes empty, causing `mkdir` to create `.beads/agent-summaries/_session-/` (a directory with a trailing slash/empty ID). Additionally, `shasum` output contains a trailing ` -` (space and dash) after the hex digest; `head -c 6` on the hex prefix is fine, but the command does not handle the case where `date +%s` produces a timestamp starting with `0` followed by very short output (no truncation needed, but the 6-char extraction is technically brittle to platform variations in digest format).
- **Suggested fix**: Use a cross-platform fallback:
  ```bash
  SESSION_ID=$(date +%s | md5sum 2>/dev/null || date +%s | md5 2>/dev/null | head -c 6)
  ```
  Or use `openssl rand -hex 3` which is portable. Also add a guard: `[ -z "$SESSION_ID" ] && echo "ERROR: SESSION_ID generation failed" && exit 1`.
- **Cross-reference**: Also present in `orchestration/RULES.md:184` where `SESSION_DIR` references `SESSION_ID`.

### Finding 4: `bd list` output parsing in P3 auto-filing is fragile for "Future Work" epic discovery
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:696-700`, `/Users/correy/projects/ant-farm/orchestration/templates/big-head-skeleton.md:93-95`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The P3 auto-filing section instructs:
  ```bash
  bd list --status=open | grep -i "future work"
  ```
  This relies on free-text grep against the human-readable output of `bd list`. If `bd list` output changes format, or if the epic title is "Future Work (P3 Backlog)" or "future_work", the grep returns no matches and Big Head creates a duplicate epic. There is also no extraction of the epic ID from the grep output — the instruction says "if not found" but does not show how to parse the ID when it IS found, leaving the agent to infer the extraction step.
- **Suggested fix**: Either use a dedicated `bd epic list | grep -i "future work"` with explicit ID extraction (`awk '{print $1}'` or equivalent), or store the "Future Work" epic ID in a well-known location (e.g., the session state file) after first creation to avoid repeated grep-based discovery.

### Finding 5: Pantry empty-file-list guard does not handle whitespace-only list
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md:216-226`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The guard comment says "empty or whitespace-only" but the failure condition says "empty or contains only whitespace" — this is consistent. However, the detection is delegated to the Pantry agent's own judgment ("verify that the 'list of ALL changed files across all epics' provided by the Queen is non-empty"). There is no explicit instruction on HOW to perform the empty check. A Pantry implementation might check `len(file_list) == 0` while failing to strip whitespace first, letting a list of `[" ", "\n"]` pass the guard. The fix artifact path is also written to `{session-dir}/prompts/review-FAILED.md` without ensuring the prompts directory exists.
- **Suggested fix**: Add explicit check: "strip all whitespace; if the result is empty, fail." Add `mkdir -p {session-dir}/prompts/` before writing the failure artifact, or note that this directory is guaranteed to exist by prior Pantry steps.

### Finding 6: CCB Check 7 (bead provenance) uses `bd list --status=open` which may include pre-existing open beads
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md:544-548`
- **Severity**: P2
- **Category**: edge-case
- **Description**: Check 7 instructs Pest Control to run `bd list --status=open` and cross-reference against the consolidated summary's "Beads filed" list, then "Flag any beads that were filed during the review phase." However, `bd list --status=open` will include ALL open beads from prior sessions — not just beads from the current session. Without a session-scoped filter (e.g., filtering by creation timestamp or by the IDs listed in the consolidated summary), the check becomes noise-heavy: Pest Control must manually exclude every pre-existing open bead to determine whether any were filed during the review phase. The verification is unreliable for projects with many existing open beads.
- **Suggested fix**: Change the instruction to compare `bd list --status=open` results against the explicit list of bead IDs in the consolidated summary. The correct check is: "Every bead in the consolidated summary's 'Beads filed' list must exist and have status=open. Any beads filed during the review phase (not in the consolidated summary) are unauthorized." This inverts the direction: check the summary list against `bd show`, not `bd list` against the summary.

### Finding 7: Big Head consolidation brief "polling loop adaptation" instruction is ambiguous for the `<IF ROUND 1>` conditional
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/reviews.md:484-495`, `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md:267`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The polling loop in reviews.md uses a `# <IF ROUND 1> ... # </IF ROUND 1>` comment block to mark lines that should only appear in round 1. The instruction to the Pantry is: "In round 2+, include only correctness and edge-cases checks (omit the clarity and excellence variables and their `[ -f ]` check)." However, the template still includes the round 1 variable assignments (`CLARITY_REPORT=...`, etc.) above the `<IF ROUND 1>` block without marking them for omission. If the Pantry omits only the `[ -f ]` check but keeps the variable assignment lines, the bash script has unused variables but no syntax error — the omission is partial and hard to verify. The delineation of "what to omit" is spread across two sections of the template.
- **Suggested fix**: Wrap the full round-1-only block (both variable assignments and `[ -f ]` checks) in a single `# <IF ROUND 1> ... # </IF ROUND 1>` comment. Or better: provide two complete, separate polling loop variants (one for round 1, one for round 2+) instead of a conditional template.

### Finding 8: DMVDC "bd show Failure Handling" guard does not address the case where the summary doc itself is missing
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md:323-345`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The DMVDC section says "Read the summary doc first" and then provides a guard for `bd show` failure. However, there is no guard for the case where the summary doc at `{SESSION_DIR}/summaries/{TASK_SUFFIX}.md` does not exist. If an agent failed before writing its summary doc, Pest Control would encounter a file-not-found error on the very first step. The template does not specify what Pest Control should do: fail immediately, flag as FAIL, or search for an alternative location.
- **Suggested fix**: Add a summary doc existence check at the top of the DMVDC verification block:
  ```
  If the summary doc does not exist at {SESSION_DIR}/summaries/{TASK_SUFFIX}.md:
  - Record: "Summary doc missing — agent likely failed before Step 6"
  - Return FAIL: "Summary doc not found at expected path"
  - Do NOT proceed with the 4 checks
  ```

### Finding 9: WWD template uses `{list files from task description}` as a literal placeholder
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/checkpoints.md:251`
- **Severity**: P3
- **Category**: edge-case
- **Description**: The WWD verification template contains:
  ```
  **Expected files** (from `bd show {TASK_ID}`): {list files from task description}
  ```
  The `{list files from task description}` is a Tier 2 placeholder (lowercase-kebab convention violation aside — it uses spaces, not kebab-case) that the Queen must fill before passing to Pest Control. If the Queen passes this template verbatim without substituting the file list, Pest Control receives an unfilled placeholder and cannot perform the verification. There is no CCO-equivalent check that validates the WWD prompt before Pest Control runs it.
- **Suggested fix**: Change the placeholder to match Tier 1 convention (Queen-provided): `{EXPECTED_FILES}` and document it in the "Placeholders" section. Alternatively, restructure the template to instruct Pest Control to derive the file list itself from `bd show {TASK_ID}` (which it already has), removing the need for Queen pre-filling.

### Finding 10: Scout Step 5.5 coverage verification only checks strategy completeness, not wave capacity
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/scout.md:143-179`
- **Severity**: P3
- **Category**: edge-case
- **Description**: Step 5.5 verifies that every ready task appears in every proposed strategy's wave groupings. However, the verification does not check whether any single wave exceeds the 7-agent limit. A strategy could pass the coverage check (`assigned_count == inventory_count`) while having Wave 1 with 10 agents, violating the concurrency constraint. The constraint is stated in Step 5 ("respecting the max 7 concurrent limit") but the mandatory gate in Step 5.5 does not enforce it.
- **Suggested fix**: Add a second pass condition to Step 5.5: "For each wave in each strategy, verify `agent_count <= 7`." If any wave exceeds 7, list the overflow tasks and split them into an additional wave.

### Finding 11: SESSION_PLAN_TEMPLATE.md spawn code uses `background=True` in the pseudocode
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/SESSION_PLAN_TEMPLATE.md:153`
- **Severity**: P2
- **Category**: edge-case
- **Description**: The agent spawn pseudocode example includes `background=True`:
  ```python
  spawn(
      subagent_type='python-pro',
      ...
      background=True,
  )
  ```
  The project's CLAUDE.md and MEMORY.md both explicitly prohibit `run_in_background: true` on Task agents because it causes raw JSONL transcript leakage into the Queen's context window. This pseudocode example directly contradicts the project's established rule. A user or agent following this template for session planning would include `background=True` in their spawn calls, introducing a known failure mode.
- **Suggested fix**: Remove `background=True` from all spawn examples in SESSION_PLAN_TEMPLATE.md. Replace the pseudocode comment with a note: "Do NOT use background=True — multiple Task calls in a single message already run concurrently."

### Finding 12: Pantry fail-fast Condition 3 excludes `{UPPERCASE}` tokens but could miss Tier 1 placeholders that ARE legitimate Scout output
- **File(s)**: `/Users/correy/projects/ant-farm/orchestration/templates/pantry.md:57`
- **Severity**: P3
- **Category**: edge-case
- **Description**: Condition 3 (placeholder-contaminated metadata) says: "Note: `{UPPERCASE}` tokens in this Pantry template are Pantry instruction text, not Scout placeholders — do NOT treat them as contamination." This carve-out is correct for the Pantry's own template tokens. However, if a Scout task metadata file legitimately contains a `{UPPERCASE}` token in its content (e.g., a task description quoting a placeholder like "The function uses `{SESSION_DIR}` as input"), the Pantry would skip this false contamination detection — which is the intended behavior. The risk is the reverse: if the Scout writes actual unfilled `{UPPERCASE}` placeholders (e.g., a bug in the Scout writes `{ROOT_CAUSE}` instead of the real text), Condition 3 would NOT catch it because `{UPPERCASE}` tokens are explicitly excluded. This is a gap in contamination detection.
- **Suggested fix**: Narrow the carve-out: instead of excluding ALL `{UPPERCASE}` tokens, exclude only the specific tokens used in the Pantry template (`{TASK_ID}`, `{TASK_SUFFIX}`, `{SESSION_DIR}`, `{AGENT_TYPE}`, etc.). Add an explicit list of "expected Tier 1 tokens to ignore" to Condition 3.

---

## Preliminary Groupings

### Group A: Incomplete or broken error-path handling in verification protocols
- Finding 8 (summary doc missing before DMVDC), Finding 6 (CCB provenance check unreliable for multi-session repos)
- These both affect Pest Control's ability to produce reliable verdicts when inputs are in unexpected state.
- **Suggested combined fix**: Add a pre-condition existence check block at the top of each DMVDC and CCB verification template that checks for all required artifacts before proceeding. Standardize the "missing artifact" FAIL response format across both.

### Group B: Template-to-agent communication gaps (escalation paths that cannot be executed)
- Finding 2 (P1 — Big Head cannot SendMessage to Queen inside TeamCreate; both TIMEOUT and FAIL paths affected), Finding 9 (unfilled placeholder in WWD template passed to Pest Control)
- Both involve instructions that are unactionable as written: either the communication channel does not exist (Finding 2), or the template contains content that should have been substituted before use (Finding 9).
- **Suggested combined fix**: For Finding 2: replace all "escalate to the Queen" instructions with disk-write BLOCKED artifacts; update RULES.md Step 3c to poll for BLOCKED artifacts before reading consolidated report. For Finding 9: upgrade `{list files from task description}` to a Tier 1 `{EXPECTED_FILES}` placeholder or remove it and instruct Pest Control to derive the file list from `bd show`.

### Group C: Bash portability and silent failure in session setup
- Finding 3 (`shasum` not cross-platform, empty SESSION_ID), Finding 11 (`background=True` in pseudocode violates CLAUDE.md rule)
- Both are bash/scripting issues in templates that could produce silent, hard-to-diagnose failures at session start.
- **Suggested combined fix**: Audit all bash snippets in templates for portability. Add `set -e` or explicit error guards to session setup scripts.

### Group D: Round-aware logic gaps
- Finding 7 (polling loop `<IF ROUND 1>` delineation is ambiguous), Finding 10 (Scout coverage verification does not enforce wave capacity)
- Both involve conditional logic that is partially specified — correct for the stated case but missing enforcement for boundary cases.
- **Suggested combined fix**: For round-conditional logic, provide two complete variants rather than one template with conditional markers. For the wave capacity check, add it as a second pass condition to the mandatory Step 5.5 gate.

### Group E: Fragile output parsing for future-work epic discovery
- Finding 4 (`bd list` grep for "Future Work" epic is fragile)
- Standalone — no related finding shares exactly this root cause.

### Group F: Contamination detection blind spot
- Finding 12 (Pantry Condition 3 carve-out excludes all `{UPPERCASE}` tokens)
- Standalone — specific to the Pantry's fail-fast logic.

### Group G: Whitespace handling edge case in Pantry guard
- Finding 5 (empty-file-list guard does not specify strip behavior)
- Standalone.

---

## Summary Statistics
- Total findings: 12
- By severity: P1: 1, P2: 5, P3: 6
- Preliminary groups: 7

---

## Cross-Review Messages

### Sent
- To correctness-reviewer: "Finding 2 (Big Head escalation to Queen impossible inside TeamCreate) also has a correctness dimension — the protocol cannot be executed as specified. Please check whether the reviews.md Step 4 escalation path is internally consistent with the TeamCreate structure."

### Received
- From correctness-reviewer: "Confirmed P1 — both TIMEOUT and FAIL escalation paths in reviews.md Step 4 are unexecutable inside TeamCreate. Verified via RULES.md Step 3b: Queen reads files post-hoc, no in-band channel from running team. Escalation block is formatted as a message body with no recipient and no SendMessage call. No fallback artifact write specified. Filed as Finding 8 (P1) in correctness report." — Action taken: upgraded Finding 2 from P3 to P1, expanded description to cover both affected escalation paths, added cross-reference to correctness review Finding 8.

### Deferred Items
- "SESSION_PLAN_TEMPLATE.md `background=True` pseudocode" — also relevant to the clarity reviewer for consistency with CLAUDE.md rules; flagging in cross-review for awareness. No action deferred — reported here as P2.

---

## Coverage Log

| File | Status | Evidence |
|------|--------|----------|
| `README.md` | Reviewed — no issues | 334 lines, 7 sections examined: Architecture, Workflow Steps 0-6, Information diet, Hard gates, Priority calibration, Retry limits, Known failure modes, Custom agents, Forking, Path reference convention, File reference table. No unhandled edge cases found — README is descriptive, not executable. |
| `orchestration/GLOSSARY.md` | Reviewed — no issues | 86 lines, 3 sections (Naming Conventions, Workflow Concepts, Checkpoint Acronyms, Ant Metaphor Roles). Definitional document only; no executable logic or error paths. |
| `orchestration/PLACEHOLDER_CONVENTIONS.md` | Reviewed — no issues | 232 lines, 5 sections (Overview, Tier 1-3 definitions, File-by-File Audit, Validation Rules, Compliance Status). The grep patterns in Validation Rules are syntactically correct. No edge cases in a conventions document of this nature. |
| `orchestration/RULES.md` | Findings: #3 | 260 lines, 9 sections. `shasum` portability issue in Session Directory setup at line 183. All other workflow steps, gates, and retry limits reviewed — logic is coherent, no missing branches for standard cases. |
| `orchestration/templates/SESSION_PLAN_TEMPLATE.md` | Findings: #11 | 368 lines, 10 sections. `background=True` in spawn pseudocode at line 153. Review decision thresholds at lines 228-236 use `<5`, `5-15`, `>15` which are reasonable, non-overlapping ranges. Quality gate thresholds are documented for all 4 reviews. No other edge cases. |
| `orchestration/templates/big-head-skeleton.md` | Findings: #4 (indirect) | 105 lines. Big Head skeleton references the P3 auto-filing logic at lines 93-95; fragile `bd list` grep is in reviews.md but referenced here. The 60s/120s timeout at lines 88-91 is specified. No missing state transitions. |
| `orchestration/templates/checkpoints.md` | Findings: #6, #8, #9 | 572 lines, 4 major checkpoint sections. All 8 CCB checks examined; all 4 DMVDC checks examined; WWD and CCO verdict thresholds examined. Identified 3 issues: CCB Check 7 unreliable (Finding 6), missing summary doc existence guard (Finding 8), unfilled placeholder in WWD template (Finding 9). |
| `orchestration/templates/dirt-pusher-skeleton.md` | Reviewed — no issues | 46 lines. 6-step skeleton examined. Placeholders are Tier 1. The scope boundary language is explicit. `git pull --rebase` conditional re-review instruction at line 39 is sound. No edge cases in a skeleton template of this size. |
| `orchestration/templates/implementation.md` | Reviewed — no issues | 270 lines, 5 sections. Examined all 6 steps, scope boundary insert, pre-spawn checklist, information diet, prompt optimization section. The "GUARD: bd show Failure Handling" at checkpoints.md is mirrored here at lines 25-26 ("Run `bd show <id>` to get full details"). The conditional re-review in Step 5 is present. No unhandled paths. |
| `orchestration/templates/nitpicker-skeleton.md` | Reviewed — no issues | 43 lines. Minimal skeleton; placeholders all Tier 1. The {REVIEW_ROUND} placeholder (line 13) is properly defined and used at line 22. No edge cases. |
| `orchestration/templates/pantry.md` | Findings: #5, #12 | 316 lines. Both implementation and review modes examined. Fail-fast conditions 1-3 reviewed; Finding 5 (whitespace guard) and Finding 12 (contamination carve-out gap) identified. Step 5 session-summary format is exhaustive. Review mode Step 3 round-aware composition logic examined — no additional gaps found. |
| `orchestration/templates/reviews.md` | Findings: #1, #2, #4, #7 | 845 lines. Transition gate, agent teams protocol, round-aware review protocol, all 4 review type specs, Nitpicker report format, Big Head consolidation protocol (Steps 0-4), P3 auto-filing, Queen checklists examined. Identified 4 findings. |
| `orchestration/templates/scout.md` | Findings: #10 | 266 lines. All 7 steps examined plus error handling. Coverage verification gate (Step 5.5) is well-designed but missing wave capacity validation (Finding 10). Error handling for `bd show` failure, filter zero results, and all-blocked cases is present. |

---

## Overall Assessment
**Score**: 0/10
**Verdict**: NEEDS WORK

One P1 finding blocks shipping: the Big Head escalation paths to the Queen (both TIMEOUT and FAIL) are architecturally unexecutable inside a TeamCreate team. When Pest Control is unavailable or returns FAIL, Big Head has no way to reach the Queen and no disk-write fallback is specified — the system silently stalls. This is confirmed cross-review with the correctness reviewer. Additionally, 5 P2 findings represent meaningful gaps: the `shasum` portability issue, the CCB provenance check unreliable against multi-session repos, the missing DMVDC guard for absent summary docs, the fragile "Future Work" epic grep, and the `background=True` pseudocode that contradicts a CLAUDE.md prohibition. The P1 must be resolved before the review protocol can be considered safe to operate.
