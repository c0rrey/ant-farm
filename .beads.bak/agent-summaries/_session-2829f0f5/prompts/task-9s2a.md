# Task Brief: ant-farm-9s2a
**Task**: fix: dummy reviewer prompt created but output report never materializes
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-2829f0f5/summaries/9s2a.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L186-219 -- dummy reviewer step documentation
- **Root cause**: RULES.md describes spawning a dummy reviewer that writes to review-reports/dummy-review-${TIMESTAMP}.md but actual sessions show the prompt file exists with no corresponding output. The dummy reviewer output is documented as "discarded" so absence does not affect workflow, but the instrumentation goal is silently not achieved.
- **Expected behavior**: RULES.md documents expected dummy reviewer behavior (output may not appear) or, if sunset, removes the step entirely.
- **Acceptance criteria**:
  1. RULES.md documents expected dummy reviewer behavior (output may not appear)
  2. If dummy reviewer is sunset, remove the step entirely

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L180-230
Do NOT edit: Any file other than orchestration/RULES.md. Do not change the review pipeline logic or any other steps.

## Focus
Your task is ONLY to clarify or remove the dummy reviewer step documentation in RULES.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
