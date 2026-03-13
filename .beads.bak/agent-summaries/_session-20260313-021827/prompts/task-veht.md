# Task Brief: ant-farm-veht
**Task**: Add TDV checkpoint definition to checkpoints.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-20260313-021827/summaries/veht.md

## Context
- **Affected files**: orchestration/templates/checkpoints.md (entire file; new section to be appended after existing checkpoint definitions ending at ~L870)
- **Root cause**: TDV (Trail Decomposition Verification) checkpoint needs to be added alongside existing checkpoints (SSV, CCO, WWD, DMVDC, CCB, ESV) for the decomposition workflow. The checkpoint is currently missing from checkpoints.md.
- **Expected behavior**: TDV checkpoint added with 5 structural checks, 3 heuristic warnings, verdict definitions, and retry logic.
- **Acceptance criteria**:
  1. TDV checkpoint added to checkpoints.md with same format as existing checkpoints
  2. All 5 structural checks documented with pass/fail criteria
  3. 3 heuristic warnings documented as warnings (not blockers)
  4. Verdict definitions: TDV PASS -> handoff, TDV FAIL -> Architect retry with gap list
  5. Max 2 retries documented with escalation to user after limit
  6. Provisional wave computation algorithm documented (for scope coherence check)
  7. TDV property table included: name, run by, model, when, blocks, max retries, checks

## Scope Boundaries
Read ONLY:
- orchestration/templates/checkpoints.md:L1-870 (full file, to understand existing checkpoint format and structure)
- Specifically study these existing checkpoints for format reference:
  - SSV checkpoint: orchestration/templates/checkpoints.md:L647-755
  - CCO checkpoint: orchestration/templates/checkpoints.md:L117-275
  - ESV checkpoint: orchestration/templates/checkpoints.md:L757-870

Do NOT edit:
- Any existing checkpoint definitions (SSV, CCO, WWD, DMVDC, CCB, ESV sections)
- orchestration/templates/checkpoints.md:L1-870 (existing content must remain unchanged)
- Any files outside orchestration/templates/checkpoints.md

## Focus
Your task is ONLY to add the TDV checkpoint definition to checkpoints.md.
Do NOT fix adjacent issues you notice.
Do NOT modify existing checkpoint definitions.
Append the new TDV section after the existing content, following the same structural patterns used by SSV, CCO, and ESV.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
