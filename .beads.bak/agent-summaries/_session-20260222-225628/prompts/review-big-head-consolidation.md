<!-- Big Head prompt | Built by build-review-prompts.sh -->


Consolidate the Nitpicker reports into a unified summary.

**Review round**: 3
**Input guard**: If 3 is blank or non-numeric, halt immediately and return: "BIG HEAD ABORTED: REVIEW_ROUND is invalid. Expected a positive integer; got: '3'." Do NOT read any reports or proceed.
- Round 1: expect 4 reports (clarity, edge-cases, correctness, drift)
- Round 2+: expect 2 reports (correctness, edge-cases only)

Step 0: Read your consolidation brief from .beads/agent-summaries/_session-20260222-225628/prompts/review-big-head-consolidation.md
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
   - **On timeout (REPORTS_FOUND=0)**: Before returning the error to the Queen, write a failure artifact using this bash block:
     ```bash
     # NOTE: .beads/agent-summaries/_session-20260222-225628/review-reports/review-consolidated-20260223-003636.md below is a shell variable — it is substituted at
     # runtime by build-review-prompts.sh via fill_slot, NOT a template-time placeholder
     # you fill manually. By the time Big Head runs this block, the braces are gone.
     cat > ".beads/agent-summaries/_session-20260222-225628/review-reports/review-consolidated-20260223-003636.md" << 'EOF'
     # Big Head Consolidation — BLOCKED: Missing Nitpicker Reports
     **Status**: FAILED — prerequisite gate timeout
     **Timestamp**: <current ISO 8601 timestamp>
     **Reason**: Not all expected Nitpicker reports arrived within 30 seconds. <list missing reports>
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
     exit 1
   fi
   ```
   For each root cause group, compare against existing bead titles (from `/tmp/open-beads-$$.txt`):
   - **Exact title match** (case-insensitive): Do NOT file. Log in the summary: "Dedup: RC-N matches existing bead ant-farm-XXXX — skipped."
   - **Similar title** (same root cause, different wording): Run `bd search "<key phrases>" --status open` to confirm. If the existing bead covers the same root cause, do NOT file. Log the match.
   - **No match found**: Mark for filing.
   When uncertain whether a match is truly the same root cause, err on the side of filing (a human can merge later; a missed filing is harder to recover).
8. Write consolidated summary to .beads/agent-summaries/_session-20260222-225628/review-reports/review-consolidated-20260223-003636.md
9. Send consolidated report path to Pest Control (SendMessage): "Consolidated report ready at .beads/agent-summaries/_session-20260222-225628/review-reports/review-consolidated-20260223-003636.md. Please run DMVDC and CCB checkpoints and reply with verdict."
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

Your output MUST include (see brief for full format):
- Root cause groups with all affected surfaces and merge rationale
- Deduplication log (which findings merged, why)
- Cross-session dedup log: for each root cause, whether it was filed (new bead ID), skipped (matched existing bead ID), or merged with existing
- Bead IDs filed, with priority breakdown
- Overall verdict

---
## Consolidation Brief

**Review round**: 3
**Data file**: .beads/agent-summaries/_session-20260222-225628/prompts/review-big-head-consolidation.md
**Consolidated output**: .beads/agent-summaries/_session-20260222-225628/review-reports/review-consolidated-20260223-003636.md
**Timestamp**: 20260223-003636

**Expected report paths** (all must exist before consolidation begins):
- .beads/agent-summaries/_session-20260222-225628/review-reports/correctness-review-20260223-003636.md
- .beads/agent-summaries/_session-20260222-225628/review-reports/edge-cases-review-20260223-003636.md
