# Task Brief: ant-farm-7h3g
**Task**: Pass 1-A: Verify 33 beads against orchestration/RULES.md
**Agent Type**: code-reviewer
**Summary output path**: .beads/agent-summaries/_session-e76a488f/summaries/7h3g.md

## Context
- **Affected files**:
  - orchestration/RULES.md -- primary file to verify beads against
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-A-input.jsonl -- input bead records
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-A-output.json -- output verdicts (to create)
  - .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt -- cross-batch duplicate detection
- **Root cause**: 33 beads reference RULES.md issues (step numbering, stale terminology, missing entries, documentation drift). Recent commits have modified RULES.md; beads may be already fixed.
- **Expected behavior**: Each bead gets a verdict (STILL_VALID, ALREADY_FIXED, IRRELEVANT, NEEDS_CONTEXT, DUPLICATE_SUSPECT) with evidence.
- **Acceptance criteria**:
  1. Output file contains exactly 33 entries, one per bead
  2. Output is valid JSON array
  3. Every ALREADY_FIXED verdict cites specific evidence (current file content or commit hash)
  4. Every DUPLICATE_SUSPECT cites the other bead ID and explains the overlap
  5. Feature requests (ant-farm-f0x, ant-farm-b89w) are not marked ALREADY_FIXED just because RULES.md changed

## Scope Boundaries
Read ONLY:
- orchestration/RULES.md (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-A-input.jsonl (full file)
- .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt (full file)

Do NOT edit:
- Any orchestration template files
- Any files outside the audit output directory
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-A-input.jsonl (read-only input)

## Focus
Your task is ONLY to verify 33 beads against orchestration/RULES.md and write verdicts to the output JSON file.
Do NOT fix adjacent issues you notice.
Do NOT modify RULES.md itself -- only produce verdicts about the beads.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
