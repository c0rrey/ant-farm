# Review Consolidator Skeleton Template

<!-- Orchestrator-facing wiring instructions: orchestration/reference/review-consolidator-wiring.md -->
<!-- Agent-facing template starts below the --- separator. -->
<!-- Do NOT include anything above --- in the TeamCreate prompt. -->

---

Consolidate the Reviewer reports into a unified summary.

**Review round**: {REVIEW_ROUND}
**Input guard**: If {REVIEW_ROUND} is blank or non-numeric, halt immediately and return: "REVIEW_CONSOLIDATOR ABORTED: REVIEW_ROUND is invalid. Expected a positive integer; got: '{REVIEW_ROUND}'." Do NOT read any reports or proceed.
- Expected reports: read the `expected_paths` list in your consolidation brief (Step 0) — the count varies based on how many reviewers were spawned. Do NOT assume a fixed number.
- Round 1 typical: clarity, edge-cases, correctness, drift (but split instances of a type may produce additional paths)
- Round 2+ typical: correctness, edge-cases only

Step 0: Read your consolidation brief from {DATA_FILE_PATH}
(Format: markdown. Sections: Report Paths, Deduplication Protocol, Crumb Filing Instructions, Consolidated Output Path, Checkpoint Auditor Coordination Note, Review Round, P3 Auto-Filing Instructions (round 2+ only).)

**Failure Artifact Convention** (applies to ALL failure conditions in this workflow):
When any step reaches a FAIL condition, write a brief failure artifact to the expected output path before returning an error. Standard format:
```
# [COMPONENT] — [FAILURE TYPE]
**Status**: FAILED — <one-line description>
**Timestamp**: <ISO 8601>
**Reason**: <what went wrong>
**Recovery**: <what to do next>
```
This ensures downstream consumers (Orchestrator, Checkpoint Auditor) have a written record of the failure at the path they expect — even if the output is a FAILED file rather than a consolidated summary.

