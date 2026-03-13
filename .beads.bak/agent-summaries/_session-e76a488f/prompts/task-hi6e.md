# Task Brief: ant-farm-hi6e
**Task**: Pass 1-B: Verify 22 beads against pantry.md and pantry-review.md
**Agent Type**: code-reviewer
**Summary output path**: .beads/agent-summaries/_session-e76a488f/summaries/hi6e.md

## Context
- **Affected files**:
  - orchestration/templates/pantry.md -- primary file to verify beads against
  - orchestration/_archive/pantry-review.md -- archived file referenced by some beads
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-B-input.jsonl -- input bead records
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-B-output.json -- output verdicts (to create)
  - .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt -- cross-batch duplicate detection
- **Root cause**: 22 beads reference pantry template issues (fail-fast wording, placeholders, guards, TOCTOU races, Section 2 deprecation). pantry-review.md is archived; beads about it may be irrelevant.
- **Expected behavior**: Each bead gets a verdict with evidence. Known duplicates (bo7d/gl11, e66h/onmp, 4u4s/wlo4) are identified.
- **Acceptance criteria**:
  1. Output file contains exactly 22 entries
  2. Output is valid JSON array
  3. Known duplicates (bo7d/gl11, e66h/onmp, 4u4s/wlo4) are marked DUPLICATE_SUSPECT with cross-references
  4. Beads referencing archived pantry-review.md have clear rationale for IRRELEVANT or STILL_VALID
  5. Every ALREADY_FIXED verdict cites specific evidence

## Scope Boundaries
Read ONLY:
- orchestration/templates/pantry.md (full file)
- orchestration/_archive/pantry-review.md (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-B-input.jsonl (full file)
- .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt (full file)

Do NOT edit:
- orchestration/templates/pantry.md
- orchestration/_archive/pantry-review.md
- Any files outside the audit output directory

## Focus
Your task is ONLY to verify 22 beads against pantry.md and pantry-review.md and write verdicts to the output JSON file.
Do NOT fix adjacent issues you notice.
Do NOT modify the template files -- only produce verdicts about the beads.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
