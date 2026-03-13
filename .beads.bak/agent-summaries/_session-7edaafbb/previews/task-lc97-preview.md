Execute bug for ant-farm-lc97.

Step 0: Read your task context from .beads/agent-summaries/_session-7edaafbb/prompts/task-lc97.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-lc97` + `bd update ant-farm-lc97 --status=in_progress`
2. **Design** (MANDATORY) -- 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) -- Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-lc97)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) -- Write to .beads/agent-summaries/_session-7edaafbb/summaries/lc97.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-lc97`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.
