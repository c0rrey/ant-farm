Execute task for ant-farm-8jg.

Step 0: Read your task context from .beads/agent-summaries/_session-8b93f5/prompts/task-8jg.md
(Format: markdown. Sections: Context, Scope Boundaries, Focus.)

Execute these 6 steps in order:

1. **Claim**: `bd show ant-farm-8jg` + `bd update ant-farm-8jg --status=in_progress`
2. **Design** (MANDATORY): 4+ genuinely distinct approaches with tradeoffs. Document choice before coding.
3. **Implement**: Write clean, minimal code satisfying acceptance criteria.
4. **Review** (MANDATORY): Re-read EVERY changed file. Verify acceptance criteria. Assumptions audit.
5. **Commit**: `git pull --rebase && git add <changed-files> && git commit -m "<type>: <description> (ant-farm-8jg)"`
   Use conventional commit type (fix/feat/refactor/etc). Record commit hash in summary doc.
6. **Summary doc** (MANDATORY): Write to .beads/agent-summaries/_session-8b93f5/summaries/8jg.md with all required sections
   (see data file for section list). Only after the summary doc is successfully written:
   `bd close ant-farm-8jg`

SCOPE: Only edit files listed in the task context. Document adjacent issues, don't fix them.
Do NOT push to remote. Do NOT modify CHANGELOG/README/CLAUDE.md.

---

# Task Brief: ant-farm-8jg
**Task**: AGG-026: Standardize agent name casing and article usage
**Agent Type**: refactoring-specialist
**Summary output path**: .beads/agent-summaries/_session-8b93f5/summaries/8jg.md

## Context
- **Affected files**:
  - `orchestration/RULES.md:L16,L21,L25,L31,L37,L51,L60,L70-71,L74,L91,L98,L100-101,L103-106,L109,L113,L140,L146,L148,L167,L175-177,L205,L210-212,L214,L223-224,L226,L228,L230,L242,L257` — Prose references to agent names with mixed casing (the Queen / The Queen, the Pantry, the Scout, Big Head, Nitpickers)
  - `README.md:L7,L11,L25,L39,L47,L49,L53,L56,L61,L90,L103,L108,L129,L133,L141,L150,L154,L156,L165,L223,L225,L319,L321,L323-330` — Prose references and architecture diagram with agent names
  - `orchestration/templates/dirt-pusher-skeleton.md:L3,L14,L17,L19-20` — "Instructions for The Queen" header and prose
  - `orchestration/templates/nitpicker-skeleton.md:L3,L10-11,L41` — "Instructions for The Queen" header, Pantry/Big Head references
  - `orchestration/templates/big-head-skeleton.md:L3,L5-6,L19-20,L23-24,L26,L42,L56-59,L97-98` — "Instructions for The Queen" header and Big Head/Pantry references
  - `orchestration/templates/scout.md:L1,L3-4,L40,L114,L233,L259,L262` — "# The Scout" header and prose references
  - `orchestration/templates/checkpoints.md:L1,L36,L38,L40,L115,L165,L202,L227,L285,L440,L473,L564` — "The Queen" and "The Nitpickers" references
  - `orchestration/templates/reviews.md:L1,L12,L21,L53,L75,L96,L112,L148,L179,L213,L253,L299,L317,L454,L459,L464,L529,L708,L744-745` — Mixed "The Queen" / "the Queen" and agent name references
  - `orchestration/templates/implementation.md:L1,L66,L116,L152,L162,L192,L197,L257` — "The Queen" references
  - `orchestration/templates/pantry.md:L1,L87-88,L315` — "# The Pantry" header and agent references
  - `orchestration/templates/queen-state.md:L1,L8,L18` — "The Queen's Session State", "The Scout", "The Pantry" headers
- **Root cause**: Agent names are capitalized and articled inconsistently across the codebase: "the Queen" / "Queen" / "The Queen", "the Nitpickers" / "Nitpicker team", "Big Head" (always title case). Filenames use kebab-case while prose mixes forms. No documented convention exists.
- **Expected behavior**: Standardized convention: lowercase article in prose ("the Queen", "the Scout"), title case for role names, kebab-case in filenames. Convention documented in the glossary (which ant-farm-jxf creates).
- **Acceptance criteria**:
  1. All prose references use consistent article/casing pattern (e.g., "the Queen" not "The Queen" mid-sentence)
  2. All filenames use kebab-case for agent names
  3. The naming convention is documented in the glossary

## Scope Boundaries
Read ONLY:
- `orchestration/RULES.md` (full file, 260 lines)
- `README.md` (full file, 332 lines)
- `orchestration/templates/dirt-pusher-skeleton.md` (full file, 46 lines)
- `orchestration/templates/nitpicker-skeleton.md` (full file, ~45 lines)
- `orchestration/templates/big-head-skeleton.md` (full file, ~100 lines)
- `orchestration/templates/scout.md` (full file)
- `orchestration/templates/checkpoints.md` (full file)
- `orchestration/templates/reviews.md` (full file)
- `orchestration/templates/implementation.md` (full file)
- `orchestration/templates/pantry.md` (full file)
- `orchestration/templates/queen-state.md` (full file)
- `orchestration/GLOSSARY.md` (if it exists — created by ant-farm-jxf dependency)

Do NOT edit:
- `agents/*.md` (agent definition files — different from templates)
- `orchestration/reference/*.md` (reference docs not in scope)
- `orchestration/SETUP.md`
- `.beads/` directory contents
- Any source code, tests, or config files outside orchestration/

## Focus
Your task is ONLY to standardize agent name casing and article usage across all orchestration template files and documentation.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
