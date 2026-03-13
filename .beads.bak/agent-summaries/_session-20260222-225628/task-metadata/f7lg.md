# Task: ant-farm-f7lg
**Status**: success
**Title**: Incomplete round-transition spec: phantom briefs/ path and missing edge-cases output path
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: prompt-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/reviews.md:1091 — phantom `briefs/` path reference
- orchestration/templates/reviews.md:1094 — "same fields as above" with no edge-cases output path
- orchestration/RULES.md:393 — "same fields as above" for edge-cases reviewer, no distinct output path

## Root Cause
The round-transition SendMessage specification references a `{session-dir}/briefs/review-brief-<timestamp>.md` path that does not exist in the canonical session layout. Additionally, the Edge Cases reviewer has no explicit output path -- it just says "same fields as above" without defining a distinct path, risking both reviewers writing to the same correctness path.

## Expected Behavior
1. No references to phantom `briefs/` path in round-transition section
2. Edge Cases reviewer has an explicit, distinct output path in both RULES.md and reviews.md

## Acceptance Criteria
1. No references to `{session-dir}/briefs/` exist in reviews.md round-transition section
2. Edge Cases reviewer has an explicit, distinct output path in the round-transition SendMessage fields
3. Both RULES.md and reviews.md round-transition fields are consistent with each other
