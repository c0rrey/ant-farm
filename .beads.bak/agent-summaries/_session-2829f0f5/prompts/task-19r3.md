# Task Brief: ant-farm-19r3
**Task**: fix: SESSION_PLAN_TEMPLATE.md uses stale Boss-Bot term and Claude Sonnet 4.5 model
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2829f0f5/summaries/19r3.md

## Context
- **Affected files**:
  - orchestration/templates/SESSION_PLAN_TEMPLATE.md:L8 -- "Boss-Bot: Claude Sonnet 4.5"
  - orchestration/templates/SESSION_PLAN_TEMPLATE.md:L340 -- "Implementation files read in boss-bot window"
  - orchestration/templates/SESSION_PLAN_TEMPLATE.md:L342 -- "Boss-bot stayed focused"
- **Root cause**: SESSION_PLAN_TEMPLATE.md uses outdated "Boss-Bot" terminology (should be "Queen") and stale "Claude Sonnet 4.5" model name (Queen runs on opus).
- **Expected behavior**: No "Boss-Bot" or "boss-bot" references in active templates. Model reference updated to current tier.
- **Acceptance criteria**:
  1. No "Boss-Bot" or "boss-bot" references in active templates
  2. Model reference updated to current tier

## Scope Boundaries
Read ONLY: orchestration/templates/SESSION_PLAN_TEMPLATE.md:L1-15, L335-350
Do NOT edit: Any file other than orchestration/templates/SESSION_PLAN_TEMPLATE.md. Do not restructure the template layout.

## Focus
Your task is ONLY to replace Boss-Bot references with Queen and update the model name in SESSION_PLAN_TEMPLATE.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
