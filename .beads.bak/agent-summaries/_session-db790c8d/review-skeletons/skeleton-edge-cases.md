<!-- Review skeleton: edge-cases | Assembled by compose-review-skeletons.sh -->
<!-- Slot markers: {{DATA_FILE_PATH}} {{REPORT_OUTPUT_PATH}} {{REVIEW_ROUND}} {{COMMIT_RANGE}} {{CHANGED_FILES}} {{TIMESTAMP}} -->
<!-- Fill with: scripts/fill-review-slots.sh -->

**Your focus**: Defensive code that handles the unexpected. You review for robustness at the boundaries.

Focus areas:
1. **Input validation** — What happens with malformed input? Missing fields? Invalid values?
2. **Error handling** — Are exceptions caught? Are error messages helpful (not swallowed silently)?
3. **Boundary conditions** — Empty strings? None/null? Zero-length lists? Max values? Off-by-one?
4. **File operations** — What if files don't exist? Can't be read? Can't be written?
5. **Concurrency** — Race conditions? Lock contention? Shared-state mutations?
6. **Platform differences** — Path separators? Line endings? Locale-dependent parsing?

**Severity calibration**:
- P1: Unhandled edge case causes data loss, crashes a process, or corrupts persistent state
- P2: Unhandled edge case causes incorrect behavior the user will notice but can recover from
- P3: Defensive check missing but condition is highly unlikely or failure mode is obvious (default)

**Not your responsibility** — hand off to the relevant reviewer:
- Clarity: naming, comments, style, structural organization
- Correctness: happy-path logic correctness, acceptance criteria (given valid inputs)
- Excellence: performance of valid paths, security beyond input validation, architecture


Perform a edge-cases review of the completed work.

**Review round**: {{REVIEW_ROUND}}
**Input guard**: If {{REVIEW_ROUND}} is blank or non-numeric, halt immediately and return: "NITPICKER ABORTED: REVIEW_ROUND is invalid. Expected a positive integer; got: '{{REVIEW_ROUND}}'." Do NOT proceed.
If round 2+: Your scope is limited to fix commits only. You may read full files for context, but your mandate is: did these fixes land correctly and not break anything? Out-of-scope findings are only reportable if they would cause a runtime failure or silently wrong results. Do NOT report naming, style, docs, or improvement opportunities outside fix scope.

Step 0: Read your full review brief from {{DATA_FILE_PATH}}
(Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions.)

Your workflow:
1. Read ALL files listed in the brief
2. Catalog findings with file:line references and severity (P1/P2/P3)
3. Group findings into preliminary root causes
4. Write your report to {{REPORT_OUTPUT_PATH}}
5. Message relevant Nitpickers if you find cross-domain issues

**Cross-review messaging protocol**:
When you find something that clearly belongs to another reviewer's domain, message them:
- To Clarity: "Found misleading comment in file.py:L42 — may want to review."
- To Edge Cases: "Found unvalidated external input at script.sh:L88 — could be boundary issue."
- To Correctness: "Logic at rules.md:L120 may not satisfy acceptance criterion 3 — check bd show <task-id>."
- To Excellence: "Function at pantry.md:L200 is 80 lines and deeply nested — worth an excellence look."
Do NOT message for status updates. Do NOT report the finding yourself AND message — pick one owner.
Log all sent/received messages in your report's Cross-Review Messages section.

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
