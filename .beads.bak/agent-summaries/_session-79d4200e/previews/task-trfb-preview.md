Execute bug for ant-farm-trfb.

Step 0: Read your task context from .beads/agent-summaries/_session-79d4200e/prompts/task-trfb.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-trfb` + `bd update ant-farm-trfb --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-trfb)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-79d4200e/summaries/trfb.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-trfb`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-trfb
**Task**: fix: one-TeamCreate-per-session constraint undocumented in operator-facing docs
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-79d4200e/summaries/trfb.md

## Context
- **Affected files**:
  - orchestration/RULES.md (Step 3b-iv, near team setup) -- add TeamCreate constraint note
  - CONTRIBUTING.md or orchestration/SETUP.md -- mention constraint for framework extenders
- **Root cause**: One-TeamCreate-per-session constraint was discovered empirically and captured in MEMORY.md but never propagated to RULES.md, CLAUDE.md, or CONTRIBUTING.md.
- **Expected behavior**: RULES.md should document the constraint near the Nitpicker team setup, explaining why PC is a team member.
- **Acceptance criteria**:
  1. RULES.md documents the one-TeamCreate-per-session constraint
  2. Note explains the architectural implication (PC must be team member, not separate spawn)
  3. CONTRIBUTING.md or SETUP.md mentions the constraint for framework extenders

## Scope Boundaries
Read ONLY: orchestration/RULES.md (Step 3b-iv section), CONTRIBUTING.md:L1-248, orchestration/SETUP.md:L1-269
Do NOT edit: CLAUDE.md, any template files, any script files

## Focus
Your task is ONLY to document the one-TeamCreate-per-session constraint in RULES.md and either CONTRIBUTING.md or SETUP.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
