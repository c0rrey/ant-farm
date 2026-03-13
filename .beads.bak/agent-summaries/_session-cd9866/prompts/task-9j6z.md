# Task Brief: ant-farm-9j6z
**Task**: Filename typo: review-clarify.md should be review-clarity.md in fallback workflow
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/9j6z.md

## Context
- **Affected files**: Unknown -- the Scout metadata reports this typo "review-clarify" should be "review-clarity" in a fallback workflow, but grep found no remaining instances of "review-clarify" in the current codebase outside the bead/issue itself. The typo may have already been fixed in a prior commit.
- **Root cause**: The bead reports a filename typo where "review-clarify.md" was used instead of "review-clarity.md" in a fallback workflow. However, codebase grep shows no current instances of "review-clarify" outside the issue definition in .beads/issues.jsonl. The agent must: (1) Search comprehensively for any remaining "review-clarify" references (including git history). (2) If no instances are found, confirm the fix is already complete and close the task with documentation. (3) If instances are found, fix them.
- **Expected behavior**: All references use the correct filename "review-clarity.md" with no "review-clarify" typos remaining.
- **Acceptance criteria**:
  1. No "review-clarify" typos remain in the codebase (excluding .beads/issues.jsonl which is the issue tracking file)
  2. Fallback workflow references correct filename "review-clarity.md" (if applicable)

## Scope Boundaries
Read ONLY: Full codebase search for "review-clarify" pattern (grep -r), agents/pantry-review.md:L1-74 (fallback agent, likely location), orchestration/templates/pantry.md:L251-557 (Section 2 deprecated content)
Do NOT edit: .beads/issues.jsonl, orchestration/templates/reviews.md (unless typo found there), orchestration/RULES.md (unless typo found there)

## Focus
Your task is ONLY to find and fix any remaining "review-clarify" filename typos in the codebase.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
