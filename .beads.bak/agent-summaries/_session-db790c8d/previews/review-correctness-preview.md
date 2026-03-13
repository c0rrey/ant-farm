<!-- Review skeleton: correctness | Assembled by compose-review-skeletons.sh -->
<!-- Slot markers: .beads/agent-summaries/_session-db790c8d/prompts/review-correctness.md .beads/agent-summaries/_session-db790c8d/review-reports/correctness-review-20260222-103344.md 2 3f52803^..3f52803 scripts/parse-progress-log.sh 20260222-103344 -->
<!-- Fill with: scripts/fill-review-slots.sh -->

**Your focus**: The code does what it claims. You review for logical soundness and acceptance criteria compliance.

Focus areas:
1. **Acceptance criteria** — Run `bd show <task-id>` for each task. Did each fix solve what was requested?
2. **Logic correctness** — Inverted conditions? Off-by-one? Wrong operator precedence? Always-true/false?
3. **Data integrity** — Are all data transformations correct? No data loss between source and destination?
4. **Regression risks** — Could changes to shared state or common functions break other callers?
5. **Cross-file consistency** — If file A exports a contract file B depends on, do they still agree?
6. **Algorithm correctness** — Sorting, filtering, aggregation, calculations — are they right?

**Severity calibration**:
- P1: Wrong output for common production inputs, OR an acceptance criterion is explicitly unmet
- P2: Wrong output for occasional inputs, OR high-confidence regression in a shared function
- P3: Theoretical logic error needing unusual conditions, or cosmetic cross-file inconsistency (default)

**Not your responsibility** — hand off to the relevant reviewer:
- Clarity: naming, comments, style (even if logic is correct but hard to read)
- Edge Cases: what happens with invalid inputs (your scope is valid-input behavior)
- Excellence: performance, security hardening, architectural elegance


Perform a correctness review of the completed work.

**Review round**: 2
**Input guard**: If 2 is blank or non-numeric, halt immediately and return: "NITPICKER ABORTED: REVIEW_ROUND is invalid. Expected a positive integer; got: '2'." Do NOT proceed.
If round 2+: Your scope is limited to fix commits only. You may read full files for context, but your mandate is: did these fixes land correctly and not break anything? Out-of-scope findings are only reportable if they would cause a runtime failure or silently wrong results. Do NOT report naming, style, docs, or improvement opportunities outside fix scope.

Step 0: Read your full review brief from .beads/agent-summaries/_session-db790c8d/prompts/review-correctness.md
(Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions.)

Your workflow:
1. Read ALL files listed in the brief
2. Catalog findings with file:line references and severity (P1/P2/P3)
3. Group findings into preliminary root causes
4. Write your report to .beads/agent-summaries/_session-db790c8d/review-reports/correctness-review-20260222-103344.md
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

**Commit range**: 3f52803^..3f52803

**Review round**: 2

**Files to review**:
scripts/parse-progress-log.sh

**Task IDs** (for correctness review — run `bd show <id>` to retrieve acceptance criteria):
ant-farm-951b

**Report output path**: .beads/agent-summaries/_session-db790c8d/review-reports/correctness-review-20260222-103344.md

**Timestamp**: 20260222-103344

Do NOT file beads — Big Head handles all bead filing.
