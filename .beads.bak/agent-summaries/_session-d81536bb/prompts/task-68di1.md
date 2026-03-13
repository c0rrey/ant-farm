# Task Brief: ant-farm-68di.1
**Task**: Create Scribe skeleton template
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-d81536bb/summaries/68di1.md

## Context
- **Affected files**:
  - orchestration/templates/scribe-skeleton.md — NEW FILE to create (Scribe agent template)
  - orchestration/templates/dirt-pusher-skeleton.md:L27-32 — read-only reference for Step 0 pattern
  - CHANGELOG.md:L1-50 — read-only reference for existing convention
  - docs/plans/2026-02-22-exec-summary-scribe-design.md:L1-207 — read-only reference for full Scribe specification
- **Root cause**: N/A (feature task). No Scribe skeleton template exists yet. The exec summary agent needs a skeleton template following the same structural pattern as the dirt-pusher-skeleton.md.
- **Expected behavior**: A complete Scribe skeleton template exists at orchestration/templates/scribe-skeleton.md that follows the dirt-pusher-skeleton.md structural pattern, specifies all 7 input sources, defines the exec-summary.md output format with 5 sections, and includes CHANGELOG derivation rules.
- **Acceptance criteria**:
  1. File orchestration/templates/scribe-skeleton.md exists and is valid markdown
  2. Template includes Step 0 (read data file) matching the pattern in dirt-pusher-skeleton.md:L28-32
  3. Template specifies all 7 input sources to read (briefing.md, summaries/*.md, review-consolidated-*.md, progress.log, git diff --stat, git log --oneline, bd show)
  4. Template includes the exact exec-summary.md output format with all 5 required sections: At a Glance (metrics table), Work Completed, Review Findings, Open Issues, Observations
  5. Template includes CHANGELOG derivation rules specifying what to include (session header, summary, work completed, review stats) and what to omit (Observations, Open Issues)
  6. Template's CHANGELOG format matches the existing convention observable in CHANGELOG.md (verify by reading the current file)
  7. Template includes a duration calculation instruction (derive from progress.log first and last timestamps)
  8. No placeholder text or TODOs remain in the template — it is ready for agent consumption

## Scope Boundaries
Read ONLY:
- orchestration/templates/dirt-pusher-skeleton.md:L1-48 (full file, structural reference for skeleton pattern)
- CHANGELOG.md:L1-50 (convention reference for CHANGELOG format)
- docs/plans/2026-02-22-exec-summary-scribe-design.md:L1-207 (full design specification)

Do NOT edit:
- orchestration/templates/dirt-pusher-skeleton.md (read-only reference)
- CHANGELOG.md (read-only reference)
- docs/plans/2026-02-22-exec-summary-scribe-design.md (read-only reference)
- orchestration/templates/checkpoints.md (belongs to ant-farm-68di.2)
- orchestration/RULES.md (belongs to ant-farm-68di.3)
- Any other existing orchestration templates

## Focus
Your task is ONLY to create the Scribe skeleton template at orchestration/templates/scribe-skeleton.md.
Do NOT fix adjacent issues you notice.
The design spec at docs/plans/2026-02-22-exec-summary-scribe-design.md contains the full specification for inputs, outputs, exec-summary format, and CHANGELOG derivation rules. Use it as your primary source of truth.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
