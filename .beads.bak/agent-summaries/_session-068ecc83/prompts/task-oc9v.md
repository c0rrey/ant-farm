# Task Brief: ant-farm-oc9v
**Task**: Incomplete pantry-review deprecation across docs and agent configs
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-068ecc83/summaries/oc9v.md

## Context
- **Affected files**:
  - orchestration/RULES.md:L182-183 -- duplicated deprecated row with inconsistent wording
  - orchestration/templates/scout.md:L61 -- stale pantry-review in exclusion list
  - orchestration/GLOSSARY.md:L28,L81 -- references pantry-review.md as live
  - README.md:L275 -- lists pantry-review as active agent
- **Root cause**: The deprecation of pantry-review was applied to RULES.md and pantry.md but not propagated to all downstream references. Multiple files still reference pantry-review as if it were a live agent type. Found by: Clarity (P3 - F5), Edge Cases (P3 - F10), Excellence (P3 - F6, F7). 4 findings across 3 reviewers, all P3. Same root cause: incomplete deprecation rollout.
- **Expected behavior**: No file references pantry-review without a deprecation marker. All references should either be removed or clearly marked as deprecated.
- **Acceptance criteria**:
  1. No file references pantry-review without a deprecation marker
  2. GLOSSARY.md:L28 and L81 updated to remove or mark deprecated pantry-review references
  3. scout.md:L61 exclusion list cleaned up (remove stale pantry-review entry or mark deprecated)
  4. RULES.md:L182-183 deprecated row wording unified (remove duplication)

## Scope Boundaries
Read ONLY:
- orchestration/RULES.md:L175-195
- orchestration/templates/scout.md:L55-70
- orchestration/GLOSSARY.md:L23-37 and L76-85
- README.md:L270-280

Do NOT edit:
- Any file outside the 4 listed above
- orchestration/templates/reviews.md (managed by ant-farm-6jxn)
- orchestration/templates/pantry.md (managed by ant-farm-6jxn)
- orchestration/_archive/pantry-review.md (managed by ant-farm-6jxn)
- scripts/ directory (managed by ant-farm-n0or)

## Focus
Your task is ONLY to clean up 4 files that still reference pantry-review without proper deprecation markers, ensuring consistent deprecation language across RULES.md, scout.md, GLOSSARY.md, and README.md.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
