Execute bug for ant-farm-geou.

Step 0: Read your task context from .beads/agent-summaries/_session-79d4200e/prompts/task-geou.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-geou` + `bd update ant-farm-geou --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-geou)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-79d4200e/summaries/geou.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-geou`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-geou
**Task**: fix: document artifact naming convention transition point for historical sessions
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-79d4200e/summaries/geou.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md (near naming convention section, around L26-34) -- add historical variation note
- **Root cause**: checkpoints.md documents the current naming standard but does not acknowledge that historical sessions used different formats (wave-based naming, mixed naming).
- **Expected behavior**: checkpoints.md should acknowledge historical naming variation and document the transition point.
- **Acceptance criteria**:
  1. checkpoints.md acknowledges historical naming variation
  2. Transition point (_session-068ecc83 as first fully-compliant session) is documented
  3. Note clarifies that historical artifacts are expected to diverge from current convention

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md:L20-40 (artifact naming conventions section)
Do NOT edit: Any other section of checkpoints.md, any other file

## Focus
Your task is ONLY to add a historical naming variation note near the naming conventions section in checkpoints.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
