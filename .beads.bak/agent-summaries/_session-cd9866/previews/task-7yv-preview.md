Execute bug for ant-farm-7yv.

Step 0: Read your task context from .beads/agent-summaries/_session-cd9866/prompts/task-7yv.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-7yv` + `bd update ant-farm-7yv --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-7yv)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-cd9866/summaries/7yv.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-7yv`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-7yv
**Task**: Pre-commit hook silently allows PII when scrub script not executable
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/7yv.md

## Context
- **Affected files**: scripts/install-hooks.sh:L72-75 (generated pre-commit hook exits 0 with WARNING when scrub script not executable, silently allowing PII into git history), scripts/scrub-pii.sh:L1 (needs chmod +x during installation)
- **Root cause**: The generated pre-commit hook in install-hooks.sh:L72-75 checks `if [[ ! -x "$SCRUB_SCRIPT" ]]` and then exits 0 (allows commit) with only a WARNING message. This means a missing or non-executable scrub-pii.sh silently allows issues.jsonl with PII (raw email addresses) to enter git history. The hook should fail (exit 1) when the scrub script is not available, preventing PII leakage. Additionally, install-hooks.sh should ensure scrub-pii.sh is chmod +x after installation.
- **Expected behavior**: PII cannot enter git history when scrub script is missing or non-executable. install-hooks.sh ensures scrub-pii.sh is executable after installation.
- **Acceptance criteria**:
  1. Pre-commit hook exits non-zero (blocks commit) when scrub-pii.sh is missing or not executable, preventing PII from entering git history
  2. install-hooks.sh ensures scrub-pii.sh is executable (chmod +x) after hook installation

## Scope Boundaries
Read ONLY: scripts/install-hooks.sh:L51-89, scripts/scrub-pii.sh:L1-5 (shebang and header only)
Do NOT edit: scripts/scrub-pii.sh (beyond verifying it exists), docs/installation-guide.md, orchestration/ files

## Focus
Your task is ONLY to change the pre-commit hook to fail when scrub script is missing/non-executable, and ensure install-hooks.sh makes scrub-pii.sh executable.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
