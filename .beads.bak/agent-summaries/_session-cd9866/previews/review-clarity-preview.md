<!-- Review skeleton: clarity | Assembled by compose-review-skeletons.sh -->
<!-- Slot markers: .beads/agent-summaries/_session-cd9866/prompts/review-clarity.md .beads/agent-summaries/_session-cd9866/review-reports/clarity-review-20260220-190615.md 1 f9ad7d9..HEAD agents/big-head.md,docs/installation-guide.md,orchestration/_archive/pantry-review.md,orchestration/PLACEHOLDER_CONVENTIONS.md,orchestration/RULES.md,orchestration/templates/big-head-skeleton.md,orchestration/templates/checkpoints.md,orchestration/templates/dirt-pusher-skeleton.md,orchestration/templates/nitpicker-skeleton.md,orchestration/templates/pantry.md,orchestration/templates/reviews.md,README.md,scripts/install-hooks.sh,scripts/scrub-pii.sh 20260220-190615 -->
<!-- Fill with: scripts/fill-review-slots.sh -->


Perform a clarity review of the completed work.

**Review round**: 1
If round 2+: Your scope is limited to fix commits only. You may read full files for context, but your mandate is: did these fixes land correctly and not break anything? Out-of-scope findings are only reportable if they would cause a runtime failure or silently wrong results. Do NOT report naming, style, docs, or improvement opportunities outside fix scope.

Step 0: Read your full review brief from .beads/agent-summaries/_session-cd9866/prompts/review-clarity.md
(Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions.)

Your workflow:
1. Read ALL files listed in the brief
2. Catalog findings with file:line references and severity (P1/P2/P3)
3. Group findings into preliminary root causes
4. Write your report to .beads/agent-summaries/_session-cd9866/review-reports/clarity-review-20260220-190615.md
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

**Commit range**: f9ad7d9..HEAD

**Review round**: 1

**Files to review**:
agents/big-head.md,docs/installation-guide.md,orchestration/_archive/pantry-review.md,orchestration/PLACEHOLDER_CONVENTIONS.md,orchestration/RULES.md,orchestration/templates/big-head-skeleton.md,orchestration/templates/checkpoints.md,orchestration/templates/dirt-pusher-skeleton.md,orchestration/templates/nitpicker-skeleton.md,orchestration/templates/pantry.md,orchestration/templates/reviews.md,README.md,scripts/install-hooks.sh,scripts/scrub-pii.sh

**Task IDs** (for correctness review — run `bd show <id>` to retrieve acceptance criteria):
ant-farm-bi3,ant-farm-yfnj,ant-farm-yb95,ant-farm-txw,ant-farm-auas,ant-farm-0gs,ant-farm-32gz,ant-farm-033,ant-farm-1b8,ant-farm-7yv,ant-farm-z69,ant-farm-cl8,ant-farm-1e1,ant-farm-1y4,ant-farm-27x,ant-farm-9j6z,ant-farm-z3j

**Report output path**: .beads/agent-summaries/_session-cd9866/review-reports/clarity-review-20260220-190615.md

**Timestamp**: 20260220-190615

Do NOT file beads — Big Head handles all bead filing.
