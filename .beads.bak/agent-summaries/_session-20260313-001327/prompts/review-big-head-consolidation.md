<!-- Big Head prompt | Built by build-review-prompts.sh -->


Consolidate the Nitpicker reports into a unified summary.

**Review round**: 2
**Input guard**: If 2 is blank or non-numeric, halt immediately and return: "BIG HEAD ABORTED: REVIEW_ROUND is invalid. Expected a positive integer; got: '2'." Do NOT read any reports or proceed.
- Round 1: expect 4 reports (clarity, edge-cases, correctness, drift)
- Round 2+: expect 2 reports (correctness, edge-cases only)

Step 0: Read your consolidation brief from .beads/agent-summaries/_session-20260313-001327/prompts/review-big-head-consolidation.md
(Contains: round-appropriate report paths, dedup protocol, bead filing instructions, output path.)

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
   - **Timeout note**: The polling timeout is 60 seconds (30 iterations × 2 seconds). This allows up to 60 seconds for all reviewers to finish writing their reports. If your reviewers are consistently timing out, the Queen should re-spawn Big Head rather than increasing the timeout — a longer timeout blocks the Queen's context with an idle agent.
   - **On timeout (REPORTS_FOUND=0)**: Before returning the error to the Queen, write a failure artifact using this bash block:
     ```bash
     # NOTE: .beads/agent-summaries/_session-20260313-001327/review-reports/review-consolidated-20260313-014143.md below is a shell variable — it is substituted at
     # runtime by build-review-prompts.sh via fill_slot, NOT a template-time placeholder
     # you fill manually. By the time Big Head runs this block, the braces are gone.
     cat > ".beads/agent-summaries/_session-20260313-001327/review-reports/review-consolidated-20260313-014143.md" << 'EOF'
     # Big Head Consolidation — BLOCKED: Missing Nitpicker Reports
     **Status**: FAILED — prerequisite gate timeout
     **Timestamp**: <current ISO 8601 timestamp>
     **Reason**: Not all expected Nitpicker reports arrived within 60 seconds. <list missing reports>
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
7. **Cross-session dedup**: Before writing the summary or filing beads, check for existing open beads that already cover your root causes:
   ```bash
   if ! bd list --status=open -n 0 --short > /tmp/open-beads-$$.txt 2>&1; then
     echo "ERROR: bd list failed (lock contention or bd error). Aborting bead filing to prevent duplicates."
     cat > ".beads/agent-summaries/_session-20260313-001327/review-reports/review-consolidated-20260313-014143.md" << 'EOF'
     # Big Head Consolidation — BLOCKED: Cross-Session Dedup Infrastructure Error
     **Status**: FAILED — bd list infrastructure error
     **Timestamp**: <current ISO 8601 timestamp>
     **Reason**: `bd list --status=open` failed. Bead filing aborted to prevent duplicate filing. This is likely a lock contention or bd connectivity issue.
     **Recovery**: Retry after the lock clears. If the issue persists, run `bd doctor` and re-spawn Big Head.
     EOF
     exit 1
   fi
   ```
   If the bash block above exits with code 1, stop immediately. Do NOT proceed to consolidation or bead filing. Use the SendMessage tool to notify the Queen: "Big Head FAILED: bd list infrastructure error during cross-session dedup. Bead filing aborted to prevent duplicates. Consolidated output written to .beads/agent-summaries/_session-20260313-001327/review-reports/review-consolidated-20260313-014143.md. Please check bd status and re-spawn Big Head when ready." Then end your turn.
   For each root cause group, compare against existing bead titles (from `/tmp/open-beads-$$.txt`):
   - **Exact title match** (case-insensitive): Do NOT file. Log in the summary: "Dedup: RC-N matches existing bead ant-farm-XXXX — skipped."
   - **Similar title** (same root cause, different wording): Run `bd search "<key phrases>" --status open` to confirm. If the existing bead covers the same root cause, do NOT file. Log the match.
   - **No match found**: Mark for filing.
   When uncertain whether a match is truly the same root cause, err on the side of filing (a human can merge later; a missed filing is harder to recover).
8. Write consolidated summary to .beads/agent-summaries/_session-20260313-001327/review-reports/review-consolidated-20260313-014143.md
9. Send consolidated report path to Pest Control (SendMessage): "Consolidated report ready at .beads/agent-summaries/_session-20260313-001327/review-reports/review-consolidated-20260313-014143.md. Please run DMVDC and CCB checkpoints and reply with verdict."
   - Do NOT file any beads before receiving Pest Control's reply
10. **End your turn** after sending to Pest Control. Do NOT sleep or poll — doing so blocks incoming messages. Pest Control's reply arrives as a new conversation turn. When it arrives, act on the verdict — follow the turn-based retry protocol in reviews.md (Big Head Consolidation Protocol > Step 4: Checkpoint Gate):
    - If no reply after 2 subsequent turns, retry once; if still no reply after 2 more turns, escalate to Queen
    - **PASS**: File ONE bead per root cause (skip any marked as duplicates in step 7). For each bead, write a description to a temp file, then create:
      ```bash
      cat > /tmp/bead-desc-$$.md << 'BEAD_DESC'
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
      BEAD_DESC

      bd create --type=bug --priority=<P> --title="<title>" --body-file /tmp/bead-desc-$$.md
      bd label add <new-bead-id> <primary-review-type>
      rm -f /tmp/bead-desc-$$.md
      ```
    - **FAIL**: Escalate to Queen with specifics (which findings failed, why); file beads ONLY for validated findings
    - **TIMEOUT/UNAVAILABLE**: Escalate to Queen with consolidated report path; do NOT file beads
11. **Round 2+ only — P3 auto-filing**: After filing P1/P2 beads, auto-file P3 findings to "Future Work" epic:
    - Find or create the epic: `bd list --status=open | grep -i "future work"` or `bd epic create --title="Future Work" --description="Low-priority polish and improvements from review sessions"`
    - For each P3 (skip any marked as duplicates in step 7):
      ```bash
      cat > /tmp/bead-desc-$$.md << 'BEAD_DESC'
      ## Root Cause
      <What is wrong — file:line refs to the primary location.>

      ## Affected Surfaces
      - `file:line` — <instance> (from <reviewer>)

      ## Acceptance Criteria
      - [ ] <testable criterion>
      BEAD_DESC

      bd create --type=bug --priority=3 --title="<title>" --body-file /tmp/bead-desc-$$.md
      bd dep add <new-bead-id> <epic-id> --type parent-child
      rm -f /tmp/bead-desc-$$.md
      ```
    - Mark P3s as "auto-filed, no action required" in the consolidated summary
    - Do NOT include P3 findings in the fix-or-defer prompt to the Queen
    - In round 1, skip this step — P3s are handled by the Queen's existing flow

12. **Send bead list to Queen** — After all bead filing is complete (step 10 PASS for round 1; after step 11 for round 2+), send a structured handoff message to the Queen via SendMessage:

    **Round 1**: Send after step 10 PASS filing is complete (no P3 auto-filing in round 1).
    **Round 2+**: Send after step 11 P3 auto-filing is complete.

    Use this exact format:

    ```
    Fix handoff: <N> root causes filed.
    P1: <count>, P2: <count>, P3: <count>

    Beads requiring fixes:
    - <bead-id-1> (P1): <root cause title>
    - <bead-id-2> (P2): <root cause title>
    ...

    P3 beads (no action required — auto-filed to Future Work):
    - <bead-id-N> (P3): <root cause title>
    ...

    Consolidated report: .beads/agent-summaries/_session-20260313-001327/review-reports/review-consolidated-20260313-014143.md
    ```

    Rules for this message:
    - List P1 beads first, then P2, then P3 (separate P3 under its own header as shown)
    - If there are no P3 beads, omit the "P3 beads" section entirely
    - In round 1, P3s are not auto-filed — omit the "P3 beads" section entirely; the Queen handles P3 disposition in the fix-or-defer flow
    - Include only beads that were newly filed in this round; exclude any root causes skipped as cross-session duplicates
    - `<N>` in the first line is the total count of newly-filed beads (P1 + P2 + P3 combined)
    - Do NOT include bead IDs for skipped duplicates; mention them in your output summary instead

    After sending, your work is complete. End your turn.

Your output MUST include (see brief for full format):
- Root cause groups with all affected surfaces and merge rationale
- Deduplication log (which findings merged, why)
- Cross-session dedup log: for each root cause, whether it was filed (new bead ID), skipped (matched existing bead ID), or merged with existing
- Bead IDs filed, with priority breakdown
- Overall verdict

---
## Consolidation Brief

**Review round**: 2
**Data file**: .beads/agent-summaries/_session-20260313-001327/prompts/review-big-head-consolidation.md
**Consolidated output**: .beads/agent-summaries/_session-20260313-001327/review-reports/review-consolidated-20260313-014143.md
**Timestamp**: 20260313-014143

**Expected report paths** (all must exist before consolidation begins):
- .beads/agent-summaries/_session-20260313-001327/review-reports/correctness-review-20260313-014143.md
- .beads/agent-summaries/_session-20260313-001327/review-reports/edge-cases-review-20260313-014143.md
