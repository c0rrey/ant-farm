# Task Brief: ant-farm-7qp
**Task**: AGG-010: Resolve timestamp ownership conflict between Queen and Pantry
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8ae30b/summaries/7qp.md

## Context
- **Affected files**:
  - `~/.claude/orchestration/templates/pantry.md:L106,L115` — says "use the Queen's timestamp" (Section 2 input spec and Step 2)
  - `~/.claude/agents/pantry-review.md:L38-40` — says "Generate ONE timestamp" (contradicts pantry.md)
  - `~/.claude/orchestration/templates/reviews.md:L247` — says "The Queen generates the timestamp once per review cycle"
  - `~/.claude/orchestration/RULES.md:L48-62` — Step 3b does not instruct the Queen to generate a timestamp before spawning Pantry
- **Root cause**: Three files give contradictory instructions about who generates the review timestamp. pantry.md says use the Queen's timestamp, pantry-review.md says generate one, reviews.md says the Queen generates it, but RULES.md Step 3b does not instruct the Queen to do so. The result is undefined behavior: whoever runs first "wins" the timestamp.
- **Expected behavior**: Exactly one file contains the timestamp generation instruction; all others reference it. The chosen owner's workflow step explicitly includes when and how to generate the timestamp.
- **Acceptance criteria**:
  1. Exactly one file contains the timestamp generation instruction; all others reference it
  2. grep for timestamp generation across pantry.md, pantry-review.md, reviews.md, RULES.md shows consistent ownership
  3. The chosen owner's workflow step explicitly includes when and how to generate the timestamp

## Scope Boundaries
Read ONLY:
- `~/.claude/orchestration/templates/pantry.md` (full file, focus on L106-115 and Section 2 header)
- `~/.claude/agents/pantry-review.md` (full file, focus on L38-40)
- `~/.claude/orchestration/templates/reviews.md` (focus on L247 and surrounding context)
- `~/.claude/orchestration/RULES.md` (focus on L48-62 Step 3b)

Do NOT edit:
- Any files outside the 4 listed above
- pantry.md Section 1 (Implementation Mode)
- reviews.md review type definitions (Reviews 1-4)
- RULES.md Steps 0, 1, 2, 3, 4-6

## Focus
Your task is ONLY to resolve the timestamp ownership conflict by designating exactly one file as the source of truth for timestamp generation and making all other files reference it consistently.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
