Execute bug for ant-farm-sd12.

Step 0: Read your task context from .beads/agent-summaries/_session-2829f0f5/prompts/task-sd12.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-sd12` + `bd update ant-farm-sd12 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-sd12)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-2829f0f5/summaries/sd12.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-sd12`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-sd12
**Task**: fix: remove archived pantry-review from scout.md exclusion list
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2829f0f5/summaries/sd12.md

## Context
- **Affected files**:
  - orchestration/templates/scout.md:L63 -- agent exclusion list
- **Root cause**: scout.md:L63 lists `pantry-review` in the agent exclusion list but the pantry-review agent is archived and has no file in agents/. The reference is harmless (it would not appear in the Scout's catalog anyway) but signals the list was not updated on deprecation.
- **Expected behavior**: scout.md exclusion list no longer references pantry-review.
- **Acceptance criteria**:
  1. scout.md exclusion list no longer references pantry-review

## Scope Boundaries
Read ONLY: orchestration/templates/scout.md:L55-70
Do NOT edit: Any file other than orchestration/templates/scout.md. Do not change any other entries in the exclusion list.

## Focus
Your task is ONLY to remove the pantry-review entry from the scout.md exclusion list.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
