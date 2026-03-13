Execute bug for ant-farm-x8iw.

Step 0: Read your task context from .beads/agent-summaries/_session-db790c8d/prompts/task-x8iw.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-x8iw` + `bd update ant-farm-x8iw --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-x8iw)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-db790c8d/summaries/x8iw.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-x8iw`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-x8iw
**Task**: fix: Scout agent frontmatter declares model: sonnet, contradicting RULES.md model: opus
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-db790c8d/summaries/x8iw.md

## Context
- **Affected files**:
  - agents/scout-organizer.md:L5 -- frontmatter model field says "sonnet", should say "opus"
  - orchestration/GLOSSARY.md:L80 -- Scout row model says "sonnet", should say "opus"
  - orchestration/GLOSSARY.md:L81 -- Pantry row model says "sonnet", should say "opus"
  - README.md:L75 -- says "a sonnet subagent", should say "an opus subagent"
- **Root cause**: When the Scout was promoted from sonnet to opus (for orchestration complexity), the RULES.md Model Assignments table was updated but the agent frontmatter was not. The same stale model value propagated to GLOSSARY.md and README.md.
- **Expected behavior**: All references to Scout and Pantry model tier should say "opus", matching RULES.md Model Assignments table.
- **Acceptance criteria**:
  1. agents/scout-organizer.md frontmatter says model: opus
  2. orchestration/GLOSSARY.md Scout row says opus
  3. orchestration/GLOSSARY.md Pantry row says opus
  4. README.md Scout description says "opus" not "sonnet"
  5. No other files reference Scout or Pantry as sonnet-tier agents (grep verification)

## Scope Boundaries
Read ONLY:
- agents/scout-organizer.md:L1-10 (frontmatter block)
- orchestration/GLOSSARY.md:L75-86 (Ant Metaphor Roles table)
- README.md:L70-80 (Step 1 Recon description)
- orchestration/RULES.md (reference only -- Model Assignments table, do NOT edit)

Do NOT edit:
- orchestration/RULES.md (already correct; source of truth)
- agents/pest-control.md, agents/pantry-impl.md, or any other agent files not listed above
- Any implementation template files in orchestration/templates/

## Focus
Your task is ONLY to update stale "sonnet" model references to "opus" for Scout and Pantry in the four affected files.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
