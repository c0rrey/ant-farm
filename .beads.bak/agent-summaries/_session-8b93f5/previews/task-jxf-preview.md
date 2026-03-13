Execute task for ant-farm-jxf.

Step 0: Read your task context from .beads/agent-summaries/_session-8b93f5/prompts/task-jxf.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-jxf` + `bd update ant-farm-jxf --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-jxf)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-8b93f5/summaries/jxf.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-jxf`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-jxf
**Task**: AGG-025: Create canonical glossary for key terms
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8b93f5/summaries/jxf.md

## Context
- **Affected files**:
  - `README.md:L7` — uses "the Queen", "Dirt Pushers", "Pest Control" without formal definitions
  - `README.md:L11-26` — architecture diagram lists roles (Queen, Scout, Pantry, Pest Control, Dirt Pushers, Nitpickers, Big Head) without defining them
  - `README.md:L17-20` — uses acronyms CCO, WWD, DMVDC, CCB with only parenthetical expansions
  - `README.md:L46` — uses "wave" without defining boundaries
  - `README.md:L103-106` — expands WWD and DMVDC inline but definitions are not centralized
  - `README.md:L233-236` — Hard gates table uses CCO/WWD/DMVDC/CCB abbreviations
  - No `orchestration/GLOSSARY.md` exists currently (confirmed via glob search)
- **Root cause**: Key operational terms lack canonical definitions. "Wave" appears without defining boundaries. CCO/WWD/DMVDC/CCB are expanded differently across files. Ant metaphor names are never mapped to role descriptions in a single table.
- **Expected behavior**: A glossary document exists with definitions for all framework terms (wave, checkpoint, etc.), all checkpoint acronyms expanded, and all ant metaphor names mapped to role descriptions.
- **Acceptance criteria**:
  1. A glossary document exists with definitions for all framework terms (wave, checkpoint, etc.)
  2. All checkpoint acronyms (CCO, WWD, DMVDC, CCB) are expanded with one-line descriptions
  3. All ant metaphor names (Queen, Scout, Pantry, Dirt Pusher, etc.) map to role descriptions

## Scope Boundaries
Read ONLY:
- `README.md:L1-332` (full file, for term discovery)
- `orchestration/templates/checkpoints.md:L12-36` (for checkpoint acronym definitions)
- `orchestration/templates/reviews.md:L143-155` (for review type definitions)

Do NOT edit:
- `orchestration/templates/checkpoints.md` (reference only)
- `orchestration/templates/reviews.md` (reference only)
- `orchestration/RULES.md` (reference only)
- `CLAUDE.md` (off-limits per process rules)

## Focus
Your task is ONLY to create a canonical glossary document at `orchestration/GLOSSARY.md` with definitions for all framework terms, checkpoint acronyms, and ant metaphor role mappings.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
