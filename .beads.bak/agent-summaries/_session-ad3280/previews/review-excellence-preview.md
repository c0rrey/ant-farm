<!-- Review skeleton: excellence | Assembled by compose-review-skeletons.sh -->
<!-- Slot markers: .beads/agent-summaries/_session-ad3280/prompts/review-excellence.md .beads/agent-summaries/_session-ad3280/review-reports/excellence-review-20260220-113708.md 1 201ee96~1..HEAD agents/big-head.md agents/nitpicker.md orchestration/RULES.md orchestration/templates/pantry.md orchestration/templates/scout.md scripts/compose-review-skeletons.sh scripts/fill-review-slots.sh scripts/sync-to-claude.sh 20260220-113708 -->
<!-- Fill with: scripts/fill-review-slots.sh -->


Perform a excellence review of the completed work.

Step 0: Read your full review brief from .beads/agent-summaries/_session-ad3280/prompts/review-excellence.md
(Contains: commit range, files to review, focus areas, detailed instructions.)

Your workflow:
1. Read ALL files listed in the brief
2. Catalog findings with file:line references and severity (P1/P2/P3)
3. Group findings into preliminary root causes
4. Write your report to .beads/agent-summaries/_session-ad3280/review-reports/excellence-review-20260220-113708.md
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

**Commit range**: 201ee96~1..HEAD

**Review round**: 1

**Files to review**:
agents/big-head.md agents/nitpicker.md orchestration/RULES.md orchestration/templates/pantry.md orchestration/templates/scout.md scripts/compose-review-skeletons.sh scripts/fill-review-slots.sh scripts/sync-to-claude.sh

**Task IDs** (for correctness review — run `bd show <id>` to retrieve acceptance criteria):
ant-farm-0cf ant-farm-cifp ant-farm-7k1 ant-farm-w7p

**Report output path**: .beads/agent-summaries/_session-ad3280/review-reports/excellence-review-20260220-113708.md

**Timestamp**: 20260220-113708

Do NOT file beads — Big Head handles all bead filing.
