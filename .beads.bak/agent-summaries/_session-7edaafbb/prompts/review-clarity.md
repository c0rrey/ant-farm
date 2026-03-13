<!-- Review skeleton: clarity | Assembled by compose-review-skeletons.sh -->
<!-- Slot markers: .beads/agent-summaries/_session-7edaafbb/prompts/review-clarity.md .beads/agent-summaries/_session-7edaafbb/review-reports/clarity-review-20260220-231026.md 1 60bdcb4..HEAD orchestration/RULES.md orchestration/SETUP.md orchestration/reference/dependency-analysis.md orchestration/templates/checkpoints.md orchestration/templates/implementation.md orchestration/templates/reviews.md orchestration/templates/scout.md scripts/compose-review-skeletons.sh scripts/fill-review-slots.sh scripts/install-hooks.sh scripts/parse-progress-log.sh scripts/scrub-pii.sh scripts/sync-to-claude.sh 20260220-231026 -->
<!-- Fill with: scripts/fill-review-slots.sh -->


Perform a clarity review of the completed work.

**Review round**: 1
If round 2+: Your scope is limited to fix commits only. You may read full files for context, but your mandate is: did these fixes land correctly and not break anything? Out-of-scope findings are only reportable if they would cause a runtime failure or silently wrong results. Do NOT report naming, style, docs, or improvement opportunities outside fix scope.

Step 0: Read your full review brief from .beads/agent-summaries/_session-7edaafbb/prompts/review-clarity.md
(Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions.)

Your workflow:
1. Read ALL files listed in the brief
2. Catalog findings with file:line references and severity (P1/P2/P3)
3. Group findings into preliminary root causes
4. Write your report to .beads/agent-summaries/_session-7edaafbb/review-reports/clarity-review-20260220-231026.md
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

**Commit range**: 60bdcb4..HEAD

**Review round**: 1

**Files to review**:
orchestration/RULES.md orchestration/SETUP.md orchestration/reference/dependency-analysis.md orchestration/templates/checkpoints.md orchestration/templates/implementation.md orchestration/templates/reviews.md orchestration/templates/scout.md scripts/compose-review-skeletons.sh scripts/fill-review-slots.sh scripts/install-hooks.sh scripts/parse-progress-log.sh scripts/scrub-pii.sh scripts/sync-to-claude.sh

**Task IDs** (for correctness review — run `bd show <id>` to retrieve acceptance criteria):
ant-farm-39zq ant-farm-i2zd ant-farm-lc97 ant-farm-ti6g ant-farm-9wk8 ant-farm-ns95 ant-farm-9vq ant-farm-50m ant-farm-wtp ant-farm-40z ant-farm-g29r ant-farm-szcy ant-farm-3r9 ant-farm-rja ant-farm-3mg ant-farm-4fx ant-farm-4g7 ant-farm-dv9g ant-farm-o058 ant-farm-yn1r ant-farm-npfx ant-farm-e1u6 ant-farm-qoig ant-farm-a66 ant-farm-kwp ant-farm-lhq ant-farm-352c.1 ant-farm-w2i1 ant-farm-j6jq ant-farm-a1rf

**Report output path**: .beads/agent-summaries/_session-7edaafbb/review-reports/clarity-review-20260220-231026.md

**Timestamp**: 20260220-231026

Do NOT file beads — Big Head handles all bead filing.
