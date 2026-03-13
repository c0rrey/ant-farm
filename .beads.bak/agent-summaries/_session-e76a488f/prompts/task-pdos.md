# Task Brief: ant-farm-pdos
**Task**: Pass 1-E: Verify 16 beads against PLACEHOLDER_CONVENTIONS.md
**Agent Type**: code-reviewer
**Summary output path**: .beads/agent-summaries/_session-e76a488f/summaries/pdos.md

## Context
- **Affected files**:
  - orchestration/PLACEHOLDER_CONVENTIONS.md -- primary file
  - orchestration/templates/dirt-pusher-skeleton.md -- for ant-farm-omwi
  - orchestration/templates/queen-state.md -- for ant-farm-glzg
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-E-input.jsonl -- input bead records
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-E-output.json -- output verdicts (to create)
  - .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt -- cross-batch duplicate detection
- **Root cause**: 16 beads cover placeholder convention issues (angle-bracket syntax, tier naming, compliance status, enforcement strategy, validation regex). 14 of 16 lack descriptions. Many are closely related and may overlap semantically.
- **Expected behavior**: Each bead gets a verdict. Near-duplicate clusters (enforcement strategy, angle-bracket docs) identified.
- **Acceptance criteria**:
  1. Output file contains exactly 16 entries
  2. Output is valid JSON array
  3. Near-duplicate clusters (enforcement strategy, angle-bracket docs) are identified and cross-referenced
  4. Title-only beads (14 of 16) have clear rationale for their verdict
  5. Every ALREADY_FIXED verdict cites specific evidence

## Scope Boundaries
Read ONLY:
- orchestration/PLACEHOLDER_CONVENTIONS.md (full file)
- orchestration/templates/dirt-pusher-skeleton.md (full file)
- orchestration/templates/queen-state.md (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-E-input.jsonl (full file)
- .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt (full file)

Do NOT edit:
- orchestration/PLACEHOLDER_CONVENTIONS.md
- orchestration/templates/dirt-pusher-skeleton.md
- orchestration/templates/queen-state.md
- Any files outside the audit output directory

## Focus
Your task is ONLY to verify 16 beads against PLACEHOLDER_CONVENTIONS.md and related files and write verdicts to the output JSON file.
Do NOT fix adjacent issues you notice.
Do NOT modify the convention or template files -- only produce verdicts about the beads.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
