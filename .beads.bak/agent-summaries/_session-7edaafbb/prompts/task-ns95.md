# Task Brief: ant-farm-ns95
**Task**: scrub-pii.sh email regex has limited pattern coverage
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/ns95.md

## Context
- **Affected files**: scripts/scrub-pii.sh:L35 -- PII_FIELD_PATTERN email regex definition; scripts/scrub-pii.sh:L52 -- perl substitution regex; scripts/scrub-pii.sh:L54-55 -- post-scrub verification regex
- **Root cause**: Email regex does not match RFC 5321 quoted local parts or uncommon characters. Low risk given typical data sources.
- **Expected behavior**: Widen pattern or document intentional coverage scope.
- **Acceptance criteria**:
  1. Email regex coverage is either widened or explicitly documented as intentionally limited

## Scope Boundaries
Read ONLY: scripts/scrub-pii.sh:L1-61 (full file, focus on L35, L52, L54-55 regex patterns)
Do NOT edit: scripts/install-hooks.sh, scripts/fill-review-slots.sh, any other scripts

## Focus
Your task is ONLY to address email regex coverage in scrub-pii.sh by widening the pattern or documenting the intentional limitation.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
