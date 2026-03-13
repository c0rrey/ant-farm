Execute bug for ant-farm-zg7t.

Step 0: Read your task context from .beads/agent-summaries/_session-5da05acb/prompts/task-zg7t.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-zg7t` + `bd update ant-farm-zg7t --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-zg7t)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-5da05acb/summaries/zg7t.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-zg7t`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-zg7t
**Task**: macOS (Darwin) incompatible shell commands in RULES.md
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-5da05acb/summaries/zg7t.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L381 — session ID generation uses date +%s%N which is GNU-only
  - orchestration/RULES.md:L156-176 — TASK_IDS validation uses tr | sed pipeline instead of bash parameter expansion
  - orchestration/RULES.md:L157-159 — REVIEW_ROUND validation uses echo | grep instead of bash-native [[ =~ ]]
- **Root cause**: Shell commands in RULES.md assume GNU tooling behavior, but the documented platform (Darwin/macOS) uses BSD tooling. date +%s%N silently produces literal %N on macOS instead of nanoseconds.
- **Expected behavior**: All shell commands should use portable macOS-compatible alternatives (uuidgen for session IDs, bash parameter expansion for validation, bash-native regex matching).
- **Acceptance criteria**:
  1. Session ID generation does not use date +%s%N or any GNU-only date format
  2. TASK_IDS validation uses bash parameter expansion (matching CHANGED_FILES pattern)
  3. REVIEW_ROUND validation uses bash-native regex matching
  4. All three changes verified to work on macOS (Darwin)

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L150-180 and L375-390
Do NOT edit: scripts/sync-to-claude.sh, scripts/build-review-prompts.sh, any file outside orchestration/RULES.md

## Focus
Your task is ONLY to replace GNU-only shell commands in RULES.md with macOS-compatible alternatives.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
