Execute bug for ant-farm-ti6g.

Step 0: Read your task context from .beads/agent-summaries/_session-7edaafbb/prompts/task-ti6g.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-ti6g` + `bd update ant-farm-ti6g --status=in_progress`
2. **Design** (MANDATORY) -- 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) -- Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-ti6g)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) -- Write to .beads/agent-summaries/_session-7edaafbb/summaries/ti6g.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-ti6g`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.
