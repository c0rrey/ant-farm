# Task: ant-farm-3iye
**Status**: success
**Title**: Heredoc/JSON injection via unsanitized user input in plan.md
**Type**: bug
**Priority**: P2
**Epic**: none
**Agent Type**: general-purpose
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- skills/plan.md:127-145 — heredoc delimiter collision risk with SPEC_EOF
- skills/plan.md:119-122 — JSON injection via unescaped INPUT_SOURCE in manifest.json

## Root Cause
skills/plan.md constructs file content via heredocs and string interpolation without sanitizing user-supplied content. Two injection vectors: heredoc delimiter collision and unescaped JSON interpolation.

## Expected Behavior
Use jq -n for JSON construction and collision-resistant heredoc delimiters.

## Acceptance Criteria
1. manifest.json is constructed via jq -n or equivalent JSON-safe method
2. User input containing double quotes, backslashes, or the heredoc delimiter does not corrupt output files
