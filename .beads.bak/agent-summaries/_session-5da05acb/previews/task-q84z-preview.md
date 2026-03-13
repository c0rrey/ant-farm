Execute bug for ant-farm-q84z.

Step 0: Read your task context from .beads/agent-summaries/_session-5da05acb/prompts/task-q84z.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-q84z` + `bd update ant-farm-q84z --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-q84z)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-5da05acb/summaries/q84z.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-q84z`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-q84z
**Task**: Dual TIMESTAMP/REVIEW_TIMESTAMP naming convention creates cognitive burden
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-5da05acb/summaries/q84z.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L148-149 — dual naming: shell ${TIMESTAMP} vs placeholder {REVIEW_TIMESTAMP}
- **Root cause**: RULES.md introduces two different identifiers for the same concept: ${TIMESTAMP} as a shell variable and {REVIEW_TIMESTAMP} as a placeholder. No other placeholder uses this dual-name convention, creating cognitive burden.
- **Expected behavior**: Only one name should be used for the review timestamp concept in both shell and prose contexts.
- **Acceptance criteria**:
  1. Only one name is used for the review timestamp concept (shell and prose use the same identifier)
  2. No inline mapping explanation is needed between two different names
  3. All bash snippets and template references use the unified name

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L140-165 (timestamp naming section)
Do NOT edit: orchestration/templates/pantry.md, orchestration/templates/reviews.md, scripts/build-review-prompts.sh

## Focus
Your task is ONLY to unify the dual TIMESTAMP/REVIEW_TIMESTAMP naming convention in RULES.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
