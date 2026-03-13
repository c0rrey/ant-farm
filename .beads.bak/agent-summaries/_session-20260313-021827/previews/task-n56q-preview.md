Execute task for ant-farm-n56q.

Step 0: Read your task context from .beads/agent-summaries/_session-20260313-021827/prompts/task-n56q.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `crumb show ant-farm-n56q` + `crumb update ant-farm-n56q --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-n56q)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-20260313-021827/summaries/n56q.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `crumb close ant-farm-n56q`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-n56q
**Task**: Migrate reviews.md (semantic)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/n56q.md

## Context
- **Affected files**: orchestration/templates/reviews.md:L67,L309,L316,L731-738,L744,L749,L807,L867,L893-894,L905,L907,L923-924,L1046,L1052,L1145-1146,L1151 (30+ bd references across 8 distinct command patterns)
- **Root cause**: Reviews template is the most complex migration file with 30+ bd references across 8 distinct command patterns requiring semantic understanding of each command's context.
- **Expected behavior**: All 30+ bd references migrated with correct crumb CLI syntax; review logic (Nitpicker workflow, Big Head dedup) preserved.
- **Acceptance criteria**:
  1. All 30+ bd references migrated with correct crumb CLI syntax
  2. bd create --type=bug patterns converted to crumb create --from-json with proper JSON structure
  3. bd label add references removed -- review type uses review_source field in --from-json
  4. bd dep add --type parent-child patterns converted to crumb link --parent
  5. bd epic create patterns converted to crumb trail create
  6. grep -c '\bbd\b' orchestration/templates/reviews.md returns 0
  7. Surrounding review logic (Nitpicker workflow, Big Head dedup) remains functionally correct

## Scope Boundaries
Read ONLY: orchestration/templates/reviews.md (full file)
Do NOT edit: Any file other than orchestration/templates/reviews.md. Do not change Nitpicker report format, review type definitions, or Big Head consolidation logic beyond the command syntax changes.

## Focus
Your task is ONLY to migrate bd CLI commands to crumb CLI equivalents in reviews.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
