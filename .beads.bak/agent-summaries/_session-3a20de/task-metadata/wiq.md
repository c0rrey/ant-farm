# Task: ant-farm-wiq
**Status**: success
**Title**: Checkpoints CCO FAIL verdict format has no example
**Type**: task
**Priority**: P3
**Epic**: ant-farm-753
**Agent Type**: technical-writer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/checkpoints.md — CCO section, add FAIL verdict example

## Root Cause
checkpoints.md shows PASS verdict format but no example of a FAIL verdict with specific check failures listed. A fresh Pest Control agent might format FAIL output incorrectly.

## Expected Behavior
FAIL example showing check number, name, and evidence added to CCO section.

## Acceptance Criteria
1. CCO section includes a FAIL verdict example with check number, name, and evidence
