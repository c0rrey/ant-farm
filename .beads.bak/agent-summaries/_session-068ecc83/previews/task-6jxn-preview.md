Execute bug for ant-farm-6jxn.

Step 0: Read your task context from .beads/agent-summaries/_session-068ecc83/prompts/task-6jxn.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-6jxn` + `bd update ant-farm-6jxn --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-6jxn)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-068ecc83/summaries/6jxn.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-6jxn`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-6jxn
**Task**: Stale documentation from pantry-review deprecation (5 surfaces)
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-068ecc83/summaries/6jxn.md

## Context
- **Affected files**:
  - orchestration/templates/reviews.md:L1 -- reader comment referencing pantry-review as active
  - README.md:L171-197 -- architecture diagram listing pantry-review as active component
  - orchestration/templates/pantry.md:L271-277 -- deprecation notice and heading for pantry-review
  - orchestration/_archive/pantry-review.md:L1-7 -- active YAML frontmatter (should be marked deprecated/archived)
- **Root cause**: When Pantry review-mode was deprecated and replaced by fill-review-slots.sh, consumer-facing annotations and architecture diagrams were not updated. 5 surfaces still reference pantry-review as if it were active. Consolidated from: Clarity F2, F7, F8, Excellence F6, F8, F9.
- **Expected behavior**: All 5 surfaces should reflect current architecture (fill-review-slots.sh replaced pantry-review). No references to pantry-review as a live/active agent.
- **Acceptance criteria**:
  1. reviews.md:L1 reader comment updated to reflect current review architecture
  2. README.md:L171-197 architecture diagram updated to show fill-review-slots.sh instead of pantry-review
  3. pantry.md:L271-277 deprecation notice and heading updated
  4. _archive/pantry-review.md:L1-7 YAML frontmatter marked as archived/deprecated
  5. No surface references pantry-review as active

## Scope Boundaries
Read ONLY:
- orchestration/templates/reviews.md:L1-5
- README.md:L165-205
- orchestration/templates/pantry.md:L249-285
- orchestration/_archive/pantry-review.md:L1-10

Do NOT edit:
- Any file outside the 4 listed above
- orchestration/RULES.md (has its own deprecation references managed by ant-farm-oc9v)
- orchestration/GLOSSARY.md (managed by ant-farm-oc9v)
- orchestration/templates/scout.md (managed by ant-farm-oc9v)
- scripts/ directory (managed by ant-farm-n0or)

## Focus
Your task is ONLY to update 4 files that still reference pantry-review as active/live, bringing them in line with the fill-review-slots.sh replacement architecture.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
