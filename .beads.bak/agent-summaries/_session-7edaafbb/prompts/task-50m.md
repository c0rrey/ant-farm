# Task Brief: ant-farm-50m
**Task**: scrub-pii.sh assumes perl is installed without checking
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/50m.md

## Context
- **Affected files**: scripts/scrub-pii.sh:L52 -- perl -i -pe usage without availability check
- **Root cause**: scrub-pii.sh:L52 uses 'perl -i -pe' without checking if perl is available. In minimal Docker/CI environments, perl may be absent. Script would silently fail to scrub.
- **Expected behavior**: Script should check for perl availability at startup and fail with a clear error message.
- **Acceptance criteria**:
  1. Script checks for perl with 'command -v perl' at startup
  2. Clear error message if perl is not found

## Scope Boundaries
Read ONLY: scripts/scrub-pii.sh:L1-61 (full file, focus on adding check near top after set -euo pipefail)
Do NOT edit: scripts/install-hooks.sh, scripts/fill-review-slots.sh, any other scripts

## Focus
Your task is ONLY to add a perl availability check at startup in scrub-pii.sh.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
