Execute bug for ant-farm-yfnj.

Step 0: Read your task context from .beads/agent-summaries/_session-cd9866/prompts/task-yfnj.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-yfnj` + `bd update ant-farm-yfnj --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-yfnj)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-cd9866/summaries/yfnj.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-yfnj`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-yfnj
**Task**: pantry.md Section 2 circular reference fix incomplete: Big Head Step 0/0a and polling loop not inlined
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/yfnj.md

## Context
- **Affected files**: orchestration/templates/pantry.md:L251-557 (Section 2 review mode, Big Head consolidation brief composition)
- **Root cause**: pantry.md Section 2 still references external Big Head Step 0/0a and polling loop specifications from reviews.md instead of having them fully inlined. This creates a circular dependency where the Pantry must read reviews.md to compose the Big Head brief, which then tells Big Head to read the brief for the protocol. The Step 0/0a and polling loop content should be inlined directly in pantry.md Section 2 so the Pantry can compose self-contained Big Head briefs without circular references.
- **Expected behavior**: Big Head Step 0/0a prerequisite gate specification and polling loop are fully inlined in pantry.md Section 2, eliminating circular references. The Pantry can compose a complete Big Head consolidation brief without needing to cross-reference reviews.md for Step 0/0a content.
- **Acceptance criteria**:
  1. Big Head Step 0/0a prerequisite gate fully inlined in pantry.md Section 2 (or Section 1 Step 2.5 area, wherever Big Head brief is composed)
  2. Polling loop specification fully inlined with no external references to reviews.md for Step 0/0a
  3. No circular references remain between pantry.md and reviews.md for Big Head Step 0/0a content

## Scope Boundaries
Read ONLY: orchestration/templates/pantry.md:L1-557, orchestration/templates/reviews.md:L455-590 (Step 0/0a source content)
Do NOT edit: orchestration/templates/reviews.md, orchestration/templates/big-head-skeleton.md, orchestration/RULES.md, any scripts/ files

## Focus
Your task is ONLY to inline Big Head Step 0/0a and polling loop specifications into pantry.md, eliminating circular references.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
