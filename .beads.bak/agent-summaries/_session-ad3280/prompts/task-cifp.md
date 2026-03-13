# Task Brief: ant-farm-cifp
**Task**: Add explicit scope fencing to Nitpicker agent definitions per review type
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-ad3280/summaries/cifp.md

## Context
- **Affected files**:
  - `~/.claude/agents/nitpicker.md:L1-25` — Add per-type specialization blocks with scope fences, heuristics, and severity calibration
  - `orchestration/templates/reviews.md:L86-243` — May need to reference new scope boundaries for consistency (Review 1-4 sections)
  - `orchestration/templates/pantry.md:L119-135` — Review data files section; may need a REVIEW_TYPE marker if using conditional blocks
- **Root cause**: All four Nitpicker reviewers (clarity, edge-cases, correctness, excellence) share a single agent MD file (`~/.claude/agents/nitpicker.md:L1-25`) with no review-type-specific identity. Differentiation comes entirely from the Pantry-composed data files. Each reviewer has no baked-in understanding of what is NOT its responsibility, leading to duplicate findings across reviewers that Big Head must deduplicate after the fact.
- **Expected behavior**: Add per-review-type specialization blocks to the Nitpicker agent definition(s). For each review type, define explicit 'NOT your responsibility' list referencing other three review types, type-specific heuristics, and type-specific severity calibration. Option (b) — single agent MD file with conditional sections keyed to a REVIEW_TYPE variable — is preferred for maintainability.
- **Acceptance criteria**:
  1. Each Nitpicker reviewer has explicit 'not my job' boundaries that reference the other three review types by name
  2. Type-specific severity calibration is defined (what constitutes P1/P2/P3 for each type)
  3. Big Head deduplication load is reduced — fewer cross-type duplicate findings at source
  4. Shared concerns (report format, output structure, messaging guidelines) remain in one place, not duplicated across 4 files

## Scope Boundaries
Read ONLY:
- `~/.claude/agents/nitpicker.md:L1-25` (current agent definition)
- `orchestration/templates/reviews.md:L86-243` (Review 1-4 focus areas and scope)
- `orchestration/templates/pantry.md:L104-155` (Section 2 review data file composition)
- `~/.claude/agents/big-head.md:L1-31` (understand how Big Head deduplicates, for context)

Do NOT edit:
- `~/.claude/agents/big-head.md` (separate task ant-farm-7k1 owns this)
- `orchestration/templates/implementation.md` (unrelated)
- `orchestration/templates/scout.md` (unrelated)
- `orchestration/templates/checkpoints.md` (unrelated)
- `orchestration/RULES.md` (separate task ant-farm-0cf may touch this)

## Focus
Your task is ONLY to add per-review-type scope fences, heuristics, and severity calibration to the Nitpicker agent definition(s).
Do NOT fix adjacent issues you notice.
Do NOT change Big Head's consolidation logic.
Do NOT restructure the review protocol in reviews.md beyond referencing scope boundaries.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
