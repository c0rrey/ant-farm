Execute bug for ant-farm-3fm.

Step 0: Read your task context from .beads/agent-summaries/_session-3a20de/prompts/task-3fm.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-3fm` + `bd update ant-farm-3fm --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-3fm)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-3a20de/summaries/3fm.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-3fm`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-3fm
**Task**: checkpoints.md CCB lists report paths twice (duplication risk)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/3fm.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L383-387 -- Individual reports section
  - orchestration/templates/checkpoints.md:L392-396 -- Check 0 section (duplicate listing)
- **Root cause**: The CCB template in checkpoints.md lists the 4 individual report paths in both the 'Individual reports' section (lines 383-387) and the 'Check 0: Report Existence Verification' section (lines 392-396). Path format changes must be updated in two places.
- **Expected behavior**: Report paths appear only once in the CCB template, with Check 0 referencing the earlier listing.
- **Acceptance criteria**:
  1. Report paths appear only once in the CCB template, with Check 0 referencing the earlier listing

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md:L370-500 (CCB section)
Do NOT edit: CCO section (L97-163), WWD section (L235-303), DMVDC section (L306-454), Verdict Thresholds Summary (L44-94)

## Focus
Your task is ONLY to deduplicate the CCB report path listings so paths appear once and Check 0 references the earlier listing.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
