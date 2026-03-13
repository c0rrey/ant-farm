# Task Brief: ant-farm-4vg
**Task**: AGG-027: Standardize review type naming between display titles and short names
**Agent Type**: technical-writer
**Summary output path**: .beads/agent-summaries/_session-8b93f5/summaries/4vg.md

## Context
- **Affected files**:
  - `orchestration/templates/reviews.md:L69` — uses "Correctness Redux Review (P1-P2)" as display title in team setup
  - `orchestration/templates/reviews.md:L90` — uses "Correctness Redux Review (P1-P2)" in round 2+ team setup
  - `orchestration/templates/reviews.md:L147` — table header uses "Correctness Redux" as display name
  - `orchestration/templates/reviews.md:L227` — section header "Review 3: Correctness Redux (P1-P2)"
  - `orchestration/templates/reviews.md:L253` — file output uses short name `correctness-review-<timestamp>.md`
  - `orchestration/templates/reviews.md:L156` — "Review 1: Clarity (P3)" display title
  - `orchestration/templates/reviews.md:L189` — "Review 2: Edge Cases (P2)" display title
  - `orchestration/templates/reviews.md:L272` — "Review 4: Excellence (P3)" display title
  - `orchestration/templates/nitpicker-skeleton.md:L9` — uses short names: "clarity / edge-cases / correctness / excellence"
  - `orchestration/templates/nitpicker-skeleton.md:L18` — template uses `{REVIEW_TYPE}` placeholder with short names
  - `orchestration/templates/implementation.md:L6` — no review type naming (reference only)
- **Root cause**: reviews.md uses "Correctness Redux" as a display title while filenames and skeleton placeholders use "correctness". This inconsistency increases parsing friction in chained prompts. The other three review types (Clarity, Edge Cases, Excellence) have display titles that closely match their short names, but no explicit mapping table exists for any of them.
- **Expected behavior**: Each review type has one canonical name used in both templates and filenames. If display and short forms both exist, a mapping table documents the correspondence.
- **Acceptance criteria**:
  1. Each review type has one canonical name used in both templates and filenames
  2. If display and short forms both exist, a mapping table documents the correspondence
  3. No template uses a review type name that differs from the canonical form without explanation

## Scope Boundaries
Read ONLY:
- `orchestration/templates/reviews.md:L1-828` (full file)
- `orchestration/templates/nitpicker-skeleton.md:L1-42` (full file)
- `orchestration/templates/checkpoints.md:L475-500` (review-related sections referencing review type names)

Do NOT edit:
- `orchestration/templates/implementation.md` (not a review naming concern)
- `orchestration/templates/checkpoints.md` (downstream consumer; if naming changes here are needed, document as adjacent issue)
- `orchestration/templates/big-head-skeleton.md` (downstream consumer; document as adjacent issue if affected)
- `orchestration/templates/pantry.md` (downstream consumer; document as adjacent issue if affected)
- `CLAUDE.md`, `README.md` (off-limits per process rules)

## Focus
Your task is ONLY to standardize review type naming between display titles and short names in reviews.md and nitpicker-skeleton.md, and add a mapping table if both forms are retained.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
