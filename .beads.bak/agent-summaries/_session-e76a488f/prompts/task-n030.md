# Task Brief: ant-farm-n030
**Task**: Pass 1-H: Verify 15 beads against README, CONTRIBUTING, SETUP, GLOSSARY docs
**Agent Type**: code-reviewer
**Summary output path**: .beads/agent-summaries/_session-e76a488f/summaries/n030.md

## Context
- **Affected files**:
  - README.md -- architecture diagram, agent rows
  - CONTRIBUTING.md -- cross-file update checklist
  - orchestration/SETUP.md -- paths, duplicate content
  - orchestration/GLOSSARY.md -- pre-push hook entry
  - orchestration/templates/SESSION_PLAN_TEMPLATE.md -- stale hardcoded values
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-H-input.jsonl -- input bead records
  - .beads/agent-summaries/_session-39adef65/audit/pass1-batch-H-output.json -- output verdicts (to create)
  - .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt -- cross-batch duplicate detection
- **Root cause**: 15 beads cover documentation issues across README, CONTRIBUTING, SETUP, GLOSSARY, MEMORY, and SESSION_PLAN_TEMPLATE. Known exact duplicates: 4 pairs.
- **Expected behavior**: Each bead gets a verdict. MEMORY.md beads account for it being a user-maintained file outside the repo.
- **Acceptance criteria**:
  1. Output file contains exactly 15 entries
  2. Output is valid JSON array
  3. Known duplicates (4 pairs) are marked DUPLICATE_SUSPECT
  4. Every ALREADY_FIXED verdict cites specific evidence
  5. MEMORY.md beads account for the fact that MEMORY.md is a user-maintained file outside the repo

## Scope Boundaries
Read ONLY:
- README.md (full file)
- CONTRIBUTING.md (full file)
- orchestration/SETUP.md (full file)
- orchestration/GLOSSARY.md (full file)
- orchestration/templates/SESSION_PLAN_TEMPLATE.md (full file)
- .beads/agent-summaries/_session-39adef65/audit/pass1-batch-H-input.jsonl (full file)
- .beads/agent-summaries/_session-39adef65/audit/all-bead-titles.txt (full file)

Do NOT edit:
- README.md
- CONTRIBUTING.md
- orchestration/SETUP.md
- orchestration/GLOSSARY.md
- orchestration/templates/SESSION_PLAN_TEMPLATE.md
- Any files outside the audit output directory

## Focus
Your task is ONLY to verify 15 beads against README, CONTRIBUTING, SETUP, GLOSSARY, and SESSION_PLAN_TEMPLATE docs and write verdicts to the output JSON file.
Do NOT fix adjacent issues you notice.
Do NOT modify the documentation files -- only produce verdicts about the beads.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
