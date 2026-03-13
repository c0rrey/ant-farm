# Task: ant-farm-4vg
**Status**: success
**Title**: AGG-027: Standardize review type naming between display titles and short names
**Type**: task
**Priority**: P2
**Epic**: ant-farm-amk
**Agent Type**: technical-writer
**Dependencies**: blocks: [], blockedBy: []

## Affected Files
- orchestration/templates/reviews.md — Uses "Correctness Redux" as display title while short name is "correctness"
- orchestration/templates/nitpicker-skeleton.md — May use review type names in filenames/placeholders
- orchestration/templates/implementation.md — May reference review types

## Root Cause
reviews.md uses "Correctness Redux" as a display title while filenames and skeleton placeholders use "correctness". This inconsistency increases parsing friction in chained prompts.

## Expected Behavior
Each review type has one canonical name used in both templates and filenames. If display and short forms both exist, a mapping table documents the correspondence.

## Acceptance Criteria
1. Each review type has one canonical name used in both templates and filenames
2. If display and short forms both exist, a mapping table documents the correspondence
3. No template uses a review type name that differs from the canonical form without explanation
