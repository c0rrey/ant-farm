# Task Brief: ant-farm-1b8
**Task**: Installation guide uninstall uses wrong path ~/.git/ instead of .git/
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/1b8.md

## Context
- **Affected files**: docs/installation-guide.md:L193 (uninstall step uses `rm ~/.git/hooks/pre-push` which resolves to the user's home directory .git, not the repo's .git)
- **Root cause**: docs/installation-guide.md:L193 uses `rm ~/.git/hooks/pre-push` which resolves to `~/.git/hooks/pre-push` -- the user's home directory .git. This is wrong because the pre-push hook is installed to the repo's `.git/hooks/pre-push` (relative to repo root). Any user running this verbatim will either hit 'No such file or directory' or delete a hook from the wrong repository. Additionally, uninstall instructions only cover the pre-push hook; the pre-commit hook (installed by the same script) has no uninstall instructions.
- **Expected behavior**: Uninstall path is `.git/hooks/pre-push` (relative to repo root). Both hooks (pre-push and pre-commit) have uninstall instructions.
- **Acceptance criteria**:
  1. Uninstall path corrected from `~/.git/hooks/pre-push` to `.git/hooks/pre-push` (repo-relative)
  2. Both hooks (pre-push and pre-commit) have uninstall instructions

## Scope Boundaries
Read ONLY: docs/installation-guide.md:L185-245
Do NOT edit: scripts/install-hooks.sh, scripts/scrub-pii.sh, orchestration/SETUP.md, README.md

## Focus
Your task is ONLY to fix the uninstall path and add pre-commit hook uninstall instructions.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
