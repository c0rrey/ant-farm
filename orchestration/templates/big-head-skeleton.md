# Big Head Consolidation Skeleton Template

## Instructions for The Queen

Fill in all `{PLACEHOLDER}` values (uppercase) and use the result as the Task tool `prompt` parameter.
The agent-facing text starts below the `---` separator. Do NOT include this instruction block.

Placeholders:
- {DATA_FILE_PATH}: Big Head consolidation data file from the Pantry
- {EPIC_ID}: epic being reviewed
- {CONSOLIDATED_OUTPUT_PATH}: .beads/agent-summaries/{epic-id}/review-reports/review-consolidated-<timestamp>.md

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
