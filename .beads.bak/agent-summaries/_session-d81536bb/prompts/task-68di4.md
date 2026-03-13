# Task Brief: ant-farm-68di.4
**Task**: Update crash recovery script for Scribe progress log entries
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-d81536bb/summaries/68di4.md

## Context
- **Affected files**: scripts/parse-progress-log.sh:L62-73 (STEP_KEYS array), scripts/parse-progress-log.sh:L75-89 (step_label function), scripts/parse-progress-log.sh:L91-105 (step_resume_action function)
- **Root cause**: N/A (feature task -- infrastructure update). The crash recovery script does not yet recognize SCRIBE_COMPLETE or ESV_PASS milestones, so sessions that crash during the Scribe/ESV phase cannot produce correct resume instructions.
- **Expected behavior**: parse-progress-log.sh recognizes SCRIBE_COMPLETE and ESV_PASS milestones in the correct workflow order, and generates appropriate resume instructions when a session crashes during the Scribe/ESV phase.
- **Acceptance criteria**:
  1. SCRIBE_COMPLETE appears in the step keys list in parse-progress-log.sh, after XREF_VERIFIED
  2. ESV_PASS appears in the step keys list in parse-progress-log.sh, after SCRIBE_COMPLETE
  3. A progress.log containing XREF_VERIFIED but missing SCRIBE_COMPLETE produces a resume plan that says to resume at Step 5b (Scribe)
  4. A progress.log containing SCRIBE_COMPLETE but missing ESV_PASS produces a resume plan that says to resume at Step 5c (ESV)
  5. Existing tests (if any) still pass with the new step keys added

## Scope Boundaries
Read ONLY: scripts/parse-progress-log.sh:L1-301 (entire file)
Do NOT edit: Any file other than scripts/parse-progress-log.sh. Do NOT edit the map_* utility functions (L118-154) or the log-parsing loop (L160-185) or the resume-plan markdown generation (L228-297) unless strictly required by the new step keys.

## Focus
Your task is ONLY to add SCRIBE_COMPLETE and ESV_PASS step keys to parse-progress-log.sh and provide corresponding labels and resume actions.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
