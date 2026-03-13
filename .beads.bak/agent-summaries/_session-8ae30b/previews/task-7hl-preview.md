Execute task for ant-farm-7hl.

Step 0: Read your task context from .beads/agent-summaries/_session-8ae30b/prompts/task-7hl.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-7hl` + `bd update ant-farm-7hl --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-7hl)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-8ae30b/summaries/7hl.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-7hl`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-7hl
**Task**: AGG-018: Align landing instructions between CLAUDE.md and AGENTS.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8ae30b/summaries/7hl.md

## Context
- **Affected files**:
  - `~/.claude/CLAUDE.md:L50-79` — Landing the Plane section includes Review-findings gate (Step 3) and 8 steps total
  - `/Users/correy/projects/ant-farm/AGENTS.md:L15-40` — Landing the Plane section omits the review-findings gate and has only 7 steps
- **Root cause**: CLAUDE.md includes a Review-findings gate as Step 3 (L60: "If reviews ran and found P1 issues, present findings to user before proceeding") and has 8 landing steps. AGENTS.md omits this review gate entirely and has only 7 steps (going directly from "Run quality gates" to "Update issue status"). An agent following AGENTS.md could skip the mandatory review gate, allowing P1 blockers to be pushed without user disclosure.
- **Expected behavior**: Both CLAUDE.md and AGENTS.md reference the same landing procedure steps with no contradictions in step sequence.
- **Acceptance criteria**:
  1. Both CLAUDE.md and AGENTS.md reference the same landing procedure steps
  2. The review-findings gate is present or cross-referenced in both files
  3. diff of landing sections between files shows no contradictions in step sequence

## Scope Boundaries
Read ONLY:
- `~/.claude/CLAUDE.md` (focus on L50-79, Landing the Plane section)
- `/Users/correy/projects/ant-farm/AGENTS.md` (focus on L15-40, Landing the Plane section)

Do NOT edit:
- CLAUDE.md sections above Landing the Plane (Prompt Engineering Mode, Parallel Work Mode)
- CLAUDE.md Critical Rules subsection (L74-78) unless step numbering changes require it
- AGENTS.md Quick Reference section (L1-13)
- Any files other than CLAUDE.md and AGENTS.md

## Focus
Your task is ONLY to align the landing instructions between CLAUDE.md and AGENTS.md so both files have the same steps in the same sequence, including the review-findings gate.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
