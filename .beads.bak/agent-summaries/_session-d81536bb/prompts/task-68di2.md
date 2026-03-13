# Task Brief: ant-farm-68di.2
**Task**: Add ESV checkpoint to checkpoints.md
**Agent Type**: prompt-engineer
**Summary output path**: .beads/agent-summaries/_session-d81536bb/summaries/68di2.md

## Context
- **Affected files**:
  - orchestration/templates/checkpoints.md:L1-723 — add new ESV section following existing checkpoint patterns (WWD at L270, DMVDC at L342, CCB at L507, SSV at L616)
- **Root cause**: N/A (feature task). The ESV (Exec Summary Verification) checkpoint does not exist yet. It needs to be added to checkpoints.md so Pest Control can verify exec summary and CHANGELOG correctness before push.
- **Expected behavior**: An ESV (Exec Summary Verification) section exists in checkpoints.md with 6 mechanical checks (task coverage, commit coverage, open bead accuracy, CHANGELOG fidelity, section completeness, metric consistency), following the structural pattern of existing checkpoints.
- **Acceptance criteria**:
  1. ESV section added to checkpoints.md with all 6 checks documented (task coverage, commit coverage, open bead accuracy, CHANGELOG fidelity, section completeness, metric consistency)
  2. Each check specifies: what inputs the PC agent reads, the exact pass condition, and the failure output format
  3. ESV section structure matches the pattern of existing checkpoints (WWD at L270, DMVDC at L342, CCB at L507, SSV at L616) — header, overview, numbered checks, verdict format, artifact path
  4. Artifact output path documented as {SESSION_DIR}/pc/pc-session-esv-{timestamp}.md
  5. Verdict format includes per-check PASS/FAIL status and an overall PASS/FAIL verdict
  6. The bd show guard pattern from DMVDC Check 2 (checkpoints.md:L373-378) is applied to the open bead accuracy check (Check 3)

## Scope Boundaries
Read ONLY:
- orchestration/templates/checkpoints.md:L1-723 (full file, to understand existing patterns and find correct insertion point)
- docs/plans/2026-02-22-exec-summary-scribe-design.md:L121-145 (ESV checkpoint specification from design doc)

Do NOT edit:
- orchestration/templates/scribe-skeleton.md (belongs to ant-farm-68di.1)
- orchestration/RULES.md (belongs to ant-farm-68di.3)
- docs/plans/2026-02-22-exec-summary-scribe-design.md (read-only reference)
- Any existing checkpoint sections (WWD, DMVDC, CCB, SSV, CCO) — only ADD the new ESV section

## Focus
Your task is ONLY to add the ESV checkpoint section to orchestration/templates/checkpoints.md.
Do NOT fix adjacent issues you notice in existing checkpoint sections.
The design spec at docs/plans/2026-02-22-exec-summary-scribe-design.md:L121-145 contains the ESV checkpoint specification. Use it as your primary source of truth for the 6 checks. Follow the structural pattern of existing checkpoints (especially SSV at L616 as the most recently added checkpoint) for formatting conventions.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
