Execute task for ant-farm-o0wu.

Step 0: Read your task context from .beads/agent-summaries/_session-20260313-021827/prompts/task-o0wu.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `crumb show ant-farm-o0wu` + `crumb update ant-farm-o0wu --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-o0wu)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-20260313-021827/summaries/o0wu.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `crumb close ant-farm-o0wu`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-o0wu
**Task**: Migrate RULES-review.md (semantic)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/o0wu.md

## Context
- **Affected files**:
  - orchestration/RULES-review.md:L23,L155,L158 (bd command references and .beads/ paths in review workflow rules)
- **Root cause**: RULES-review.md contains review workflow rules referencing bd commands for issue queries and status updates.
- **Expected behavior**: All bd command references replaced with crumb equivalents; review workflow logic preserved.
- **Acceptance criteria**:
  1. All bd command references replaced with crumb equivalents
  2. Review workflow logic preserved -- only command syntax changes
  3. grep -c '\bbd\b' orchestration/RULES-review.md returns 0
  4. Any .beads/ path references updated to .crumbs/ (L23: .beads/issues.jsonl exclusion)

## Scope Boundaries
Read ONLY: orchestration/RULES-review.md (full file, focus on L23, L155, L158)
Do NOT edit: Any file other than orchestration/RULES-review.md. Do not change review step ordering, commit range logic, or file list generation workflow.

## Focus
Your task is ONLY to migrate bd CLI commands and .beads/ paths to crumb/.crumbs/ equivalents in RULES-review.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
