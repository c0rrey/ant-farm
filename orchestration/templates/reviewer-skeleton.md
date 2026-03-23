# Reviewer Skeleton Template

## Instructions for the Orchestrator

Fill in all `{PLACEHOLDER}` values (uppercase) and use the result as the Task tool `prompt` parameter.
The agent-facing text starts below the `---` separator. Do NOT include this instruction block.

Placeholders:
- {REVIEW_TYPE}: clarity / edge-cases / correctness / drift
  (These are the canonical short names. See "Review Type Canonical Names" in reviews.md for the full short-name → display-title mapping.)
- {DATA_FILE_PATH}: from build-review-prompts.sh output table
- {REPORT_OUTPUT_PATH}: from build-review-prompts.sh output table (session-scoped)
- {REVIEW_ROUND}: 1, 2, 3, ... (determines scope instructions; filled by build-review-prompts.sh)

## Template (send everything below this line)

---

Perform a {REVIEW_TYPE} review of the completed work.

**Review round**: {REVIEW_ROUND}
**Input guard**: If {REVIEW_ROUND} is blank or non-numeric, halt immediately and return: "NITPICKER ABORTED: REVIEW_ROUND is invalid. Expected a positive integer; got: '{REVIEW_ROUND}'." Do NOT proceed.
If round 2+: **Fix verification scope**: Your scope is limited to fix commits only. You may read full files for context, but your mandate is: did these fixes land correctly and not break anything?
**Out-of-scope findings**: If you notice something outside the fix commits that would cause a runtime failure, incorrect agent behavior, or silently wrong results (e.g., stale cross-references pointing to wrong sections), report it. Do NOT report naming conventions, style preferences, documentation gaps, or improvement opportunities outside the fix scope.

Step 0: Read your full review brief from {DATA_FILE_PATH}
(Format: markdown. Sections: Commit Range, File List, Focus Areas, Report Output Path, Crumb Filing Prohibition, Messaging Guidelines.)

Your workflow:
1. Read ALL files listed in the brief
2. Catalog findings with file:line references and severity (P1/P2/P3)
3. Group findings into preliminary root causes
4. Write your report to {REPORT_OUTPUT_PATH}
5. Message relevant Reviewers if you find cross-domain issues

**Cross-review messaging protocol**:
When you find something that clearly belongs to another reviewer's domain, message them:
- To Clarity: "Found misleading comment in file.py:L42 — may want to review."
- To Edge Cases: "Found unvalidated external input at script.sh:L88 — could be boundary issue."
- To Correctness: "Logic at rules.md:L120 may not satisfy acceptance criterion 3 — check `crumb_show` MCP tool for <task-id> (CLI fallback: `crumb show <task-id>`)."
- To Drift: "Function signature at api.py:L42 changed arity — check if callers in routes.py still match."
Do NOT message for status updates. Do NOT report the finding yourself AND message — pick one owner.
Log all sent/received messages in your report's Cross-Review Messages section.

Your report MUST include these sections (see brief for full format):
- **Findings Catalog**: each finding with file:line, severity, category, description, suggested fix
- **Preliminary Groupings**: findings grouped by root cause
- **Summary Statistics**: total findings, breakdown by severity
- **Cross-Review Messages**: log of messages sent/received with other reviewers
- **Coverage Log**: every scoped file listed, even those with no issues found
- **Overall Assessment**: score out of 10 + verdict (PASS / PASS WITH ISSUES / NEEDS WORK)

Do NOT file crumbs (do not call the `crumb_create` MCP tool or `crumb create` CLI) — Review Consolidator handles all crumb filing.
