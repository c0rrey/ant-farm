Execute bug for ant-farm-9dp7.

Step 0: Read your task context from .beads/agent-summaries/_session-2829f0f5/prompts/task-9dp7.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-9dp7` + `bd update ant-farm-9dp7 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-9dp7)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-2829f0f5/summaries/9dp7.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-9dp7`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README.
Note: CLAUDE.md IS an affected file for this task -- editing it is permitted per the task brief scope.

---

# Task Brief: ant-farm-9dp7
**Task**: fix: minor bd prohibition wording drift between CLAUDE.md and RULES.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2829f0f5/summaries/9dp7.md

## Context
- **Affected files**:
  - CLAUDE.md:L38 -- bd prohibition text (plain "NEVER")
  - orchestration/RULES.md:L16 -- bd prohibition text (bold "**NEVER**")
- **Root cause**: CLAUDE.md and RULES.md both prohibit the same bd commands but with slightly different formatting: plain "NEVER" vs bold "**NEVER**", "The Scout subagent does this." vs "the Scout does this". Functionally identical, cosmetically drifted.
- **Expected behavior**: bd prohibition text identical between CLAUDE.md and RULES.md.
- **Acceptance criteria**:
  1. bd prohibition text identical between CLAUDE.md and RULES.md

## Scope Boundaries
Read ONLY: CLAUDE.md:L30-50, orchestration/RULES.md:L1-30
Do NOT edit: Any file other than CLAUDE.md and orchestration/RULES.md. Do not change the semantic meaning of the prohibition, only harmonize formatting and wording.

## Focus
Your task is ONLY to harmonize the bd prohibition wording between CLAUDE.md and RULES.md so they are identical.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
