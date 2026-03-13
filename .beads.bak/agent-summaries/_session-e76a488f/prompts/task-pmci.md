# Task Brief: ant-farm-pmci
**Task**: Pass 1-F: Verify 8 beads against scout.md
**Agent Type**: code-reviewer
**Summary output path**: .beads/agent-summaries/_session-e76a488f/summaries/pmci.md

## Context
- **Affected files**:
  - orchestration/templates/scout.md -- primary file (292 lines)
  - orchestration/reference/dependency-analysis.md -- for ant-farm-dz4 cross-reference
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-F-input.jsonl -- input bead records
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-F-output.json -- output verdicts (to create)
  - .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt -- cross-batch duplicate detection
- **Root cause**: 8 beads cover Scout template issues (missing Errors section, frontmatter skipping, bd blocked assumption, parallel vs sequential discrepancy, wave capacity validation, PICK ONE syntax). 5 of 8 lack descriptions.
- **Expected behavior**: Each bead gets a verdict. Step number references checked for shifts.
- **Acceptance criteria**:
  1. Output file contains exactly 8 entries
  2. Output is valid JSON array
  3. Every ALREADY_FIXED verdict cites specific evidence
  4. Beads referencing step numbers note whether numbering has shifted

## Scope Boundaries
Read ONLY:
- orchestration/templates/scout.md (full file, 292 lines)
- orchestration/reference/dependency-analysis.md (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-F-input.jsonl (full file)
- .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt (full file)

Do NOT edit:
- orchestration/templates/scout.md
- orchestration/reference/dependency-analysis.md
- Any files outside the audit output directory

## Focus
Your task is ONLY to verify 8 beads against scout.md and write verdicts to the output JSON file.
Do NOT fix adjacent issues you notice.
Do NOT modify the template files -- only produce verdicts about the beads.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
