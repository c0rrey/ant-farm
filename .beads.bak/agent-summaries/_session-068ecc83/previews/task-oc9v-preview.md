Execute bug for ant-farm-oc9v.

Step 0: Read your task context from .beads/agent-summaries/_session-068ecc83/prompts/task-oc9v.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-oc9v` + `bd update ant-farm-oc9v --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-oc9v)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-068ecc83/summaries/oc9v.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-oc9v`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

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
