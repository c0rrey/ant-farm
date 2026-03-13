Execute bug for ant-farm-5365.

Step 0: Read your task context from .beads/agent-summaries/_session-2829f0f5/prompts/task-5365.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-5365` + `bd update ant-farm-5365 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-5365)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-2829f0f5/summaries/5365.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-5365`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/CLAUDE.md.
Note: README.md IS an affected file for this task -- editing it is permitted per the task brief scope.

---

# Task Brief: ant-farm-5365
**Task**: fix: scrub-pii.sh and pre-commit hook not described in SETUP.md or README.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2829f0f5/summaries/5365.md

## Context
- **Affected files**:
  - SETUP.md -- Quick Setup section, missing pre-commit hook mention (Scout note: no specific line; content to be added)
  - README.md -- setup section, optionally missing PII scrubbing mention (Scout note: no specific line; content to be added)
- **Root cause**: The pre-commit hook runs scripts/scrub-pii.sh to strip email addresses from .beads/issues.jsonl before staging. Documented in CONTRIBUTING.md:L176-178 but absent from SETUP.md and README.md. Developers following SETUP.md will learn about the pre-push hook but not the pre-commit hook.
- **Expected behavior**: SETUP.md mentions both pre-push (sync) and pre-commit (PII scrub) hooks. README.md optionally mentions PII scrubbing.
- **Acceptance criteria**:
  1. SETUP.md mentions both pre-push (sync) and pre-commit (PII scrub) hooks
  2. README.md optionally mentions PII scrubbing in the setup section

## Scope Boundaries
Read ONLY: SETUP.md (full file), README.md (full file), CONTRIBUTING.md:L170-185 (reference for existing documentation)
Do NOT edit: CONTRIBUTING.md, scripts/scrub-pii.sh, or .git/hooks/. This is a documentation-only task.

## Focus
Your task is ONLY to add pre-commit hook and PII scrubbing mentions to SETUP.md and optionally README.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
