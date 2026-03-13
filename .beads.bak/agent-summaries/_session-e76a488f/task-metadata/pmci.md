# Task: ant-farm-pmci
**Status**: success
**Title**: Pass 1-F: Verify 8 beads against scout.md
**Type**: task
**Priority**: P2
**Epic**: ant-farm-v2h1
**Agent Type**: code-reviewer
**Dependencies**: {blocks: [], blockedBy: []}

## Affected Files
- orchestration/templates/scout.md -- primary file (292 lines)
- orchestration/reference/dependency-analysis.md -- for ant-farm-dz4 cross-reference
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-F-input.jsonl -- input bead records
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-F-output.json -- output verdicts (to create)
- .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt -- cross-batch duplicate detection

## Root Cause
8 beads cover Scout template issues (missing Errors section, frontmatter skipping, bd blocked assumption, parallel vs sequential discrepancy, wave capacity validation, PICK ONE syntax). 5 of 8 lack descriptions.

## Expected Behavior
Each bead gets a verdict. Step number references checked for shifts.

## Acceptance Criteria
1. Output file contains exactly 8 entries
2. Output is valid JSON array
3. Every ALREADY_FIXED verdict cites specific evidence
4. Beads referencing step numbers note whether numbering has shifted
