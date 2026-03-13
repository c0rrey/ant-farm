# Task Brief: ant-farm-5q3
**Task**: AGG-039: Add complete error recovery procedures
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/5q3.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L269-278 — Retry limits table; currently has 4 rows (Agent fails DMVDC, CCB fails, Agent stuck, Total retries per session) but omits Pantry and Scout entirely
- **Root cause**: The retry limits table at RULES.md:L269-278 omits Pantry and Scout entirely. No retry path exists for Pantry CCO failures. Stuck-agent escalation at L275 lacks diagnostic steps (just says "Check status; escalate to user"). No wave-level failure threshold exists to handle scenarios where multiple agents in a wave fail simultaneously.
- **Expected behavior**: Pantry/Scout added to retry table (1 retry, then escalate). Stuck-agent diagnostic procedure documented with step-by-step instructions. Wave failure threshold defined (>50% agent failures in a wave triggers pause and user notification).
- **Acceptance criteria**:
  1. RULES.md retry limits table includes entries for Pantry and Scout with retry counts
  2. A step-by-step stuck-agent diagnostic procedure is documented
  3. A wave-level failure threshold (>50%) triggers pause and user notification

## Scope Boundaries
Read ONLY:
- orchestration/RULES.md:L269-296 (Retry Limits section and Context Preservation Targets)
- orchestration/RULES.md:L152-161 (Hard Gates table — for understanding retry/gate relationship)
- orchestration/RULES.md:L205-213 (Concurrency Rules — for understanding wave structure)

Do NOT edit:
- orchestration/RULES.md:L1-268 (everything above Retry Limits section)
- orchestration/RULES.md:L289-296 (Priority Calibration and Context Preservation Targets sections — content only; if new sections are added between Retry Limits and Priority Calibration, that is within scope)
- Any file other than orchestration/RULES.md
- CLAUDE.md, CHANGELOG, README

## Focus
Your task is ONLY to add error recovery procedures: expand the retry limits table with Pantry/Scout entries, document a stuck-agent diagnostic procedure, and define a wave-level failure threshold.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
