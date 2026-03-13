Execute bug for ant-farm-32gz.

Step 0: Read your task context from .beads/agent-summaries/_session-cd9866/prompts/task-32gz.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-32gz` + `bd update ant-farm-32gz --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-32gz)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-cd9866/summaries/32gz.md with all required sections
   (see task brief for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-32gz`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-32gz
**Task**: SESSION_ID collision: same-second Queens produce identical session directory
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-cd9866/summaries/32gz.md

## Context
- **Affected files**: orchestration/RULES.md:L290-291 (SESSION_ID generation uses `echo "$$-$(date +%s%N)" | shasum | head -c 8` which can collide if two Queens start in the same second with the same PID namespace), orchestration/PLACEHOLDER_CONVENTIONS.md:L89-91 (documents SESSION_ID generation pattern, needs update if generation changes)
- **Root cause**: SESSION_ID generation at RULES.md:L290 uses `echo "$$-$(date +%s%N)" | shasum | head -c 8`. The `$$` (PID) and `date +%s%N` (epoch nanoseconds) should provide uniqueness, but: (1) on macOS, `date +%s%N` may not support nanoseconds (BSD date returns literal 'N'), reducing to second-level granularity. (2) Two Queens started in the same second on macOS would get `PID-epochN` where %N is literal 'N', and if PIDs happen to collide (unlikely but possible in containers), session directories collide. (3) The 8-char hash truncation further increases collision probability.
- **Expected behavior**: SESSION_ID is unique even when multiple Queens start in the same second, on both Linux and macOS.
- **Acceptance criteria**:
  1. SESSION_ID generation includes enough entropy to avoid collisions even with same-second launches (e.g., add random component via $RANDOM, /dev/urandom, or uuidgen)
  2. Same-second Queens produce different session directories on both macOS and Linux

## Scope Boundaries
Read ONLY: orchestration/RULES.md:L286-295, orchestration/PLACEHOLDER_CONVENTIONS.md:L84-92
Do NOT edit: orchestration/templates/pantry.md, orchestration/templates/implementation.md, orchestration/templates/reviews.md, any scripts/ files, agents/ files

## Focus
Your task is ONLY to fix SESSION_ID generation to avoid collisions with same-second Queens.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
