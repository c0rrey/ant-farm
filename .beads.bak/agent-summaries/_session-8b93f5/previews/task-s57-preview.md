Execute task for ant-farm-s57.

Step 0: Read your task context from .beads/agent-summaries/_session-8b93f5/prompts/task-s57.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-s57` + `bd update ant-farm-s57 --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-s57)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-8b93f5/summaries/s57.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-s57`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-s57
**Task**: AGG-028: Standardize timestamp format string across templates
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8b93f5/summaries/s57.md

## Context
- **Affected files**:
  - `orchestration/templates/checkpoints.md:L34` — defines format as `YYYYMMDD-HHMMSS` (all uppercase)
  - `orchestration/templates/checkpoints.md:L40` — repeats `YYYYMMDD-HHMMSS` in review timestamp convention
  - `orchestration/templates/checkpoints.md:L162` — uses `YYYYMMDD-HHMMSS` in CCO artifact naming
  - `orchestration/templates/checkpoints.md:L224` — uses `YYYYMMDD-HHMMSS` in WWD artifact naming
  - `orchestration/templates/checkpoints.md:L379` — uses `YYYYMMDD-HHMMSS` in DMVDC artifact naming
  - `orchestration/templates/checkpoints.md:L437` — uses `YYYYMMDD-HHMMSS` in CCB artifact naming
  - `orchestration/templates/checkpoints.md:L559` — uses `YYYYMMDD-HHMMSS` in DMVDC-review artifact naming
  - `orchestration/templates/big-head-skeleton.md:L11` — defines format as `YYYYMMDD-HHmmss` (lowercase mm for minutes) with UTC qualifier
  - `orchestration/templates/pantry.md:L201` — uses `YYYYMMDD-HHMMSS` format in input specification
- **Root cause**: checkpoints.md specifies `YYYYMMDD-HHMMSS` (uppercase) but big-head-skeleton.md defines `YYYYMMDD-HHmmss` (lowercase minutes). These inconsistencies could cause mismatched paths or naming errors when agents generate filenames using different format strings.
- **Expected behavior**: One canonical location defines the timestamp format string (with UTC qualifier if applicable). All templates reference the canonical format and all examples use the standardized string.
- **Acceptance criteria**:
  1. One canonical location defines the timestamp format string with UTC qualifier
  2. grep for timestamp format definitions across orchestration/ shows all match the canonical format
  3. All examples in templates use the standardized format string

## Scope Boundaries
Read ONLY:
- `orchestration/templates/checkpoints.md:L30-45` (timestamp format definition section)
- `orchestration/templates/checkpoints.md:L155-170, L220-230, L375-385, L433-445, L555-565` (all timestamp format usages)
- `orchestration/templates/big-head-skeleton.md:L8-14` (term definitions with timestamp format)
- `orchestration/templates/pantry.md:L195-210` (timestamp format in review mode input)

Do NOT edit:
- `orchestration/RULES.md` (does not define timestamp formats)
- `orchestration/templates/implementation.md` (no timestamp format definitions)
- `orchestration/templates/reviews.md` (uses `<timestamp>` placeholder, not format definition)
- `CLAUDE.md`, `README.md` (off-limits per process rules)

## Focus
Your task is ONLY to standardize the timestamp format string across all template files so that one canonical definition exists and all references match.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
