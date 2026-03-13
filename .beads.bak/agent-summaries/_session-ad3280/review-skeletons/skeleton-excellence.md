<!-- Review skeleton: excellence | Assembled by compose-review-skeletons.sh -->
<!-- Slot markers: {{DATA_FILE_PATH}} {{REPORT_OUTPUT_PATH}} {{REVIEW_ROUND}} {{COMMIT_RANGE}} {{CHANGED_FILES}} {{TIMESTAMP}} -->
<!-- Fill with: scripts/fill-review-slots.sh -->


Perform a excellence review of the completed work.

Step 0: Read your full review brief from {{DATA_FILE_PATH}}
(Contains: commit range, files to review, focus areas, detailed instructions.)

Your workflow:
1. Read ALL files listed in the brief
2. Catalog findings with file:line references and severity (P1/P2/P3)
3. Group findings into preliminary root causes
4. Write your report to {{REPORT_OUTPUT_PATH}}
5. Message relevant Nitpickers if you find cross-domain issues

Your report MUST include these sections (see brief for full format):
- **Findings Catalog**: each finding with file:line, severity, category, description, suggested fix
- **Preliminary Groupings**: findings grouped by root cause
- **Summary Statistics**: total findings, breakdown by severity
- **Cross-Review Messages**: log of messages sent/received with other reviewers
- **Coverage Log**: every scoped file listed, even those with no issues found
- **Overall Assessment**: score out of 10 + verdict (PASS / PASS WITH ISSUES / NEEDS WORK)

Do NOT file beads (`bd create`) — Big Head handles all bead filing.

---
## Review Brief

**Commit range**: {{COMMIT_RANGE}}

**Review round**: {{REVIEW_ROUND}}

**Files to review**:
{{CHANGED_FILES}}

**Task IDs** (for correctness review — run `bd show <id>` to retrieve acceptance criteria):
{{TASK_IDS}}

**Report output path**: {{REPORT_OUTPUT_PATH}}

**Timestamp**: {{TIMESTAMP}}

Do NOT file beads — Big Head handles all bead filing.
