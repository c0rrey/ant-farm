# Big Head Consolidation Skeleton Template

<!-- Queen-facing wiring instructions: orchestration/reference/big-head-wiring.md -->
<!-- Agent-facing template starts below the --- separator. -->
<!-- Do NOT include anything above --- in the TeamCreate prompt. -->

---

Consolidate the Nitpicker reports into a unified summary.

**Review round**: {REVIEW_ROUND}
**Input guard**: If {REVIEW_ROUND} is blank or non-numeric, halt immediately and return: "BIG HEAD ABORTED: REVIEW_ROUND is invalid. Expected a positive integer; got: '{REVIEW_ROUND}'." Do NOT read any reports or proceed.
- Round 1: expect 4 reports (clarity, edge-cases, correctness, drift)
- Round 2+: expect 2 reports (correctness, edge-cases only)

Step 0: Read your consolidation brief from {DATA_FILE_PATH}
(Format: markdown. Sections: Report Paths, Deduplication Protocol, Crumb Filing Instructions, Consolidated Output Path, Pest Control Coordination Note, Review Round, P3 Auto-Filing Instructions (round 2+ only).)

**Failure Artifact Convention** (applies to ALL failure conditions in this workflow):
When any step reaches a FAIL condition, write a brief failure artifact to the expected output path before returning an error. Standard format:
```
# [COMPONENT] — [FAILURE TYPE]
**Status**: FAILED — <one-line description>
**Timestamp**: <ISO 8601>
**Reason**: <what went wrong>
**Recovery**: <what to do next>
```
This ensures downstream consumers (Queen, Pest Control) have a written record of the failure at the path they expect — even if the output is a FAILED file rather than a consolidated summary.

Your workflow:
1. Verify all expected report files exist (4 for round 1; 2 for round 2+) — follow the missing-report handling protocol in your consolidation brief (Step 0a)
   - The brief is authoritative for this step: it specifies the polling timeout, error return format, and failure conditions
   - **Single-invocation constraint**: The polling bash block in the brief (the `while` loop with `sleep`) MUST be executed in a single Bash tool call. Do NOT attempt to poll by calling Bash repeatedly across multiple turns — the shell state does not persist between turns and you cannot `sleep` across turns. Submit the entire polling block as one Bash tool invocation and wait for its result.
   - **Timeout note**: The polling timeout is determined by the consolidation brief (the `while` loop parameters in Step 0a are authoritative — the value here is approximate). This allows reviewers to finish writing their reports before Big Head proceeds. If your reviewers are consistently timing out, the Queen should re-spawn Big Head rather than increasing the timeout — a longer timeout blocks the Queen's context with an idle agent.
   - **On timeout (REPORTS_FOUND=0)**: Before returning the error to the Queen, write a failure artifact using this bash block:
     ```bash
     # NOTE: {CONSOLIDATED_OUTPUT_PATH} is a template placeholder (pre-substitution form).
     # build-review-prompts.sh replaces it with a literal path (e.g.
     # /path/to/session/consolidated.md) before this prompt reaches Big Head.
     # By the time Big Head executes this block, the braces are gone and a real
     # filesystem path appears in their place.
     mkdir -p "$(dirname "{CONSOLIDATED_OUTPUT_PATH}")" || { echo "ERROR: failed to create output directory for {CONSOLIDATED_OUTPUT_PATH}. Aborting."; exit 1; }
     cat > "{CONSOLIDATED_OUTPUT_PATH}" << 'EOF'
     # Big Head Consolidation — BLOCKED: Missing Nitpicker Reports
     **Status**: FAILED — prerequisite gate timeout
     **Timestamp**: <current ISO 8601 timestamp>
     **Reason**: Not all expected Nitpicker reports arrived within the timeout specified in the consolidation brief. <list missing reports>
     **Recovery**: Check reviewer logs. Once all expected reports are present, re-spawn Big Head consolidation.
     EOF
     ```
   - After writing the failure artifact, return the error to the Queen as specified in the brief
   - Do NOT proceed to read reports or perform consolidation
2. Read all expected reports
3. Collect all findings into a single list
4. Deduplicate: merge findings about the same issue across reviewers
5. Group by root cause: one group per underlying problem, not per occurrence
6. For each merge, document WHY findings share a root cause
7. **Cross-session dedup**: Before writing the summary or filing crumbs, check for existing open crumbs that already cover your root causes:
   ```bash
   if ! crumb list --open --short > /tmp/open-crumbs-$$.txt 2>&1; then
     echo "ERROR: crumb list failed (file error or crumb error). Aborting crumb filing to prevent duplicates."
     mkdir -p "$(dirname "{CONSOLIDATED_OUTPUT_PATH}")" || { echo "ERROR: failed to create output directory for {CONSOLIDATED_OUTPUT_PATH}. Aborting."; exit 1; }
     cat > "{CONSOLIDATED_OUTPUT_PATH}" << 'EOF'
     # Big Head Consolidation — BLOCKED: Cross-Session Dedup Infrastructure Error
     **Status**: FAILED — crumb list infrastructure error
     **Timestamp**: <current ISO 8601 timestamp>
     **Reason**: `crumb list --open` failed. Crumb filing aborted to prevent duplicate filing. This is likely a file access or crumb CLI issue.
     **Recovery**: Retry after the issue clears. If the issue persists, run `crumb doctor` and re-spawn Big Head.
     EOF
     exit 1
   fi
   ```
   If the bash block above exits with code 1, stop immediately. Do NOT proceed to consolidation or crumb filing. Use the SendMessage tool to notify the Queen: "Big Head FAILED: crumb list infrastructure error during cross-session dedup. Crumb filing aborted to prevent duplicates. Consolidated output written to {CONSOLIDATED_OUTPUT_PATH}. Please check crumb status and re-spawn Big Head when ready." Then end your turn.
   For each root cause group, compare against existing crumb titles (from `/tmp/open-crumbs-$$.txt`):
   - **Exact title match** (case-insensitive): Do NOT file. Log in the summary: "Dedup: RC-N matches existing crumb <ID> — skipped."
   - **Similar title** (same root cause, different wording): Run `crumb search "<key phrases>"` to confirm. If the existing crumb covers the same root cause, do NOT file. Log the match.
   - **No match found**: Mark for filing.
   When uncertain whether a match is truly the same root cause, err on the side of filing (a human can merge later; a missed filing is harder to recover).
   After completing the dedup comparison, clean up the temp file:
   ```bash
   rm -f /tmp/open-crumbs-$$.txt
   ```
