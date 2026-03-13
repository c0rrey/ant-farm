# Task: ant-farm-6jxn
**Status**: success
**Title**: Stale documentation from pantry-review deprecation (5 surfaces)
**Type**: bug
**Priority**: P3
**Epic**: none
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/reviews.md:1 -- reader comment referencing pantry-review as active
- README.md:171-197 -- architecture diagram listing pantry-review as active component
- orchestration/templates/pantry.md:271-277 -- deprecation notice and heading for pantry-review
- orchestration/_archive/pantry-review.md:1-7 -- active YAML frontmatter (should be marked deprecated/archived)

## Root Cause
When Pantry review-mode was deprecated and replaced by fill-review-slots.sh, consumer-facing annotations and architecture diagrams were not updated. 5 surfaces still reference pantry-review as if it were active. Consolidated from: Clarity F2, F7, F8, Excellence F6, F8, F9.

## Expected Behavior
All 5 surfaces should reflect current architecture (fill-review-slots.sh replaced pantry-review). No references to pantry-review as a live/active agent.

## Acceptance Criteria
1. reviews.md:1 reader comment updated to reflect current review architecture
2. README.md:171-197 architecture diagram updated to show fill-review-slots.sh instead of pantry-review
3. pantry.md:271-277 deprecation notice and heading updated
4. _archive/pantry-review.md:1-7 YAML frontmatter marked as archived/deprecated
5. No surface references pantry-review as active
