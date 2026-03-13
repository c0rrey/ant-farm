Execute bug for ant-farm-m4si.

Step 0: Read your task context from .beads/agent-summaries/_session-86c76859/prompts/task-m4si.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-m4si` + `bd update ant-farm-m4si --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-m4si)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-86c76859/summaries/m4si.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-m4si`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-m4si
**Task**: Progress log key tasks_approved misleading after auto-approve change
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-86c76859/summaries/m4si.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L116 -- progress log key `tasks_approved=<N>` that implies human approval
  - scripts/parse-progress-log.sh -- listed as potentially referencing `tasks_approved` but grep confirms no direct match in the parse script (it parses step keys like SCOUT_COMPLETE, not payload fields)
- **Root cause**: The progress log line at orchestration/RULES.md:L116 was not fully updated when the user-approval gate was removed in ant-farm-fomy. The key name `tasks_approved=<N>` implies a human approved the task list, which is no longer accurate -- approval is now automatic after SSV PASS. The derivation of `<N>` is also unspecified.
- **Expected behavior**: Key should be renamed from `tasks_approved` to `tasks_accepted` or `tasks_scheduled` to reflect automatic acceptance. The derivation of `<N>` (count of tasks in briefing task list after SSV PASS) should be documented inline.
- **Acceptance criteria**:
  1. Progress log key at RULES.md:L116 no longer uses the word "approved"
  2. The derivation of `<N>` (task count from briefing) is documented inline or in an adjacent comment
  3. `parse-progress-log.sh` (if it parses `tasks_approved`) is updated to match the new key name

## Scope Boundaries
Read ONLY:
- orchestration/RULES.md:L110-125 (the progress log line and surrounding context for Step 1b)
- scripts/parse-progress-log.sh (full file -- to confirm no references to `tasks_approved` payload field)

Do NOT edit:
- orchestration/RULES.md outside L116 area (other workflow steps are not relevant)
- orchestration/templates/ (template files are not affected)
- scripts/parse-progress-log.sh (grep confirms it does not reference `tasks_approved`; only edit if a reference is discovered at implementation time)

## Focus
Your task is ONLY to rename the `tasks_approved` key in the progress log line at RULES.md:L116 and document the derivation of `<N>`.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
