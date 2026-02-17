# Nitpicker Skeleton Template

## Instructions for The Queen

Fill in all `{PLACEHOLDER}` values (uppercase) and use the result as the Task tool `prompt` parameter.
The agent-facing text starts below the `---` separator. Do NOT include this instruction block.

Placeholders:
- {REVIEW_TYPE}: clarity / edge-cases / correctness / excellence
- {DATA_FILE_PATH}: from the Pantry (review mode) verdict table
- {EPIC_ID}: epic being reviewed
- {REPORT_OUTPUT_PATH}: from the Pantry verdict table

## Template (send everything below this line)

---

Perform a {REVIEW_TYPE} review of the completed work.

Step 0: Read your full review brief from {DATA_FILE_PATH}
(Contains: commit range, files to review, focus areas, detailed instructions.)

Your workflow:
1. Read ALL files listed in the brief
2. Catalog findings with file:line references and severity (P1/P2/P3)
3. Group findings into preliminary root causes
4. Write your report to {REPORT_OUTPUT_PATH}
5. Message relevant Nitpickers if you find cross-domain issues

Your report MUST include these sections (see brief for full format):
- **Findings Catalog**: each finding with file:line, severity, category, description, suggested fix
- **Preliminary Groupings**: findings grouped by root cause
- **Summary Statistics**: total findings, breakdown by severity
- **Cross-Review Messages**: log of messages sent/received with other reviewers
- **Coverage Log**: every scoped file listed, even those with no issues found
- **Overall Assessment**: score out of 10 + verdict (PASS / PASS WITH ISSUES / NEEDS WORK)

Do NOT file beads (`bd create`) — Big Head handles all bead filing.
