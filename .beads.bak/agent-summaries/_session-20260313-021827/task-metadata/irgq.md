# Task: ant-farm-irgq
**Status**: success
**Title**: Epic 2: Beads Migration (Mechanical)
**Type**: epic
**Priority**: P2
**Epic**: none (is epic)
**Agent Type**: general-purpose
**Dependencies**: {blocks: [ant-farm-2sar, ant-farm-ud2k], blockedBy: [ant-farm-e7em (closed)]}

## Affected Files
- orchestration/templates/scout.md — bd command references
- orchestration/templates/implementation.md — bd command references
- orchestration/templates/dirt-pusher-skeleton.md — bd command references
- orchestration/templates/nitpicker-skeleton.md — bd command references
- orchestration/templates/scribe-skeleton.md — bd command references
- orchestration/templates/queen-state.md — session paths, bd commands
- orchestration/templates/SESSION_PLAN_TEMPLATE.md — bd commands
- orchestration/reference/dependency-analysis.md — bd references
- orchestration/SETUP.md — bd references
- agents/scout-organizer.md — bd command references
- agents/nitpicker.md — bd references
- README.md — bd references
- AGENTS.md — bd references
- CONTRIBUTING.md — bd reference
- docs/installation-guide.md — bd reference

## Root Cause
Pure bd -> crumb string substitution across ~15 files. High volume, low risk -- find-and-replace with terminology updates (beads->crumbs, .beads/->.crumbs/).

## Expected Behavior
All mechanical bd references replaced with crumb equivalents across all child task files.

## Acceptance Criteria
1. All child tasks completed (6 children)
2. Zero bd references remaining in affected files
3. .beads/ paths updated to .crumbs/ where present
