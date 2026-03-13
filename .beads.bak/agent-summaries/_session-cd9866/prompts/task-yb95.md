# Task Brief: ant-farm-yb95
**Task**: Incomplete deprecation cleanup: pantry-review agent file, Section 2, and RULES.md table rows still structurally present
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/yb95.md

## Context
- **Affected files**: agents/pantry-review.md:L1-74 (deprecated agent file still present in agents/ directory), orchestration/templates/pantry.md:L251-557 (Section 2 still structurally present with deprecation notice but not cleaned up), orchestration/RULES.md:L251 and L265 (deprecated pantry-review table rows with strikethrough but still present)
- **Root cause**: Incomplete deprecation cleanup from the transition to fill-review-slots.sh. Three artifacts remain: (1) agents/pantry-review.md is the full deprecated agent file still synced to ~/.claude/agents/. (2) pantry.md Section 2 is marked deprecated but still contains ~300 lines of obsolete instructions. (3) RULES.md has two strikethrough table rows for pantry-review that should be removed entirely.
- **Expected behavior**: Deprecated artifacts fully removed or clearly marked as deprecated with minimal footprint. The pantry-review agent file should be deleted or moved to _archive/. Section 2 should be reduced to a minimal deprecation stub. RULES.md table rows should be removed.
- **Acceptance criteria**:
  1. pantry-review agent file (agents/pantry-review.md) removed or moved to orchestration/_archive/
  2. Section 2 of pantry.md cleaned up (reduced to minimal deprecation notice referencing fill-review-slots.sh, not 300+ lines of obsolete instructions)
  3. RULES.md deprecated table rows at L251 and L265 removed

## Scope Boundaries
Read ONLY: agents/pantry-review.md:L1-74, orchestration/templates/pantry.md:L249-557, orchestration/RULES.md:L245-270
Do NOT edit: orchestration/templates/implementation.md, orchestration/templates/reviews.md, orchestration/templates/checkpoints.md, any scripts/ files, README.md

## Focus
Your task is ONLY to clean up deprecated pantry-review artifacts from agents/, pantry.md Section 2, and RULES.md table rows.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
