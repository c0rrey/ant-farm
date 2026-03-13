# Task Brief: ant-farm-wiq
**Task**: Checkpoints CCO FAIL verdict format has no example
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/wiq.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L107-118 -- CCO Verdict Thresholds section (PASS/WARN/FAIL definitions)
  - orchestration/templates/checkpoints.md:L151-154 -- CCO verdict section inside the template block
  - NOTE: Scout metadata had bare filename (no line numbers). Lines identified by Pantry via grep.
- **Root cause**: checkpoints.md shows PASS verdict format but no example of a FAIL verdict with specific check failures listed. A fresh Pest Control agent might format FAIL output incorrectly.
- **Expected behavior**: FAIL example showing check number, name, and evidence added to CCO section.
- **Acceptance criteria**:
  1. CCO section includes a FAIL verdict example with check number, name, and evidence

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md:L97-163 (CCO Dirt Pushers section, including verdict thresholds and template block)
Do NOT edit: CCO Nitpickers section (L165-225), WWD section (L235-303), DMVDC section (L306-454), CCB section (L457-572), Verdict Thresholds Summary (L44-94)

## Focus
Your task is ONLY to add a FAIL verdict example to the CCO section showing check number, name, and evidence.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
