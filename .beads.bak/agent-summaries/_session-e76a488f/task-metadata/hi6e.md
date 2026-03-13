# Task: ant-farm-hi6e
**Status**: success
**Title**: Pass 1-B: Verify 22 beads against pantry.md and pantry-review.md
**Type**: task
**Priority**: P2
**Epic**: ant-farm-v2h1
**Agent Type**: code-reviewer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/pantry.md -- primary file to verify beads against
- orchestration/_archive/pantry-review.md -- archived file referenced by some beads
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-B-input.jsonl -- input bead records
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-B-output.json -- output verdicts (to create)
- .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt -- cross-batch duplicate detection

## Root Cause
22 beads reference pantry template issues (fail-fast wording, placeholders, guards, TOCTOU races, Section 2 deprecation). pantry-review.md is archived; beads about it may be irrelevant.

## Expected Behavior
Each bead gets a verdict with evidence. Known duplicates (bo7d/gl11, e66h/onmp, 4u4s/wlo4) are identified.

## Acceptance Criteria
1. Output file contains exactly 22 entries
2. Output is valid JSON array
3. Known duplicates (bo7d/gl11, e66h/onmp, 4u4s/wlo4) are marked DUPLICATE_SUSPECT with cross-references
4. Beads referencing archived pantry-review.md have clear rationale for IRRELEVANT or STILL_VALID
5. Every ALREADY_FIXED verdict cites specific evidence
