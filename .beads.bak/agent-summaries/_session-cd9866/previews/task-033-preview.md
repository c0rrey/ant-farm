Execute bug for ant-farm-033.

Step 0: Read your task context from .beads/agent-summaries/_session-cd9866/prompts/task-033.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-033` + `bd update ant-farm-033 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-033)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-cd9866/summaries/033.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-033`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

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
