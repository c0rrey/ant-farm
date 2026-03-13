# Task Brief: ant-farm-9wk8
**Task**: Undocumented magic value ctc in scrub-pii.sh
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/9wk8.md

## Context
- **Affected files**: scripts/scrub-pii.sh:L8,L48,L52 -- magic value 'ctc' used as replacement token
- **Root cause**: The replacement token 'ctc' used for scrubbed PII is not defined or explained anywhere. It appears in the header comment (L8), the explanatory comment (L48), and the perl substitution (L52).
- **Expected behavior**: Add explanatory comment or use self-documenting value like [REDACTED].
- **Acceptance criteria**:
  1. Magic value is either documented with a comment or replaced with self-documenting value

## Scope Boundaries
Read ONLY: scripts/scrub-pii.sh:L1-61 (full file)
Do NOT edit: scripts/install-hooks.sh, scripts/fill-review-slots.sh, any other scripts

## Focus
Your task is ONLY to document or replace the magic 'ctc' value in scrub-pii.sh.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
