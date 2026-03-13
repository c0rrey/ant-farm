# Task Brief: ant-farm-m2cb
**Task**: Split definitions/calibration guidance across distant locations — rename Priority Calibration, consolidate Information Diet, move Review Quality Metrics
**Agent Type**: general-purpose
**Summary output path**: .beads/agent-summaries/_session-86c76859/summaries/m2cb.md

## Context
- **Affected files**:
  - `orchestration/RULES.md:L572-579` -- Priority Calibration section defines P1/P2/P3 differently from the Nitpicker severity system used in Step 3c
  - `orchestration/RULES.md:L389-399` -- Information Diet section partially duplicates Queen Read Permissions at L23-54 without clear rationale for the duplication
  - `orchestration/templates/reviews.md:L1049-1063` -- Review Quality Metrics section placed at end of file, far from reviewer instructions that consume it
- **Root cause**: Secondary definitions (Priority Calibration), summaries (Information Diet), and calibration targets (Review Quality Metrics) are placed far from their primary usage context. Priority Calibration at RULES.md:L572-579 defines P1 as "build failure, broken links, data loss, security vulnerability" while the Nitpicker severity system in reviews.md defines P1-P2 as "critical, must fix before deploy" for correctness -- these are related but distinct scales. Information Diet at RULES.md:L389-399 duplicates the READ/DO NOT READ/NEVER READ summary that Queen Read Permissions at L23-54 already provides authoritatively. Review Quality Metrics at reviews.md:L1049-1063 is 1000+ lines away from the reviewer instructions it calibrates.
- **Expected behavior**: (1) Priority Calibration is clearly distinguished from review severity by renaming to "Bead Priority Calibration" with a note. (2) Information Diet either consolidates into Queen Read Permissions or adds an explicit cross-reference stating which is authoritative. (3) Review Quality Metrics is relocated to immediately after the review type sections so reviewers encounter it in context.
- **Acceptance criteria**:
  1. RULES.md:L572-579 "Priority Calibration" is renamed to "Bead Priority Calibration" and includes a note distinguishing it from the Nitpicker review severity scale (e.g., "This calibration applies to bead filing priority, not review finding severity")
  2. RULES.md:L389-399 Information Diet section either consolidates with Queen Read Permissions (L23-54) or adds an explicit cross-reference stating "Authoritative source: Queen Read Permissions above"
  3. reviews.md Review Quality Metrics section (currently L1049-1063) is relocated to appear immediately after the last review type section (Review 4: Drift, ending around L365) and before the Nitpicker Report Format section
  4. No content is lost -- all original guidance text is preserved in its new location
  5. Cross-references from other files to these sections (if any) still resolve correctly after the move

## Scope Boundaries
Read ONLY:
- `orchestration/RULES.md:L1-587` (full file -- need to understand Queen Read Permissions at L23-54, Information Diet at L389-399, Priority Calibration at L572-579)
- `orchestration/templates/reviews.md:L1-1063` (full file -- need to understand review type sections ending ~L365, Nitpicker Report Format at L367, Review Quality Metrics at L1049-1063)

Do NOT edit:
- `orchestration/templates/pantry.md` (not in scope)
- `orchestration/templates/big-head-skeleton.md` (not in scope -- ant-farm-60em handles this file)
- `scripts/build-review-prompts.sh` (not in scope -- ant-farm-bzl6 handles this file)
- Any file not listed in Affected files above

## Focus
Your task is ONLY to rename Priority Calibration, consolidate Information Diet, and move Review Quality Metrics.
Do NOT fix adjacent issues you notice.

## Summary Doc Sections (all required)
1. Approaches Considered (4+ genuinely distinct)
2. Selected Approach with rationale
3. Implementation description
4. Correctness Review (per-file, with acceptance criteria verification)
5. Build/Test Validation
6. Acceptance Criteria checklist (each criterion + PASS/FAIL)
