# Task: ant-farm-cl8
**Status**: success
**Title**: scrub-pii.sh only matches quoted emails, misses unquoted occurrences
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: devops-engineer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- scripts/scrub-pii.sh:38,52 — PII regex only matches quoted emails

## Root Cause
Both --check mode (line 38) and post-scrub verification (line 52) in scrub-pii.sh wrap the PII regex with double-quote anchors, only matching '"email@example.com"' patterns. If an email appears unquoted, the scrub misses it silently.

## Expected Behavior
--check mode detects emails regardless of quoting context. Scrub handles both quoted and unquoted emails.

## Acceptance Criteria
1. --check mode detects emails regardless of quoting context
2. Scrub handles both quoted and unquoted emails
