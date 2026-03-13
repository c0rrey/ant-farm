<!-- Review prompt: drift | Built by build-review-prompts.sh -->


Perform a drift review of the completed work.

**Review round**: 1
**Input guard**: If 1 is blank or non-numeric, halt immediately and return: "NITPICKER ABORTED: REVIEW_ROUND is invalid. Expected a positive integer; got: '1'." Do NOT proceed.
If round 2+: Your scope is limited to fix commits only. You may read full files for context, but your mandate is: did these fixes land correctly and not break anything? Out-of-scope findings are only reportable if they would cause a runtime failure or silently wrong results. Do NOT report naming, style, docs, or improvement opportunities outside fix scope.

Step 0: Read your full review brief from .beads/agent-summaries/_session-20260313-001327/prompts/review-drift.md
(Format: markdown. Sections: Scope, Files, Focus, Detailed Instructions.)

Your workflow:
1. Read ALL files listed in the brief
2. Catalog findings with file:line references and severity (P1/P2/P3)
3. Group findings into preliminary root causes
4. Write your report to .beads/agent-summaries/_session-20260313-001327/review-reports/drift-review-20260313-010342.md
5. Message relevant Nitpickers if you find cross-domain issues

**Cross-review messaging protocol**:
When you find something that clearly belongs to another reviewer's domain, message them:
- To Clarity: "Found misleading comment in file.py:L42 — may want to review."
- To Edge Cases: "Found unvalidated external input at script.sh:L88 — could be boundary issue."
- To Correctness: "Logic at rules.md:L120 may not satisfy acceptance criterion 3 — check bd show <task-id>."
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

Do NOT file beads (`bd create`) — Big Head handles all bead filing.

---
## Review Brief

**Commit range**: 25219ff..HEAD

**Review round**: 1

**Files to review**:
crumb.py

## Focus

**Your focus**: The system agrees with itself after this change. You review for stale assumptions across file boundaries.

Focus areas:
1. **Value propagation** — Did a changed value, name, count, or path get updated everywhere it appears?
2. **Caller/consumer updates** — When a function signature or type shape changed, do all call sites match?
3. **Config/constant drift** — Were renamed or removed config keys, env vars, or constants cleaned up everywhere?
4. **Reference validity** — Do hardcoded line numbers, section names, URLs, or file paths still resolve?
5. **Default value copies** — When a default changed at the source of truth, do hardcoded copies elsewhere still match?
6. **Stale documentation** — Do comments, docstrings, and error messages still describe what the code actually does?

**Severity calibration**:
- P1: Stale assumption causes runtime failure or silently wrong results in a common path
- P2: Stale assumption creates inconsistency a developer will encounter but can work around
- P3: Stale reference that is cosmetic or low-impact (default)

**Not your responsibility** — hand off to the relevant reviewer:
- Clarity: naming quality, comment style, readability (even within a single file)
- Edge Cases: missing validation, error handling, boundary conditions
- Correctness: whether logic is right given current inputs (bugs, not drift)

**Task IDs** (for correctness review — run `bd show <id>` to retrieve acceptance criteria):
ant-farm-mg0r ant-farm-l7pk ant-farm-cmcd ant-farm-h7af ant-farm-jmvi ant-farm-vxpr ant-farm-izng ant-farm-fdz2 ant-farm-dhh8

**Report output path**: .beads/agent-summaries/_session-20260313-001327/review-reports/drift-review-20260313-010342.md

**Timestamp**: 20260313-010342

Do NOT file beads — Big Head handles all bead filing.
