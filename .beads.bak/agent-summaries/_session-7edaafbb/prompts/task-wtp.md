# Task Brief: ant-farm-wtp
**Task**: scrub-pii.sh does not re-stage issues.jsonl when run standalone outside pre-commit
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/wtp.md

## Context
- **Affected files**: scripts/scrub-pii.sh:L46-60 -- standalone (non-check) execution path; scripts/install-hooks.sh:L80-83 -- git add in generated pre-commit hook
- **Root cause**: When run standalone (not as pre-commit hook), scrub-pii.sh modifies issues.jsonl in place but does not re-stage it. The git add is in install-hooks.sh's generated hook (L80-83), not in scrub-pii.sh itself.
- **Expected behavior**: Script should detect non-hook context and print reminder to run 'git add .beads/issues.jsonl'.
- **Acceptance criteria**:
  1. Standalone execution prints reminder about re-staging
  2. Pre-commit hook behavior unchanged

## Scope Boundaries
Read ONLY: scripts/scrub-pii.sh:L1-61 (full file); scripts/install-hooks.sh:L63-85 (generated pre-commit hook section, for reference only)
Do NOT edit: scripts/install-hooks.sh, scripts/fill-review-slots.sh, any other scripts

## Focus
Your task is ONLY to add a re-staging reminder when scrub-pii.sh is run standalone (outside a git hook).
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
