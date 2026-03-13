Execute task for ant-farm-957.

Step 0: Read your task context from .beads/agent-summaries/_session-3a20de/prompts/task-957.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-957` + `bd update ant-farm-957 --status=in_progress`
2. **Design** (MANDATORY) — 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY) — Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-957)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY) — Write to .beads/agent-summaries/_session-3a20de/summaries/957.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-957`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-957
**Task**: AGG-041: Clarify Agent type: code-reviewer role in checkpoints.md
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-3a20de/summaries/957.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L12-14 -- Pest Control Overview (where the orchestrator vs executor distinction should be stated)
  - orchestration/templates/checkpoints.md:L103 -- CCO Dirt Pushers Agent type field
  - orchestration/templates/checkpoints.md:L169 -- CCO Nitpickers Agent type field
  - orchestration/templates/checkpoints.md:L239 -- WWD Agent type field
  - orchestration/templates/checkpoints.md:L312 -- DMVDC Dirt Pushers Agent type field
  - orchestration/templates/checkpoints.md:L386 -- DMVDC Nitpickers Agent type field
  - orchestration/templates/checkpoints.md:L461 -- CCB Agent type field
  - NOTE: Scout metadata had bare filename (no line numbers). Lines identified by Pantry via grep.
- **Root cause**: Each checkpoint section says Agent type: code-reviewer but checkpoints are executed by Pest Control. A cold Pest Control agent cannot tell whether it should BE code-reviewer or SPAWN code-reviewer subagents.
- **Expected behavior**: Clarified: Pest Control orchestrates and code-reviewer executes. The distinction is stated once at the top and referenced throughout.
- **Acceptance criteria**:
  1. checkpoints.md explicitly states Pest Control orchestrates and code-reviewer executes
  2. The Agent type field is annotated with "spawned agent type" to prevent misinterpretation
  3. The Pest Control vs code-reviewer distinction is stated once at the top and referenced throughout

## Scope Boundaries
Read ONLY: orchestration/templates/checkpoints.md:L1-40 (header and Pest Control Overview), L97-169 (CCO sections), L235-240 (WWD header), L306-320 (DMVDC header), L382-390 (DMVDC Nitpickers header), L457-465 (CCB header)
Do NOT edit: The internal verification steps/checks within each checkpoint template block, the Verdict Thresholds Summary (L44-94)

## Focus
Your task is ONLY to clarify the Pest Control vs code-reviewer role distinction in Agent type annotations.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
