Execute task for ant-farm-68di.5.

Step 0: Read your task context from .beads/agent-summaries/_session-d81536bb/prompts/task-68di5.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-68di.5` + `bd update ant-farm-68di.5 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-68di.5)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-d81536bb/summaries/68di5.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-68di.5`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-68di.5
**Task**: Update cross-references to Step 4 CHANGELOG in secondary docs
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-d81536bb/summaries/68di5.md

## Context
- **Affected files**:
  - orchestration/templates/reviews.md:L193-194 (termination rule referencing Step 4), L933 (proceed to Step 4 Documentation), L943 (defer proceed to Step 4), L1014 (Handle P3 Issues heading referencing Step 4), L1031 (proceed to Step 4 after P3 handling)
  - orchestration/templates/SESSION_PLAN_TEMPLATE.md:L219 (proceed to Step 4 documentation), L237 (CHANGELOG checklist item), L282 (CHANGELOG updated checklist)
  - README.md:L233-237 (Step 4-5 document and verify section)
  - orchestration/GLOSSARY.md:L1-87 (entire file -- needs new Scribe, ESV, exec summary definitions added)
  - orchestration/templates/queen-state.md:L1-70 (entire file -- needs Scribe/ESV tracking fields added)
- **Root cause**: N/A (docs/refactor task -- cross-reference consistency). Multiple documentation files still reference the old workflow where CHANGELOG authoring happens at Step 4. The new workflow has the Scribe handle CHANGELOG at Step 5b, followed by ESV at Step 5c. These cross-references are now stale.
- **Expected behavior**: All secondary documentation files that reference Step 4 CHANGELOG authoring are updated to reflect the new workflow where the Scribe handles CHANGELOG at Step 5b. GLOSSARY.md contains new definitions for Scribe, ESV, and exec summary. queen-state.md includes new Scribe/ESV tracking fields.
- **Acceptance criteria**:
  1. grep -n 'Step 4.*CHANGELOG' across all files in orchestration/templates/ returns zero matches (excluding _archive/)
  2. reviews.md lines 933, 943, 1031 reference Step 5b/Scribe for CHANGELOG instead of Step 4
  3. SESSION_PLAN_TEMPLATE.md CHANGELOG checklist items note Scribe authorship
  4. README.md workflow description reflects the new Step 4 (no CHANGELOG) -> Step 5b (Scribe) -> Step 5c (ESV) -> Step 6 (push) sequence
  5. GLOSSARY.md contains definitions for Scribe, ESV, and exec summary
  6. queen-state.md includes Scribe/ESV tracking fields

## Scope Boundaries
Read ONLY:
- orchestration/templates/reviews.md:L188-198, L925-935, L938-945, L1008-1032
- orchestration/templates/SESSION_PLAN_TEMPLATE.md:L210-290
- README.md:L225-244
- orchestration/GLOSSARY.md:L1-87
- orchestration/templates/queen-state.md:L1-70

Do NOT edit:
- Any file in orchestration/_archive/
- CLAUDE.md, CHANGELOG.md
- orchestration/RULES.md
- orchestration/templates/implementation.md
- orchestration/templates/checkpoints.md
- orchestration/templates/pantry.md
- orchestration/templates/dirt-pusher-skeleton.md
- Any scripts/ files
- Any agents/ files

## Focus
Your task is ONLY to update cross-references from Step 4 CHANGELOG to Step 5b/Scribe in secondary docs, add glossary definitions, and add queen-state tracking fields.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