Your workflow:
1. Verify all expected report files exist (count determined by the consolidation brief's `expected_paths` list) — follow the missing-report handling protocol in your consolidation brief (Step 0a)
   - The brief is authoritative for this step: it specifies the polling timeout, error return format, and failure conditions
   - **Single-invocation constraint**: The polling bash block in the brief (the `while` loop with `sleep`) MUST be executed in a single Bash tool call. Do NOT attempt to poll by calling Bash repeatedly across multiple turns — the shell state does not persist between turns and you cannot `sleep` across turns. Submit the entire polling block as one Bash tool invocation and wait for its result.
   - **Timeout note**: The polling timeout is determined by the consolidation brief (the `while` loop parameters in Step 0a are authoritative — the value here is approximate). This allows reviewers to finish writing their reports before Review Consolidator proceeds. If your reviewers are consistently timing out, the Orchestrator should re-spawn Review Consolidator rather than increasing the timeout — a longer timeout blocks the Orchestrator's context with an idle agent.
   - **On timeout (REPORTS_FOUND=0)**: Before returning the error to the Orchestrator, write a failure artifact using this bash block:
     ```bash
     # NOTE: {CONSOLIDATED_OUTPUT_PATH} is a template placeholder (pre-substitution form).
     # build-review-prompts.sh replaces it with a literal path (e.g.
     # /path/to/session/consolidated.md) before this prompt reaches Review Consolidator.
     # By the time Review Consolidator executes this block, the braces are gone and a real
     # filesystem path appears in their place.
     [[ "{CONSOLIDATED_OUTPUT_PATH}" == *"{"* ]] && { echo "ERROR: CONSOLIDATED_OUTPUT_PATH not substituted — build-review-prompts.sh failed to replace the placeholder. Aborting."; exit 1; }
     mkdir -p "$(dirname "{CONSOLIDATED_OUTPUT_PATH}")" || { echo "ERROR: failed to create output directory for {CONSOLIDATED_OUTPUT_PATH}. Aborting."; exit 1; }
     cat > "{CONSOLIDATED_OUTPUT_PATH}" << 'EOF'
     # Review Consolidator — BLOCKED: Missing Reviewer Reports
     **Status**: FAILED — prerequisite gate timeout
     **Timestamp**: <current ISO 8601 timestamp>
     **Reason**: Not all expected Reviewer reports arrived within the timeout specified in the consolidation brief. <list missing reports>
     **Recovery**: Check reviewer logs. Once all expected reports are present, re-spawn Review Consolidator consolidation.
     EOF
     ```
   - If the Bash block exits with code 1 (directory creation failed before the artifact could be written), use the SendMessage tool to notify the Orchestrator immediately: "Review Consolidator FAILED: could not create output directory for failure artifact. Filesystem issue — manual intervention required." Then end your turn.
   - After writing the failure artifact (Bash exit code 0), return the error to the Orchestrator as specified in the brief
   - Do NOT proceed to read reports or perform consolidation
2. Read all expected reports
3. Collect all findings into a single list
4. Deduplicate: merge findings about the same issue across reviewers
   **Split-instance dedup rule**: If the same reviewer type was spawned multiple times (e.g., `clarity-1` and `clarity-2`), treat them as a single logical review type for root-cause grouping — do NOT treat a finding from `clarity-1` and a finding from `clarity-2` about the same root cause as cross-type duplicates. Merge them under one root cause entry. Dedup across split instances by file path + line range (not solely prose similarity): if two findings reference the same file:line range, they are the same instance regardless of wording.
5. Group by root cause: one group per underlying problem, not per occurrence
   **[OUT-OF-SCOPE] severity rule**: when a root-cause group contains both in-scope and `[OUT-OF-SCOPE]` findings, determine the group's combined severity using ONLY in-scope severity levels. `[OUT-OF-SCOPE]` findings contribute their affected surfaces to the group but do NOT contribute to severity. Example: in-scope P2 + out-of-scope P3 in the same group → group severity is P2.
6. For each merge, document WHY findings share a root cause
7. **Cross-session dedup**: Before writing the summary or filing crumbs, check for existing open crumbs that already cover your root causes:
   ```bash
   _CRUMB_LIST_TMP="$(mktemp /tmp/open-crumbs-XXXXXX.txt)"
   if ! crumb list --open --short > "$_CRUMB_LIST_TMP" 2>/dev/null; then
     echo "ERROR: crumb list failed (file error or crumb error). Aborting crumb filing to prevent duplicates."
     rm -f "$_CRUMB_LIST_TMP"
     [[ "{CONSOLIDATED_OUTPUT_PATH}" == *"{"* ]] && { echo "ERROR: CONSOLIDATED_OUTPUT_PATH not substituted — build-review-prompts.sh failed to replace the placeholder. Aborting."; exit 1; }
     mkdir -p "$(dirname "{CONSOLIDATED_OUTPUT_PATH}")" || { echo "ERROR: failed to create output directory for {CONSOLIDATED_OUTPUT_PATH}. Aborting."; exit 1; }
     cat > "{CONSOLIDATED_OUTPUT_PATH}" << 'EOF'
     # Review Consolidator Consolidation — BLOCKED: Cross-Session Dedup Infrastructure Error
     **Status**: FAILED — crumb list infrastructure error
     **Timestamp**: <current ISO 8601 timestamp>
     **Reason**: `crumb list --open` failed. Crumb filing aborted to prevent duplicate filing. This is likely a file access or crumb CLI issue.
     **Recovery**: Retry after the issue clears. If the issue persists, run `crumb doctor` and re-spawn Review Consolidator.
     EOF
     exit 1
   fi
   ```
   If the bash block above exits with code 1 due to the mkdir guard (directory creation failed before the failure artifact could be written), use the SendMessage tool to notify the Orchestrator immediately: "Review Consolidator FAILED: could not create output directory for failure artifact during cross-session dedup. Filesystem issue — manual intervention required." Then end your turn.
   If the bash block above exits with code 1 due to `crumb list` CLI failure (the `if !` condition), stop immediately. Do NOT proceed to consolidation or crumb filing. Use the SendMessage tool to notify the Orchestrator: "Review Consolidator FAILED: crumb list infrastructure error during cross-session dedup. Crumb filing aborted to prevent duplicates. Consolidated output written to {CONSOLIDATED_OUTPUT_PATH}. Please check crumb status and re-spawn Review Consolidator when ready." Then end your turn.
   <!-- NOTE: {CONSOLIDATED_OUTPUT_PATH} in the SendMessage text above is a template placeholder substituted by build-review-prompts.sh at build time — a real filesystem path appears in its place when Review Consolidator receives this prompt. Consistent with the bash-block comment above. -->
   For each root cause group, compare against existing crumb titles (from `"$_CRUMB_LIST_TMP"`):
   - **Exact title match** (case-insensitive): Do NOT file. Log in the summary: "Dedup: RC-N matches existing crumb <ID> — skipped."
   - **Similar title** (same root cause, different wording): Run `crumb search "<key phrases>"` to confirm. If the existing crumb covers the same root cause, do NOT file. Log the match.
   - **No match found**: Mark for filing.
   When uncertain whether a match is truly the same root cause, err on the side of filing (a human can merge later; a missed filing is harder to recover).
   After completing the dedup comparison, clean up the temp file:
   ```bash
   rm -f "$_CRUMB_LIST_TMP"
   ```
8. Write consolidated summary to {CONSOLIDATED_OUTPUT_PATH}
9. Send consolidated report path to the Checkpoint Auditor (SendMessage): "Consolidated report ready at {CONSOLIDATED_OUTPUT_PATH}. Please run claims-vs-code and review-integrity checkpoints and reply with verdict."
   - Do NOT file any crumbs before receiving the Checkpoint Auditor's reply
10. **End your turn now** — do NOT sleep or poll. The Checkpoint Auditor's reply arrives as a new conversation turn. Do not proceed to step 10a until you receive that reply.

10a. *(Async reply handler — executes only when the Checkpoint Auditor replies in a new conversation turn. Do NOT execute this step proactively.)* **When the Checkpoint Auditor replies** — act on the verdict (follow the turn-based retry protocol in reviews.md, Review Consolidator Protocol > Step 4: Checkpoint Gate):
    - If no reply after 2 subsequent turns (from any teammate), retry once; if still no reply after 2 more turns, escalate to Orchestrator
    - **PASS**: File ONE crumb per root cause (skip any marked as duplicates in the cross-session dedup step (step 7)). For each crumb, write a description to a temp file, then create:
      ```bash
      _DESC_TMP="$(mktemp /tmp/crumb-desc-XXXXXX.md)"
      cat > "$_DESC_TMP" << 'CRUMB_DESC'
      ## Root Cause
      <What is specifically wrong — cite the code path, pattern, or design flaw.
      Reference file:line locations where the issue originates. This must be
      substantive analysis, NOT a restatement of the title.>

      ## Affected Surfaces
      - `file1.py:L42` — <specific instance> (from correctness review)
      - `file2.sh:L15` — <specific instance> (from edge-cases review)

      ## Fix
      <Specific corrective action — what to change, where, and why.>

      ## Changes Needed
      - `path/to/file1.py`: <what to change>
      - `path/to/file2.sh`: <what to change>

      ## Acceptance Criteria
      - [ ] <First independently testable criterion>
      - [ ] <Second independently testable criterion>
      - [ ] <Third independently testable criterion>
      CRUMB_DESC

      _CRUMB_TITLE="<title>"
      _CRUMB_PRIORITY="P<severity>"
      _CRUMB_JSON_TMP="$(mktemp /tmp/crumb-XXXXXX.json)"
      python3 -c "
import json, pathlib, sys
title, priority = sys.argv[1], sys.argv[2]
desc = pathlib.Path(sys.argv[3]).read_text()
print(json.dumps({'type': 'bug', 'priority': priority, 'title': title, 'description': desc, 'acceptance_criteria': [], 'scope': {}, 'links': {}}))
" "$_CRUMB_TITLE" "$_CRUMB_PRIORITY" "$_DESC_TMP" > "$_CRUMB_JSON_TMP" || { echo "ERROR: JSON generation failed" >&2; exit 1; }
      crumb create --from-file "$_CRUMB_JSON_TMP"
      rm -f "$_DESC_TMP" "$_CRUMB_JSON_TMP"
      ```
    - **FAIL**: Escalate to Orchestrator with specifics (which findings failed, why); file crumbs ONLY for validated findings
    - **TIMEOUT/UNAVAILABLE**: Escalate to Orchestrator with consolidated report path; do NOT file crumbs
11. **Round 2+ only — P3 auto-filing**: After filing P1/P2 crumbs, auto-file P3 findings to "Future Work" trail:
    - Find or create the trail: use `crumb_trail_list` MCP tool to check for "future work" (CLI fallback: `crumb trail list | grep -i "future work"`); if not found, create via CLI `crumb trail create --title "Future Work" --description "Low-priority polish and improvements from review sessions"` (no MCP create-trail tool; CLI required)
    - For each P3 (skip any marked as duplicates in the cross-session dedup step (step 7)):
      ```bash
      _DESC_TMP="$(mktemp /tmp/crumb-desc-XXXXXX.md)"
      cat > "$_DESC_TMP" << 'CRUMB_DESC'
      ## Root Cause
      <What is wrong — file:line refs to the primary location.>

      ## Affected Surfaces
      - `file:line` — <instance> (from <reviewer>)

      ## Acceptance Criteria
      - [ ] <testable criterion>
      CRUMB_DESC

      _CRUMB_TITLE="<title>"
      _CRUMB_JSON_TMP="$(mktemp /tmp/crumb-XXXXXX.json)"
      python3 -c "
import json, pathlib, sys
title = sys.argv[1]
desc = pathlib.Path(sys.argv[2]).read_text()
print(json.dumps({'type': 'bug', 'priority': 'P3', 'title': title, 'description': desc, 'acceptance_criteria': [], 'scope': {}, 'links': {}}))
" "$_CRUMB_TITLE" "$_DESC_TMP" > "$_CRUMB_JSON_TMP" || { echo "ERROR: JSON generation failed" >&2; exit 1; }
      crumb create --from-file "$_CRUMB_JSON_TMP"
      crumb link <new-crumb-id> --parent <trail-id>
      rm -f "$_DESC_TMP" "$_CRUMB_JSON_TMP"
      ```
    - Mark P3s as "auto-filed, no action required" in the consolidated summary
    - Do NOT include P3 findings in the fix-or-defer prompt to the Orchestrator
    - In round 1, skip this step — P3s are handled by the Orchestrator's existing flow

12. **Send crumb list to Orchestrator** — After all crumb filing is complete (step 10 PASS for round 1; after step 11 for round 2+), send a structured handoff message to the Orchestrator via SendMessage:

    **Round 1**: Send after step 10 PASS filing is complete (no P3 auto-filing in round 1).
    **Round 2+**: Send after step 11 P3 auto-filing is complete.

    Use this exact format:

    ```
    Review complete: <N> root causes filed.
    P1: <count>, P2: <count>, P3: <count>

    Crumbs requiring fixes:
    - <crumb-id-1> (P1): <root cause title>
    - <crumb-id-2> (P2): <root cause title>
    ...

    P3 crumbs (no action required — auto-filed to Future Work):
    - <crumb-id-N> (P3): <root cause title>
    ...

    Consolidated report: {CONSOLIDATED_OUTPUT_PATH}
    ```

    Rules for this message:
    - List P1 crumbs first, then P2, then P3 (separate P3 under its own header as shown)
    - If there are no P3 crumbs, omit the "P3 crumbs" section entirely
    - In round 1, P3s are not auto-filed — omit the "P3 crumbs" section entirely; the Orchestrator handles P3 disposition in the fix-or-defer flow
    - Include only crumbs that were newly filed in this round; exclude any root causes skipped as cross-session duplicates
    - `<N>` in the first line is the total count of newly-filed crumbs (P1 + P2 + P3 combined)
    - Do NOT include crumb IDs for skipped duplicates; mention them in your output summary instead

    After sending, your work is complete. End your turn.

Your output MUST include (see brief for full format):
- **Reports Received**: a section listing every path from the consolidation brief's `expected_paths` list with present/missing status. Example:
  ```
  ## Reports Received
  | Path | Status |
  |------|--------|
  | .../clarity-review-{timestamp}.md | PRESENT |
  | .../clarity-2-review-{timestamp}.md | MISSING |
  | .../edge-cases-review-{timestamp}.md | PRESENT |
  ```
  Every path in `expected_paths` MUST appear in this table — do not omit paths that were present.
- Root cause groups with all affected surfaces and merge rationale
- Deduplication log (which findings merged, why; include split-instance merges)
- Cross-session dedup log: for each root cause, whether it was filed (new crumb ID), skipped (matched existing crumb ID), or merged with existing
- Crumb IDs filed, with priority breakdown
- Overall verdict
