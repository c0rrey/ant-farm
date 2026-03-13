Execute bug for ant-farm-w7p.

Step 0: Read your task context from .beads/agent-summaries/_session-ad3280/prompts/task-w7p.md
(Contains: affected files, root cause, acceptance criteria, scope boundaries.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-w7p` + `bd update ant-farm-w7p --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "fix: <description> (ant-farm-w7p)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-ad3280/summaries/w7p.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-w7p`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-w7p
**Task**: (BUG) Improve Scout agent type tie-breaking with deeper catalog reads and explicit fallback
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-ad3280/summaries/w7p.md

## Context
- **Affected files**:
  - `orchestration/templates/scout.md:L37-56` — Step 2.5 catalog build: add deep-read-on-tie logic (read full agent MD for tied candidates only)
  - `orchestration/templates/scout.md:L93-99` — Step 3 agent type selection criteria: update tie handling to use deeper reads before fallback
  - `orchestration/templates/scout.md:L116-126` — Step 5 strategy presentation: update format to show tied types as PICK ONE list
- **Root cause**: When the Scout cannot clearly differentiate between agent types for a task, it falls back to returning 'group' as the agent type -- an opaque label with no information about which types were tied or why. The Scout's agent catalog (`scout.md:L37-56`, Step 2.5) only reads YAML frontmatter -- one sentence of description per agent -- providing insufficient signal for 'description match' (selection criterion 3 at `scout.md:L98`), making ties more likely than necessary.
- **Expected behavior**: Two-pronged fix: (1) When selection criteria produce a tie, Scout reads full agent MD files for ONLY the tied candidates. If the tie persists after deeper reads, proceed to step 2. (2) When a tie cannot be broken, list all tied agent types in format: '{task-id}: {task-title} -- PICK ONE: [type-a | type-b]' instead of 'group'.
- **Acceptance criteria**:
  1. Scout reads full agent MD files for tied candidates (and only tied candidates) before falling back
  2. Unresolved ties surface in strategy as '{task-id}: {task-title} -- PICK ONE: [type-a | type-b]' instead of 'group'
  3. Each task with a tie lists its own candidates independently
  4. No increase in Scout context usage when there are no ties (frontmatter-only reads remain the default)

## Scope Boundaries
Read ONLY:
- `orchestration/templates/scout.md:L1-205` (full file, focus on Steps 2.5, 3, and 5)
- `~/.claude/agents/*.md` (frontmatter only, to understand agent catalog format)

Do NOT edit:
- `~/.claude/agents/*.md` (agent definitions are not in scope)
- `orchestration/templates/pantry.md` (unrelated)
- `orchestration/templates/reviews.md` (unrelated)
- `orchestration/templates/implementation.md` (unrelated)
- `orchestration/RULES.md` (unrelated)
- `orchestration/templates/checkpoints.md` (unrelated)

## Focus
Your task is ONLY to improve Scout agent type tie-breaking by adding deeper catalog reads on tie and explicit PICK ONE fallback format.
Do NOT fix adjacent issues you notice.
Do NOT change the Scout's task discovery logic (Steps 1-2).
Do NOT change the metadata file format (Step 3) except for agent type field on ties.
Do NOT change the briefing format (Step 6) except to reflect the PICK ONE format in strategy presentation.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
