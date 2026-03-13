# Task Brief: ant-farm-033
**Task**: Installation guide omits pre-commit PII scrub hook documentation
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/033.md

## Context
- **Affected files**: docs/installation-guide.md:L20-31 (Step 1 only describes pre-push hook; no mention of pre-commit hook), docs/installation-guide.md:L28-31 (install-hooks.sh description lists only pre-push behavior), docs/installation-guide.md:L150-158 (backup section only covers pre-push backup)
- **Root cause**: install-hooks.sh (scripts/install-hooks.sh:L51-88) now installs both a pre-push hook (sync-to-claude.sh) and a pre-commit hook (scrub-pii.sh), but docs/installation-guide.md only describes the pre-push hook. The pre-commit hook's purpose (PII scrubbing of issues.jsonl), behavior (runs scrub-pii.sh on staged issues.jsonl), backup path (.git/hooks/pre-commit.bak), and verification steps are entirely absent from the documentation.
- **Expected behavior**: Both hooks are documented in the installation guide with purpose, behavior, backup, and verification steps.
- **Acceptance criteria**:
  1. Both hooks (pre-push and pre-commit) documented in the installation guide with purpose, behavior, and verification steps
  2. Pre-commit.bak backup path mentioned in the backup section

## Scope Boundaries
Read ONLY: docs/installation-guide.md:L1-357, scripts/install-hooks.sh:L51-88 (pre-commit hook source for accurate documentation)
Do NOT edit: scripts/install-hooks.sh, scripts/scrub-pii.sh, orchestration/SETUP.md, README.md

## Focus
Your task is ONLY to add pre-commit PII scrub hook documentation to the installation guide.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
