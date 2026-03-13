# Task Brief: ant-farm-3mk
**Task**: AGG-019: Add fallback path for TeamCreate unavailability in reviews.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8ae30b/summaries/3mk.md

## Context
- **Affected files**:
  - `~/.claude/orchestration/templates/reviews.md:L33-35` — mandates TeamCreate with no fallback ("Reviews MUST use Agent Teams (TeamCreate + SendMessage), NOT plain Task tool subagents")
- **Root cause**: reviews.md mandates TeamCreate for the Nitpicker review workflow (L33 and L35) but does not specify what to do if the runtime environment cannot create teams or messaging fails. Claude Code supports only one TeamCreate per session (documented in MEMORY.md), so if the slot is already used or the environment does not support teams, the review workflow has no graceful degradation path.
- **Expected behavior**: reviews.md contains an explicit fallback section for when TeamCreate is unavailable, using individual Task agents with file-based coordination.
- **Acceptance criteria**:
  1. reviews.md contains an explicit fallback section for when TeamCreate is unavailable
  2. The fallback uses individual Task agents with file-based coordination
  3. Both the team path and fallback path produce the same output artifacts (4 review reports)

## Scope Boundaries
Read ONLY:
- `~/.claude/orchestration/templates/reviews.md` (focus on L30-72 Agent Teams Protocol section)

Do NOT edit:
- reviews.md Transition Gate Checklist (L1-28)
- reviews.md Review 1-4 definitions (L86-243) — these define content, not delivery mechanism
- reviews.md Nitpicker Report Format (L245-318)
- reviews.md Big Head Consolidation Protocol (L320-469)
- reviews.md After Consolidation Complete (L471-533)
- Any files other than reviews.md

## Focus
Your task is ONLY to add a fallback path in reviews.md for when TeamCreate is unavailable, ensuring the same 4 review reports are produced via individual Task agents with file-based coordination.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
