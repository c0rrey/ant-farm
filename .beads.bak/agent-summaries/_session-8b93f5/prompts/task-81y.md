# Task Brief: ant-farm-81y
**Task**: AGG-029: Add inline acronym expansions to architecture diagram
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8b93f5/summaries/81y.md

## Context
- **Affected files**:
  - `README.md:L9-27` — Architecture diagram section where CCO (L17), WWD (L18), DMVDC (L19), and CCB (L20-21) appear as unexpanded acronyms. First expansions currently appear much later: CCO at L61, WWD at L105, DMVDC at L106, CCB at L165.
- **Root cause**: The README architecture diagram uses CCO, WWD, DMVDC, and CCB without inline expansions. Full names appear much later in the document (38-145 lines after first use). First-time readers encounter unexpanded acronyms with no context.
- **Expected behavior**: One-line expansions immediately under the diagram (e.g., CCO = Colony Cartography Office, WWD = Wandering Worker Detection, DMVDC = Dirt Moved vs Dirt Claimed, CCB = Colony Census Bureau) so readers never need to hunt for definitions.
- **Acceptance criteria**:
  1. The README architecture diagram section includes inline acronym expansions
  2. All four acronyms (CCO, WWD, DMVDC, CCB) are expanded within 5 lines of first use
  3. Expansions appear before the detailed description sections later in the document

## Scope Boundaries
Read ONLY:
- `README.md:L1-70` (architecture diagram section and immediately following text)

Do NOT edit:
- `README.md` sections after L70 (workflow descriptions, hard gates table, etc.)
- `orchestration/` directory (any file)
- `agents/` directory (any file)
- `CLAUDE.md`
- `.beads/` directory contents

## Focus
Your task is ONLY to add inline acronym expansions near the architecture diagram in README.md (around L27-28, immediately after the diagram's closing code fence).
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
