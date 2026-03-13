# Task Brief: ant-farm-9vq
**Task**: scrub-pii.sh grep pattern defined as variable but duplicated inline in verification
**Agent Type**: devops-engineer
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/9vq.md

## Context
- **Affected files**: scripts/scrub-pii.sh:L35 -- PII_FIELD_PATTERN variable definition; scripts/scrub-pii.sh:L38 -- check mode usage; scripts/scrub-pii.sh:L54-55 -- post-scrub verification with inlined regex
- **Root cause**: PII_PATTERN is defined at line 35 and used in --check mode (line 38), but post-scrub verification (lines 54-55) re-inlines the same regex pattern. If either drifts, check and verification validate against different definitions.
- **Expected behavior**: Single PII pattern source used in all grep calls.
- **Acceptance criteria**:
  1. PII_FIELD_PATTERN variable is used in all three grep calls
  2. No duplicated inline patterns

## Scope Boundaries
Read ONLY: scripts/scrub-pii.sh:L1-61 (full file, focus on L35, L38, L54-55)
Do NOT edit: scripts/install-hooks.sh, scripts/fill-review-slots.sh, any other scripts

## Focus
Your task is ONLY to consolidate the grep pattern usage to use PII_FIELD_PATTERN variable consistently.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
