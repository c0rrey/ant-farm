# Big Head Consolidation Skeleton Template

## Instructions for The Queen

Big Head is a **member of the Nitpicker team** (spawned via TeamCreate, NOT as a separate Task agent).
Do NOT use the Task tool for Big Head — it runs inside the same TeamCreate call as the 4 Nitpickers.

### Wiring: TeamCreate + SendMessage

**Step 1 — Fill placeholders before building the TeamCreate call.**
Replace `{PLACEHOLDER}` values (uppercase) in the agent-facing template below:
- `{DATA_FILE_PATH}`: Big Head consolidation data file written by the Pantry (review mode)
- `{EPIC_ID}`: epic being reviewed (e.g., `ant-farm`)
- `{CONSOLIDATED_OUTPUT_PATH}`: `beads/agent-summaries/{epic-id}/review-reports/review-consolidated-<timestamp>.md`

**Step 2 — Create the Nitpicker team.**
Big Head is the 5th member. Pass the filled-in template text as Big Head's `prompt`. Example:

```
TeamCreate(
  name="nitpicker-team",
  members=[
    { "name": "clarity-reviewer",      "prompt": "<filled nitpicker template with REVIEW_TYPE=clarity>" },
    { "name": "edge-cases-reviewer",   "prompt": "<filled nitpicker template with REVIEW_TYPE=edge-cases>" },
    { "name": "correctness-reviewer",  "prompt": "<filled nitpicker template with REVIEW_TYPE=correctness>" },
    { "name": "excellence-reviewer",   "prompt": "<filled nitpicker template with REVIEW_TYPE=excellence>" },
    { "name": "big-head",              "prompt": "<filled big-head template (this file, below the --- separator)>" }
  ]
)
```

**Step 3 — Send report paths to Big Head via SendMessage.**
After the 4 Nitpickers finish and write their reports, send Big Head a message with the paths:

```
SendMessage(
  to="big-head",
  message="All 4 Nitpicker reports are ready. Report paths:\n- {CLARITY_REPORT_PATH}\n- {EDGE_CASES_REPORT_PATH}\n- {CORRECTNESS_REPORT_PATH}\n- {EXCELLENCE_REPORT_PATH}\n\nProceed with consolidation."
)
```

Big Head then reads those paths and performs consolidation. The Pantry writes all report paths into
`{DATA_FILE_PATH}` so Big Head can also discover them from the brief if SendMessage is delayed.

The agent-facing text starts below the `---` separator. Do NOT include this instruction block in the TeamCreate prompt.

## Template (send everything below this line)

---

Consolidate the 4 Nitpicker reports into a unified summary.

Step 0: Read your consolidation brief from {DATA_FILE_PATH}
(Contains: all 4 report paths, dedup protocol, bead filing instructions, output path.)

Your workflow:
1. Verify all 4 report files exist (FAIL immediately if any missing)
2. Read all 4 reports
3. Collect all findings into a single list
4. Deduplicate: merge findings about the same issue across reviewers
5. Group by root cause: one group per underlying problem, not per occurrence
6. For each merge, document WHY findings share a root cause
7. File ONE bead per root cause: `bd create --type=bug --priority=<P> --title="<title>"`
8. Write consolidated summary to {CONSOLIDATED_OUTPUT_PATH}

Your output MUST include (see brief for full format):
- Root cause groups with all affected surfaces and merge rationale
- Deduplication log (which findings merged, why)
- Bead IDs filed, with priority breakdown
- Overall verdict
