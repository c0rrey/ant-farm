<!-- Review prompt: excellence | Built by build-review-prompts.sh -->


Perform a excellence review of the completed work.

**Review round**: 1
**Input guard**: If 1 is blank or non-numeric, halt immediately and return: "NITPICKER ABORTED: REVIEW_ROUND is invalid. Expected a positive integer; got: '1'." Do NOT proceed.
If round 2+: Your scope is limited to fix commits only. You may read full files for context, but your mandate is: did these fixes land correctly and not break anything? Out-of-scope findings are only reportable if they would cause a runtime failure or silently wrong results. Do NOT report naming, style, docs, or improvement opportunities outside fix scope.

Step 0: Read your full review brief from .beads/agent-summaries/_session-79d4200e/prompts/review-excellence.md
(Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions.)

Your workflow:
1. Read ALL files listed in the brief
2. Catalog findings with file:line references and severity (P1/P2/P3)
3. Group findings into preliminary root causes
4. Write your report to .beads/agent-summaries/_session-79d4200e/review-reports/excellence-review-20260222-142808.md
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

**Commit range**: 94e350d^..HEAD

**Review round**: 1

**Files to review**:
CLAUDE.md CONTRIBUTING.md README.md orchestration/GLOSSARY.md orchestration/PLACEHOLDER_CONVENTIONS.md orchestration/RULES.md orchestration/SETUP.md orchestration/templates/checkpoints.md

**Task IDs** (for correctness review — run `bd show <id>` to retrieve acceptance criteria):
ant-farm-9iyp ant-farm-m5lg ant-farm-x9yx ant-farm-trfb ant-farm-f1xn ant-farm-a87o ant-farm-geou ant-farm-ng0e ant-farm-70ti ant-farm-9hxz ant-farm-lbcy ant-farm-x9eu

**Report output path**: .beads/agent-summaries/_session-79d4200e/review-reports/excellence-review-20260222-142808.md

**Timestamp**: 20260222-142808

Do NOT file beads — Big Head handles all bead filing.
