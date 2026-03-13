# Task: ant-farm-oc9v
**Status**: success
**Title**: Incomplete pantry-review deprecation across docs and agent configs
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/RULES.md:182-183 -- duplicated deprecated row with inconsistent wording
- orchestration/templates/scout.md:61 -- stale pantry-review in exclusion list
- orchestration/GLOSSARY.md:28,81 -- references pantry-review.md as live
- README.md:275 -- lists pantry-review as active agent

## Root Cause
The deprecation of pantry-review was applied to RULES.md and pantry.md but not propagated to all downstream references. Multiple files still reference pantry-review as if it were a live agent type. Found by: Clarity (P3 - F5), Edge Cases (P3 - F10), Excellence (P3 - F6, F7). 4 findings across 3 reviewers, all P3. Same root cause: incomplete deprecation rollout.

## Expected Behavior
No file references pantry-review without a deprecation marker. All references should either be removed or clearly marked as deprecated.

## Acceptance Criteria
1. No file references pantry-review without a deprecation marker
2. GLOSSARY.md and README.md updated to remove or mark deprecated pantry-review references
3. scout.md exclusion list cleaned up (remove stale pantry-review entry)
4. RULES.md deprecated row wording unified (remove duplication at lines 182-183)
