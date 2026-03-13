# Task Brief: ant-farm-npfx
**Task**: parse-progress-log.sh hardening gaps (overwrite, dead branch, corruption)
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/npfx.md

## Context
- **Affected files**: scripts/parse-progress-log.sh:L117-124 -- no validation for corrupted/malformed log lines (timestamp format not validated); scripts/parse-progress-log.sh:L148-151 -- redundant dead branch with misleading comment (code after SESSION_COMPLETE check); scripts/parse-progress-log.sh:L157-224 -- silently overwrites existing resume-plan.md
- **Root cause**: First-pass implementation handles happy path but lacks defensive coding for edge scenarios: (1) no timestamp validation on log lines, (2) dead branch code after the SESSION_COMPLETE guard, (3) silent overwrite of existing resume-plan.md.
- **Expected behavior**: Overwrite produces stderr notice. Dead branch comment is accurate. Malformed lines rejected with timestamp validation.
- **Acceptance criteria**:
  1. Overwrite produces stderr notice
  2. Dead branch comment is accurate
  3. Malformed lines rejected with timestamp validation

## Scope Boundaries
Read ONLY: scripts/parse-progress-log.sh:L1-280 (full file, focus on L117-124, L148-151, L157-224)
Do NOT edit: scripts/compose-review-skeletons.sh, scripts/fill-review-slots.sh, any other scripts

## Focus
Your task is ONLY to harden parse-progress-log.sh against overwrite, dead branch, and corruption scenarios.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
