Execute task for ant-farm-wiq.

Step 0: Read your task context from .beads/agent-summaries/_session-3a20de/prompts/task-wiq.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-wiq` + `bd update ant-farm-wiq --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-wiq)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-3a20de/summaries/wiq.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-wiq`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-wiq
**Task**: Checkpoints CCO FAIL verdict format has no example
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/wiq.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L107-118 -- CCO Verdict Thresholds section (PASS/WARN/FAIL definitions)
  - orchestration/templates/checkpoints.md:L151-154 -- CCO verdict section inside the template block
  - NOTE: Scout metadata had bare filename (no line numbers). Lines identified by Pantry via grep.
- **Root cause**: checkpoints.md shows PASS verdict format but no example of a FAIL verdict with specific check failures listed. A fresh Pest Control agent might format FAIL output incorrectly.
- **Expected behavior**: FAIL example showing check number, name, and evidence added to CCO section.
- **Acceptance criteria**:
  1. CCO section includes a FAIL verdict example with check number, name, and evidence

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md:L97-163 (CCO Dirt Pushers section, including verdict thresholds and template block)
Do NOT edit: CCO Nitpickers section (L165-225), WWD section (L235-303), DMVDC section (L306-454), CCB section (L457-572), Verdict Thresholds Summary (L44-94)

## Focus
Your task is ONLY to add a FAIL verdict example to the CCO section showing check number, name, and evidence.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
