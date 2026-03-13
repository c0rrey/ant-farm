# Task: ant-farm-cifp
**Status**: success
**Title**: Add explicit scope fencing to Nitpicker agent definitions per review type
**Type**: task
**Priority**: P2
**Epic**: ant-farm-6k0
**Agent Type**: technical-writer
**Dependencies**: blocks: [], blockedBy: []

## Affected Files
- `~/.claude/agents/nitpicker.md` — Add per-type specialization blocks with scope fences, heuristics, and severity calibration
- `orchestration/templates/reviews.md` — May need to reference new scope boundaries for consistency
- `orchestration/templates/pantry.md` — Review data files may need a REVIEW_TYPE marker if using conditional blocks

## Root Cause
All four Nitpicker reviewers (clarity, edge-cases, correctness, excellence) share a single agent MD file with no review-type-specific identity. Differentiation comes entirely from the Pantry-composed data files. Each reviewer has no baked-in understanding of what is NOT its responsibility, leading to duplicate findings across reviewers that Big Head must deduplicate after the fact.

## Expected Behavior
Add per-review-type specialization blocks to the Nitpicker agent definition(s). For each review type, define explicit 'NOT your responsibility' list referencing other three review types, type-specific heuristics, and type-specific severity calibration. Option (b) — single agent MD file with conditional sections keyed to a REVIEW_TYPE variable — is preferred for maintainability.

## Acceptance Criteria
1. Each Nitpicker reviewer has explicit 'not my job' boundaries that reference the other three review types by name
2. Type-specific severity calibration is defined (what constitutes P1/P2/P3 for each type)
3. Big Head deduplication load is reduced — fewer cross-type duplicate findings at source
4. Shared concerns (report format, output structure, messaging guidelines) remain in one place, not duplicated across 4 files
