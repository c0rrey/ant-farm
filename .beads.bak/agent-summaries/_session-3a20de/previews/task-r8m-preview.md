Execute bug for ant-farm-r8m.

Step 0: Read your task context from .beads/agent-summaries/_session-3a20de/prompts/task-r8m.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-r8m` + `bd update ant-farm-r8m --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-r8m)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-3a20de/summaries/r8m.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-r8m`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-r8m
**Task**: checkpoints.md {checkpoint} placeholder not defined in term definitions block
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/r8m.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L20 -- {checkpoint} used in filename pattern without definition
  - orchestration/templates/checkpoints.md:L4-7 -- Term definitions block
- **Root cause**: The filename pattern on line 20 of checkpoints.md uses {checkpoint} as a placeholder, but this is not defined in the term definitions block (lines 4-7). While its meaning is inferable from context, it breaks the convention of all placeholders being explicitly defined.
- **Expected behavior**: {checkpoint} is defined in the term definitions block or has an explanatory note.
- **Acceptance criteria**:
  1. {checkpoint} is defined in the term definitions block or has an explanatory note

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md:L1-35 (header, term definitions, and Pest Control Overview including artifact naming)
Do NOT edit: Any checkpoint section below line 42 (Verdict Thresholds Summary, CCO, WWD, DMVDC, CCB)

## Focus
Your task is ONLY to define the {checkpoint} placeholder in the term definitions block.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
