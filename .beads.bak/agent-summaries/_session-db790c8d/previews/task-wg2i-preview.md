Execute bug for ant-farm-wg2i.

Step 0: Read your task context from .beads/agent-summaries/_session-db790c8d/prompts/task-wg2i.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-wg2i` + `bd update ant-farm-wg2i --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-wg2i)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-db790c8d/summaries/wg2i.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-wg2i`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-wg2i
**Task**: fix: installed pre-push hook is fatal on sync failure, contradicting install-hooks.sh non-fatal design
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-db790c8d/summaries/wg2i.md

## Context
- **Affected files**:
  - .git/hooks/pre-push -- regenerate via install-hooks.sh to get non-fatal sync wrapper
  - CONTRIBUTING.md:L161 -- fix rsync --delete claim, add _archive/ exclusion note
  - CONTRIBUTING.md -- add reminder about re-running install-hooks.sh after changes
  - scripts/install-hooks.sh -- source of truth (read-only reference, not modified)
- **Root cause**: The installed .git/hooks/pre-push is an older version that runs sync-to-claude.sh under set -euo pipefail with no error handling. The current install-hooks.sh wraps sync in a non-fatal if block. The hook was never regenerated after install-hooks.sh was updated.
- **Expected behavior**: Push should succeed even when sync-to-claude.sh fails. The installed hook should match the current install-hooks.sh output (non-fatal sync).
- **Acceptance criteria**:
  1. Installed .git/hooks/pre-push matches output of install-hooks.sh (non-fatal sync)
  2. CONTRIBUTING.md rsync description matches actual sync-to-claude.sh behavior (no --delete, excludes _archive/)
  3. CONTRIBUTING.md includes guidance on re-running install-hooks.sh after pulling changes
  4. Push succeeds even when sync-to-claude.sh fails (manual test)

## Scope Boundaries
Read ONLY:
- scripts/install-hooks.sh (full file -- source of truth for hook generation)
- scripts/sync-to-claude.sh (full file -- to verify actual rsync behavior for CONTRIBUTING.md accuracy)
- .git/hooks/pre-push (current installed version -- to confirm the stale state)
- CONTRIBUTING.md:L155-170 (sync documentation section)

Do NOT edit:
- scripts/install-hooks.sh (source of truth; not modified)
- scripts/sync-to-claude.sh (not part of this task)
- orchestration/ directory (no orchestration changes)
- agents/ directory (no agent changes)

## Focus
Your task is ONLY to regenerate the pre-push hook via install-hooks.sh and update CONTRIBUTING.md sync documentation to match actual behavior.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
