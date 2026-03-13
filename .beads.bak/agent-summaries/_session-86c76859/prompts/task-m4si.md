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
