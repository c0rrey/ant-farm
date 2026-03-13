<!-- Review skeleton: edge-cases | Assembled by compose-review-skeletons.sh -->
<!-- Slot markers: .beads/agent-summaries/_session-7edaafbb/prompts/review-edge-cases.md .beads/agent-summaries/_session-7edaafbb/review-reports/edge-cases-review-20260220-233433.md 2 e584ba5..HEAD orchestration/SETUP.md orchestration/templates/big-head-skeleton.md orchestration/templates/reviews.md scripts/compose-review-skeletons.sh scripts/install-hooks.sh scripts/scrub-pii.sh scripts/sync-to-claude.sh 20260220-233433 -->
<!-- Fill with: scripts/fill-review-slots.sh -->


Perform a edge-cases review of the completed work.

**Review round**: 2
If round 2+: Your scope is limited to fix commits only. You may read full files for context, but your mandate is: did these fixes land correctly and not break anything? Out-of-scope findings are only reportable if they would cause a runtime failure or silently wrong results. Do NOT report naming, style, docs, or improvement opportunities outside fix scope.

Step 0: Read your full review brief from .beads/agent-summaries/_session-7edaafbb/prompts/review-edge-cases.md
(Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions.)

Your workflow:
1. Read ALL files listed in the brief
2. Catalog findings with file:line references and severity (P1/P2/P3)
3. Group findings into preliminary root causes
4. Write your report to .beads/agent-summaries/_session-7edaafbb/review-reports/edge-cases-review-20260220-233433.md
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

**Commit range**: e584ba5..HEAD

**Review round**: 2

**Files to review**:
orchestration/SETUP.md orchestration/templates/big-head-skeleton.md orchestration/templates/reviews.md scripts/compose-review-skeletons.sh scripts/install-hooks.sh scripts/scrub-pii.sh scripts/sync-to-claude.sh

**Task IDs** (for correctness review — run `bd show <id>` to retrieve acceptance criteria):
ant-farm-ul02 ant-farm-viyd ant-farm-ub8a ant-farm-shkt ant-farm-sjyg ant-farm-2qmt ant-farm-bhgt

**Report output path**: .beads/agent-summaries/_session-7edaafbb/review-reports/edge-cases-review-20260220-233433.md

**Timestamp**: 20260220-233433

Do NOT file beads — Big Head handles all bead filing.
