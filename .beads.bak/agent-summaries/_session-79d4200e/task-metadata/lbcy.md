# Task: ant-farm-lbcy
**Status**: success
**Title**: fix: double-brace placeholder tier {{SLOT}} absent from PLACEHOLDER_CONVENTIONS.md
**Type**: bug
**Priority**: P2
**Epic**: ant-farm-908t
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/PLACEHOLDER_CONVENTIONS.md — add Tier 4 (Script-Substituted {{DOUBLE_BRACE}})
- orchestration/templates/PLACEHOLDER_CONVENTIONS.md (File-by-File Audit table) — fix reviews.md row

## Root Cause
Double-brace convention was introduced by review slot-filling scripts without updating the placeholder conventions document.

## Expected Behavior
PLACEHOLDER_CONVENTIONS.md should document the {{DOUBLE_BRACE}} tier and correctly reflect reviews.md usage in the audit table.

## Acceptance Criteria
1. PLACEHOLDER_CONVENTIONS.md documents the {{DOUBLE_BRACE}} tier
2. Tier 4 description identifies fill-review-slots.sh as the substitution mechanism
3. File-by-File Audit table for reviews.md reflects the double-brace usage
4. All {{SLOT}} markers across templates are accounted for in the new tier description
