# Task: ant-farm-crky
**Status**: success
**Title**: Big Head skeleton and reviews.md have divergent failure handling for missing reports
**Type**: bug
**Priority**: P2
**Epic**: _standalone
**Agent Type**: prompt-engineer
**Dependencies**: blocks: [], blockedBy: []

## Affected Files
- orchestration/templates/big-head-skeleton.md:57-66 — Says "FAIL immediately if any missing" with no waiting; failure artifact written to review-consolidated-{TIMESTAMP}-FAILED.md
- orchestration/templates/reviews.md:354-424 — Specifies a 30-second polling loop with timeout before failing; returns inline structured error on timeout

## Root Cause
Big Head receives contradictory instructions about handling missing Nitpicker reports from two sources: (1) big-head-skeleton.md (lines 57-66) says 'FAIL immediately if any missing' with no waiting; (2) reviews.md Step 0a (lines 354-424) specifies a 30-second polling loop with timeout before failing. Big Head must resolve the ambiguity at runtime. Additionally, the failure artifact paths differ: skeleton writes to review-consolidated-{TIMESTAMP}-FAILED.md while reviews.md returns an inline structured error.

## Expected Behavior
Designate one template as authoritative. Update skeleton to reference the brief for remediation details, or add the polling protocol to the skeleton with consistent failure artifact paths.

## Acceptance Criteria
1. One template is designated authoritative for missing-report handling
2. The other template references the authoritative one rather than contradicting it
3. Failure artifact paths are consistent between both templates
4. Big Head has unambiguous instructions at runtime with no need to resolve contradictions
