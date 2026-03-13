Execute task for ant-farm-wi0.

Step 0: Read your task context from .beads/agent-summaries/_session-8b93f5/prompts/task-wi0.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-wi0` + `bd update ant-farm-wi0 --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-wi0)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-8b93f5/summaries/wi0.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-wi0`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-wi0
**Task**: AGG-022: Standardize variable naming across templates
**Agent Type**: refactoring-specialist
**Summary output path**: .beads/agent-summaries/_session-8b93f5/summaries/wi0.md

## Context
- **Affected files**:
  - `orchestration/templates/scout.md:L78` — uses `{task-id-suffix}` instead of canonical `{TASK_SUFFIX}`
  - `orchestration/templates/scout.md:L81` — uses `{full-task-id}` instead of canonical `{TASK_ID}` (or Tier 2 equivalent)
  - `orchestration/templates/scout.md:L254` — uses `{full-task-id}` in error example template
  - `orchestration/PLACEHOLDER_CONVENTIONS.md:L63` — lists deprecated `{task-id-suffix}` as a Tier 2 example; should be updated or reconciled with canonical naming
- **Root cause**: The same concepts use different variable names across files: `{task-id-suffix}` vs `{TASK_SUFFIX}`, `{full-task-id}` vs `{TASK_ID}`, and the terms "task ID" vs "bead ID" are used interchangeably. The PLACEHOLDER_CONVENTIONS.md glossary defines canonical Tier 1 names (`{TASK_ID}`, `{TASK_SUFFIX}`, `{SESSION_DIR}`) but scout.md still uses non-canonical Tier 2 synonyms for the same concepts in its output template format, creating confusion and drift.
- **Expected behavior**: All templates use canonical variable names: `{TASK_ID}` for full ID (Tier 1 contexts), `{TASK_SUFFIX}` for suffix (Tier 1 contexts). Within Tier 2 (agent-runtime) template blocks, the lowercase equivalents should be clearly mapped to their Tier 1 canonical names. A glossary section in PLACEHOLDER_CONVENTIONS.md defines each canonical variable. Deprecated variable names like `{task-id-suffix}` and `{full-task-id}` are removed or mapped.
- **Acceptance criteria**:
  1. All templates use the same variable name for each concept (no synonyms like `{task-id-suffix}` vs `{TASK_SUFFIX}` for the suffix concept, or `{full-task-id}` vs `{TASK_ID}` for the full ID concept)
  2. A glossary section defines each canonical variable name with its meaning (already partially exists in PLACEHOLDER_CONVENTIONS.md; ensure it is complete and covers all Tier 1 and Tier 2 canonical names)
  3. `grep` for deprecated variable names (`{task-id-suffix}`, `{full-task-id}`) across `orchestration/` (excluding `_archive/`) returns zero matches

## Scope Boundaries
Read ONLY:
- `orchestration/templates/scout.md` (full file, focus on L78, L81, L254)
- `orchestration/PLACEHOLDER_CONVENTIONS.md` (full file, focus on L63 and glossary sections)
- `orchestration/templates/pantry.md:L1-10` (term definitions block, for reference on canonical names)
- `orchestration/templates/dirt-pusher-skeleton.md:L8-16` (term definitions block, for reference)
- `orchestration/templates/checkpoints.md:L4-10` (term definitions block, for reference)
- `orchestration/templates/big-head-skeleton.md:L8-12` (term definitions block, for reference)

Do NOT edit:
- `orchestration/_archive/` (archived files are historical records)
- `orchestration/RULES.md` (no variable name issues found)
- `orchestration/templates/implementation.md` (uses angle-bracket syntax, not curly-brace placeholders)
- `orchestration/templates/reviews.md` (uses "standalone" as an English word, not as a variable name)
- `orchestration/templates/checkpoints.md` (already uses canonical names correctly)
- `orchestration/templates/pantry.md` (already uses canonical names correctly)
- `orchestration/templates/dirt-pusher-skeleton.md` (already uses canonical names correctly)
- `CLAUDE.md`, `CHANGELOG.md`, `README.md`

## Focus
Your task is ONLY to standardize variable naming across templates by replacing deprecated synonyms with canonical names and ensuring the glossary is complete.
Do NOT fix adjacent issues you notice.
Do NOT change the Tiered Placeholder Convention system itself -- only enforce it consistently.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
