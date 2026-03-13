Execute task for ant-farm-cn0.

Step 0: Read your task context from .beads/agent-summaries/_session-8b93f5/prompts/task-cn0.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-cn0` + `bd update ant-farm-cn0 --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-cn0)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-8b93f5/summaries/cn0.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-cn0`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-cn0
**Task**: Timestamp format YYYYMMDD-HHMMSS repeated 5+ times across files
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8b93f5/summaries/cn0.md

## Context
- **Affected files**:
  - `orchestration/templates/checkpoints.md:L34` -- canonical timestamp format definition
  - `orchestration/templates/checkpoints.md:L40` -- review timestamp convention
  - `orchestration/templates/checkpoints.md:L162` -- timestamp field in checkpoint artifact
  - `orchestration/templates/checkpoints.md:L224` -- timestamp field in checkpoint artifact
  - `orchestration/templates/checkpoints.md:L379` -- timestamp field in checkpoint artifact
  - `orchestration/templates/checkpoints.md:L437` -- timestamp field in checkpoint artifact
  - `orchestration/templates/checkpoints.md:L559` -- timestamp field in checkpoint artifact
  - `orchestration/templates/pantry.md:L201` -- review timestamp format in Section 2 input description
- **Root cause**: The timestamp format string `YYYYMMDD-HHmmss` is redefined at 7 locations in checkpoints.md and 1 location in pantry.md. If the format ever changes, all 8 locations must be updated manually. This is a DRY (Don't Repeat Yourself) violation.
- **Expected behavior**: The timestamp format should be defined exactly once in a canonical location (at the top of checkpoints.md, which is the authoritative source). All other occurrences should reference that canonical definition rather than repeating the literal format string.
- **Acceptance criteria**:
  1. Timestamp format string defined exactly once in a canonical location
  2. All other occurrences in checkpoints.md and pantry.md replaced with references to the canonical definition
  3. grep for the literal format string across orchestration/ returns only the single canonical definition

## Scope Boundaries
Read ONLY:
- `orchestration/templates/checkpoints.md` (full file -- lines 1-600+)
- `orchestration/templates/pantry.md` (full file -- lines 1-201+)

Do NOT edit:
- `orchestration/RULES.md`
- `orchestration/templates/implementation.md`
- `orchestration/templates/dirt-pusher-skeleton.md`
- `orchestration/templates/nitpicker-skeleton.md`
- `orchestration/templates/scout.md`
- `orchestration/templates/reviews.md`
- `CLAUDE.md`
- `CHANGELOG.md`
- Any files outside `orchestration/templates/checkpoints.md` and `orchestration/templates/pantry.md`

## Focus
Your task is ONLY to deduplicate the timestamp format string so it is defined once and referenced everywhere else.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
