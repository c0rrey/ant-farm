Execute bug for ant-farm-19r3.

Step 0: Read your task context from .beads/agent-summaries/_session-2829f0f5/prompts/task-19r3.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-19r3` + `bd update ant-farm-19r3 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-19r3)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-2829f0f5/summaries/19r3.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-19r3`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-19r3
**Task**: fix: SESSION_PLAN_TEMPLATE.md uses stale Boss-Bot term and Claude Sonnet 4.5 model
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2829f0f5/summaries/19r3.md

## Context
- **Affected files**:
  - orchestration/templates/SESSION_PLAN_TEMPLATE.md:L8 -- "Boss-Bot: Claude Sonnet 4.5"
  - orchestration/templates/SESSION_PLAN_TEMPLATE.md:L340 -- "Implementation files read in boss-bot window"
  - orchestration/templates/SESSION_PLAN_TEMPLATE.md:L342 -- "Boss-bot stayed focused"
- **Root cause**: SESSION_PLAN_TEMPLATE.md uses outdated "Boss-Bot" terminology (should be "Queen") and stale "Claude Sonnet 4.5" model name (Queen runs on opus).
- **Expected behavior**: No "Boss-Bot" or "boss-bot" references in active templates. Model reference updated to current tier.
- **Acceptance criteria**:
  1. No "Boss-Bot" or "boss-bot" references in active templates
  2. Model reference updated to current tier

## Scope Boundaries
Read ONLY: orchestration/templates/SESSION_PLAN_TEMPLATE.md:L1-15, L335-350
Do NOT edit: Any file other than orchestration/templates/SESSION_PLAN_TEMPLATE.md. Do not restructure the template layout.

## Focus
Your task is ONLY to replace Boss-Bot references with Queen and update the model name in SESSION_PLAN_TEMPLATE.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
