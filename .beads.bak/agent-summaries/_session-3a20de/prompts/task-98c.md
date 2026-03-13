# Task Brief: ant-farm-98c
**Task**: RULES.md retry counter interaction between per-checkpoint and session-total limits is unspecified
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/98c.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L269-278 -- Retry Limits table, specifically the Checkpoint C row and session total row
- **Root cause**: The retry limits table says Checkpoint C failures allow 1 retry, and a session total of 5 retries. But it does not specify whether a Checkpoint C re-run counts toward the session total. The interaction between per-checkpoint limits and the global session cap is ambiguous.
- **Expected behavior**: Retry table explicitly states how per-checkpoint retries interact with the session total.
- **Acceptance criteria**:
  1. Retry table explicitly states: Each Checkpoint C re-run counts as 1 toward both the per-checkpoint limit (1) and the session total (5)

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L269-278 (Retry Limits section)
Do NOT edit: Workflow section (L53-150), Hard Gates (L152-162), Session Directory (L216-234), any other section

## Focus
Your task is ONLY to clarify the retry counter interaction in the Retry Limits table.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
