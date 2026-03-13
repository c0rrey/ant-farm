<!-- Review skeleton: edge-cases | Assembled by compose-review-skeletons.sh -->
<!-- Slot markers: .beads/agent-summaries/_session-cd9866/prompts/review-edge-cases.md .beads/agent-summaries/_session-cd9866/review-reports/edge-cases-review-20260220-201414.md 3 d4aa294..HEAD orchestration/templates/reviews.md 20260220-201414 -->
<!-- Fill with: scripts/fill-review-slots.sh -->


Perform a edge-cases review of the completed work.

**Review round**: 3
If round 2+: Your scope is limited to fix commits only. You may read full files for context, but your mandate is: did these fixes land correctly and not break anything? Out-of-scope findings are only reportable if they would cause a runtime failure or silently wrong results. Do NOT report naming, style, docs, or improvement opportunities outside fix scope.

Step 0: Read your full review brief from .beads/agent-summaries/_session-cd9866/prompts/review-edge-cases.md
(Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions.)

Your workflow:
1. Read ALL files listed in the brief
2. Catalog findings with file:line references and severity (P1/P2/P3)
3. Group findings into preliminary root causes
4. Write your report to .beads/agent-summaries/_session-cd9866/review-reports/edge-cases-review-20260220-201414.md
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

**Commit range**: d4aa294..HEAD

**Review round**: 3

**Files to review**:
orchestration/templates/reviews.md

**Task IDs** (for correctness review — run `bd show <id>` to retrieve acceptance criteria):
ant-farm-12u9

**Report output path**: .beads/agent-summaries/_session-cd9866/review-reports/edge-cases-review-20260220-201414.md

**Timestamp**: 20260220-201414

Do NOT file beads — Big Head handles all bead filing.
