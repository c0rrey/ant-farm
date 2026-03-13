# Task Brief: ant-farm-kwp
**Task**: SETUP.md test checklist says Queen runs bd show, contradicts Information Diet
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-7edaafbb/summaries/kwp.md

## Context
- **Affected files**: orchestration/SETUP.md:L69-83 -- Step 4 "Test it" checklist instructs Queen to run bd show
- **Root cause**: SETUP.md test checklist (L69-83) instructs the Queen to run bd show (comment on L78: "Spawns the Scout, which runs bd show"), but the Information Diet rule in CLAUDE.md prohibits the Queen from running bd show (the Scout subagent handles this). The numbered list at L77-83 describes the Queen's expected behavior, and item 1 mentions "Spawns the Scout, which runs bd show" -- this is actually correct (Scout does it), but the test setup at L72 says "Start session" without clarifying that the Queen delegates. Review the full test checklist to ensure no instruction tells the Queen to run bd show directly.
- **Expected behavior**: SETUP.md should not instruct the Queen to run bd show. Test checklist should reference Scout subagent behavior instead.
- **Acceptance criteria**:
  1. SETUP.md test checklist no longer instructs Queen to run bd show
  2. Checklist is consistent with Information Diet constraints in CLAUDE.md

## Scope Boundaries
Read ONLY: orchestration/SETUP.md:L1-269 (full file, focus on L69-83 test checklist); CLAUDE.md:L1-50 (Information Diet reference)
Do NOT edit: orchestration/RULES.md, orchestration/templates/, scripts/, CLAUDE.md

## Focus
Your task is ONLY to fix the test checklist in SETUP.md to be consistent with Information Diet rules.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