8. Write consolidated summary to {CONSOLIDATED_OUTPUT_PATH}
9. Send consolidated report path to Pest Control (SendMessage): "Consolidated report ready at {CONSOLIDATED_OUTPUT_PATH}. Please run DMVDC and CCB checkpoints and reply with verdict."
   - Do NOT file any crumbs before receiving Pest Control's reply
10. **End your turn** after sending to Pest Control. Do NOT sleep or poll — doing so blocks incoming messages. Pest Control's reply arrives as a new conversation turn. When it arrives, act on the verdict — follow the turn-based retry protocol in reviews.md (Big Head Consolidation Protocol > Step 4: Checkpoint Gate):
    - If no reply after 2 subsequent turns, retry once; if still no reply after 2 more turns, escalate to Queen
    - **PASS**: File ONE crumb per root cause (skip any marked as duplicates in step 7). For each crumb, write a description to a temp file, then create:
      ```bash
      cat > /tmp/crumb-desc-$$.md << 'CRUMB_DESC'
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

      crumb create --from-json "{\"type\":\"bug\",\"priority\":\"P<P>\",\"title\":\"<title>\",\"description\":\"$(cat /tmp/crumb-desc-$$.md)\",\"acceptance_criteria\":[],\"scope\":{},\"links\":{}}"
      rm -f /tmp/crumb-desc-$$.md
      ```
    - **FAIL**: Escalate to Queen with specifics (which findings failed, why); file crumbs ONLY for validated findings
    - **TIMEOUT/UNAVAILABLE**: Escalate to Queen with consolidated report path; do NOT file crumbs
11. **Round 2+ only — P3 auto-filing**: After filing P1/P2 crumbs, auto-file P3 findings to "Future Work" trail:
    - Find or create the trail: `crumb trail list | grep -i "future work"` or `crumb trail create --title "Future Work" --description "Low-priority polish and improvements from review sessions"`
    - For each P3 (skip any marked as duplicates in step 7):
      ```bash
      cat > /tmp/crumb-desc-$$.md << 'CRUMB_DESC'
      ## Root Cause
      <What is wrong — file:line refs to the primary location.>

      ## Affected Surfaces
      - `file:line` — <instance> (from <reviewer>)

      ## Acceptance Criteria
      - [ ] <testable criterion>
      CRUMB_DESC

      crumb create --from-json "{\"type\":\"bug\",\"priority\":\"P3\",\"title\":\"<title>\",\"description\":\"$(cat /tmp/crumb-desc-$$.md)\",\"acceptance_criteria\":[],\"scope\":{},\"links\":{}}"
      crumb link <new-crumb-id> --parent <trail-id>
      rm -f /tmp/crumb-desc-$$.md
      ```
    - Mark P3s as "auto-filed, no action required" in the consolidated summary
    - Do NOT include P3 findings in the fix-or-defer prompt to the Queen
    - In round 1, skip this step — P3s are handled by the Queen's existing flow

12. **Send crumb list to Queen** — After all crumb filing is complete (step 10 PASS for round 1; after step 11 for round 2+), send a structured handoff message to the Queen via SendMessage:

    **Round 1**: Send after step 10 PASS filing is complete (no P3 auto-filing in round 1).
    **Round 2+**: Send after step 11 P3 auto-filing is complete.

    Use this exact format:

    ```
    Fix handoff: <N> root causes filed.
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
    - In round 1, P3s are not auto-filed — omit the "P3 crumbs" section entirely; the Queen handles P3 disposition in the fix-or-defer flow
    - Include only crumbs that were newly filed in this round; exclude any root causes skipped as cross-session duplicates
    - `<N>` in the first line is the total count of newly-filed crumbs (P1 + P2 + P3 combined)
    - Do NOT include crumb IDs for skipped duplicates; mention them in your output summary instead

    After sending, your work is complete. End your turn.

Your output MUST include (see brief for full format):
- Root cause groups with all affected surfaces and merge rationale
- Deduplication log (which findings merged, why)
- Cross-session dedup log: for each root cause, whether it was filed (new crumb ID), skipped (matched existing crumb ID), or merged with existing
- Crumb IDs filed, with priority breakdown
- Overall verdict
