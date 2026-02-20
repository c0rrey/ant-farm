# Big Head Consolidation Skeleton Template

## Instructions for The Queen

Big Head is a **member of the Nitpicker team** (spawned via TeamCreate, NOT as a separate Task agent).
Do NOT use the Task tool for Big Head — it runs inside the same TeamCreate call as the 4 Nitpickers.

**Term definitions (canonical across all orchestration templates):**
- `{TASK_ID}` — full bead ID including project prefix (e.g., `ant-farm-9oa`)
- `{TASK_SUFFIX}` — suffix portion only; extracted by splitting on the LAST hyphen (e.g., `9oa` from `ant-farm-9oa`, or `74g1` from `my-project-74g.1`)
- `{TIMESTAMP}` — UTC timestamp in `YYYYMMDD-HHmmss` format (e.g., `20260217-143000`)
- `{SESSION_DIR}` — session artifact directory (e.g., `.beads/agent-summaries/_session-abc123`)
- `{REVIEW_ROUND}`: review round number (1, 2, 3, ...). Determines report count and P3 handling.

### Wiring: TeamCreate + direct spawn prompt

**Step 1 — Fill placeholders before building the TeamCreate call.**
Replace `{PLACEHOLDER}` values (uppercase) in the agent-facing template below:
- `{MODEL}`: Big Head model (specified in orchestration/templates/reviews.md line 322; currently `opus`)
- `{DATA_FILE_PATH}`: Big Head consolidation data file written by the Pantry (review mode)
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
    { "name": "excellence-reviewer",   "prompt": "<filled nitpicker template with REVIEW_TYPE=excellence>", "model": "sonnet" },
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
initial prompt (the agent-facing template below). The Pantry writes all report paths into
`{DATA_FILE_PATH}`, so Big Head discovers them from the brief. No SendMessage step is required.

The agent-facing text starts below the `---` separator. Do NOT include this instruction block in the TeamCreate prompt.

## Template (send everything below this line)

---

Consolidate the Nitpicker reports into a unified summary.

**Review round**: {REVIEW_ROUND}
- Round 1: expect 4 reports (clarity, edge-cases, correctness, excellence)
- Round 2+: expect 2 reports (correctness, edge-cases only)

Step 0: Read your consolidation brief from {DATA_FILE_PATH}
(Contains: all 4 report paths, dedup protocol, bead filing instructions, output path.)

Your workflow:
1. Verify all 4 report files exist — follow the missing-report handling protocol in your consolidation brief (Step 0a)
   - The brief is authoritative for this step: it specifies the polling timeout, error return format, and failure conditions
   - Do NOT proceed to read reports or perform consolidation until the brief's Step 0a protocol completes successfully
2. Read all 4 reports
3. Collect all findings into a single list
4. Deduplicate: merge findings about the same issue across reviewers
5. Group by root cause: one group per underlying problem, not per occurrence
6. For each merge, document WHY findings share a root cause
7. Write consolidated summary to {CONSOLIDATED_OUTPUT_PATH}
8. Send consolidated report path to Pest Control (SendMessage): "Consolidated report ready at {CONSOLIDATED_OUTPUT_PATH}. Please run DMVDC and CCB checkpoints and reply with verdict."
   - Do NOT file any beads before receiving Pest Control's reply
9. Await Pest Control verdict — follow the timeout/retry protocol in reviews.md Step 4:
   - Wait up to 60 seconds; retry once if no response; escalate to Queen after 120s total with no reply
   - **PASS**: File ONE bead per root cause: `bd create --type=bug --priority=<P> --title="<title>"`
   - **FAIL**: Escalate to Queen with specifics (which findings failed, why); file beads ONLY for validated findings
   - **TIMEOUT/UNAVAILABLE**: Escalate to Queen with consolidated report path; do NOT file beads
10. **Round 2+ only — P3 auto-filing**: After filing P1/P2 beads, auto-file P3 findings to "Future Work" epic:
    - Find or create the epic: `bd list --status=open | grep -i "future work"` or `bd epic create --title="Future Work" --description="Low-priority polish and improvements from review sessions"`
    - For each P3: `bd create --type=bug --priority=3 --title="<title>"` then `bd dep add <id> <epic-id> --type parent-child`
    - Mark P3s as "auto-filed, no action required" in the consolidated summary
    - Do NOT include P3 findings in the fix-or-defer prompt to the Queen
    - In round 1, skip this step — P3s are handled by the Queen's existing flow

Your output MUST include (see brief for full format):
- Root cause groups with all affected surfaces and merge rationale
- Deduplication log (which findings merged, why)
- Bead IDs filed, with priority breakdown
- Overall verdict
