# Big Head Consolidation Skeleton Template

## Instructions for The Queen

Big Head is a **member of the Nitpicker team** (spawned via TeamCreate, NOT as a separate Task agent).
Do NOT use the Task tool for Big Head — it runs inside the same TeamCreate call as the 4 Nitpickers.

**Term definitions (canonical across all orchestration templates):**
- `{TASK_ID}` — full bead ID including project prefix (e.g., `ant-farm-9oa`)
- `{TASK_SUFFIX}` — suffix portion only, no project prefix (e.g., `9oa` from `ant-farm-9oa`, or `74g1` from `hs_website-74g.1`)
- `{EPIC_ID}` — epic suffix only (e.g., `74g` from `hs_website-74g`), or `_standalone` for tasks with no epic parent
- `{TIMESTAMP}` — UTC timestamp in `YYYYMMDD-HHmmss` format (e.g., `20260217-143000`)

### Wiring: TeamCreate + direct spawn prompt

**Step 1 — Fill placeholders before building the TeamCreate call.**
Replace `{PLACEHOLDER}` values (uppercase) in the agent-facing template below:
- `{DATA_FILE_PATH}`: Big Head consolidation data file written by the Pantry (review mode)
- `{EPIC_ID}`: epic being reviewed (e.g., `ant-farm`)
- `{CONSOLIDATED_OUTPUT_PATH}`: `.beads/agent-summaries/{EPIC_ID}/review-reports/review-consolidated-{TIMESTAMP}.md`

**Step 2 — Create the Nitpicker team.**
Big Head is the 5th member. Pass the filled-in template text as Big Head's `prompt`. Include all 4
Nitpicker report paths directly in Big Head's spawn prompt so it can begin consolidation as soon as
the reports are ready. Example:

```
TeamCreate(
  name="nitpicker-team",
  members=[
    { "name": "clarity-reviewer",      "prompt": "<filled nitpicker template with REVIEW_TYPE=clarity>" },
    { "name": "edge-cases-reviewer",   "prompt": "<filled nitpicker template with REVIEW_TYPE=edge-cases>" },
    { "name": "correctness-reviewer",  "prompt": "<filled nitpicker template with REVIEW_TYPE=correctness>" },
    { "name": "excellence-reviewer",   "prompt": "<filled nitpicker template with REVIEW_TYPE=excellence>" },
    { "name": "big-head",              "prompt": "<filled big-head template with all 4 expected report paths embedded>" }
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
