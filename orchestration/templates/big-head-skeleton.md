# Big Head Consolidation Skeleton Template

## Instructions for the Queen

Big Head is a **member of the Nitpicker team** (spawned via TeamCreate, NOT as a separate Task agent).
Do NOT use the Task tool for Big Head — it runs inside the same TeamCreate call as the Nitpickers (4 in round 1; 2 in round 2+).

**Term definitions (canonical across all orchestration templates):**
- `{TASK_ID}` — full bead ID including project prefix (e.g., `ant-farm-9oa`)
- `{TASK_SUFFIX}` — suffix portion only; extracted by splitting on the LAST hyphen (e.g., `9oa` from `ant-farm-9oa`, or `74g1` from `my-project-74g.1`)
- `{TIMESTAMP}` — UTC timestamp in `YYYYMMDD-HHmmss` format (e.g., `20260217-143000`)
- `{SESSION_DIR}` — session artifact directory (e.g., `.beads/agent-summaries/_session-abc123`)
- `{REVIEW_ROUND}`: review round number (1, 2, 3, ...). Determines report count and P3 handling.

### Wiring: TeamCreate + direct spawn prompt

**Step 1 — Fill placeholders before building the TeamCreate call.**
Replace `{PLACEHOLDER}` values (uppercase) in the agent-facing template below:
- `{MODEL}`: Big Head model (specified in the Big Head Consolidation Protocol section of orchestration/templates/reviews.md; currently `opus`)
- `{DATA_FILE_PATH}`: Big Head consolidation brief written by build-review-prompts.sh
- `{CONSOLIDATED_OUTPUT_PATH}`: `{SESSION_DIR}/review-reports/review-consolidated-{TIMESTAMP}.md`

**Step 2 — Create the Nitpicker team.**
Pass the filled-in template text as Big Head's `prompt`. Include all expected Nitpicker report paths directly in Big Head's spawn prompt so it can begin consolidation as soon as the reports are ready. Pest Control must be a team member so Big Head can SendMessage to it directly for checkpoint validation (see Step 4 in reviews.md).

**Round 1**: Big Head is the 5th member; Pest Control is the 6th. Pass the filled-in template text as Big Head's `prompt`.

```
TeamCreate(
  name="nitpicker-team",
  members=[
    { "name": "clarity-reviewer",      "prompt": "<filled nitpicker template with REVIEW_TYPE=clarity>", "model": "sonnet" },
    { "name": "edge-cases-reviewer",   "prompt": "<filled nitpicker template with REVIEW_TYPE=edge-cases>", "model": "sonnet" },
    { "name": "correctness-reviewer",  "prompt": "<filled nitpicker template with REVIEW_TYPE=correctness>", "model": "sonnet" },
    { "name": "drift-reviewer",        "prompt": "<filled nitpicker template with REVIEW_TYPE=drift>", "model": "sonnet" },
    { "name": "big-head",              "prompt": "<filled big-head template with all 4 expected report paths embedded>", "model": "{MODEL}" },
    { "name": "pest-control",          "prompt": "<pest-control prompt>", "model": "sonnet" }
  ]
)
```

**Round 2+**: Big Head is the 3rd member; Pest Control is the 4th. Only Correctness and Edge Cases reviewers are spawned.

```
TeamCreate(
  name="nitpicker-team",
  members=[
    { "name": "correctness-reviewer",  "prompt": "<filled nitpicker template with REVIEW_TYPE=correctness>", "model": "sonnet" },
    { "name": "edge-cases-reviewer",   "prompt": "<filled nitpicker template with REVIEW_TYPE=edge-cases>", "model": "sonnet" },
    { "name": "big-head",              "prompt": "<filled big-head template with 2 expected report paths embedded>", "model": "{MODEL}" },
    { "name": "pest-control",          "prompt": "<pest-control prompt>", "model": "sonnet" }
  ]
)
```

**Step 3 — Embed report paths in Big Head's spawn prompt.**
Rather than sending a follow-up SendMessage, include the expected report paths directly in Big Head's
initial prompt (the agent-facing template below). build-review-prompts.sh writes all report paths into
`{DATA_FILE_PATH}`, so Big Head discovers them from the brief. No SendMessage step is required.

The agent-facing text starts below the `---` separator. Do NOT include this instruction block in the TeamCreate prompt.

## Template (send everything below this line)

---

Consolidate the Nitpicker reports into a unified summary.

**Review round**: {REVIEW_ROUND}
**Input guard**: If {REVIEW_ROUND} is blank or non-numeric, halt immediately and return: "BIG HEAD ABORTED: REVIEW_ROUND is invalid. Expected a positive integer; got: '{REVIEW_ROUND}'." Do NOT read any reports or proceed.
- Round 1: expect 4 reports (clarity, edge-cases, correctness, drift)
- Round 2+: expect 2 reports (correctness, edge-cases only)

Step 0: Read your consolidation brief from {DATA_FILE_PATH}
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
     cat > "{CONSOLIDATED_OUTPUT_PATH}" << 'EOF'
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
8. Write consolidated summary to {CONSOLIDATED_OUTPUT_PATH}
9. Send consolidated report path to Pest Control (SendMessage): "Consolidated report ready at {CONSOLIDATED_OUTPUT_PATH}. Please run DMVDC and CCB checkpoints and reply with verdict."
   - Do NOT file any beads before receiving Pest Control's reply
10. Await Pest Control verdict — follow the timeout/retry protocol in reviews.md Step 4:
    - Wait up to 60 seconds; retry once if no response; escalate to Queen after 120s total with no reply
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
